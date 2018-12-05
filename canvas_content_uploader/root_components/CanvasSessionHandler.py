import re
from pathlib import Path
from typing import Iterable, List

import canvasapi
import canvasapi.course
import canvasapi.file
import canvasapi.page


class CanvasSessionHandler:
    """
    Create Canvas session and handle Canvas API calls.
    """
    def __init__(self, url):
        self.url = url
        self.token = None
        self.__session: canvasapi.Canvas = None

    def login(self):
        self.__session = canvasapi.Canvas(self.url, self.token)

    def get_course_url(self, course_id: int) -> str:
        base_url = self.url

        if base_url.endswith('/'):
            base_url = base_url[:-1]

        course_url = f'{base_url}/courses/{course_id}'
        return course_url

    def get_page_url(self, course_id: int, page_short_url: str) -> str:
        course_url = self.get_course_url(course_id)
        page_url = f'{course_url}/pages/{page_short_url}'
        return page_url

    def get_file_url(self, course_id: int, file_id: int) -> str:
        course_url = self.get_course_url(course_id)
        file_url = f'{course_url}/files/{file_id}'
        return file_url

    def get_course(self, course_id: int) -> canvasapi.course.Course:
        course = self.__session.get_course(course_id)
        return course

    def get_enrolled_courses(self):
        courses = self.__session.get_courses()
        return courses

    def add_page_to_course(self, page_dict: dict, course_id: int):
        course = self.get_course(course_id)
        course.create_page(page_dict)

    def upload_file_to_course(self, file: Path, course_id: int):
        course = self.get_course(course_id)
        course.upload(file.as_posix())

    def get_course_pages(self, course_id: int) -> Iterable[canvasapi.page.Page]:
        course = self.get_course(course_id)
        pages = course.get_pages()
        return pages

    def get_course_page_titles(self, course_id: int) -> List[str]:
        pages = self.get_course_pages(course_id)
        page_titles = [p.title for p in pages]
        return page_titles

    def get_file_id_from_display_name(self, course_id: int, display_name: str) -> int:
        course = self.get_course(course_id)
        course_files = course.get_files()

        for f in course_files:
            if f.display_name == display_name:
                return f.id

    def delete_page_by_url(self, url: str, course_id: int):
        course = self.get_course(course_id)
        page = course.get_page(url)
        page.delete()

    def get_course_files(self, course_id: int) -> Iterable[canvasapi.file.File]:
        course = self.get_course(course_id)
        files = course.get_files()
        return files

    def overwrite_page_by_url(self, course_id: int, url: str, new_page: dict):
        self.delete_page_by_url(url, course_id)
        self.add_page_to_course(new_page, course_id)

    def search_pages_from_enrolled_courses(self, search_string: str,
                                           ignore_case=True, whole_word=False) -> Iterable[canvasapi.page.Page]:
        pages = self.get_pages_for_enrolled_courses()
        matches = self.search_pages_with_term(search_string, pages, ignore_case=ignore_case, whole_word=whole_word)
        return matches

    def search_pages_from_course(self, course_id, search_string,
                                 ignore_case=True, whole_word=False) -> Iterable[canvasapi.page.Page]:
        course = self.__session.get_course(course_id)
        pages = course.get_pages()
        matches = self.search_pages_with_term(search_string, pages, ignore_case=ignore_case, whole_word=whole_word)
        return matches

    def delete_file(self, course_id: int, target_display_name: str):
        course_files = self.get_course_files(course_id)

        for f in course_files:
            try:
                if target_display_name in f.display_name:
                    f.delete()
                    break
            except AttributeError:
                pass

        course_files = self.get_course_files(course_id)
        assert target_display_name not in [f.display_name for f in course_files]

    def get_pages_for_enrolled_courses(self) -> Iterable[canvasapi.page.Page]:
        courses = self.get_enrolled_courses()
        for c in courses:
            pages = c.get_pages()
            for p in pages:
                yield p

    @staticmethod
    def search_pages_with_term(search_term: str, pages: Iterable[canvasapi.page.Page],
                               ignore_case=True, whole_word=False) -> Iterable[canvasapi.page.Page]:
        if whole_word:
            pattern = r'\b' + re.escape(search_term) + r'\b'
        else:
            pattern = r'' + re.escape(search_term) + r''

        if ignore_case:
            regex = re.compile(pattern, flags=re.IGNORECASE)
        else:
            regex = re.compile(pattern)

        for p in pages:
            r = p.show_latest_revision()
            content = r.body
            if content:
                match = regex.search(content)
                if match:
                    yield p
