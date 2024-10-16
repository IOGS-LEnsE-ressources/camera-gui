# -*- coding: utf-8 -*-
"""*camera_settings_widget.py* file.

This file is attached to a 2nd year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-Detection.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>

"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal
if __name__ == '__main__':
    from slider_bloc import SliderBloc
else:
    from gui.slider_bloc import SliderBloc

from lensepy import load_dictionary, translate
from lensepy.css import *
from lensecam.ids.camera_ids import CameraIds
from lensecam.basler.camera_basler import CameraBasler


# %% Widget
class CameraSettingsWidget(QWidget):

    settings_changed = pyqtSignal(str)

    def __init__(self, camera: CameraIds or CameraBasler):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.camera = camera

        # Title
        # -----
        self.label_title_camera_settings = QLabel(translate('title_camera_settings'))
        self.label_title_camera_settings.setStyleSheet(styleH1)

        # Camera ID
        # ---------
        self.subwidget_camera_id = QWidget()
        self.sublayout_camera_id = QHBoxLayout()

        self.label_title_camera_id = QLabel(translate("label_title_camera_id"))
        self.label_title_camera_id.setStyleSheet(styleH2)

        self.label_value_camera_id = QLabel(translate("label_value_camera_id"))
        self.label_value_camera_id.setStyleSheet(styleH3)

        self.sublayout_camera_id.addWidget(self.label_title_camera_id)
        self.sublayout_camera_id.addStretch()
        self.sublayout_camera_id.addWidget(self.label_value_camera_id)
        self.sublayout_camera_id.setContentsMargins(0, 0, 0, 0)

        self.subwidget_camera_id.setLayout(self.sublayout_camera_id)

        # Settings
        # --------
        self.slider_exposure_time = SliderBloc(title='name_slider_exposure_time', unit='ms', min_value=0, max_value=10)
        self.slider_exposure_time.slider_changed.connect(self.slider_exposure_time_changing)

        self.slider_black_level = SliderBloc(title='name_slider_black_level', unit='gray',
                                              min_value=0, max_value=255, is_integer=True)
        self.slider_black_level.slider_changed.connect(self.slider_black_level_changing)

        self.layout.addWidget(self.label_title_camera_settings)
        self.layout.addWidget(self.subwidget_camera_id)
        self.layout.addWidget(self.slider_exposure_time)
        self.layout.addWidget(self.slider_black_level)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def slider_exposure_time_changing(self, event):
        """Action performed when the exposure time slider changed."""
        if self.camera is not None:
            exposure_time_value = self.slider_exposure_time.get_value() * 1000
            self.camera.set_exposure(exposure_time_value)
            self.settings_changed.emit('camera_settings_changed')
        else:
            print('No Camera Connected')

    def slider_black_level_changing(self, event):
        """Action performed when the exposure time slider changed."""
        if self.camera is not None:
            black_level_value = self.slider_black_level.get_value()
            self.camera.set_black_level((black_level_value//4) * 4)
            self.settings_changed.emit('changed')
        else:
            print('No Camera Connected')

    def update_parameters(self, auto_min_max: bool = False) -> None:
        """Update displayed parameters values, from the camera.

        """
        if auto_min_max:
            exposure_min, exposure_max = self.camera.get_exposure_range()
            if exposure_max > 400000:
                exposure_max = 400000
            self.slider_exposure_time.set_min_max_slider_values(exposure_min // 1000, exposure_max // 1000)
            bl_min, bl_max = self.camera.get_black_level_range()
            self.slider_black_level.set_min_max_slider_values(bl_min, bl_max)
        exposure_time = self.camera.get_exposure()
        self.slider_exposure_time.set_value(exposure_time / 1000)
        bl = self.camera.get_black_level()
        self.slider_black_level.set_value(bl)


class CameraInfosWidget(QWidget):
    def __init__(self, parent = None):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.first_display = True

        # Title
        # -----
        self.label_title_camera_settings = QLabel(translate('title_camera_infos_view'))
        self.label_title_camera_settings.setStyleSheet(styleH1)

        # Camera Name
        # ---------
        self.subwidget_camera_name = QWidget()
        self.sublayout_camera_name = QHBoxLayout()
        self.label_title_camera_name = QLabel(translate("label_title_camera_name"))
        self.label_title_camera_name.setStyleSheet(styleH2)
        self.label_value_camera_name = QLabel()
        self.label_value_camera_name.setStyleSheet(styleH3)
        self.sublayout_camera_name.addWidget(self.label_title_camera_name)
        self.sublayout_camera_name.addStretch()
        self.sublayout_camera_name.addWidget(self.label_value_camera_name)
        self.sublayout_camera_name.setContentsMargins(0, 0, 0, 0)
        self.subwidget_camera_name.setLayout(self.sublayout_camera_name)

        # Camera ID
        # ---------
        self.subwidget_camera_id = QWidget()
        self.sublayout_camera_id = QHBoxLayout()
        self.label_title_camera_id = QLabel(translate("label_title_camera_id"))
        self.label_title_camera_id.setStyleSheet(styleH2)
        self.label_value_camera_id = QLabel()
        self.label_value_camera_id.setStyleSheet(styleH3)
        self.sublayout_camera_id.addWidget(self.label_title_camera_id)
        self.sublayout_camera_id.addStretch()
        self.sublayout_camera_id.addWidget(self.label_value_camera_id)
        self.sublayout_camera_id.setContentsMargins(0, 0, 0, 0)
        self.subwidget_camera_id.setLayout(self.sublayout_camera_id)

        # Camera Size
        # ---------
        self.subwidget_camera_size = QWidget()
        self.sublayout_camera_size = QHBoxLayout()
        self.label_title_camera_size = QLabel(translate("label_title_camera_size"))
        self.label_title_camera_size.setStyleSheet(styleH2)
        self.label_value_camera_size = QLabel()
        self.label_value_camera_size.setStyleSheet(styleH3)
        self.sublayout_camera_size.addWidget(self.label_title_camera_size)
        self.sublayout_camera_size.addStretch()
        self.sublayout_camera_size.addWidget(self.label_value_camera_size)
        self.sublayout_camera_size.setContentsMargins(0, 0, 0, 0)
        self.subwidget_camera_size.setLayout(self.sublayout_camera_size)

        # Camera Main Parameters / Exposure Time
        self.subwidget_camera_expo = QWidget()
        self.sublayout_camera_expo = QHBoxLayout()
        self.label_title_camera_exposure = QLabel(translate("label_title_camera_exposure"))
        self.label_title_camera_exposure.setStyleSheet(styleH2)
        self.label_value_camera_exposure = QLabel()
        self.label_value_camera_exposure.setStyleSheet(styleH3)
        self.sublayout_camera_expo.addWidget(self.label_title_camera_exposure)
        self.sublayout_camera_expo.addStretch()
        self.sublayout_camera_expo.addWidget(self.label_value_camera_exposure)
        self.sublayout_camera_expo.setContentsMargins(0, 0, 0, 0)
        self.subwidget_camera_expo.setLayout(self.sublayout_camera_expo)
        # Camera Main Parameters / FPS
        self.subwidget_camera_fps = QWidget()
        self.sublayout_camera_fps = QHBoxLayout()
        self.label_title_camera_fps = QLabel(translate("label_title_camera_fps"))
        self.label_title_camera_fps.setStyleSheet(styleH2)
        self.label_value_camera_fps = QLabel()
        self.label_value_camera_fps.setStyleSheet(styleH3)
        self.sublayout_camera_fps.addWidget(self.label_title_camera_fps)
        self.sublayout_camera_fps.addStretch()
        self.sublayout_camera_fps.addWidget(self.label_value_camera_fps)
        self.sublayout_camera_fps.setContentsMargins(0, 0, 0, 0)
        self.subwidget_camera_fps.setLayout(self.sublayout_camera_fps)

        # Add elements
        self.layout.addWidget(self.label_title_camera_settings)
        self.layout.addWidget(self.subwidget_camera_name)
        self.layout.addWidget(self.subwidget_camera_id)
        self.layout.addWidget(self.subwidget_camera_size)
        self.layout.addStretch()
        self.layout.addWidget(self.subwidget_camera_expo)
        self.layout.addWidget(self.subwidget_camera_fps)
        self.setLayout(self.layout)
        self.update_parameters()

    def update_parameters(self):
        if self.parent.camera is not None:
            serial_no, camera_name = self.parent.camera.get_cam_info()
            self.label_value_camera_name.setText(camera_name)
            self.label_value_camera_id.setText(serial_no)
            max_width, max_height = self.parent.camera.get_sensor_size()
            self.label_value_camera_size.setText(f'W={max_width} x H={max_height} px')
            fps = self.parent.camera.get_frame_rate()
            self.label_value_camera_fps.setText(f'{fps} Frame/s (fps)')
            expo = self.parent.camera.get_exposure() / 1000
            self.label_value_camera_exposure.setText(f'{expo} ms')
        else:
            self.label_value_camera_name.setText('No Camera')
            self.label_value_camera_id.setText('No Camera')






# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication


    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Translation
            dictionary = {}
            # Load French dictionary
            # dictionary = load_dictionary('../lang/dict_FR.txt')
            # Load English dictionary
            dictionary = load_dictionary('../lang/dict_EN.txt')

            self.setWindowTitle(translate("window_title_camera_settings"))
            self.setGeometry(300, 300, 400, 600)

            self.central_widget = CameraSettingsWidget(camera=None)
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