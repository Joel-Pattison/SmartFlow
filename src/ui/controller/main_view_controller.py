from PyQt5.QtWidgets import QApplication, QMainWindow
from src.ui.view.main_view import Ui_Form
from qframelesswindow import FramelessWindow, FramelessMainWindow, StandardTitleBar
import sys


class MainWindow(FramelessMainWindow, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
