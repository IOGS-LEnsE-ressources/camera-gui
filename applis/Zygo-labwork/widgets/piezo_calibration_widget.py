# -*- coding: utf-8 -*-
"""*acquisition_menu_widget.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QPixmap
import numpy as np

from x_y_chart_widget import XYChartWidget

from lensecam.ids.camera_ids_widget import CameraIdsWidget
from lensecam.ids.camera_ids import CameraIds
from lensecam.camera_thread import CameraThread
from ids_peak import ids_peak

from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from lensepy.images.conversion import array_to_qimage, resize_image_ratio

# %% To add in lensepy library
# Styles
# ------
styleH1 = f"font-size:20px; padding:7px; color:{BLUE_IOGS}; font-weight: bold;"  # Added missing styleH1
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS}; font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"
styleCheckbox = f"font-size: 12px; padding: 7px; color: {BLUE_IOGS}; font-weight: normal;"

# %% Params
BUTTON_HEIGHT = 30  # px

# %% Widget
class PiezoCalibrationWidget(QWidget):
   
    def __init__(self):
        super().__init__(parent=None)

        # Layout
        # ------
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Master
        # ------
        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        self.master_widget.setStyleSheet("background-color: white;")
        
        # Title
        # -----
        self.label_title_calibration_menu = QLabel(translate('label_title_calibration_menu'))
        self.setStyleSheet(styleH1)
        
        # Camera
        # ------
        self.camera_device = self.init_camera()
        self.camera = CameraIds()
        self.camera.init_camera(self.camera_device)
        self.camera_widget = CameraIdsWidget(self.camera)
        self.camera_widget.camera_display_params.update_params()
        self.camera_widget.camera_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Graph
        # -----
        self.graph_calibration = XYChartWidget()
        self.graph_calibration.set_background('white')

        # Button
        # ------
        self.button_start_calibration = QPushButton(translate('button_start_calibration'))
        self.button_start_calibration.setStyleSheet(unactived_button)
        
        # Create a horizontal layout for the camera and the graph
        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.addWidget(self.camera_widget)
        self.horizontal_layout.addWidget(self.graph_calibration)

        # Add widgets to the main layout
        self.layout.addWidget(self.label_title_calibration_menu)
        self.layout.addLayout(self.horizontal_layout)
        self.layout.addWidget(self.button_start_calibration)

        self.master_widget.setLayout(self.layout)

        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

        # Other initializations
        # ---------------------
        self.camera_thread = CameraThread()
        self.camera_thread.set_camera(self.camera)
        self.camera_thread.image_acquired.connect(self.thread_update_image)
        self.camera_thread.start()
    
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

            msg_box = QMessageBox()
            msg_box.setStyleSheet(styleH3)
            msg_box.warning(self, translate('error'), translate('message_no_cam_error'))
            print('No cam => Quit')
            sys.exit(QApplication.instance())
        else:
            print("Camera")
            device = manager.Devices()[0].OpenDevice(ids_peak.DeviceAccessType_Exclusive)
        return device
    
    def thread_update_image(self, image_array):
        """Action performed when the live acquisition (via CameraThread) is running."""
        try:
            frame_width = self.camera_widget.width()
            frame_height = self.camera_widget.height()
            if self.camera_thread.running:
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
        except Exception as e:
            print(f'Exception - update_image {e}')

# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    from ids_peak import ids_peak

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle('Test - Piezo calibration')
            self.setGeometry(300, 300, 1000, 600)

            self.central_widget = PiezoCalibrationWidget()
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
                event.accept()
            else:
                event.ignore()


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
