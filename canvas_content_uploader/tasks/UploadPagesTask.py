from pathlib import Path

from canvas_content_uploader.gui_abcs.ContentUploader import ContentUploader


class UploadPagesTask(ContentUploader):
    """
    Upload new wiki pages to the selected course, using existing HTML files.
    """
    def __init__(self, master_gui):
        super().__init__(master_gui, 'Page')
        self.browse_file_types = ("html files", "*.html")

    def handle_course_change(self):
        pass

    def get_existing_item_titles_as_list(self) -> list:
        course_id = self.get_selected_course_id()
        existing_titles = self.csh.get_course_page_titles(course_id)
        return existing_titles

    def upload_item_to_course(self, item):
        super().upload_item_to_course(item)
        course_id = self.get_selected_course_id()
        self.csh.add_page_to_course(item, course_id)

    def overwrite_item(self, title, new_item):
        super().overwrite_item(title, new_item)
        course_id = self.get_selected_course_id()
        self.csh.overwrite_page_by_url(course_id, title, new_item)

    def prepare_item_with_title(self, file_path: Path, title) -> dict:
        body = file_path.read_text(encoding='utf-8')
        page = {'title': title,
                'body': body}
        return page

    def get_title_from_file_path(self, file_path: Path) -> str:
        return file_path.stem
