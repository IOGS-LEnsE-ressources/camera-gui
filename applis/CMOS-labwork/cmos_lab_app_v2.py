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
import sys
import os
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow,
                             QGridLayout, QWidget,
                             QMessageBox)
from gui.camera_choice_widget import CameraChoice
from gui.main_menu_widget import MainMenuWidget
from gui.title_widget import TitleWidget
from gui.camera_settings_widget import CameraSettingsWidget
from lensecam.ids.camera_ids import CameraIds
from _tests.camera_ids import CameraIds
from lensecam.basler.camera_basler import CameraBasler
from lensecam.ids.camera_ids_widget import CameraIdsWidget, CameraIdsParamsWidget
from _tests.camera_ids_widget import CameraIdsWidget, CameraIdsParamsWidget
from lensecam.basler.camera_basler_widget import CameraBaslerWidget, CameraBaslerParamsWidget

cam_widget_brands = {
    'Basler': CameraBaslerWidget,
    'IDS': CameraIdsWidget,
}
cam_from_brands = {
    'Basler': CameraBasler,
    'IDS': CameraIds,
}
cam_params_widget_brands = {
    'Basler': CameraBaslerParamsWidget,
    'IDS': CameraIdsParamsWidget,
}

# -------------------------------

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
        self.brand = None
        self.default_parameters = {}

        # Init default parameters
        print(f"CMOS App {dictionary['version']}")
        self.default = self.init_default_parameters()
        if self.default:
            if 'language' in self.default_parameters:
                file_name_dict = './lang/dict_'+str(self.default_parameters['language'])+'.txt'
                load_dictionary(file_name_dict)
                print('Dict OK')

        # Define Window title
        self.setWindowTitle("LEnsE - CMOS Sensor Labwork")
        # Main Widget
        self.main_widget = QWidget()

        # Main Layout
        self.main_layout = QGridLayout()
        self.title_widget = TitleWidget(dictionary)
        self.main_menu_widget = MainMenuWidget()
        self.camera_widget = QWidget()
        self.camera_widget.setStyleSheet("background-color: lightblue;")
        self.params_widget = QWidget()
        self.time_graph = QWidget()
        self.time_graph.setStyleSheet("background-color: lightblue;")
        self.histo_graph = QWidget()

        self.main_layout.addWidget(self.title_widget, 0, 0, 1, 3)
        self.main_layout.addWidget(self.main_menu_widget, 1, 0, 2, 1)
        self.main_layout.addWidget(self.camera_widget, 1, 1)
        self.main_layout.addWidget(self.histo_graph, 1, 2)
        self.main_layout.addWidget(self.params_widget, 2, 1)  # params_widget
        self.main_layout.addWidget(self.time_graph, 2, 2)

        self.main_layout.setColumnStretch(0,1)
        self.main_layout.setColumnStretch(1,3)
        self.main_layout.setColumnStretch(2,3)
        self.main_layout.setRowStretch(0,1)
        self.main_layout.setRowStretch(1,5)
        self.main_layout.setRowStretch(2,4)

        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Events
        self.main_menu_widget.camera_settings_clicked.connect(self.camera_settings_action)

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
                print(self.default_parameters['language'])
            return True
        else:
            return False

    def camera_settings_action(self, event) -> None:
        self.clear_layout(2, 1)
        if self.camera is None:
            print('No Camera')
            self.params_widget = CameraChoice()
            self.params_widget.selected.connect(self.action_brand_selected)
            self.main_layout.addWidget(self.params_widget, 2, 1)
        else:
            print('Camera OK')
            # display camera settings and sliders
            self.params_widget = cam_params_widget_brands[self.brand](self)
            self.main_layout.addWidget(self.params_widget, 2, 1)

    def action_brand_selected(self, event):
        type_event = event.split(':')[0]
        if type_event == 'nobrand':
            self.clear_layout(1, 1)  # camera_widget
            print('No Brand')
        elif type_event == 'brand':
            self.brand = event.split(':')[1]
            print(self.brand)
            self.clear_layout(1,1)   # camera_widget
            self.camera_widget = cam_widget_brands[self.brand](params_disp=False)
            self.camera_widget.connected.connect(self.action_camera_connected)
            self.main_layout.addWidget(self.camera_widget, 1, 1)

    def action_camera_connected(self, event):
        self.clear_layout(2,1)   # params_widget
        self.camera = self.camera_widget.camera
        self.params_widget = cam_params_widget_brands[self.brand](self)
        self.main_layout.addWidget(self.params_widget, 2, 1)


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
