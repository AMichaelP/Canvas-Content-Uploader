import tkinter
from pathlib import Path
from tkinter import ttk, messagebox

from canvas_content_uploader.gui_abcs.Task import Task
from canvas_content_uploader.root_components.CanvasSessionHandler import CanvasSessionHandler
from canvas_content_uploader.root_components.LoginFrameHandler import LoginFrameHandler
from canvas_content_uploader.tasks.ManageFilesTask import ManageFilesTask
from canvas_content_uploader.tasks.ManagePagesTask import ManagePagesTask
from canvas_content_uploader.tasks.SearchPagesTask import SearchPagesTask
from canvas_content_uploader.tasks.TaskName import TaskName
from canvas_content_uploader.tasks.UploadFilesTask import UploadFilesTask
from canvas_content_uploader.tasks.UploadPagesTask import UploadPagesTask

DEFAULT_TASK = TaskName.UPLOAD_PAGES.name


class MasterGui:
    """
    Display and handle operations between root GUI components and Tasks.
    """
    def __init__(self, canvas_url: str, title: str, icon_path: Path = None):

        self.root = self.init_root(title, icon_path)
        self.root.resizable(0, 0)

        self.has_token_var = tkinter.BooleanVar()
        self.task_var = tkinter.StringVar()

        self.current_task: Task = None

        self.selected_course_combo_var = tkinter.StringVar()
        self.selected_course_id_var = tkinter.IntVar()

        self.csh = CanvasSessionHandler(canvas_url)

        self.login_frame = self.init_login_frame()
        self.task_frame = self.init_task_frame()

        self.set_course_change_traces()

        self.separator = self.init_separator()

        self.login_handler = LoginFrameHandler(self)
        self.login_handler.get_frame().grid()

        self.menu_bar = self.init_menu_bar()
        self.task_menu = self.init_task_menu(DEFAULT_TASK)
        self.menu_bar.add_cascade(label='Task', menu=self.task_menu, state='disabled')

        self.root.config(menu=self.menu_bar)

    def enable_task_selection(self):
        self.menu_bar.entryconfigure(2, state='normal')

    def set_course_change_traces(self):
        self.selected_course_combo_var.trace('wu', lambda x, y, z: self.current_task.handle_course_change())
        self.selected_course_id_var.trace('wu', lambda x, y, z: self.current_task.handle_course_change())

    def run(self):
        self.root.mainloop()

    @staticmethod
    def init_root(title: str, icon_path: str = None):
        r = tkinter.Tk()
        r.title(title)

        if icon_path:
            p = Path(icon_path)
            try:
                assert p.is_file()
                r.iconbitmap(p.as_posix())
            except AssertionError:
                messagebox.showerror('Icon File Not Found',
                                     'Could not locate the icon file defined in config.ini.\n'
                                     'The default icon will be used.')
            except tkinter.TclError:
                messagebox.showerror('Invalid Icon',
                                     'Could not set the icon defined in config.ini.\n'
                                     'Verify that the file is a .ico file or remove the entry to use the default icon.')

        return r

    def init_menu_bar(self) -> tkinter.Menu:
        menu = tkinter.Menu(self.root)

        file_menu = tkinter.Menu(menu, tearoff=0)
        file_menu.add_command(label='Quit', command=self.root.quit)
        menu.add_cascade(label='File', menu=file_menu)

        return menu

    def init_task_menu(self, default_task) -> tkinter.Menu:
        task_menu = tkinter.Menu(self.menu_bar, tearoff=0)
        self.task_var.trace('w', lambda x, y, z: self.handle_task_selection())

        self.task_var.set(default_task)

        task_menu.add_radiobutton(label='Upload New Pages',
                                  value=TaskName.UPLOAD_PAGES.name,
                                  variable=self.task_var)
        task_menu.add_radiobutton(label='Manage Existing Pages',
                                  value=TaskName.MANAGE_PAGES.name,
                                  variable=self.task_var)
        task_menu.add_radiobutton(label='Search Course Pages',
                                  value=TaskName.SEARCH_PAGES.name,
                                  variable=self.task_var)
        task_menu.add_separator()

        task_menu.add_radiobutton(label='Upload Files',
                                  value=TaskName.UPLOAD_FILES.name,
                                  variable=self.task_var)
        task_menu.add_radiobutton(label='Manage Existing Files',
                                  value=TaskName.MANAGE_FILES.name,
                                  variable=self.task_var)
        return task_menu

    def handle_task_selection(self):
        self.reset_task_frame()
        self.current_task = self.get_selected_task()
        self.current_task.grid()
        if self.has_token_var.get():
            self.current_task.enable_selection()

    def get_selected_task(self) -> Task:
        t = self.task_var.get()
        if t == TaskName.UPLOAD_PAGES.name:
            return UploadPagesTask(self)
        elif t == TaskName.MANAGE_PAGES.name:
            return ManagePagesTask(self)
        elif t == TaskName.SEARCH_PAGES.name:
            return SearchPagesTask(self)
        elif t == TaskName.UPLOAD_FILES.name:
            return UploadFilesTask(self)
        elif t == TaskName.MANAGE_FILES.name:
            return ManageFilesTask(self)

    def reset_task_frame(self):
        self.task_frame.destroy()
        del self.current_task
        self.task_frame = self.init_task_frame()

    def init_login_frame(self) -> ttk.Frame:
        frame = ttk.Frame(self.root, borderwidth=5)
        frame.grid(row=0, sticky='W')
        return frame

    def init_separator(self) -> ttk.Separator:
        sep = ttk.Separator(self.root, orient='horizontal')
        sep.grid(row=1, sticky='EW')
        return sep

    def init_task_frame(self) -> ttk.Frame:
        frame = ttk.Frame(self.root, borderwidth=5)
        frame.grid(row=2, sticky='W', pady=5)
        return frame
