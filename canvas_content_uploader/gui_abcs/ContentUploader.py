import tkinter
from abc import ABC, abstractmethod
from pathlib import Path
from tkinter import ttk, messagebox, filedialog, simpledialog
from typing import List
from typing import TYPE_CHECKING

from canvasapi.exceptions import BadRequest

from canvas_content_uploader.exceptions import UserCanceledUpload
from canvas_content_uploader.gui_abcs.Task import Task, show_progress_bar

if TYPE_CHECKING:
    from canvas_content_uploader.root_components.MasterGui import MasterGui


class ContentUploader(Task, ABC):
    """
    Abstract Base Class used to upload new Canvas content.
    """
    def __init__(self, master_gui: 'MasterGui', item_name: str, check_for_conflicts=True, title_required=True):
        super().__init__(master_gui)
        self.browse_file_types = None
        self.queued_files = []
        self.item_name = item_name
        self.check_for_conflicts = check_for_conflicts
        self.title_required = title_required

        self.selected_lbl = ttk.Label(self.frame,
                                      text='Selected files: None', state='disabled')

        self.browse_btn = ttk.Button(self.frame,
                                     text='Browse...', command=self.browse_btn_callback, state='disabled')

        self.upload_btn = ttk.Button(self.frame,
                                     text=f'Upload {self.item_name}(s)', command=self.upload_btn_callback,
                                     state='disabled')

        self.overwrite_checkbox_var = tkinter.IntVar()
        self.overwrite_checkbox = ttk.Checkbutton(self.frame,
                                                  text='Force Overwrite', variable=self.overwrite_checkbox_var,
                                                  state='disabled')

        self.selected_lbl.grid(row=0, column=0, columnspan=2, padx=5, pady=2.5, sticky='W')
        self.browse_btn.grid(row=1, column=0, padx=5)
        self.upload_btn.grid(row=1, column=1, padx=5)
        self.overwrite_checkbox.grid(row=1, column=2, padx=5)

    @abstractmethod
    def get_existing_item_titles_as_list(self) -> list:
        pass

    @abstractmethod
    def prepare_item_with_title(self, file_path: Path, title: str):
        pass

    @abstractmethod
    def handle_course_change(self):
        pass

    @show_progress_bar
    @abstractmethod
    def upload_item_to_course(self, item):
        pass

    @show_progress_bar
    @abstractmethod
    def overwrite_item(self, title: str, new_item):
        pass

    @abstractmethod
    def get_title_from_file_path(self, file_path: Path) -> str:
        pass

    def enable_selection(self):
        self.browse_btn.configure(state='active')
        self.selected_lbl.configure(state='active')

        if self.check_for_conflicts:
            self.overwrite_checkbox.configure(state='active')

    def get_selected_course_id(self):
        return super().get_selected_course_id()

    def upload_btn_callback(self):
        existing_titles = self.get_existing_item_titles_as_list()
        force_overwrite = self.overwrite_checkbox_var.get()

        for path in self.queued_files:
            try:
                if self.check_for_conflicts:
                    self.upload_item_with_conflict_check(existing_titles, force_overwrite, path)
                else:
                    self.upload_item_without_conflict_check(path)
            except UserCanceledUpload:
                continue
            except BadRequest as e:
                if '"message":"too_long"' in e.message:
                    messagebox.showerror('Body Too Long',
                                         f'The following file is too large to upload:'
                                         f'\n\n{path}')
                    continue
        messagebox.showinfo('Upload Complete',
                            f'Finished uploading {self.item_name}(s)')
        self.queued_files = []
        self.update_widgets()

    def upload_item_without_conflict_check(self, path: Path):
        if self.title_required:
            title = self.get_title_from_file_path(path)
            item = self.prepare_item_with_title(path, title)
        else:
            item = path
        self.upload_item_to_course(item)

    def upload_item_with_conflict_check(self, existing_titles: List[str], force_overwrite: bool, item):
        title = self.get_title_from_file_path(item)
        if force_overwrite == 1:
            overwrite = True
        else:
            overwrite = False
        if title in existing_titles:
            name_conflict = True
        else:
            name_conflict = False
        while name_conflict:
            if title not in existing_titles or overwrite:
                break

            rename = self.ask_rename_item(title)

            if rename == 'yes':
                title = simpledialog.askstring(f'Rename {self.item_name}', 'New Title:')
            elif rename == 'no':
                overwrite = self.prompt_ask_overwrite(title)
            else:
                raise UserCanceledUpload
        item = self.prepare_item_with_title(item, title)
        if overwrite and title in existing_titles:
            self.overwrite_item(title, item)
        else:
            self.upload_item_to_course(item)
        existing_titles.append(title)

    def browse_btn_callback(self):
        selected_files = self.prompt_files()
        self.queued_files = [Path(x) for x in selected_files]
        self.update_widgets()

    def prompt_ask_overwrite(self, title: str) -> str:
        r = messagebox.askokcancel('Overwrite Page',
                                   message=f'Are you sure you wish to overwrite the following {self.item_name}?'
                                           f'\n\n"{title}"',
                                   icon='warning')
        return r

    def ask_rename_item(self, title) -> str:
        r = messagebox.showwarning('Conflicting Title',
                                   f'WARNING: A {self.item_name} with the following title already exists:\n\n'
                                   f'"{title}"\n\n'
                                   'Rename file before uploading? \n\n'
                                   f'(Selecting "No" will OVERWRITE the existing {self.item_name}.)',
                                   type='yesnocancel')
        return r

    def prompt_files(self):
        if self.browse_file_types:
            files = filedialog.askopenfilename(multiple=True,
                                               filetypes=(self.browse_file_types,
                                                          ("all files", "*.*")))
        else:
            files = filedialog.askopenfilename(multiple=True)
        return files

    def update_selection_lbl(self):
        num_selected = len(self.queued_files)
        if num_selected == 0:
            num_selected = 'None'
        self.selected_lbl.configure(text=f'{self.item_name}(s) to Upload: {num_selected}')

    def update_upload_btn(self):
        num_selected = len(self.queued_files)
        if num_selected == 0:
            self.upload_btn.configure(state='disabled')
        else:
            self.upload_btn.configure(state='active')

    def update_widgets(self):
        self.update_selection_lbl()
        self.update_upload_btn()



