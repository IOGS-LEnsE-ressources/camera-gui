# -*- coding: utf-8 -*-
"""*mini_params_widget.py* file.

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
    QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox, QSlider,
    QMessageBox
)
from PyQt6.QtCore import Qt

from lensepy import load_dictionary, translate
from lensepy.css import *
from lensecam.ids.camera_ids import CameraIds

if __name__ == '__main__':
    from slider_bloc import SliderBloc
else:
    from gui.slider_bloc import SliderBloc

# %% To add in lensepy librairy
# Styles
# ------
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

# %% Params
BUTTON_HEIGHT = 60  # px
OPTIONS_BUTTON_HEIGHT = 20  # px


# %% Widget
class MiniParamsWidget(QWidget):
    def __init__(self, parent):
        """

        """
        super().__init__(parent=parent)
        self.parent = parent
        self.layout = QGridLayout()

        self.slider_exposure = SliderBloc('Exposure Time', 'ms', 0, 100)
        self.slider_exposure.set_enabled(False)
        self.slider_exposure.slider_changed.connect(self.action_slider_changing)
        self.slider_exposure_enabling = QCheckBox(parent=self)
        self.slider_exposure_enabling.clicked.connect(self.action_enabling)
        self.layout.addWidget(self.slider_exposure, 0, 0)
        self.layout.addWidget(self.slider_exposure_enabling, 0, 1)


        self.black_level_title = QLabel('Black Level (gray) = ')
        self.black_level_title.setStyleSheet(styleH2)
        self.black_level_value = QLabel('')
        self.black_level_value.setStyleSheet(styleH2)
        self.layout.addWidget(self.black_level_title, 1, 0)
        self.layout.addWidget(self.black_level_value, 1, 1)

        self.size_title = QLabel('Size (W x H) = ')
        self.size_title.setStyleSheet(styleH2)
        self.size_value = QLabel('')
        self.size_value.setStyleSheet(styleH2)


        self.layout.addWidget(self.size_title, 2, 0)
        self.layout.addWidget(self.size_value, 2, 1)

        self.setLayout(self.layout)

    def set_parameters(self, camera):
        """ Update displayed parameters from the sensor."""
        exposure = round(camera.get_exposure() / 1000, 2)
        black_level = int(camera.get_black_level())
        width, height = camera.get_sensor_size()
        self.slider_exposure.set_value(exposure)
        self.black_level_value.setText(str(black_level))
        self.size_value.setText(f'{int(width)} x {int(height)}')

    def action_enabling(self):
        if self.slider_exposure_enabling.isChecked():
            self.slider_exposure.set_enabled(True)
            min_val, max_val = self.parent.parent.camera.get_exposure_range()
            if self.parent.parent.brand == "Basler":
                if max_val > 100000:
                    max_val = 100000
            self.slider_exposure.set_min_max_slider_values(round(min_val/1000, 1), round(max_val/1000, 1))
        else:
            self.slider_exposure.set_enabled(False)

    def action_slider_changing(self):
        value = self.slider_exposure.get_value() * 1000
        self.parent.parent.camera.set_exposure(value)

    def set_enabled(self):
        self.slider_exposure_enabling.setEnabled(True)
        if self.slider_exposure_enabling.isChecked():
            self.slider_exposure.set_enabled(True)

    def set_disabled(self):
        self.slider_exposure.set_enabled(False)
        self.slider_exposure_enabling.setEnabled(False)

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
            self.setGeometry(300, 300, 600, 300)

            self.central_widget = MiniParamsWidget(self)
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