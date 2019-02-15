import webbrowser

from canvas_content_uploader.gui_abcs.ContentManager import ContentManager


class ManageFilesTask(ContentManager):
    """
    View or remove files existing within the selected course.
    """
    def __init__(self, master_gui):
        super().__init__(master_gui, 'File')

    def get_items(self):
        course_id = self.get_selected_course_id()
        files = list(self.csh.get_course_files(course_id))
        return files

    def get_display_names(self, item_list):
        display_names = list(f.display_name for f in item_list)
        return display_names

    def recent_sort_key(self, item):
        k = item.modified_at
        return k

    def alpha_sort_key(self, item):
        k = item.display_name
        return k

    def delete_item_by_displayed_name(self, displayed_name):
        course_id = self.get_selected_course_id()
        self.csh.delete_file(course_id, displayed_name)

    def double_click_callback(self):
        course_id = self.get_selected_course_id()
        file_display_name = self.get_selected_item()
        file_id = self.csh.get_file_id_from_display_name(course_id, file_display_name)
        file_url = self.csh.get_file_url(course_id, file_id)
        webbrowser.open(file_url)

    def cleanup_displayed_name(self, displayed_name):
        return displayed_name
