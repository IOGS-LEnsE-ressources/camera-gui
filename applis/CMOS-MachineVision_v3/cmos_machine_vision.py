# -*- coding: utf-8 -*-
"""*cmos_lab_app.py* file.

*cmos_lab_app* file that contains :class::CmosLabApp

This file is attached to engineer training labworks in photonics.
- 1st year subject :
- 2nd year subject : http://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-Detection.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/contents/appli_CMOS_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>

Creation : sept/2023
Modification : oct/2024
"""
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
import time
import numpy as np
from lensepy.css import *
from PyQt6.QtWidgets import (
    QWidget, QPushButton,
    QMainWindow, QApplication, QMessageBox)
from widgets.main_widget import *
from widgets.histo_widget import *
from widgets.aoi_select_widget import *
from widgets.camera import *
from lensecam.camera_thread import CameraThread
from lensecam.ids.camera_ids import get_bits_per_pixel


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
        self.setWindowTitle("LEnsE - CMOS Sensor / Machine Vision / Labwork")
        # Objects
        self.image = None
        self.saved_image = None
        self.aoi = None
        self.fast_mode = False
        self.image_bits_depth = 8
        # Camera
        self.brand_camera = None
        self.camera_device = None
        self.camera = None
        self.camera_thread = CameraThread()
        self.camera_thread.image_acquired.connect(self.thread_update_image)
        # GUI structure
        self.central_widget = MainWidget(self)
        self.setCentralWidget(self.central_widget)
        load_menu('./config/menu.txt', self.central_widget.main_menu)
        self.central_widget.main_signal.connect(self.main_action)
        self.central_widget.main_menu.set_enabled([3,5,6,8,9,10,12], False)

    def main_action(self, event):
        """
        Action performed by an event in the main widget.
        :param event: Event that triggered the action.
        """
        if self.image is not None:
            size = self.image.shape[1] * self.image.shape[0]
            self.fast_mode = size > 1e5 # Fast mode if number of pixels > 1e5

        if self.central_widget.mode == 'open_image':
            self.aoi = None
            if self.camera is not None:
                self.camera_thread.stop()
            self.central_widget.options_widget.image_opened.connect(self.action_image_from_file)
            self.image_bits_depth = 8

        elif self.central_widget.mode == 'open_camera':
            self.aoi = None
            self.central_widget.options_widget.camera_opened.connect(self.action_camera_selected)

        elif self.central_widget.mode == 'aoi_select':
            # Histogram of the global image.
            self.central_widget.top_right_widget.set_bit_depth(self.image_bits_depth)
            self.central_widget.top_right_widget.set_image(self.image, fast_mode=self.fast_mode)
            self.central_widget.top_right_widget.update_info()
            # Histogram of the AOI.
            if self.aoi is not None:
                aoi_array = get_aoi_array(self.image, self.aoi)
                self.central_widget.bot_right_widget.set_bit_depth(self.image_bits_depth)
                self.central_widget.bot_right_widget.set_image(aoi_array, fast_mode=self.fast_mode)
                self.central_widget.bot_right_widget.update_info()
            # Connect signal.
            self.central_widget.options_widget.aoi_selected.connect(self.action_aoi_selected)

        elif self.central_widget.mode == 'histo':
            aoi_array = get_aoi_array(self.image, self.aoi)
            if aoi_array.shape[0] * aoi_array.shape[1] < 1000:
                fast = False
            else:
                fast = True
            self.central_widget.top_right_widget.set_bit_depth(self.image_bits_depth)
            self.central_widget.top_right_widget.set_image(aoi_array, fast_mode=fast)
            self.central_widget.top_right_widget.update_info()

        elif self.central_widget.mode == 'histo_space':
            self.central_widget.options_widget.snap_clicked.connect(self.action_histo_space)
            aoi_array = get_aoi_array(self.image, self.aoi)
            if aoi_array.shape[0] * aoi_array.shape[1] < 1000:
                fast = False
            else:
                fast = True
            self.central_widget.top_right_widget.set_bit_depth(self.image_bits_depth)
            self.central_widget.top_right_widget.set_image(aoi_array, fast_mode=fast)
            self.central_widget.top_right_widget.update_info()

        elif self.central_widget.mode == 'histo_time':
            self.central_widget.options_widget.start_acq_clicked.connect(self.action_histo_time)


    def thread_update_image(self, image_array):
        if image_array is not None:
            if self.image_bits_depth > 8:
                image = image_array.view(np.uint16)
            else:
                image = image_array.view(np.uint8)
            self.image = image.squeeze()
        self.central_widget.top_left_widget.set_image_from_array(self.image)
        if self.central_widget.mode == 'aoi_select':
            self.action_aoi_selected('aoi_selected')
        elif self.central_widget.mode == 'histo':
            self.action_histo_space('snap')
        elif self.central_widget.mode == 'histo_space':
            self.central_widget.update_image(aoi=True)
        elif self.central_widget.mode == 'histo_time':
            self.central_widget.update_image(aoi=True)


    def action_image_from_file(self, event: np.ndarray):
        """
        Action performed when an image file is opened.
        :param event: Event that triggered the action - np.ndarray.
        """
        if self.camera is not None:
            self.camera_thread.stop()
            self.camera.stop_acquisition()
            self.camera.disconnect()
            self.camera = None
            self.camera_device = None
        self.image = event.copy()
        self.aoi = None
        self.central_widget.top_left_widget.set_image_from_array(self.image)
        self.central_widget.top_left_widget.repaint()
        self.central_widget.options_widget.button_open_image.setStyleSheet(unactived_button)
        self.central_widget.main_menu.set_enabled([3], True)
        self.central_widget.main_menu.set_enabled([5, 6, 8, 9, 10, 12], False)

    def action_camera_selected(self, event):
        """
        Action performed when an industrial camera is selected.
        :param event: Event that triggered the action - np.ndarray.
        """
        self.brand_camera = event['brand']
        camera_list = cam_list_brands[self.brand_camera]()
        self.camera_device = camera_list.get_cam_device(int(event['cam_dev']))
        self.camera = cam_from_brands[self.brand_camera](self.camera_device)
        self.camera.init_camera()
        self.camera_thread.set_camera(self.camera)
        # Init default parameters !
        # TO DO
        # Start Thread
        self.image_bits_depth = get_bits_per_pixel(self.camera.get_color_mode())
        self.camera_thread.start()

    def action_aoi_selected(self, event):
        """Action performed when an event occurred in the aoi select options widget."""
        if event == 'aoi_selected':
            x, y = self.central_widget.options_widget.get_position()
            w, h = self.central_widget.options_widget.get_size()
            self.aoi = (x, y, w, h)
            self.central_widget.main_menu.set_enabled([3, 5, 6, 8, 9, 10, 12], True)

            # Histogram of the global image.
            self.central_widget.top_right_widget.set_bit_depth(self.image_bits_depth)
            self.central_widget.top_right_widget.set_image(self.image, fast_mode=self.fast_mode)
            self.central_widget.top_right_widget.update_info()
            # Histogram of the AOI.
            if self.aoi is not None:
                aoi_array = get_aoi_array(self.image, self.aoi)
                if aoi_array.shape[0]*aoi_array.shape[1] < 1000:
                    fast = False
                else:
                    fast = True
                self.central_widget.bot_right_widget.set_bit_depth(self.image_bits_depth)
                self.central_widget.bot_right_widget.set_image(aoi_array, fast_mode=fast)
                self.central_widget.bot_right_widget.update_info()
            # Display the image with a rectangle for the AOI.
            self.central_widget.update_image(aoi_disp=True)

    def action_histo_space(self, event):
        """Action performed when an event occurred in the histo space options widget."""
        image = get_aoi_array(self.image, self.aoi)
        if event == 'snap':
            self.saved_image = self.image
            self.central_widget.top_right_widget.set_image(image)
            self.central_widget.top_right_widget.update_info()
        elif event == 'live':
            self.central_widget.top_right_widget.set_image(image)
            self.central_widget.top_right_widget.update_info()
        elif event == 'save_png':
            if self.saved_image is not None:
                image = get_aoi_array(self.saved_image, self.aoi)
                bins = np.linspace(0, 2 ** self.image_bits_depth - 1, 2 ** self.image_bits_depth)
                bins, hist_data = process_hist_from_array(image, bins)
                save_hist(image, hist_data, bins,
                               f'Image Histogram',
                               f'image_histo.png')
        # Display the AOI.
        self.central_widget.update_image(aoi=True)

    def action_histo_time(self, event):
        """
        Action performed when an event occurred in the histo time options widget.
        """
        print(event)

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
            if self.camera is not None:
                self.camera_thread.stop()
                self.camera.stop_acquisition()
                self.camera.disconnect()
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    #window.showMaximized()
    sys.exit(app.exec())