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
from gui.spatial_analysis_widget import SpatialAnalysisWidget
from gui.time_analysis_widget import TimeAnalysisWidget

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
        self.snap_required = False
        self.time_acquisition_started = False
        self.time_acquisition_nb = 0
        self.time_acquisition_cpt = 0
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
        self.params_widget = QWidget()
        self.settings_displayed = False
        self.main_layout.addWidget(self.title_widget, 0, 0, 1, 3)
        self.main_layout.addWidget(self.main_menu_widget, 1, 0, 2, 1)
        self.main_layout.addWidget(self.camera_widget, 1, 1)
        self.main_layout.addWidget(self.params_widget, 2, 1)  # params_widget
        self.histo_graph = QWidget()
        self.histo_graph_started = False
        self.main_layout.addWidget(self.histo_graph, 1, 2)
        self.histo_graph_aoi = QWidget()
        self.histo_graph_aoi_started = False
        self.aoi_selection = QWidget()
        self.aoi_selection_started = False
        self.spatial_analysis = QWidget()
        self.time_analysis = QWidget()

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
            if event == 'camera_settings':
                print('>Menu / Camera Settings')
                if self.camera is None:
                    self.mode = Modes.NOMODE
                    self.params_widget = CameraChoice()
                    self.params_widget.selected.connect(self.action_brand_selected)
                    self.main_layout.addWidget(self.params_widget, 2, 1)
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
            elif event == 'space':
                self.mode = Modes.SPACE
                print('>Menu / Spatial Analysis')
                self.start_spatial_analysis()
            elif event == 'time':
                self.mode = Modes.TIME
                print('>Menu / Time Analysis')
                self.start_time_analysis()
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
                if self.bits_depth > 8:
                    coeff = int(self.bits_depth-8)
                    image = image >> coeff
                    image = image.astype(np.uint8)
                if self.aoi_selection_started:
                    # Display the AOI on the image
                    x, y = self.aoi_selection.get_position()
                    w, h = self.aoi_selection.get_size()

                    for i in range(5):
                        # Horizontal edges
                        image[y+i, x:x + w] = 255
                        image[y-i + h - 1, x:x + w] = 255
                        # Vertical edges
                        image[y:y + h, x+i] = 255
                        image[y:y + h, x-i + w - 1] = 255

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
        """Process data to display in histogram graph."""
        if self.mode == Modes.SETTINGS:
            self.main_menu_widget.update_parameters()
        if self.histo_graph_started:
            if self.mode == Modes.SPACE:
                if self.snap_required:
                    x, y = self.aoi[0], self.aoi[1]
                    h, w = self.aoi[2], self.aoi[3]
                    self.saved_image = image_array[x:x + w, y:y + h].copy()
                    self.histo_graph.set_image(self.saved_image, fast_mode=False)
                    self.histo_graph.update_info()
                    self.snap_required = False
            else:
                self.histo_graph.set_image(image_array, fast_mode=True)
                self.histo_graph.update_info()
        if self.aoi_selection_started:
            self.aoi[0], self.aoi[1] = self.aoi_selection.get_position()
            self.aoi[2], self.aoi[3] = self.aoi_selection.get_size()
        if self.histo_graph_aoi_started:
            x, y = self.aoi[0], self.aoi[1]
            h, w = self.aoi[2], self.aoi[3]
            image_aoi = image_array[x:x+w, y:y+h]
            self.histo_graph_aoi.set_image(image_aoi, fast_mode=False)
            self.histo_graph_aoi.update_info()
        if self.mode == Modes.TIME:
            if self.time_acquisition_started:
                if self.time_acquisition_cpt < self.time_acquisition_nb:
                    self.time_acquisition_cpt += 1
                    self.time_analysis.waiting_value(self.time_acquisition_cpt)
                    # Adding data from pixels
                    for i in range(4):
                        self.pixels_value[i].append(image_array[self.image_x[i],self.image_y[i]])
                else:
                    self.time_acquisition_started = False
                    # Display histo of the 4 pixels
                    histo_pixels = HistogramWidget('Time Analysis / 4 pixels')
                    histo_pixels.set_background('white')

                    # Calculate histogram
                    mean_pixel1 = int(np.mean(self.pixels_value[0]))
                    std_pixel1 = int(np.std(self.pixels_value[0]))
                    if std_pixel1 == 0:
                        std_pixel1 = 1
                    # Create bins
                    bins = np.linspace(mean_pixel1-8*std_pixel1, mean_pixel1+8*std_pixel1,
                                       16 * std_pixel1+1)
                    histo_pixels.set_data(self.pixels_value[0], bins)
                    histo_pixels.refresh_chart()
                    histo_pixels.update_info()
                    self.main_layout.addWidget(histo_pixels, 1, 2)
                    # Enable saving histograms
                    self.time_analysis.set_enabled_save()
                    print('Finish !')



    def start_cam_settings(self):
        """Display camera settings widget in the good part of the layout."""
        self.clear_layout(2, 1)
        self.params_widget = CameraSettingsWidget(self.camera)
        self.main_layout.addWidget(self.params_widget, 2, 1)  # display camera images
        self.params_widget.update_parameters(auto_min_max=True)
        self.settings_displayed = True

    def start_histo_graph(self):
        self.clear_layout(1, 2)
        self.histo_graph = ImageHistogramWidget('Image histogram')
        self.histo_graph.set_background('white')
        self.histo_graph.set_bit_depth(self.bits_depth)
        self.main_layout.addWidget(self.histo_graph, 1, 2)
        self.histo_graph_started = True

    def start_histo_aoi_graph(self):
        # Still issues !
        self.clear_layout(2, 2)
        self.histo_graph_aoi = ImageHistogramWidget('Image histogram / AOI')
        self.histo_graph_aoi.set_background('lightgray')
        self.histo_graph_aoi.set_bit_depth(self.bits_depth)
        self.main_layout.addWidget(self.histo_graph_aoi, 2, 2)
        self.histo_graph_aoi_started = True

    def start_aoi_selection(self, editable: bool = True):
        self.clear_layout(2, 1)
        self.aoi_selection = AoiSelectionWidget(self, editable)
        self.aoi_selection.set_aoi(self.aoi)
        self.main_layout.addWidget(self.aoi_selection, 2, 1)
        self.aoi_selection_started = True

    def start_spatial_analysis(self):
        """Start a spatial analysis of the sensor."""
        self.clear_layout(2, 2)
        self.spatial_analysis = SpatialAnalysisWidget(self)
        self.spatial_analysis.snap_clicked.connect(self.spatial_action)
        self.main_layout.addWidget(self.spatial_analysis, 2, 2)
        self.start_histo_graph()
        self.start_aoi_selection(editable=False)

    def start_time_analysis(self):
        """Start the time analysis of 4 pixels in the image."""
        self.clear_layout(2, 2)
        self.clear_layout(1, 2)
        self.time_analysis = TimeAnalysisWidget(self)
        self.time_analysis.start_acq_clicked.connect(self.time_action)
        self.main_layout.addWidget(self.time_analysis, 2, 2)
        self.rand_pixels()
        self.start_aoi_selection(editable=False)

    def spatial_action(self, event):
        """Action performed when a button in the spatial analysis is clicked."""
        if event == 'snap':
            self.snap_required = True
        elif event == 'save_raw':
            if self.saved_image is not None:
                # saved_image to store in a raw format (???)
                cv2.imshow('Image', self.saved_image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            pass
        elif event == 'save_png':
            if self.saved_image is not None:
                # saved_image to store in a png file
                default_dir = QDir.homePath()
                if self.saved_dir is not None:
                    default_dir = self.saved_dir
                file_path, _ = QFileDialog.getSaveFileName(self, translate('save_image_title_window'),
                                                           default_dir + "/image.png", "Images PNG (*.png)")
                if file_path:
                    cv2.imwrite(file_path, self.saved_image)
                    info = QMessageBox.information(self, 'File Saved', f'File saved to {file_path}')
                else:
                    warn = QMessageBox.warning(self, 'Saving Error', 'No file saved !')
        elif event == 'save_hist':
            if self.saved_image is not None:
                # Create bins
                bins = np.linspace(0, 2 ** self.bits_depth - 1, 2 ** self.bits_depth)
                data = self.saved_image
                plot_hist, plot_bins_data = np.histogram(data, bins=bins)

                # Create histogram graph
                mean_data = np.mean(data)
                x, y = self.aoi_selection.get_position()
                w, h = self.aoi_selection.get_size()
                if mean_data > (2**self.bits_depth) // 2:
                    x_text_pos = 0.30   # text on the left
                else:
                    x_text_pos = 0.95   # text on the right
                plt.bar(plot_bins_data[:-1], plot_hist, width=np.diff(plot_bins_data),
                        edgecolor='black', alpha=0.75, color='blue')
                plt.title(f'Image Histogram')
                text_str = f'Mean = {mean_data:.2f}\nStdDev = {np.std(data):.2f}'
                plt.text(x_text_pos, 0.95, text_str, fontsize=10, verticalalignment='top',
                         horizontalalignment='right',
                         transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.5))
                text_str = (f'Expo = {round(self.camera.get_exposure()/1000, 2)} ms\nBlack Level = '
                            f'{int(self.camera.get_black_level())}\n\n'
                            f'AOI : X={x}, Y={y}\n W={w}, H={h}')
                plt.text(x_text_pos, 0.25, text_str, fontsize=8, verticalalignment='top',
                         horizontalalignment='right',
                         transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.5))

                # histogram to store in a png file - and a txt file (array) ??
                default_dir = QDir.homePath()
                if self.saved_dir is not None:
                    default_dir = self.saved_dir
                file_path, _ = QFileDialog.getSaveFileName(self, translate('save_histogram_title_window'),
                                                           default_dir + "/image_histo.png",
                                                           "Images PNG (*.png)")
                if file_path:
                    # create an image of the histogram of the saved_image
                    plt.savefig(file_path)
                    info = QMessageBox.information(self, 'Histogram Saved', f'File saved to {file_path}')
                else:
                    warn = QMessageBox.warning(self, 'Saving Error', 'No file saved !')

    def time_action(self, event):
        """Action performed when a button in the time analysis is clicked."""
        if event == 'start':
            self.time_acquisition_cpt = 0
            self.time_acquisition_nb = self.time_analysis.get_nb_of_points()
            print(f'Nb of points {self.time_acquisition_nb}')
            self.pixels_value = [[], [], [], []]
            self.time_acquisition_started = True
            pass
        elif event == 'save_hist':
            pass
            '''
            if self.saved_image is not None:
                # Create bins
                bins = np.linspace(0, 2 ** self.bits_depth - 1, 2 ** self.bits_depth)
                data = self.saved_image
                plot_hist, plot_bins_data = np.histogram(data, bins=bins)

                # Create histogram graph
                mean_data = np.mean(data)
                x, y = self.aoi_selection.get_position()
                w, h = self.aoi_selection.get_size()
                if mean_data > (2**self.bits_depth) // 2:
                    x_text_pos = 0.30   # text on the left
                else:
                    x_text_pos = 0.95   # text on the right
                plt.bar(plot_bins_data[:-1], plot_hist, width=np.diff(plot_bins_data),
                        edgecolor='black', alpha=0.75, color='blue')
                plt.title(f'Image Histogram')
                text_str = f'Mean = {mean_data:.2f}\nStdDev = {np.std(data):.2f}'
                plt.text(x_text_pos, 0.95, text_str, fontsize=10, verticalalignment='top',
                         horizontalalignment='right',
                         transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.5))
                text_str = (f'Expo = {round(self.camera.get_exposure()/1000, 2)} ms\nBlack Level = '
                            f'{int(self.camera.get_black_level())}\n\n'
                            f'AOI : X={x}, Y={y}\n W={w}, H={h}')
                plt.text(x_text_pos, 0.25, text_str, fontsize=8, verticalalignment='top',
                         horizontalalignment='right',
                         transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.5))

                # histogram to store in a png file - and a txt file (array) ??
                default_dir = QDir.homePath()
                if self.saved_dir is not None:
                    default_dir = self.saved_dir
                file_path, _ = QFileDialog.getSaveFileName(self, translate('save_histogram_title_window'),
                                                           default_dir + "/image_histo.png",
                                                           "Images PNG (*.png)")
                if file_path:
                    # create an image of the histogram of the saved_image
                    plt.savefig(file_path)
                    info = QMessageBox.information(self, 'Histogram Saved', f'File saved to {file_path}')
                else:
                    warn = QMessageBox.warning(self, 'Saving Error', 'No file saved !')
            '''

    def rand_pixels(self):
        """Selection of 4 pixels in the area of interest."""
        self.aoi[0], self.aoi[1] = self.aoi_selection.get_position()
        self.aoi[2], self.aoi[3] = self.aoi_selection.get_size()
        # Reset old coordinates
        self.image_x = []
        self.image_y = []
        for i in range(4):
            self.image_x.append(np.random.randint(self.aoi[0], self.aoi[0]+self.aoi[2]))
            self.image_y.append(np.random.randint(self.aoi[1], self.aoi[1]+self.aoi[3]))

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
