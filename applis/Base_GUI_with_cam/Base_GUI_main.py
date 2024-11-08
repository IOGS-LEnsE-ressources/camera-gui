# -*- coding: utf-8 -*-
"""*base_gui_main.py* file.

*base_gui_main* file that contains :class::BaseGUI, an example of a
complete 5 areas GUI: 1 main menu on the left and 4 equivalent area on the right.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>

Creation : oct/2024
"""
from lensepy import load_dictionary, translate, dictionary
import sys
from PyQt6.QtWidgets import (
    QWidget, QPushButton,
    QMainWindow, QApplication, QMessageBox)
from widgets.main_widget import MainWidget, load_menu

from lensecam.ids.camera_ids_widget import CameraIdsWidget
from lensecam.ids.camera_ids import CameraIds
from lensecam.camera_thread import CameraThread
from lensepy.pyqt6.widget_image_display import ImageDisplayWidget
from widgets.camera_settings_widget import CameraSettingsWidget


def load_default_dictionary(language: str) -> bool:
    """Initialize default dictionary from default_config.txt file"""
    file_name_dict = f'./lang/dict_{language}.txt'
    load_dictionary(file_name_dict)

class MainWindow(QMainWindow):
    """
    Our main window.

    Args:
        QMainWindow (class): QMainWindow can contain several widgets.
    """

    def __init__(self):
        """
        Initialisation of the main Window.
        """
        super().__init__()
        load_default_dictionary('FR')
        ## GUI structure
        self.central_widget = MainWidget(self)
        self.setCentralWidget(self.central_widget)
        # Menu
        load_menu('./config/menu.txt', self.central_widget.main_menu)
        self.central_widget.main_signal.connect(self.main_action)


        # Initialization of the camera
        # ----------------------------
        self.camera = CameraIds()
        self.camera_connected = self.camera.find_first_camera()
        if self.camera_connected:
            self.camera.init_camera()
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No Camera Connected")
            dlg.setText("No IDS Camera is connected to the computer...\n\nThe application will not start "
                        "correctly.\n\nYou will only access to a pre-established data set.")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            # sys.exit(-1)

    def main_action(self, event):
        """
        Action performed by an event in the main widget.
        :param event: Event that triggered the action.
        """
        print(f'Main {event}')

    def closeEvent(self, event):
        """
        closeEvent redefinition. Use when the user clicks
        on the red cross to close the window
        """
        reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())