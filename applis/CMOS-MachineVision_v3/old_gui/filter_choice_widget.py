# -*- coding: utf-8 -*-
"""*filter_choice_widget.py* file.

This file is attached to a 2nd year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-Detection.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>

"""

import sys
import numpy as np
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLineEdit, QCheckBox,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from lensepy import load_dictionary, translate
from lensepy.css import *

from enum import Enum

if __name__ == '__main__':
    from slider_bloc import SliderBloc
else:
    from gui.slider_bloc import SliderBloc

class Filter(Enum):
    NOFILTER = 0
    THRESHOLD = 1
    BLUR = 2
    MORPHO = 3
    EDGE = 4
    CONTRAST = 5


# %% Widget

class NoiseWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent

        # Title
        # -----
        self.label_title_noise_choice = QLabel(translate('title_noise_choice'))
        self.label_title_noise_choice.setStyleSheet(styleH1)

        self.percent_noise = SliderBloc('Percent', '%', 0, 20)
        self.stddev_noise = SliderBloc('StdDev', '', 0, 20)

        self.layout.addWidget(self.label_title_noise_choice)
        self.layout.addStretch()
        self.layout.addWidget(self.percent_noise)
        self.layout.addWidget(self.stddev_noise)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def add_gaussian_noise(self, image: np.ndarray, std_dev: float = 0.1, noise_space: float = 0.1):
        """

        :param image: Image (8 bits) to add noise.
        :param std_dev: Standard deviation of the gaussian function.
        :param noise_space: Percent of noise in the image.
        :return: Image with added noise.
        """
        # Adding noise / Gaussian law
        mask = np.random.choice([0, 1], size=image.shape, p=[1 - noise_space, noise_space])
        mean = 0
        gaussian_noise = np.random.normal(mean, std_dev, image.shape)
        image_noisy = image + 255 * gaussian_noise * mask
        image_noisy = np.clip(image_noisy, 0, 255)
        return image_noisy.astype(np.uint8)



class FilterChoiceWidget(QWidget):
    filter_clicked = pyqtSignal(str)

    def __init__(self, parent):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.filter_selection = Filter.NOFILTER

        # Title
        # -----
        self.label_title_filter_choice = QLabel(translate('title_filter_choice'))
        self.label_title_filter_choice.setStyleSheet(styleH1)

        self.check_diff_image = QCheckBox(translate('diff_image'))
        self.check_noise = QCheckBox(translate('noise_image'))

        self.filter_choice_blur = QPushButton(translate('button_filter_choice_blur'))
        self.filter_choice_blur.setStyleSheet(styleH2)
        self.filter_choice_blur.setStyleSheet(unactived_button)
        self.filter_choice_blur.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.filter_choice_blur.clicked.connect(self.clicked_action)

        self.filter_choice_edge = QPushButton(translate('button_filter_choice_edge'))
        self.filter_choice_edge.setStyleSheet(styleH2)
        self.filter_choice_edge.setStyleSheet(unactived_button)
        self.filter_choice_edge.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.filter_choice_edge.clicked.connect(self.clicked_action)

        self.noise_widget = NoiseWidget(self)

        self.layout.addWidget(self.label_title_filter_choice)
        self.layout.addWidget(self.check_diff_image)
        self.layout.addWidget(self.filter_choice_blur)
        self.layout.addWidget(self.filter_choice_edge)
        self.layout.addStretch()
        self.layout.addWidget(self.check_noise)
        self.layout.addWidget(self.noise_widget)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def clicked_action(self):
        """Action performed when a button is clicked."""
        self.unactive_buttons()
        sender = self.sender()
        sender.setStyleSheet(actived_button)
        if sender == self.filter_choice_blur:
            self.filter_selection = Filter.BLUR
        elif sender == self.filter_choice_edge:
            self.filter_selection = Filter.EDGE

        self.filter_clicked.emit('new')

    def unactive_buttons(self):
        self.filter_choice_blur.setStyleSheet(unactived_button)
        self.filter_choice_edge.setStyleSheet(unactived_button)

    def get_selection(self):
        """Return the kind of filter selected."""
        return self.filter_selection

    def is_diff_checked(self):
        return self.check_diff_image.isChecked()

    def is_noise_checked(self):
        return self.check_diff_image.isChecked()

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

            self.central_widget = FilterChoiceWidget(self)
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
