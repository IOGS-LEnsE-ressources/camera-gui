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
import sys
import os
import numpy as np

from PyQt6.QtWidgets import (QApplication, QMainWindow,
                             QGridLayout, QWidget,
                             QMessageBox)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer

from gui.camera_choice_widget import CameraChoice
from gui.main_menu_widget import MainMenuWidget
from gui.title_widget import TitleWidget
from gui.x_y_chart_widget import XYChartWidget
from gui.camera_params_view_widget import CameraParamsViewWidget
from lensecam.ids.camera_ids import CameraIds, get_bits_per_pixel
from lensecam.camera_thread import CameraThread
from lensecam.basler.camera_basler import CameraBasler
from lensecam.ids.camera_ids_widget import CameraIdsWidget
from lensecam.basler.camera_basler_widget import CameraBaslerWidget
from lensepy.images.conversion import array_to_qimage, resize_image_ratio
from gui.camera_settings_widget import CameraSettingsWidget

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
    SPACE = 3
    TIME = 4


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
        # Data to display
        self.image_x = []   # 4 random pixels in the AOI - X coordinate
        self.image_y = []   # 4 random pixels in the AOI - Y coordinate
        self.x_time = None
        self.x_time_cpt = 0
        self.y_time = None
        self.x_histo = None
        self.y_histo = None

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
        self.params_widget = QWidget()
        self.settings_displayed = False
        self.main_layout.addWidget(self.title_widget, 0, 0, 1, 3)
        self.main_layout.addWidget(self.main_menu_widget, 1, 0, 2, 1)
        self.main_layout.addWidget(self.camera_widget, 1, 1)
        self.main_layout.addWidget(self.params_widget, 2, 1)  # params_widget
        self.histo_graph = QWidget()
        self.histo_graph_started = False
        self.main_layout.addWidget(self.histo_graph, 1, 2)
        self.time_graph = QWidget()
        self.time_graph_started = False
        self.main_layout.addWidget(self.time_graph, 2, 2)

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
                    print(c_f)
                if 'exposure' in self.default_parameters:
                    self.camera.set_exposure(int(self.default_parameters['exposure']))
                if 'blacklevel' in self.default_parameters:
                    self.camera.set_black_level(int(self.default_parameters['blacklevel']))
                if 'framerate' in self.default_parameters:
                    self.camera.set_frame_rate(int(self.default_parameters['framerate']))
                if 'colormode' in self.default_parameters:
                    self.camera.set_color_mode(self.default_parameters['colormode'])
                self.bits_depth = get_bits_per_pixel(self.camera.get_color_mode())
                self.clear_layout(1, 1)
                self.main_layout.addWidget(self.camera_widget, 1, 1)
                self.mode = Modes.SETTINGS
                self.camera_thread.start()
                self.camera_widget.camera_display_params.update_params()

    def menu_action(self, event) -> None:
        try:
            self.histo_graph_started = False
            self.time_graph_started = False
            self.settings_displayed = False
            if event == 'camera_settings':
                if self.camera is None:
                    self.mode = Modes.NOMODE
                    self.clear_layout(2, 1)
                    self.params_widget = CameraChoice()
                    self.params_widget.selected.connect(self.action_brand_selected)
                    self.main_layout.addWidget(self.params_widget, 2, 1)
                else:
                    # display camera settings and sliders
                    self.mode = Modes.SETTINGS
                    self.start_cam_settings()
                    self.start_histo_graph()
                    self.start_time_graph()
            elif event == 'aoi':
                self.mode = Modes.AOI
                self.start_histo_graph()
                self.start_time_graph()
            elif event == 'space':
                self.mode = Modes.SPACE
                print('>Menu / Spatial')
            elif event == 'time':
                self.mode = Modes.TIME
                print('>Menu / Timing')
            elif event == 'options':
                self.mode = Modes.NOMODE
                self.clear_layout(2, 2)
                self.clear_layout(1, 2)
                self.clear_layout(2, 1)
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
                if self.bits_depth > 8:
                    coeff = int(self.bits_depth-8)
                    image = image >> coeff
                    image = image.astype(np.uint8)
                # Resize to the display size
                frame_width = self.camera_widget.width()
                frame_height = self.camera_widget.height()
                image_resized = resize_image_ratio(
                    image,
                    frame_width,
                    frame_height)
                # Convert the frame into an image
                qimage = array_to_qimage(image_resized) #image_array_disp2)
                pmap = QPixmap(qimage)
                # display it in the cameraDisplay
                self.camera_widget.camera_display.setPixmap(pmap)
        except Exception as e:
            print(f'Exception - update_image {e}')

    def process_data(self, image_array):
        """Process data to display in histogram or/and time graph."""

        if self.time_graph_started:
            if self.x_time is None:
                self.x_time = np.array([0])
                self.y_time = [np.zeros(0) for _ in range(4)]
            if self.x_time_cpt == 0:
                self.y_time[0] = image_array[self.image_x[0], self.image_y[0]]
                self.y_time[1] = image_array[self.image_x[1], self.image_y[1]]
                self.y_time[2] = image_array[self.image_x[2], self.image_y[2]]
                self.y_time[3] = image_array[self.image_x[3], self.image_y[3]]
            else:
                self.x_time = np.append(self.x_time, self.x_time_cpt)
                self.y_time[0] = np.append(self.y_time[0], image_array[self.image_x[0], self.image_y[0]])
                self.y_time[1] = np.append(self.y_time[1], image_array[self.image_x[1], self.image_y[1]])
                self.y_time[2] = np.append(self.y_time[2], image_array[self.image_x[2], self.image_y[2]])
                self.y_time[3] = np.append(self.y_time[3], image_array[self.image_x[3], self.image_y[3]])
            self.x_time_cpt += 1

            self.time_graph.set_data(self.x_time, self.y_time[1:])
            self.time_graph.refresh_chart()

        if self.histo_graph_started:
            self.histo_graph.set_image(image_array)
            self.histo_graph.update_info()

    def start_cam_settings(self):
        """Display camera settings widget in the good part of the layout."""
        self.clear_layout(2, 1)
        self.params_widget = CameraSettingsWidget(self.camera)
        self.main_layout.addWidget(self.params_widget, 2, 1)  # display camera images
        self.params_widget.update_parameters(auto_min_max=True)
        self.settings_displayed = True

    def start_time_graph(self):
        self.rand_pixels()
        self.clear_layout(2, 2)
        self.x_time = np.array([0])
        self.y_time = [np.zeros(0) for _ in range(4)]
        self.x_time_cpt = 0
        self.time_graph = XYChartWidget()
        self.time_graph.set_background('white')
        self.time_graph.set_x_label('Image Number')
        self.time_graph.set_y_label('RAW Value')
        self.main_layout.addWidget(self.time_graph, 2, 2)
        #self.time_graph_started = True

    def start_histo_graph(self):
        self.clear_layout(1, 2)
        self.histo_graph = ImageHistogramWidget()
        self.histo_graph.set_background('white')
        self.histo_graph.set_name('Image histogram')
        self.histo_graph.set_bit_depth(self.bits_depth)
        self.main_layout.addWidget(self.histo_graph, 1, 2)
        self.histo_graph_started = True

    def rand_pixels(self):
        # TO DO : in the AOI !
        min_val = 200
        max_val = 300
        # Reset old coordinates
        self.image_x = []
        self.image_y = []
        for i in range(4):
            self.image_x.append(np.random.randint(min_val, max_val + 1))
            self.image_y.append(np.random.randint(min_val, max_val + 1))

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
