# -*- coding: utf-8 -*-
"""*zygo_lab_app.py* file.

*zygo_lab_app* file that contains :class::ZygoLabApp

This file is attached to a 1st year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/contents/appli_CMOS_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt, QSignalMapper
from PyQt6.QtGui import QPixmap, QIcon

from lensepy.pyqt6.widget_image_display import WidgetImageDisplay
from lensecam.ids.camera_ids_widget import CameraIdsWidget
from ids_peak import ids_peak

from lensepy import load_dictionary, translate
from lensepy.css import *

from widgets.title_widget import TitleWidget
from widgets.main_menu_widget import MainMenuWidget
from widgets.camera_settings_widget import CameraSettingsWidget
from widgets.masks_menu_widget import MasksMenuWidget
from widgets.acquisition_menu_widget import AcquisitionMenuWidget
from widgets.results_menu_widget import ResultsMenuWidget
from widgets.options_menu_widget import OptionsMenuWidget

class ZygoLabApp(QWidget):

    def __init__(self) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)

        # Initialization of the camera
        # ----------------------------
        self.camera_device = self.init_camera()
        # ----------------------------

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

        # Permanent Widgets
        # -----------------
        # Title Widget: first row of the grid layout
        self.title_widget = TitleWidget() 
        self.layout.addWidget(self.title_widget, 0, 0, 1, 3)

        # Main Menu Widget: fist column of the grid layout
        self.main_menu_widget = MainMenuWidget()
        self.layout.addWidget(self.main_menu_widget, 1, 0, 2, 1)

        # Camera Widget: top-left corner
        self.camera_widget = CameraIdsWidget(self.camera_device, params_disp=False)
        self.camera_widget.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.camera_widget, 1, 1)
        self.camera = self.camera_widget.camera

        # Other Widgets
        # -------------
        self.camera_settings_widget = CameraSettingsWidget(self.camera)
        self.masks_menu_widget = MasksMenuWidget()
        self.acquisition_menu_widget = AcquisitionMenuWidget()
        self.results_menu_widget = ResultsMenuWidget()
        self.options_menu_widget = OptionsMenuWidget()

        # Signals
        # -------
        self.main_menu_widget.signal_menu_selected.connect(self.signal_menu_selected_isReceived)
        self.options_menu_widget.signal_language_updated.connect(self.update_labels)
        self.camera_widget.connected.connect(self.signal_camera_connected_isReceived)

    def init_camera(self) -> ids_peak.Device:
        """Initialisation of the camera.
        If no IDS camera, display options to connect a camera"""
        # Init IDS Peak
        ids_peak.Library.Initialize()
        # Create a camera manager
        manager = ids_peak.DeviceManager.Instance()
        manager.Update()

        if manager.Devices().empty():
            print("No Camera")
            device = None
        else:
            print("Camera")
            device = manager.Devices()[0].OpenDevice(ids_peak.DeviceAccessType_Exclusive)
        return device

    def refresh_app(self):
        """Action performed for refreshing the display of the app."""
        pass

    def clearLayout(self, row: int, column: int) -> None:
        """Remove widgets from a specific position in the layout.

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

    def signal_camera_connected_isReceived(self, event):
        """Action performed when a camera is connected."""
        self.camera = self.camera_widget.camera
        self.camera_settings_widget = CameraSettingsWidget(self.camera)
        print(f'Connect {event}')

    def signal_menu_selected_isReceived(self, event):
        if event == 'camera_settings_main_menu':
            self.clearLayout(2,1)
            self.clearLayout(2,2)

            self.layout.addWidget(self.camera_settings_widget, 2, 1)

        elif event == 'masks_main_menu':
            self.clearLayout(2,1)
            self.clearLayout(2,2)

            self.layout.addWidget(self.masks_menu_widget, 2, 1)

        elif event == 'acquisition_main_menu':
            self.clearLayout(2,1)
            self.clearLayout(2,2)

            self.layout.addWidget(self.acquisition_menu_widget, 2, 1)
            self.layout.addWidget(self.results_menu_widget, 2, 2)

        elif event == 'analyzes_main_menu':
            pass

        elif event == 'options_main_menu':
            self.clearLayout(2,1)
            self.clearLayout(2,2)

            self.layout.addWidget(self.options_menu_widget, 2, 1)

    def update_labels(self, window):
        # Iterate through all the widgets and sub-widgets of the main window
        for widget in window.findChildren(QWidget):
            # Check if the widget is a QLabel
            if isinstance(widget, QLabel):
                # Update the text using translate
                widget.setText(translate(widget.text()))

            # If the widget is a container, recursively call the function
            if isinstance(widget, (QVBoxLayout, QHBoxLayout, QGridLayout)):
                for subwidget in widget.findChildren(QWidget):
                    self.update_labels(subwidget)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            
            # Define Window title
            self.setWindowTitle(translate("Zygo-IDS Labwork APP"))
            self.setWindowIcon(QIcon('assets\IOGS-LEnsE-icon.jpg'))
            self.setGeometry(50, 50, 700, 700)

            dictionary = load_dictionary("lang\dict_EN.txt")

            self.central_widget = ZygoLabApp()
            self.setCentralWidget(self.central_widget)

        def closeEvent(self, event):
            """
            closeEvent redefinition. Use when the user clicks
            on the red cross to close the window
            """
            reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                if self.central_widget.camera is not None:
                    self.central_widget.camera_widget.disconnect()
                event.accept()
            else:
                event.ignore()


    app = QApplication(sys.argv)
    main = MyWindow()
    main.showMaximized()
    sys.exit(app.exec())
