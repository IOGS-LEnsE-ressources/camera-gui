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

## Example for IDS Camera
from lensecam.ids.camera_ids_widget import CameraIdsWidget
from lensecam.ids.camera_ids import CameraIds
## Example for Basler Camera
from lensecam.basler.camera_basler_widget import CameraBaslerWidget
from lensecam.basler.camera_basler import CameraBasler

## Image display and thread
from lensecam.camera_thread import CameraThread
from lensepy.pyqt6.widget_image_display import ImageDisplayWidget
## Camera settings Widget for IDS
from widgets.camera import *


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

        # Data from camera
        # ----------------------------
        self.raw_image = None
        self.displayed_image = None
        self.image_bits_depth = 8

        # Initialization of the camera
        # ----------------------------
        self.camera = CameraIds()
        self.camera_thread = CameraThread()
        self.camera_connected = self.camera.find_first_camera()
        if self.camera_connected:
            self.camera.init_camera()
            self.image_bits_depth = get_bits_per_pixel(self.camera.get_color_mode())
            self.central_widget.set_top_right_widget(CameraSettingsWidget(self, self.camera))
            self.central_widget.top_right_widget.update_parameters(auto_min_max=True)
            self.camera.set_exposure(10000) # in us
            print(f'Expo = {self.camera.get_exposure()} us')
            self.camera_thread.set_camera(self.camera)
            self.camera_thread.image_acquired.connect(self.thread_update_image)
            self.camera_thread.start()
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

    def thread_update_image(self, image_array):
        """Actions performed if a camera thread is started."""
        if image_array is not None:
            if self.image_bits_depth > 8:
                self.raw_image = image_array.view(np.uint16)
                self.displayed_image = self.raw_image >> (self.image_bits_depth-8)
                self.displayed_image = self.displayed_image.astype(np.uint8)
            else:
                self.raw_image = image_array.view(np.uint8)
                self.displayed_image = self.raw_image
        self.central_widget.top_left_widget.set_image_from_array(self.displayed_image, aoi=True)

    def resizeEvent(self, event):
        """
        Action performed when the main window is resized.
        :param event: Object that triggered the event.
        """
        self.central_widget.update_size()

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