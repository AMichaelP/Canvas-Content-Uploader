from pathlib import Path

from canvas_content_uploader.gui_abcs.ContentUploader import ContentUploader


class UploadFilesTask(ContentUploader):
    """
    Upload files to the selected course.
    """
    def __init__(self, master_gui):
        super().__init__(master_gui, 'File', check_for_conflicts=False, title_required=False)

    def get_existing_item_titles_as_list(self) -> list:
        pass

    def prepare_item_with_title(self, file_path: Path, title: str):
        pass

    def handle_course_change(self):
        pass

    def overwrite_item(self, title: str, new_item):
        pass

    def get_title_from_file_path(self, file_path: Path) -> str:
        pass

    def upload_item_to_course(self, item):
        super().upload_item_to_course(item)
        course_id = self.get_selected_course_id()
        self.csh.upload_file_to_course(item, course_id)
