# -*- coding: utf-8 -*-
"""*cmos_lab_app.py* file.

*cmos_lab_app* file that contains :class::CmosLabApp

This file is attached to a 2nd year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-Detection.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/contents/appli_CMOS_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>

"""

from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.pyqt6.widget_image_histogram import ImageHistogramWidget
from lensepy.pyqt6.widget_histogram import HistogramWidget
import sys
import os
import numpy as np
from matplotlib import pyplot as plt
import cv2

from PyQt6.QtWidgets import (QApplication, QMainWindow,
                             QGridLayout, QWidget, QFileDialog,
                             QMessageBox)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QDir

from gui.camera_choice_widget import CameraChoice
from gui.main_menu_widget import MainMenuWidget
from gui.title_widget import TitleWidget

from gui.camera_params_view_widget import CameraParamsViewWidget
from gui.mini_params_widget import MiniParamsWidget
from gui.aoi_selection_widget import AoiSelectionWidget
from gui.histo_analysis_widget import HistoAnalysisWidget

from lensecam.ids.camera_ids import CameraIds, get_bits_per_pixel
from lensecam.camera_thread import CameraThread
from lensecam.basler.camera_basler import CameraBasler
from lensecam.ids.camera_ids_widget import CameraIdsWidget
from lensecam.basler.camera_basler_widget import CameraBaslerWidget
from lensepy.images.conversion import array_to_qimage, resize_image_ratio
from gui.camera_settings_widget import CameraSettingsWidget
from gui.filter_choice_widget import FilterChoiceWidget

from enum import Enum

cam_widget_brands = {
    'Basler': CameraBaslerWidget,
    'IDS': CameraIdsWidget,
}
cam_from_brands = {
    'Basler': CameraBasler,
    'IDS': CameraIds,
}

# -------------------------------

class Modes(Enum):
    NOMODE = 0
    SETTINGS = 1
    AOI = 2
    HISTO = 3
    FILTER = 4
    CONTOUR = 5
    POINTS = 6


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
        self.camera = None
        self.camera_list = None
        self.camera_device = None
        self.camera_thread = CameraThread()
        self.camera_thread.image_acquired.connect(self.thread_update_image)
        self.bits_depth = 0
        self.brand = None
        # Parameters
        self.default_parameters = {}
        self.mode = Modes.NOMODE
        self.snap_required = False
        self.aoi_selected = False
        # Data to display
        self.image_x = []   # 4 random pixels in the AOI - X coordinate
        self.image_y = []   # 4 random pixels in the AOI - Y coordinate
        self.pixels_value = [[], [], [], []]

        self.aoi = [0, 0, 0, 0]
        self.saved_image = None
        self.saved_dir = None

        # Define Window title
        self.setWindowTitle("LEnsE - CMOS Sensor Labwork")
        # Main Widget
        self.main_widget = QWidget()

        # Main Layout
        self.main_layout = QGridLayout()
        self.title_widget = TitleWidget(dictionary)
        self.main_menu_widget = MainMenuWidget(self)
        self.camera_widget = QWidget()
        self.camera_widget.setStyleSheet("background-color: lightblue;")
        self.top_right_widget = QWidget()
        self.bot_left_widget = QWidget()
        self.bot_right_widget = QWidget()
        self.main_layout.addWidget(self.title_widget, 0, 0, 1, 3)
        self.main_layout.addWidget(self.main_menu_widget, 1, 0, 2, 1)
        self.main_layout.addWidget(self.camera_widget, 1, 1)
        self.main_layout.addWidget(self.top_right_widget, 1, 2)
        self.main_layout.addWidget(self.bot_left_widget, 2, 1)
        self.main_layout.addWidget(self.bot_right_widget, 2, 2)
        self.settings_displayed = False
        self.histo_graph_started = False
        self.histo_graph_aoi_started = False
        self.aoi_selection_started = False

        self.main_layout.setColumnStretch(0,1)
        self.main_layout.setColumnStretch(1,3)
        self.main_layout.setColumnStretch(2,3)
        self.main_layout.setRowStretch(0,1)
        self.main_layout.setRowStretch(1,5)
        self.main_layout.setRowStretch(2,4)

        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.option_params_view_widget = CameraParamsViewWidget(self)

        # Init default parameters
        print(f"CMOS App {dictionary['version']}")
        self.init_default_parameters()

        # Events
        self.main_menu_widget.menu_clicked.connect(self.menu_action)

    def load_file(self, file_path: str) -> dict:
        """
        Load parameter from a CSV file.

        Parameters
        ----------
        file_path : str
            The file path to specify which CSV file to load.

        Returns
        -------
        dict containing 'key_1': 'language_word_1'

        Notes
        -----
        This function reads a CSV file that contains key-value pairs separated by semicolons (';')
        and stores them in a global dictionary variable. The CSV file may contain comments
        prefixed by '#', which will be ignored.

        The file should have the following format:
            # comment
            # comment
            key_1 ; language_word_1
            key_2 ; language_word_2

        The function will strip any leading or trailing whitespace from the keys and values.

        See Also
        --------
        numpy.genfromtxt : Load data from a text file, with missing values handled as specified.
        """
        dictionary_loaded = {}
        if os.path.exists(file_path):
            # Read the CSV file, ignoring lines starting with '//'
            data = np.genfromtxt(file_path, delimiter=';', dtype=str, comments='#', encoding='UTF-8')
            # Populate the dictionary with key-value pairs from the CSV file
            for key, value in data:
                dictionary_loaded[key.strip()] = value.strip()
            return dictionary_loaded
        else:
            print('File error')
            return {}

    def init_default_parameters(self) -> bool:
        """Initialize default parameters from default_config.txt file"""
        file_path = './default_config.txt'
        if os.path.exists(file_path):
            self.default_parameters = self.load_file(file_path)
            if 'language' in self.default_parameters:
                file_name_dict = './lang/dict_' + str(self.default_parameters['language']) + '.txt'
                dict = load_dictionary(file_name_dict)
            if 'brandname' in self.default_parameters:
                self.brand = self.default_parameters["brandname"]
                self.camera = cam_from_brands[self.brand]()
                if self.camera.find_first_camera() is False:
                    print(f'No {self.brand} Camera Connected')
                    sys.exit(-1)

                self.camera.init_camera(self.camera.camera_device)
                self.camera.init_camera()
                self.camera_widget = cam_widget_brands[self.brand](self.camera)
                self.camera_thread.set_camera(self.camera)
                # Init default param
                if 'clock_freq' in self.default_parameters:
                    c_f = float(self.default_parameters['clock_freq']) * 1e6
                    self.camera.set_clock_frequency(c_f)
                if 'exposure' in self.default_parameters:
                    self.camera.set_exposure(int(self.default_parameters['exposure']))
                if 'blacklevel' in self.default_parameters:
                    self.camera.set_black_level(int(self.default_parameters['blacklevel']))
                if 'framerate' in self.default_parameters:
                    self.camera.set_frame_rate(int(self.default_parameters['framerate']))
                if 'colormode' in self.default_parameters:
                    self.camera.set_color_mode(self.default_parameters['colormode'])
                if 'aoi_x' in self.default_parameters:
                    self.aoi[0] = int(self.default_parameters['aoi_x'])
                if 'aoi_y' in self.default_parameters:
                    self.aoi[1] = int(self.default_parameters['aoi_y'])
                if 'aoi_w' in self.default_parameters:
                    self.aoi[2] = int(self.default_parameters['aoi_w'])
                if 'aoi_h' in self.default_parameters:
                    self.aoi[3] = int(self.default_parameters['aoi_h'])
                if 'save_images_dir' in self.default_parameters:
                    self.saved_dir = self.default_parameters['save_images_dir']
                self.bits_depth = get_bits_per_pixel(self.camera.get_color_mode())
                self.clear_layout(1, 1)
                self.main_layout.addWidget(self.camera_widget, 1, 1)
                self.mode = Modes.SETTINGS
                self.camera_thread.start()
                self.camera_widget.camera_display_params.update_params()

    def menu_action(self, event) -> None:
        try:
            self.histo_graph_started = False
            self.settings_displayed = False
            self.aoi_selection_started = False
            self.clear_layout(1, 2)
            self.clear_layout(2, 1)
            self.clear_layout(2, 2)
            self.aoi_selected = False
            if event == 'camera_settings':
                print('>Menu / Camera Settings')
                if self.camera is None:
                    self.mode = Modes.NOMODE
                    self.bot_left_widget = CameraChoice()
                    self.bot_left_widget.selected.connect(self.action_brand_selected)
                    self.main_layout.addWidget(self.bot_left_widget, 2, 1)
                else:
                    # display camera settings and sliders
                    self.mode = Modes.SETTINGS
                    self.start_cam_settings()
                    self.start_histo_graph()
            elif event == 'aoi':
                self.mode = Modes.AOI
                print('>Menu / AOI Selection')
                self.start_histo_graph()
                # self.start_histo_aoi_graph()  # STILL PB WITH HISTO AOI !!
                self.start_aoi_selection()
            elif event == 'histo':
                self.mode = Modes.HISTO
                print('>Menu / Histo')
                self.start_histo_analysis()
            elif event == 'filter':
                self.mode = Modes.FILTER
                print('>Menu / Filter Transformation')
                self.start_filter_analysis()

            elif event == 'options':
                print('>Menu / Options')
                self.mode = Modes.NOMODE
                self.option_params_view_widget = CameraParamsViewWidget(self)
                self.main_layout.addWidget(self.option_params_view_widget, 1, 2, 2, 1)
        except Exception as e:
            print(f'Exception - menu_action {e}')

    def action_brand_selected(self, event):
        type_event = event.split(':')[0]
        if type_event == 'nobrand':
            self.clear_layout(1, 1)  # camera_widget
        elif type_event == 'brand':
            self.brand = event.split(':')[1]
            self.clear_layout(1,1)   # camera_widget
            self.camera_widget = cam_widget_brands[self.brand]()
            self.camera_widget.connected.connect(self.action_camera_connected)
            self.main_layout.addWidget(self.camera_widget, 1, 1)

    def action_camera_connected(self, event):
        try:
            self.clear_layout(2,1)   # params_widget
            self.clear_layout(1,2)   # histo_graph
            self.camera = self.camera_widget.camera
            self.camera.init_camera(self.camera.camera_device)
            self.camera.set_frame_rate(1)
            self.camera_thread.set_camera(self.camera)
            self.camera.init_camera()
            # Init default param
            if 'exposure' in self.default_parameters:
                self.camera.set_exposure(int(self.default_parameters['exposure']))
            if 'blacklevel' in self.default_parameters:
                self.camera.set_black_level(int(self.default_parameters['blacklevel']))
            if 'framerate' in self.default_parameters:
                self.camera.set_frame_rate(int(self.default_parameters['framerate']))
            if 'colormode' in self.default_parameters:
                self.camera.set_color_mode(self.default_parameters['colormode'])
            self.bits_depth = get_bits_per_pixel(self.camera.get_color_mode())
            self.camera_widget.camera_display_params.update_params()
            self.start_cam_settings()
            self.camera_thread.start()
        except Exception as e:
            print(f'Exception - action_camera_connected {e}')

    def thread_update_image(self, image_array):
        """Action performed when the live acquisition (via CameraThread) is running."""
        try:
            if image_array is not None:
                if self.bits_depth > 8:
                    image = image_array.view(np.uint16)
                else:
                    image = image_array.view(np.uint8)
                image = image.squeeze()
                self.process_data(image)
                frame_width = self.camera_widget.width()
                frame_height = self.camera_widget.height()
                no_resize = False
                if self.bits_depth > 8:
                    coeff = int(self.bits_depth-8)
                    image = image >> coeff
                    image = image.astype(np.uint8)
                if self.aoi_selection_started:
                    # Display the AOI on the image
                    x, y = self.bot_left_widget.get_position()
                    w, h = self.bot_left_widget.get_size()

                    for i in range(5):
                        # Horizontal edges
                        image[y+i, x:x + w] = 255
                        image[y-i + h - 1, x:x + w] = 255
                        # Vertical edges
                        image[y:y + h, x+i] = 255
                        image[y:y + h, x-i + w - 1] = 255
                elif self.aoi_selected:
                    # Display AOI instead of whole image
                    x, y = self.aoi[0], self.aoi[1]
                    h, w = self.aoi[2], self.aoi[3]
                    image = image[y:y + h, x:x + w]
                    if h < frame_height and w < frame_width:
                        no_resize = True
                # Resize to the display size
                if no_resize is False:
                    image_resized = resize_image_ratio(
                            image,
                            frame_width,
                            frame_height)
                    # Convert the frame into an image
                    qimage = array_to_qimage(image_resized) #image_array_disp2)
                else:
                    qimage = array_to_qimage(image)
                pmap = QPixmap(qimage)
                # display it in the cameraDisplay
                self.camera_widget.camera_display.setPixmap(pmap)
        except Exception as e:
            print(f'Exception - update_image {e}')

    def process_data(self, image_array):
        """Process data to display in histogram graph."""
        if self.mode == Modes.SETTINGS:
            self.main_menu_widget.update_parameters()
        if self.histo_graph_started:
            if self.mode == Modes.HISTO:
                if self.snap_required:
                    x, y = self.aoi[0], self.aoi[1]
                    h, w = self.aoi[2], self.aoi[3]
                    self.saved_image = image_array[x:x + w, y:y + h].copy()
                    self.top_right_widget.set_image(self.saved_image, fast_mode=False)
                    self.top_right_widget.update_info()
                    self.snap_required = False
            else:
                self.top_right_widget.set_image(image_array, fast_mode=True)
                self.top_right_widget.update_info()
        if self.aoi_selection_started:
            self.aoi[0], self.aoi[1] = self.bot_left_widget.get_position()
            self.aoi[2], self.aoi[3] = self.bot_left_widget.get_size()
        if self.histo_graph_aoi_started:
            x, y = self.aoi[0], self.aoi[1]
            h, w = self.aoi[2], self.aoi[3]
            image_aoi = image_array[x:x+w, y:y+h]
            self.bot_right_widget.set_image(image_aoi, fast_mode=False)
            self.bot_right_widget.update_info()
        if self.mode is Modes.FILTER:
            pass


    def start_cam_settings(self):
        """Display camera settings widget in the good part of the layout."""
        self.clear_layout(2, 1)
        self.bot_left_widget = CameraSettingsWidget(self.camera)
        self.main_layout.addWidget(self.bot_left_widget, 2, 1)  # display camera images
        self.bot_left_widget.update_parameters(auto_min_max=True)
        self.settings_displayed = True

    def start_histo_graph(self):
        self.clear_layout(1, 2)
        self.top_right_widget = ImageHistogramWidget('Image histogram')
        self.top_right_widget.set_background('white')
        self.top_right_widget.set_bit_depth(self.bits_depth)
        self.main_layout.addWidget(self.top_right_widget, 1, 2)
        self.histo_graph_started = True

    def start_histo_aoi_graph(self):
        # Still issues !
        self.clear_layout(2, 2)
        self.bot_right_widget = ImageHistogramWidget('Image histogram / AOI')
        self.bot_right_widget.set_background('lightgray')
        self.bot_right_widget.set_bit_depth(self.bits_depth)
        self.main_layout.addWidget(self.bot_right_widget, 2, 2)
        self.histo_graph_aoi_started = True

    def start_aoi_selection(self, editable: bool = True):
        self.clear_layout(2, 1)
        self.bot_left_widget = AoiSelectionWidget(self, editable)
        self.bot_left_widget.set_aoi(self.aoi)
        self.main_layout.addWidget(self.bot_left_widget, 2, 1)
        self.aoi_selection_started = True

    def start_histo_analysis(self):
        """Start a histogram analysis of the sensor."""
        self.clear_layout(2, 2)
        self.bot_right_widget = HistoAnalysisWidget(self)
        self.bot_right_widget.snap_clicked.connect(self.histo_action)
        self.main_layout.addWidget(self.bot_right_widget, 2, 2)
        self.start_histo_graph()
        self.start_aoi_selection(editable=False)

    def histo_action(self, event):
        """Action performed when a button in the histogram analysis is clicked."""
        if event == 'snap':
            self.snap_required = True


    def start_filter_analysis(self):
        # Still issues !
        self.clear_layout(2, 2)
        self.bot_left_widget = FilterChoiceWidget(self)
        self.main_layout.addWidget(self.bot_left_widget, 2, 1)
        self.aoi_selected = True
        #self.main_layout.addWidget(self.histo_graph_aoi, 2, 2)
        #self.histo_graph_aoi_started = True

    def clear_layout(self, row: int, column: int) -> None:
        """Remove widgets from a specific position in the layout.

        :param row: Row index of the layout.
        :type row: int
        :param column: Column index of the layout.
        :type column: int

        """
        try:
            item = self.main_layout.itemAtPosition(row, column)
            if item is not None:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else:
                    self.main_layout.removeItem(item)
        except Exception as e:
            print(f'Exception - clear_layout {e}')


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

# -------------------------------
# Launching as main for tests
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())
