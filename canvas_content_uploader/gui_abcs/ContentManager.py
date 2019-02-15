import tkinter
from abc import ABC, abstractmethod
from enum import Enum
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING

from canvasapi.exceptions import Unauthorized

from canvas_content_uploader.gui_abcs.Task import Task, show_progress_bar

if TYPE_CHECKING:
    from canvas_content_uploader.root_components.MasterGui import MasterGui


class SortMode(Enum):
    MOST_RECENT_UPDATE = 'Most Recently Updated'
    ALPHA = 'Alphabetical'


class ContentManager(Task, ABC):
    """
    Abstract Base Class used to view and delete existing Canvas Content.
    """
    def __init__(self, master_gui: 'MasterGui', item_name: str, has_publish_btn=False):
        super().__init__(master_gui)
        self.item_name = item_name
        self.item_list_var = tkinter.StringVar()
        self.sort_var = tkinter.StringVar()
        self.sort_var.set(SortMode.ALPHA.value)
        self.has_publish_btn = has_publish_btn

        self.item_frame = ttk.Frame(self.frame)

        self.item_listbox = tkinter.Listbox(self.item_frame, width=30, relief='sunken', state='disabled',
                                            activestyle='none', selectmode='extended',
                                            listvariable=self.item_list_var)
        self.item_listbox.bind('<Double-1>', lambda x: self.double_click_callback())

        self.x_scroll = ttk.Scrollbar(self.item_frame, orient='horizontal',
                                      command=self.item_listbox.xview)
        self.y_scroll = ttk.Scrollbar(self.item_frame, orient='vertical',
                                      command=self.item_listbox.yview)
        self.item_listbox.configure(xscrollcommand=self.x_scroll.set,
                                    yscrollcommand=self.y_scroll.set)

        self.item_listbox.grid(row=0, column=0, sticky='NSE')
        self.x_scroll.grid(row=1, column=0, sticky='NEW')
        self.y_scroll.grid(row=0, column=1, sticky='NSW')

        self.button_frame = ttk.Frame(self.frame)

        if self.has_publish_btn:
            self.publish_btn = ttk.Button(self.button_frame, text=f'Publish Selected {self.item_name}(s)',
                                          command=self.publish_selected_items, state='disabled')

        self.delete_btn = ttk.Button(self.button_frame, text=f'Delete Selected {self.item_name}(s)',
                                     command=self.delete_selected_items, state='disabled')

        if self.has_publish_btn:
            self.publish_btn.grid(row=0, column=0, padx=5, pady=5)

        self.delete_btn.grid(row=1, column=0, padx=5, pady=5)

        self.combo_frame = ttk.Frame(self.frame)
        sort_options = list(x.value for x in SortMode)
        self.sort_combo_lbl = ttk.Label(self.combo_frame, text='Sort by:', state='disabled')
        self.sort_combo = ttk.Combobox(self.combo_frame, width=22, values=sort_options,
                                       textvariable=self.sort_var,
                                       state='disabled')
        self.sort_combo_lbl.grid(row=0, column=0, sticky='NW')
        self.sort_combo.grid(row=1, column=0, sticky='NW', padx=5, pady=5)

        self.button_frame.grid(row=1, column=2, sticky='SW')
        self.item_frame.grid(row=0, column=0, rowspan=2)
        self.combo_frame.grid(row=0, column=2, sticky='NW')

        self.sort_var.trace('wu', lambda x, y, z: self.update_content_list())

    @abstractmethod
    def get_items(self):
        pass

    @abstractmethod
    def get_display_names(self, item_list):
        pass

    @abstractmethod
    def recent_sort_key(self, item):
        pass

    @abstractmethod
    def alpha_sort_key(self, item):
        pass

    @abstractmethod
    def cleanup_displayed_name(self, displayed_name):
        pass

    def publish_item_by_displayed_name(self, displayed_name):
        pass

    @abstractmethod
    def delete_item_by_displayed_name(self, displayed_name):
        pass

    @abstractmethod
    def double_click_callback(self):
        pass

    def get_selected_item(self):
        index = self.item_listbox.curselection()
        item = self.item_listbox.get(index)
        return item

    def handle_course_change(self):
        self.update_content_list()

    def enable_selection(self):
        self.item_listbox.configure(state='normal')
        self.enable_buttons()
        self.sort_combo_lbl.configure(state='enable')
        self.sort_combo.configure(state='readonly')

        course_id = self.get_selected_course_id()
        if course_id:
            self.load_and_sort_items()

    def enable_buttons(self):
        self.delete_btn.configure(state='enable')
        if self.has_publish_btn:
            self.publish_btn.configure(state='enable')

    def disable_buttons(self):
        if self.has_publish_btn:
            self.publish_btn.configure(state='disable')
        self.delete_btn.configure(state='disable')

    @show_progress_bar
    def load_and_sort_items(self):
        item_list = self.get_items()

        sort_mode = self.sort_var.get()

        if sort_mode == SortMode.MOST_RECENT_UPDATE.value:
            item_list.sort(key=self.recent_sort_key, reverse=True)
        elif sort_mode == SortMode.ALPHA.value:
            item_list.sort(key=self.alpha_sort_key)

        displayed_items = self.get_display_names(item_list)

        self.item_list_var.set(displayed_items)

        self.clear_selections()

    def clear_selections(self):
        self.item_listbox.selection_clear(0, 'end')

    def update_content_list(self):
        course_id = self.get_selected_course_id()

        if course_id:
            self.load_and_sort_items()
        else:
            self.item_list_var.set('')

        loaded_items = self.item_list_var.get()

        if not loaded_items:
            self.disable_buttons()
        else:
            self.enable_buttons()

    def get_selected_course_id(self):
        return super().get_selected_course_id()

    def publish_selected_items(self):
        selected_items = self.get_selected_items()
        for displayed_name in selected_items:
            self.publish_item_by_displayed_name(displayed_name)

        self.load_and_sort_items()

    def delete_selected_items(self):
        selected_items = self.get_selected_items()
        ok_delete = self.ask_delete(selected_items)
        if ok_delete:
            for displayed_name in selected_items:
                try:
                    self.delete_item_by_displayed_name(displayed_name)
                except Unauthorized:
                    messagebox.showerror('Unauthorized',
                                         f'User is not authorized to remove {self.item_name}: "{displayed_name}"')
            self.load_and_sort_items()

    def get_selected_items(self):
        selected = []
        for x in self.item_listbox.curselection():
            item = self.item_listbox.get(x)
            item = self.cleanup_displayed_name(item)
            selected.append(item)
        return selected

    def get_item_index_by_displayed_name(self, name):
        index = self.item_listbox.get(0, "end").index(name)
        return index

    def ask_delete(self, item_list) -> str:
        item_type = self.item_name
        item_string = ''
        for p in item_list:
            item_string += f'\"{p}\"\n'
        answer = messagebox.askokcancel(f'Deleting {item_type}(s)',
                                        message=f'Are you sure you wish to delete the following {item_type}(s)?'
                                                f'\n\n{item_string}',
                                        icon='warning')
        return answer
