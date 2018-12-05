import enum
import tkinter
import webbrowser
from tkinter import ttk

from canvas_content_uploader.gui_abcs.Task import Task, show_progress_bar


class CourseScope(enum.Enum):
    SELECTED = 0
    ENROLLED = 1


class WordScope(enum.Enum):
    FULL = 0
    PARTIAL = 1


class CaseScope(enum.Enum):
    IGNORE = 0
    MATCH = 1


class SearchPagesTask(Task):
    """
    Search for wiki pages with HTML that contain the given search term.
    """
    def __init__(self, master_gui):
        super().__init__(master_gui)

        self.results_var = tkinter.StringVar()
        self.results_lbl_var = tkinter.StringVar('')

        self.course_scope_var = tkinter.IntVar()
        self.word_scope_var = tkinter.IntVar()
        self.case_scope_var = tkinter.IntVar()

        self.entry_frame = ttk.Frame(self.frame)
        self.entry_lbl = ttk.Label(self.entry_frame, text='Search String:',
                                   state='disabled')
        self.entry_box = ttk.Entry(self.entry_frame, state='disabled')
        self.search_btn = ttk.Button(self.entry_frame, text='Search',
                                     command=self.search_btn_callback,
                                     state='disabled')

        self.entry_lbl.grid(row=0, column=0, padx=2.5, pady=2.5)
        self.entry_box.grid(row=0, column=1, padx=2.5, pady=2.5)
        self.entry_box.grid(row=0, column=2, padx=2.5, pady=2.5)
        self.search_btn.grid(row=0, column=3, padx=2.5, pady=2.5)

        self.scope_frame = ttk.Frame(self.frame)
        self.course_scope_lbl = ttk.Label(self.scope_frame, text='Course Scope:')
        self.selected_course_radio = ttk.Radiobutton(self.scope_frame, text='Selected',
                                                     variable=self.course_scope_var,
                                                     value=CourseScope.SELECTED.value)
        self.enrolled_course_radio = ttk.Radiobutton(self.scope_frame, text='Enrolled',
                                                     variable=self.course_scope_var,
                                                     value=CourseScope.ENROLLED.value)
        self.word_scope_label = ttk.Label(self.scope_frame, text='Word Scope:')
        self.full_word_radio = ttk.Radiobutton(self.scope_frame, text='Full',
                                               variable=self.word_scope_var,
                                               value=WordScope.FULL.value)
        self.partial_word_radio = ttk.Radiobutton(self.scope_frame, text='Partial',
                                                  variable=self.word_scope_var,
                                                  value=WordScope.PARTIAL.value)
        self.case_scope_label = ttk.Label(self.scope_frame, text='Case Scope:')
        self.ignore_case_radio = ttk.Radiobutton(self.scope_frame, text='Ignore',
                                                 variable=self.case_scope_var,
                                                 value=CaseScope.IGNORE.value)
        self.match_case_radio = ttk.Radiobutton(self.scope_frame, text='Match',
                                                variable=self.case_scope_var,
                                                value=CaseScope.MATCH.value)

        self.course_scope_lbl.grid(row=0, column=0, padx=2.5, pady=2.5, sticky='W')
        self.selected_course_radio.grid(row=0, column=1, padx=2.5, pady=2.5, sticky='W')
        self.enrolled_course_radio.grid(row=0, column=2, padx=2.5, pady=2.5, sticky='W')
        self.word_scope_label.grid(row=1, column=0, padx=2.5, pady=2.5, sticky='W')
        self.full_word_radio.grid(row=1, column=1, padx=2.5, pady=2.5, sticky='W')
        self.partial_word_radio.grid(row=1, column=2, padx=2.5, pady=2.5, sticky='W')
        self.case_scope_label.grid(row=2, column=0, padx=2.5, pady=2.5, sticky='W')
        self.ignore_case_radio.grid(row=2, column=1, padx=2.5, pady=2.5, sticky='W')
        self.match_case_radio.grid(row=2, column=2, padx=2.5, pady=2.5, sticky='W')

        self.results_frame = ttk.Frame(self.frame)
        self.results_lbl = ttk.Label(self.results_frame, text='No Results', textvariable=self.results_lbl_var)
        self.results_listbox = tkinter.Listbox(self.results_frame, width=50, relief='sunken', state='disabled',
                                               activestyle='none', listvariable=self.results_var)
        self.results_listbox.bind('<Double-1>', lambda x: self.open_selected_page())

        self.x_scroll = ttk.Scrollbar(self.results_frame, orient='vertical',
                                      command=self.results_listbox.yview)
        self.y_scroll = ttk.Scrollbar(self.results_frame, orient='horizontal',
                                      command=self.results_listbox.xview)
        self.results_listbox.configure(xscrollcommand=self.y_scroll.set,
                                       yscrollcommand=self.x_scroll.set)

        self.results_lbl.grid(row=0, column=0, sticky='W')
        self.results_listbox.grid(row=1, column=0, sticky='EW')
        self.x_scroll.grid(row=1, column=1, sticky='NS')
        self.y_scroll.grid(row=2, column=0, sticky='EW')

        self.entry_frame.grid(row=0, column=0, sticky='EW')
        self.scope_frame.grid(row=1, column=0, sticky='EW')
        self.scope_frame.grid(row=2, column=0, sticky='EW')
        self.results_frame.grid(row=3, column=0, sticky='EW', pady=5)

    def handle_course_change(self):
        pass

    def enable_selection(self):
        self.results_listbox.configure(state='normal')
        self.entry_lbl.configure(state='enabled')
        self.entry_box.configure(state='enabled')
        self.search_btn.configure(state='enabled')

    def get_selected_page(self):
        index = self.results_listbox.curselection()
        page = self.results_listbox.get(index)
        return page

    def open_selected_page(self):
        page_url = self.get_selected_page()
        webbrowser.open(page_url)

    def get_selected_course_id(self):
        return super().get_selected_course_id()

    @show_progress_bar
    def search_btn_callback(self):
        self.search_btn.configure(state='disabled')
        try:
            results = self.search_pages_for_string()
            self.results_var.set(results)
            self.update_results_label()
        finally:
            self.search_btn.configure(state='enabled')

    def search_pages_for_string(self):
        search_string = str(self.entry_box.get()).strip()
        assert search_string
        course_scope = self.course_scope_var.get()
        word_scope = self.word_scope_var.get()
        case_scope = self.case_scope_var.get()
        pages = []

        if word_scope == WordScope.FULL.value:
            whole_word = True
        else:
            whole_word = False

        if case_scope == CaseScope.IGNORE.value:
            ignore_case = True
        else:
            ignore_case = False

        if course_scope == CourseScope.ENROLLED.value:
            pages = self.csh.search_pages_from_enrolled_courses(search_string,
                                                                whole_word=whole_word,
                                                                ignore_case=ignore_case)
        elif course_scope == CourseScope.SELECTED.value:
            course_id = self.get_selected_course_id()
            pages = self.csh.search_pages_from_course(course_id, search_string,
                                                      whole_word=whole_word,
                                                      ignore_case=ignore_case)

        results = [p.html_url for p in pages]
        return results

    def update_results_label(self):
        num_results = len(self.results_listbox.get(0, 'end'))

        if num_results < 1:
            msg = 'No Matches Found.'
        else:
            msg = f'{num_results} Page(s) Match'

        self.results_lbl_var.set(msg)


