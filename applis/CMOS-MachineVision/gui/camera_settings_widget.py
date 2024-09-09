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

if __name__ == '__main__':
    from slider_bloc import SliderBloc
else:
    from gui.slider_bloc import SliderBloc

from lensepy import load_dictionary, translate
from lensepy.css import *
from lensecam.ids.camera_ids import CameraIds

# %% To add in lensepy librairy
# Styles
# ------
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

# %% Params
BUTTON_HEIGHT = 60  # px
OPTIONS_BUTTON_HEIGHT = 20  # px


# %% Widget
class CameraSettingsWidget(QWidget):
    def __init__(self, camera: CameraIds):
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
        else:
            print('No Camera Connected')

    def slider_black_level_changing(self, event):
        """Action performed when the exposure time slider changed."""
        if self.camera is not None:
            black_level_value = self.slider_black_level.get_value()
            self.camera.set_black_level(black_level_value)
        else:
            print('No Camera Connected')

    def update_parameters(self, auto_min_max: bool = False) -> None:
        """Update displayed parameters values, from the camera.

        """
        if auto_min_max:
            exposure_min, exposure_max = self.camera.get_exposure_range()
            self.slider_exposure_time.set_min_max_slider_values(exposure_min // 1000, exposure_max // 1000)
            bl_min, bl_max = self.camera.get_black_level_range()
            self.slider_black_level.set_min_max_slider_values(bl_min, bl_max)
        exposure_time = self.camera.get_exposure()
        self.slider_exposure_time.set_value(exposure_time / 1000)
        bl = self.camera.get_black_level()
        self.slider_black_level.set_value(bl)
        print('Updated')

    def set_parameters(self, color_mode: str = 'Mono8', frame_rate: float = 3,
                       exposure: float = 2, black_level: int = 10):
        """Useful ?

        """
        pass


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