# -*- coding: utf-8 -*-
"""*zygo_lab_app.py* file.

*zygo_lab_app* file that contains :class::ZygoLabApp

This file is attached to a 1st year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
"""

# Standard library imports
import sys

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QCheckBox, QDialog,
    QMessageBox
)
from PyQt6.QtGui import QPixmap, QIcon, QDesktopServices
from PyQt6.QtCore import Qt, pyqtSignal, QUrl

# Third-party library imports
import numpy as np

# Project-specific module imports
from lensecam.ids.camera_ids_widget import CameraIdsWidget
from lensecam.ids.camera_ids import CameraIds
from lensecam.camera_thread import CameraThread
from drivers.nidaq_piezo import *

from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.pyqt6.widget_image_histogram import ImageHistogramWidget
from lensepy.pyqt6.widget_image_display import ImageDisplayWidget
from lensepy.images.conversion import array_to_qimage, resize_image_ratio

from process.initialization_parameters import *
from widgets.title_widget import TitleWidget
from widgets.main_menu_widget import MainMenuWidget
from widgets.camera_settings_widget import CameraSettingsWidget
'''
from analyses_app import AnalysisApp

from widgets.masks_menu_widget import MasksMenuWidget
from widgets.acquisition_menu_widget import AcquisitionMenuWidget
from widgets.results_menu_widget import ResultsMenuWidget
from widgets.options_menu_widget import OptionsMenuWidget
#from widgets.piezo_calibration_widget import PiezoCalibrationWidget
from widgets.x_y_z_chart_widget import Surface3DWidget
from widgets.imshow_pyqtgraph import TwoImageWidget
#from widgets.display_zernike_widget import *

'''

def load_default_dictionary(language: str) -> bool:
    """Initialize default dictionary from default_config.txt file"""
    file_name_dict = f'./lang/dict_{language}.txt'
    load_dictionary(file_name_dict)

class ZygoLabApp(QWidget):
    analysis_requested = pyqtSignal()

    def __init__(self) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Columns stretch: 10%, 45%, 45%
        self.layout.setColumnStretch(0, 10)
        self.layout.setColumnStretch(1, 45)
        self.layout.setColumnStretch(2, 45)

        # Rows stretch: 4%, 48%, 48%
        self.layout.setRowStretch(0, 4)
        self.layout.setRowStretch(1, 48)
        self.layout.setRowStretch(2, 48)

        load_default_dictionary('FR')

        # Initialization of the camera
        # ----------------------------
        self.camera = CameraIds()
        self.camera_connected = self.camera.find_first_camera()
        if self.camera_connected:
            self.camera.init_camera()
        else:
            sys.exit(-1)
        self.zoom_activated = False     # Camera is started in a large window (imshow_pyqtgraph)
        self.mask_created = False       # Almost one mask is created and selected
        self.phase_calculated = False   # Phase from acquisition is unwrapped
        self.coeff_calculated = False   # Zernike coefficients are calculated
        self.acquisition_done = False   # Almost one acquisition is done and data are acquired

        # Initialization of the piezo
        # ---------------------------
        self.piezo = NIDaqPiezo()
        self.piezo_connected = False

        # Permanent Widgets
        # -----------------
        # Title Widget: first row of the grid layout
        self.title_widget = TitleWidget()
        self.layout.addWidget(self.title_widget, 0, 0, 1, 3)

        self.main_menu_widget = MainMenuWidget()
        self.layout.addWidget(self.main_menu_widget, 1, 0, 2, 1)

        # Camera Widget: top-left corner
        self.camera_widget = CameraIdsWidget(self.camera, params_disp=False)
        self.camera_widget.camera_display_params.update_params()
        self.camera_widget.camera_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.camera_widget, 1, 1)
        self.zoom_window = ImageDisplayWidget()
        self.zoom_window.window_closed.connect(self.zoom_closed_action)

        # Other Widgets
        # -------------
        self.camera_settings_widget = CameraSettingsWidget(self.camera)
        '''
        self.masks_menu_widget = MasksMenuWidget()
        self.acquisition_menu_widget = AcquisitionMenuWidget(parent=self)
        self.results_menu_widget = ResultsMenuWidget()
        self.options_menu_widget = OptionsMenuWidget()

        self.graphic_widget = Surface3DWidget('lightgray', 1)
        self.graphic_widget.set_title('')
        # self.graphic_widget.set_information('')
        self.graphic_widget.set_background('white')
        self.layout.addWidget(self.graphic_widget, 1, 2)

        self.analysis_window = AnalysisApp(self)
        self.analysis_window.window_closed.connect(self.signal_menu_selected_isReceived)

        # histogram of the camera image to optimize parameters.
        self.histo_widget = QWidget() # ImageHistogramWidget()
        '''
        self.histo_activated = False

        # Default settings
        # ----------------
        default_settings_dict = read_default_parameters('config.txt')

        if self.piezo.get_piezo() is not None:
            self.piezo_connected = True
            print('Piezo OK')
            if 'Piezo Channel' in default_settings_dict:
                self.piezo.set_channel(int(default_settings_dict['Piezo Channel']))

        if 'Exposure time' in default_settings_dict:
            default_exposure = float(default_settings_dict['Exposure time']) # ms
        else:
            default_exposure = 10
        default_exposure *= 1000 # µs
        self.camera.set_exposure(default_exposure) # µs

        if 'Exposure time' in default_settings_dict:
            default_black_level = int(default_settings_dict['Black level'])
        else:
            default_black_level = 100
        self.camera.set_black_level(default_black_level)

        # Main Menu Widget: fist column of the grid layout
        # ------------------------------------------------
        self.main_menu_widget.add_item_menu(translate("button_camera_settings_main_menu"))
        self.main_menu_widget.add_item_menu(translate("button_masks_main_menu"))
        self.main_menu_widget.add_item_menu(translate("button_acquisition_main_menu"), disabled=True)
        self.main_menu_widget.add_item_menu(translate("button_analyzes_main_menu"), disabled=True)
        self.main_menu_widget.add_option_item_menu(translate("button_help_main_menu"))
        self.main_menu_widget.add_option_item_menu(translate("button_options_main_menu"))
        self.main_menu_widget.add_option_item_menu(translate("button_piezo_main_menu"), disabled=not self.piezo_connected)
        self.main_menu_widget.refresh_menu()

        # Initialisation of the mask selection attributes
        # -----------------------------------------------
        self.mask = None
        self.list_masks = []
        self.list_original_masks = []
        self.mask_unactived = None

        self.phase = None

        # Other initializations
        # ---------------------
        self.camera_thread = CameraThread()
        self.camera_thread.set_camera(self.camera)
        self.camera_thread.image_acquired.connect(self.thread_update_image)
        self.camera_thread.start()

        # Signals
        # -------
        # self.analysis_requested.connect(self.show_analysis_window_maximized)
        self.main_menu_widget.signal_menu_selected.connect(self.signal_menu_selected_isReceived)

    '''
    def init_camera(self) -> ids_peak.Device:
        """Initialisation of the camera.
        If no IDS camera, display options to connect a camera"""
        # Init IDS Peak
        ids_peak.Library.Initialize()
        # Create a camera manager
        manager = ids_peak.DeviceManager.Instance()
        manager.Update()

        if manager.Devices().empty():
            device = None
            msg_box = QMessageBox()
            msg_box.setStyleSheet(styleH3)
            msg_box.warning(self, 'Erreur', 'Aucune caméra connectée')
            print('No cam => Quit')
            sys.exit(QApplication.instance())
        else:
            device = manager.Devices()[0].OpenDevice(ids_peak.DeviceAccessType_Exclusive)
        return device
    '''

    def clear_layout(self, row: int, column: int) -> None:
        """Remove widgets from a specific position in the layout without deleting them.

        :param row: Row index of the layout.
        :type row: int
        :param column: Column index of the layout.
        :type column: int
        """
        item = self.layout.itemAtPosition(row, column)
        if item is not None:
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def zoom_action(self, event):
        if event is True:
            self.zoom_activated = True
            self.camera_settings_widget.button_big_cam.setStyleSheet(actived_button)
            self.zoom_window.showMaximized()

    def zoom_closed_action(self, event):
        self.zoom_activated = False
        self.camera_settings_widget.button_big_cam.setStyleSheet(unactived_button)

    def thread_update_image(self, image_array):
        """Action performed when the live acquisition (via CameraThread) is running."""
        try:
            if self.camera_thread.running:
                if self.zoom_activated is False:
                    frame_width = self.camera_widget.width()
                    frame_height = self.camera_widget.height()
                    self.process_histo(image_array.squeeze())
                    # Resize to the display size
                    image_array_disp2 = resize_image_ratio(
                        image_array,
                        frame_width,
                        frame_height)
                    # Convert the frame into an image
                    image = array_to_qimage(image_array_disp2)
                    pmap = QPixmap(image)
                    # display it in the cameraDisplay
                    self.camera_widget.camera_display.setPixmap(pmap)
                else:
                    image = image_array.copy().squeeze()
                    self.zoom_window.set_image_from_array(image)
        except Exception as e:
            print(f'Exception - update_image {e}')

    def signal_menu_selected_isReceived(self, event):
        # Clear all layout except camera
        self.clear_layout(1, 2)
        self.clear_layout(2, 1)
        self.clear_layout(2, 2)

        # Update the interface depending on the menu item selected
        if event == translate("button_camera_settings_main_menu"):
            self.camera_settings_widget = CameraSettingsWidget(self.camera)
            self.camera_settings_widget.update_parameters()
            self.layout.addWidget(self.camera_settings_widget, 2, 1)
            self.camera_settings_widget.zoom_activated.connect(self.zoom_action)
            self.histo_widget = ImageHistogramWidget()
            self.histo_widget.set_background('white')
            self.layout.addWidget(self.histo_widget, 2, 2)
            self.histo_activated = True


        '''
        # Save information of the mask
        self.mask = self.masks_menu_widget.mask
        self.list_masks = self.masks_menu_widget.list_masks
        self.list_original_masks = self.masks_menu_widget.list_original_masks
        self.mask_unactived = self.masks_menu_widget.mask_unactived

        # Save information wedge factor
        self.wedge_factor = self.acquisition_menu_widget.wedge_factor

        try:
            self.image = self.masks_menu_widget.image
        except:
            None
        try:
            self.zernike_coefficients = self.acquisition_menu_widget.zernike_coefficients
        except:
            None

        try:
            self.phase = self.acquisition_menu_widget.phase
        except:
            pass

        self.camera_settings_widget = CameraSettingsWidget(self.camera)
        self.masks_menu_widget = MasksMenuWidget(self)
        self.acquisition_menu_widget = AcquisitionMenuWidget(self)
        self.results_menu_widget = ResultsMenuWidget()
        self.options_menu_widget = OptionsMenuWidget()
        self.options_menu_widget.signal_language_updated.connect(self.signal_language_changed_isReceived)

        self.clear_layout(2, 1)
        self.clear_layout(2, 2)
        self.histo_activated = False
        if event == 'camera_settings_main_menu':
            self.clear_layout(1, 2)
            self.camera_settings_widget.update_parameters()
            self.layout.addWidget(self.camera_settings_widget, 2, 1)
            self.camera_settings_widget.zoom_activated.connect(self.zoom_action)
            self.clear_layout(1, 2)
            self.histo_widget = ImageHistogramWidget()
            self.histo_widget.set_background('white')
            self.layout.addWidget(self.histo_widget, 2, 2)
            self.histo_activated = True

        elif event == 'masks_main_menu':
            self.display_mask_widget = TwoImageWidget()
            self.display_mask_widget.set_title('Visualisation de la zone sélectionnée')
            self.display_mask_widget.set_information('La zone sélectionnée est en vert.')
            self.display_mask_widget.set_background('white')
            try:
                self.display_mask_widget.set_image_data(np.squeeze(self.image), np.squeeze(self.mask)*255, colormap_name1='gray', colormap_name2='RdYlGn', alpha=0.2)
            except Exception as e:
                print(f"MASKS selected - {e}")
            
            self.layout.addWidget(self.display_mask_widget, 1, 2)

            self.layout.addWidget(self.masks_menu_widget, 2, 1)

        elif event == 'acquisition_main_menu':
            self.clear_layout(1, 2)
            self.layout.addWidget(self.acquisition_menu_widget, 2, 1)
            self.layout.addWidget(self.results_menu_widget, 2, 2)

            self.graphic_widget = Surface3DWidget('white', 1)
            # self.graphic_widget.set_title('')
            
            # self.graphic_widget.set_information('')
            self.graphic_widget.set_background('lightgray')

            self.layout.addWidget(self.graphic_widget, 1, 2)

        elif event == 'analyzes_main_menu':
            self.aberrations_considered = self.acquisition_menu_widget.aberrations_considered

            self.clear_layout(1, 2)
            self.analysis_requested.emit()

        elif event == 'help':
            # Call help page
            QDesktopServices.openUrl(QUrl.fromLocalFile('how_to.pdf'))
            self.main_menu_widget.button_help_main_menu.setStyleSheet(unactived_button)

        elif event == 'options_main_menu':
            self.clear_layout(1, 2)

            self.layout.addWidget(self.options_menu_widget, 2, 1)

            self.piezo_calibration_widget = PiezoCalibrationWidget(self)
            self.layout.addWidget(self.piezo_calibration_widget, 1, 2, 2, 1)
        elif event == 'analysis_window_closed':
            self.main_menu_widget.reset_menu()
            self.clear_layout(1, 2)
            self.clear_layout(2, 1)
        '''

    def signal_language_changed_isReceived(self, language_selected):
        """Handler for the language updated signal."""
        #print(f"Signal received with language selected: {language_selected}")
        #dictionary.clear()
        if language_selected == 'English':
            dictionary = load_dictionary('lang\dict_EN.txt')
        elif language_selected == 'Français':
            dictionary = load_dictionary('lang\dict_FR.txt')
        elif language_selected == '中文':
            dictionary = load_dictionary('lang\dict_CN.txt')

        #self.update_labels(self)

    def update_labels(self, window):
        """Recursively update labels and text in all widgets."""
        # Iterate through all the widgets and sub-widgets of the main window
        for widget in window.findChildren(QWidget):
            # Update labels (QLabel, QPushButton, etc.)
            if isinstance(widget, (QLabel, QPushButton)):
                widget.setText(translate(widget.text()))

            # Update titles (QMainWindow, QDialog, etc.)
            if isinstance(widget, (QMainWindow, QDialog)):
                widget.setWindowTitle(translate(widget.windowTitle()))

            # If the widget is a container, recursively call the function
            if isinstance(widget, (QVBoxLayout, QHBoxLayout, QGridLayout)):
                for subwidget in widget.findChildren(QWidget):
                    self.update_labels(subwidget)

    def process_histo(self, image):
        if self.histo_activated:
            self.histo_widget.set_image(image, fast_mode=True, black_mode=True) #, log_mode=True)
            self.histo_widget.update_info()

    def show_analysis_window_maximized(self):
        try:
            self.analysis_window.showMaximized()
        except Exception as e:
            print(f'Exception - analysis_app_open {e}')

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            
            # Define Window title
            self.setWindowTitle(translate("ZygoLab"))
            self.setWindowIcon(QIcon('assets\IOGS-LEnsE-icon.jpg'))
            self.setGeometry(50, 50, 700, 700)

            self.central_widget = ZygoLabApp()
            self.setCentralWidget(self.central_widget)

        def closeEvent(self, event):
            """
            closeEvent redefinition. Use when the user clicks
            on the red cross to close the window
            """
            """reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                if self.central_widget.camera is not None:
                    self.central_widget.camera_widget.disconnect()
                event.accept()
            else:
                event.ignore()"""

    print("Ouverture en cours ...")
    app = QApplication(sys.argv)
    main = MyWindow()
    main.showMaximized()
    sys.exit(app.exec())
