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

# %% To add in lensepy librairy
# Styles
# ------
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

# %% Params
BUTTON_HEIGHT = 60  # px
OPTIONS_BUTTON_HEIGHT = 20  # px


class Filter(Enum):
    NOFILTER = 0
    THRESHOLD = 1
    BLUR = 2
    MORPHO = 3
    EDGE = 4


# %% Widget
class ContrastWidget(QWidget):
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
        self.label_title_contrast_choice = QLabel(translate('title_contrast_choice'))
        self.label_title_contrast_choice.setStyleSheet(styleH1)

        self.check_diff_image = QCheckBox(translate('diff_image'))
        self.check_noise = QCheckBox(translate('noise_image'))

        self.filter_choice_threshold = QPushButton(translate('button_filter_choice_threshold'))
        self.filter_choice_threshold.setStyleSheet(styleH2)
        self.filter_choice_threshold.setStyleSheet(unactived_button)
        self.filter_choice_threshold.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.filter_choice_threshold.clicked.connect(self.clicked_action)

        self.noise_widget = QWidget()

        self.layout.addWidget(self.label_title_contrast_choice)
        self.layout.addWidget(self.check_diff_image)
        self.layout.addWidget(self.filter_choice_threshold)
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
        if sender == self.filter_choice_threshold:
            self.filter_selection = Filter.THRESHOLD

        self.filter_clicked.emit('new')

    def unactive_buttons(self):
        self.filter_choice_threshold.setStyleSheet(unactived_button)

    def get_selection(self):
        """Return the kind of filter selected."""
        return self.filter_selection

    def is_diff_checked(self):
        return self.check_diff_image.isChecked()

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

        self.noise_widget = QWidget()

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
