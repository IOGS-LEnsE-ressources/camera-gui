# -*- coding: utf-8 -*-
"""*camera_params_view_widget.py* file.

This file is attached to a 2nd year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-Detection.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>

"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QFrame,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)

if __name__ == '__main__':
    from slider_bloc import SliderBloc
else:
    from gui.slider_bloc import SliderBloc

from lensepy import load_dictionary, translate
from lensepy.css import *
from lensecam.ids.camera_ids import CameraIds
from lensecam.basler.camera_basler import CameraBasler


# %% Widget
class CameraParamsViewWidget(QWidget):
    def __init__(self, parent = None, editable: bool = False):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.first_display = True
        self.fps_available = True
        self.clock_available = True

        # Horizontal Line
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)

        # Title
        # -----
        self.label_title_camera_settings = QLabel(translate('title_camera_params_view'))
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

        # Clock Frequency
        # --------
        min_val, max_val = 10, 30  # MHz
        if self.parent.camera is not None and self.parent.camera.camera_connected:
            min_val, max_val = self.parent.camera.get_clock_frequency_range()
            min_val = min_val//1e6
            max_val = max_val//1e6
        else:
            min_val, max_val = 10, 30 # MHz
        if max_val == 0:
            self.slider_clock_freq = QLabel('Pixel Clock - Not Available')
            self.clock_available = False
        else:
            self.slider_clock_freq = SliderBloc(title='name_clock_freq', unit='MHz', min_value=min_val, max_value=max_val)
            self.slider_clock_freq.slider_changed.connect(self.slider_clock_freq_changing)

        # Frame Rate
        # --------
        if self.parent.camera is not None and self.parent.camera.camera_connected:
            min_fps, max_fps = self.parent.camera.get_frame_rate_range()
            fps = self.parent.camera.get_frame_rate()
        else:
            min_fps, max_fps = 2, 10 # MHz
            fps = 5

        if max_fps == 0:
            self.slider_frame_rate = QLabel('FPS - Not Available')
            self.fps_available = False
        else:
            self.slider_frame_rate = SliderBloc(title='name_frame_rate', unit='FPS', min_value=min_fps, max_value=max_fps)
            self.slider_frame_rate.set_value(fps)
            self.slider_frame_rate.slider_changed.connect(self.slider_frame_rate_changing)

        # Add elements
        self.layout.addWidget(self.label_title_camera_settings)
        self.layout.addWidget(line1)
        self.layout.addWidget(self.subwidget_camera_name)
        self.layout.addWidget(line2)
        self.layout.addWidget(self.slider_clock_freq)
        self.layout.addWidget(self.slider_frame_rate)
        self.layout.addStretch()
        self.setLayout(self.layout)
        #self.update_parameters()

    def slider_clock_freq_changing(self, event):
        """Action performed when the clock frequency slider changed."""
        if self.parent.camera is not None:
            clock_frequency_value = self.slider_clock_freq.get_value() * 1e6  # From MHz to Hz
            self.parent.camera_thread.stop()
            self.parent.camera.set_clock_frequency(clock_frequency_value) # in Hz
            self.parent.camera_thread.start()
            self.update_parameters()
        else:
            print('No Camera Connected')

    def slider_frame_rate_changing(self, event):
        """Action performed when the clock frequency slider changed."""
        if self.parent.camera is not None:
            fps = self.slider_frame_rate.get_value()
            self.parent.camera.set_frame_rate(fps) # in Hz
            self.update_parameters()
        else:
            print('No Camera Connected')

    def update_parameters(self):
        if self.parent.camera is not None:
            if self.clock_available:
                if self.first_display:
                    clock_value = self.parent.camera.get_clock_frequency()
                    self.slider_clock_freq.set_value(clock_value / 1e6)
                    self.first_display = False
                self.slider_clock_freq.set_enabled(True)
            serial_no, camera_name = self.parent.camera.get_cam_info()
            self.label_value_camera_name.setText(camera_name)
        else:
            self.label_value_camera_name.setText('No Camera')


class CameraParamsInfosWidget(QWidget):
    def __init__(self, parent=None, editable: bool = False):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.first_display = True

        # Horizontal Line
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)

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

        # Range Value - Exposure time
        # --------
        self.subwidget_exposure_time = QWidget()
        self.sublayout_exposure_time = QVBoxLayout()
        self.subwidget_exposure_time.setLayout(self.sublayout_exposure_time)
        self.label_title_exposure_time = QLabel(translate("label_title_exposure_time"))
        self.label_title_exposure_time.setStyleSheet(styleH2)
        self.sublayout_exposure_time.addWidget(self.label_title_exposure_time)

        self.subwidget_exposure_time_min = QWidget()
        self.sublayout_exposure_time_min = QHBoxLayout()
        self.label_exposure_time_min = QLabel(translate("label_exposure_time_min"))
        self.label_exposure_time_min.setStyleSheet(styleH3)
        self.label_exposure_time_min_value = QLabel(' ms')
        self.label_exposure_time_min_value.setStyleSheet(styleH3)
        self.sublayout_exposure_time_min.addWidget(self.label_exposure_time_min)
        self.sublayout_exposure_time_min.addStretch()
        self.sublayout_exposure_time_min.addWidget(self.label_exposure_time_min_value)
        self.sublayout_exposure_time_min.setContentsMargins(0, 0, 0, 0)
        self.subwidget_exposure_time_min.setLayout(self.sublayout_exposure_time_min)
        self.sublayout_exposure_time.addWidget(self.subwidget_exposure_time_min)

        self.subwidget_exposure_time_max = QWidget()
        self.sublayout_exposure_time_max = QHBoxLayout()
        self.label_exposure_time_max = QLabel(translate("label_exposure_time_max"))
        self.label_exposure_time_max.setStyleSheet(styleH3)
        self.label_exposure_time_max_value = QLabel(' ms')
        self.label_exposure_time_max_value.setStyleSheet(styleH3)
        self.sublayout_exposure_time_max.addWidget(self.label_exposure_time_max)
        self.sublayout_exposure_time_max.addStretch()
        self.sublayout_exposure_time_max.addWidget(self.label_exposure_time_max_value)
        self.sublayout_exposure_time_max.setContentsMargins(0, 0, 0, 0)
        self.subwidget_exposure_time_max.setLayout(self.sublayout_exposure_time_max)
        self.sublayout_exposure_time.addWidget(self.subwidget_exposure_time_max)

        # Range Value - Frame Rate
        # --------
        self.subwidget_frame_rate = QWidget()
        self.sublayout_frame_rate = QVBoxLayout()
        self.subwidget_frame_rate.setLayout(self.sublayout_frame_rate)
        self.label_title_frame_rate = QLabel(translate("label_title_frame_rate"))
        self.label_title_frame_rate.setStyleSheet(styleH2)
        self.sublayout_frame_rate.addWidget(self.label_title_frame_rate)

        self.subwidget_frame_rate_min = QWidget()
        self.sublayout_frame_rate_min = QHBoxLayout()
        self.label_frame_rate_min = QLabel(translate("label_frame_rate_min"))
        self.label_frame_rate_min.setStyleSheet(styleH3)
        self.label_frame_rate_min_value = QLabel(' FPS')
        self.label_frame_rate_min_value.setStyleSheet(styleH3)
        self.sublayout_frame_rate_min.addWidget(self.label_frame_rate_min)
        self.sublayout_frame_rate_min.addStretch()
        self.sublayout_frame_rate_min.addWidget(self.label_frame_rate_min_value)
        self.sublayout_frame_rate_min.setContentsMargins(0, 0, 0, 0)
        self.subwidget_frame_rate_min.setLayout(self.sublayout_frame_rate_min)
        self.sublayout_frame_rate.addWidget(self.subwidget_frame_rate_min)

        self.subwidget_frame_rate_max = QWidget()
        self.sublayout_frame_rate_max = QHBoxLayout()
        self.label_frame_rate_max = QLabel(translate("label_frame_rate_max"))
        self.label_frame_rate_max.setStyleSheet(styleH3)
        self.label_frame_rate_max_value = QLabel(' FPS')
        self.label_frame_rate_max_value.setStyleSheet(styleH3)
        self.sublayout_frame_rate_max.addWidget(self.label_frame_rate_max)
        self.sublayout_frame_rate_max.addStretch()
        self.sublayout_frame_rate_max.addWidget(self.label_frame_rate_max_value)
        self.sublayout_frame_rate_max.setContentsMargins(0, 0, 0, 0)
        self.subwidget_frame_rate_max.setLayout(self.sublayout_frame_rate_max)
        self.sublayout_frame_rate.addWidget(self.subwidget_frame_rate_max)

        # Add elements
        self.layout.addWidget(self.subwidget_camera_id)
        self.layout.addWidget(self.subwidget_camera_size)
        self.layout.addWidget(line1)
        self.layout.addWidget(self.subwidget_exposure_time)
        self.layout.addWidget(line2)
        self.layout.addWidget(self.subwidget_frame_rate)
        self.layout.addStretch()
        self.setLayout(self.layout)
        #self.update_parameters()

    def slider_clock_freq_changing(self, event):
        """Action performed when the clock frequency slider changed."""
        if self.parent.camera is not None:
            clock_frequency_value = self.slider_clock_freq.get_value() * 1e6  # From MHz to Hz
            self.parent.camera_thread.stop()
            self.parent.camera.set_clock_frequency(clock_frequency_value)  # in Hz
            self.parent.camera_thread.start()
            self.update_parameters()
        else:
            print('No Camera Connected')

    def slider_frame_rate_changing(self, event):
        """Action performed when the clock frequency slider changed."""
        if self.parent.camera is not None:
            fps = self.slider_frame_rate.get_value()
            self.parent.camera.set_frame_rate(fps)  # in Hz
            self.update_parameters()
        else:
            print('No Camera Connected')

    def update_parameters(self):
        if self.parent.camera is not None:
            serial_no, camera_name = self.parent.camera.get_cam_info()
            self.label_value_camera_id.setText(serial_no)
            max_width, max_height = self.parent.camera.get_sensor_size()
            self.label_value_camera_size.setText(f'W={max_width} x H={max_height} px')
            # Temperature sensors are not implemented in old version of camera
            # temperature = self.parent.camera.get_temperature()
            min_expo, max_expo = self.parent.camera.get_exposure_range()
            self.label_exposure_time_min_value.setText(f'{round(min_expo / 1000, 2)} ms')
            self.label_exposure_time_max_value.setText(f'{round(max_expo / 1000, 2)} ms')
            min_fps, max_fps = self.parent.camera.get_frame_rate_range()
            min_fps = round(min_fps, 1)
            max_fps = round(max_fps, 1)
            self.label_frame_rate_min_value.setText(f'{min_fps} FPS')
            self.label_frame_rate_max_value.setText(f'{max_fps} FPS')
        else:
            self.label_value_camera_id.setText('No Camera')


# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication


    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.camera = None

            # Translation
            dictionary = {}
            # Load French dictionary
            # dictionary = load_dictionary('../lang/dict_FR.txt')
            # Load English dictionary
            dictionary = load_dictionary('../lang/dict_EN.txt')

            self.setWindowTitle(translate("window_title_camera_settings"))
            self.setGeometry(300, 300, 400, 600)

            self.central_widget = CameraParamsViewWidget(self)
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