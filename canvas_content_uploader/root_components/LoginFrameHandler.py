import tkinter
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING

from canvasapi.exceptions import InvalidAccessToken, ResourceDoesNotExist, Unauthorized
from requests.exceptions import InvalidHeader, ConnectionError

from canvas_content_uploader.exceptions import NoCoursesLoaded

if TYPE_CHECKING:
    from canvas_content_uploader.root_components.MasterGui import MasterGui
    from canvas_content_uploader.root_components.CanvasSessionHandler import CanvasSessionHandler


class LoginFrameHandler:
    """
    Handle logging in and selecting Canvas courses.
    """
    def __init__(self, master_gui: 'MasterGui'):
        self.csh: 'CanvasSessionHandler' = master_gui.csh
        self.master_frame: ttk.Frame = master_gui.login_frame
        self.master_gui = master_gui
        self.frame = ttk.Frame(self.master_frame)
        self.courses = None

        self.selected_course_combo_var = self.master_gui.selected_course_combo_var
        self.selected_course_combo_var.trace('w', lambda x, y, z: self.load_selected_course_id())

        self.selected_course_id_var = self.master_gui.selected_course_id_var

        self.selected_course_name_var = tkinter.StringVar()

        self.course_id_entry_var = tkinter.StringVar()

        self.course_id_checkbox_var = tkinter.IntVar()

        self.token_frame = ttk.Frame(self.frame)

        self.token_entry_lbl = ttk.Label(self.token_frame, text='Token:')

        self.token_entry_box = ttk.Entry(self.token_frame, show='*', width=25)
        self.init_login_entry_listener()

        self.login_btn = ttk.Button(self.token_frame,
                                    text='Token Login', command=self.login_btn_callback, state='disabled')

        self.course_combo_lbl = ttk.Label(self.token_frame, text='Course:', state='disabled')
        self.course_combo = ttk.Combobox(self.token_frame,
                                         width=22, state='disabled', textvariable=self.selected_course_combo_var)

        self.course_id_check_btn = ttk.Checkbutton(self.token_frame,
                                                   text='Select by ID', variable=self.course_id_checkbox_var,
                                                   state='disabled', command=self.course_id_checkbox_callback)

        self.token_entry_lbl.grid(row=0, column=0, padx=5, pady=2.5)
        self.token_entry_box.grid(row=0, column=1, padx=5, pady=2.5)
        self.login_btn.grid(row=0, column=2, padx=5, pady=2.5)
        self.course_combo_lbl.grid(row=1, column=0, padx=5, pady=2.5)
        self.course_combo.grid(row=1, column=1, padx=5, pady=2.5)
        self.course_id_check_btn.grid(row=1, column=2, padx=5, pady=2.5)

        self.token_frame.grid(row=0, column=0, sticky='W', padx=5)

        self.course_id_entry_frame = ttk.Frame(self.frame)

        self.course_id_entry_lbl = ttk.Label(self.course_id_entry_frame, text='Course ID:')
        self.course_id_entry = ttk.Entry(self.course_id_entry_frame, width=22)
        self.course_id_entry.configure(textvariable=self.course_id_entry_var)
        self.course_id_validate_btn = ttk.Button(self.course_id_entry_frame, text='Select',
                                                 command=self.select_by_course_id_select_btn_callback)

        self.course_id_entry_lbl.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.course_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.course_id_validate_btn.grid(row=0, column=2, padx=5, pady=5, sticky='w')

        self.course_id_selection_frame = ttk.Frame(self.course_id_entry_frame)
        self.selected_course_id_lbl = ttk.Label(self.course_id_selection_frame, text='Selected Course:')
        self.selected_course_id = ttk.Label(self.course_id_selection_frame,
                                            textvariable=self.selected_course_id_var)
        self.selected_course_name_lbl = ttk.Label(self.course_id_selection_frame, wraplength=200,
                                                  textvariable=self.selected_course_name_var)

        self.course_id_selection_frame.grid(row=1, column=0, columnspan=5, sticky='W')
        self.selected_course_id_lbl.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='W')
        self.selected_course_id.grid(row=0, column=2, padx=5, pady=5, sticky='W')
        self.selected_course_name_lbl.grid(row=1, column=2, rowspan=2, columnspan=5, padx=5, pady=5, sticky='W')

    def init_sel_by_course_id_frame(self):
        self.course_id_entry_frame.grid(row=2, column=0, sticky='W', padx=5, pady=2.5)

    def init_login_entry_listener(self):
        self.token_entry_box.sv = tkinter.StringVar()
        sv = self.token_entry_box.sv
        sv.trace('w', lambda x, y, z: self.login_btn.configure(state='active'))
        self.token_entry_box.configure(textvariable=sv)

    def get_frame(self):
        return self.frame

    def login_btn_callback(self):
        try:
            self.init_session_from_token()
            self.load_courses_to_list()
            self.load_courses_into_course_combo()
            self.handle_successful_login()
        except (InvalidAccessToken, InvalidHeader, ValueError):
            messagebox.showerror('Invalid Access Token',
                                 'Invalid or missing token')
        except (ResourceDoesNotExist, ConnectionError):
            messagebox.showerror('Invalid URL',
                                 'Invalid Canvas URL.\n'
                                 'Check \"canvas_url\" entry in config.ini.')
        except NoCoursesLoaded:
            messagebox.showwarning('No Courses Loaded',
                                   'Login successful, but no enrolled courses found.\n'
                                   'Try selecting by course ID.')
            self.handle_successful_login()

    def handle_successful_login(self):
        self.disable_token_widgets()
        self.enable_course_selection()
        self.master_gui.has_token_var.set(True)
        self.master_gui.enable_task_selection()
        self.enable_selection()

    def course_id_checkbox_callback(self):
        self.clear_selected_course_vars()

        if self.course_id_checkbox_var.get() == 1:
            self.init_sel_by_course_id_frame()
            self.disable_course_combo_widgets()

        else:
            self.course_id_entry_frame.grid_forget()
            self.enable_course_combo()
            try:
                self.load_selected_course_id()
            except NoCoursesLoaded:
                self.clear_selected_course_vars()

    def disable_course_combo_widgets(self):
        self.course_combo_lbl.configure(state='disabled')
        self.course_combo.configure(state='disabled')

    def clear_selected_course_vars(self):
        self.selected_course_id_var.set(0)
        self.selected_course_name_var.set('')

    def select_by_course_id_select_btn_callback(self):
        c = self.csh
        course_id = self.course_id_entry.get()
        try:
            course = c.get_course(course_id)
            self.selected_course_id_var.set(course.id)
            self.selected_course_name_var.set(course.name)
        except TypeError:
            messagebox.showerror('Invalid Course ID',
                                 'Invalid or missing course ID.')
        except ResourceDoesNotExist:
            messagebox.showerror('Unable to Access Course',
                                 f'Can not access course with ID: {course_id}')
        except Unauthorized:
            messagebox.showerror('Unauthorized',
                                 f'User is not authorized to access course with ID: {course_id}')

    def init_session_from_token(self):
        c = self.csh
        token = self.token_entry_box.get()
        c.token = token.strip()
        c.login()

    def enable_selection(self):
        self.master_gui.current_task.enable_selection()

    def load_courses_to_list(self):
        c = self.csh
        courses = list(c for c in c.get_enrolled_courses())

        try:
            assert courses
        except AssertionError:
            raise NoCoursesLoaded

        courses.sort(key=lambda x: x.id)
        self.courses = courses

    def load_courses_into_course_combo(self):
        combo_values = list(f'{c.name}: ({c.id})' for c in self.courses)
        self.course_combo.configure(values=combo_values)
        self.course_combo.current(0)

    def load_selected_course_id(self):
        if self.course_id_checkbox_var.get() == 1:
            course_id = self.course_id_entry.get()
        else:
            try:
                course_id = self.get_course_id_from_combo_selection()
            except NoCoursesLoaded:
                raise

        self.selected_course_id_var.set(course_id)

    def get_course_id_from_combo_selection(self):
        if not self.courses:
            raise NoCoursesLoaded
        index = self.course_combo.current()
        course_id = self.courses[index].id
        return course_id

    def enable_course_selection(self):
        self.enable_course_combo()
        self.course_id_check_btn.configure(state='enable')
        if self.course_combo.get():
            self.course_combo.current(0)

    def enable_course_combo(self):
        self.course_combo_lbl.configure(state='enable')
        self.course_combo.configure(state='readonly')

    def disable_token_widgets(self):
        self.token_entry_lbl.configure(state='disabled')
        self.token_entry_box.configure(state='disabled')
        self.login_btn.configure(state='disabled')
