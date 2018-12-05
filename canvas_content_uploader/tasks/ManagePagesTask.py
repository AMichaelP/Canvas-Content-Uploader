import webbrowser

from canvas_content_uploader.gui_abcs.ContentManager import ContentManager


class ManagePagesTask(ContentManager):
    """
    View or remove wiki pages existing within the selected course.
    """
    def __init__(self, master_gui):
        super().__init__(master_gui, 'Page')

    def get_items(self):
        course_id = self.get_selected_course_id()
        pages = self.csh.get_course_pages(course_id)
        p_list = list(p for p in pages)
        return p_list

    def get_display_names(self, item_list):
        urls = list(x.url for x in item_list)
        return urls

    def delete_item_by_displayed_name(self, displayed_name):
        super().delete_item_by_displayed_name(self)
        course_id = self.get_selected_course_id()
        url = displayed_name
        self.csh.delete_page_by_url(url, course_id)

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
