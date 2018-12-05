import threading
import time
from abc import ABC, abstractmethod
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from root_components.MasterGui import MasterGui
    from root_components.CanvasSessionHandler import CanvasSessionHandler


# Progress bar decorator
def show_progress_bar(func):
    def wrapper(*args):
        self = args[0]
        pb = ttk.Progressbar(self.frame, mode='indeterminate', length=50)
        pb.grid(sticky='SWE', columnspan=5, padx=5, pady=5)
        try:
            pb.start()
            pb.update()
            t = threading.Thread(target=func, args=(*args,))
            t.start()

            while t.is_alive():
                pb.update()
                pb.step(5)
                time.sleep(.05)

        finally:
            pb.destroy()
    return wrapper


class Task(ABC):
    """
    Abstract Base Class used to build GUI components for Canvas operations.
    """
    def __init__(self, master_gui: 'MasterGui'):
        self.csh: 'CanvasSessionHandler' = master_gui.csh
        self.master_gui = master_gui
        self.course_var = master_gui.selected_course_combo_var
        self.selected_course_combo_var = master_gui.selected_course_combo_var
        self.selected_course_id_var = master_gui.selected_course_id_var
        self.frame = ttk.Frame(master_gui.task_frame)

    def grid(self):
        self.frame.grid()

    @abstractmethod
    def enable_selection(self):
        pass

    @abstractmethod
    def handle_course_change(self):
        pass

    def get_selected_course_id(self) -> int:
        return self.selected_course_id_var.get()
