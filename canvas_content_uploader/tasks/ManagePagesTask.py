import webbrowser
from pathlib import Path

from canvas_content_uploader.gui_abcs.ContentManager import ContentManager
from tkinter import messagebox


class ManagePagesTask(ContentManager):

    """
    View or remove wiki pages existing within the selected course.
    """
    def __init__(self, master_gui):
        super().__init__(master_gui, 'Page', has_publish_btn=True, has_download_btn=True)

    def get_items(self):
        course_id = self.get_selected_course_id()
        pages = self.csh.get_course_pages(course_id)
        p_list = list(p for p in pages)
        return p_list

    def get_display_names(self, item_list):
        display_names = []
        for x in item_list:
            if x.published:
                display_names.append(self.PUBLISHED_STR + x.url)
            else:
                display_names.append(x.url)
        return display_names

    def cleanup_displayed_name(self, displayed_name):
        if displayed_name.startswith(self.PUBLISHED_STR):
            return displayed_name[len(self.PUBLISHED_STR):]
        else:
            return displayed_name

    def delete_item_by_displayed_name(self, displayed_name):
        super().delete_item_by_displayed_name(self)
        course_id = self.get_selected_course_id()
        url = displayed_name
        self.csh.delete_page_by_url(url, course_id)

    def publish_item_by_displayed_name(self, displayed_name):
        super().publish_item_by_displayed_name(self)
        course_id = self.get_selected_course_id()
        url = displayed_name
        self.csh.publish_page_by_url(url, course_id)

    def download_item_by_displayed_name(self, displayed_name, output_dir):
        super().download_item_by_displayed_name(displayed_name, output_dir)
        page_file_suffix = '.html'
        course_id = self.get_selected_course_id()
        url = displayed_name
        page = self.csh.get_page(course_id, url)
        page_content = self.csh.get_page_content(page)
        new_file = Path(output_dir).joinpath(url).with_suffix(page_file_suffix)
        if new_file.exists():
            answer = messagebox.askokcancel(f'File Already Exists',
                                            message=f'The following page already exists:'
                                            f'\n\n{new_file}'
                                            '\n\nDo you wish to overwrite it?',
                                            icon='warning')
            if not answer:
                return
        new_file.write_text(page_content)

    def recent_sort_key(self, item):
        k = item.updated_at
        return k

    def alpha_sort_key(self, item):
        k = item.url
        return k

    def double_click_callback(self):
        course_id = self.get_selected_course_id()
        page_short_url = self.get_selected_item()
        page_url = self.csh.get_page_url(course_id, page_short_url)
        webbrowser.open(page_url)
