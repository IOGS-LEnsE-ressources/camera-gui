# -*- coding: utf-8 -*-
"""*preprocessing_widget.py* file.

This file is attached to engineer training labworks in photonics.
- 1st year subject :
- 2nd year subject : http://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-Detection.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/contents/appli_CMOS_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>

Creation : 08/oct/2024
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLineEdit, QProgressBar, QComboBox, QCheckBox,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal

if __name__ == '__main__':
    from slider_bloc import SliderBloc
else:
    from gui.slider_bloc import SliderBloc

from lensepy import load_dictionary, translate
from lensepy.css import *


class PreprocSubMenuWidget(QWidget):
    """

    """

    preproc_submenu_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout()
        self.parent = parent

        # Title
        # -----
        self.label_title_preprocessing = QLabel(translate('title_preprocessing'))
        self.label_title_preprocessing.setStyleSheet(styleH1)

        self.button_preproc_contrast = QPushButton(translate("button_preproc_contrast"))
        self.button_preproc_contrast.setStyleSheet(unactived_button)
        self.button_preproc_contrast.setFixedHeight(BUTTON_HEIGHT)
        self.button_preproc_contrast.clicked.connect(self.menu_action)
        self.button_preproc_enhance = QPushButton(translate("button_preproc_enhance"))
        self.button_preproc_enhance.setStyleSheet(unactived_button)
        self.button_preproc_enhance.setFixedHeight(BUTTON_HEIGHT)
        self.button_preproc_enhance.clicked.connect(self.menu_action)


        self.button_preproc_erosion = QPushButton(translate("button_preproc_erosion"))
        self.button_preproc_erosion.setStyleSheet(unactived_button)
        self.button_preproc_erosion.setFixedHeight(BUTTON_HEIGHT)
        self.button_preproc_erosion.clicked.connect(self.menu_action)
        self.button_preproc_opening = QPushButton(translate("button_preproc_opening"))
        self.button_preproc_opening.setStyleSheet(unactived_button)
        self.button_preproc_opening.setFixedHeight(BUTTON_HEIGHT)
        self.button_preproc_opening.clicked.connect(self.menu_action)
        self.button_preproc_gradient = QPushButton(translate("button_preproc_gradient"))
        self.button_preproc_gradient.setStyleSheet(unactived_button)
        self.button_preproc_gradient.setFixedHeight(BUTTON_HEIGHT)
        self.button_preproc_gradient.clicked.connect(self.menu_action)

        self.layout.addWidget(self.label_title_preprocessing)
        self.layout.addWidget(self.button_preproc_contrast)
        self.layout.addWidget(self.button_preproc_enhance)
        self.layout.addStretch()
        self.layout.addWidget(self.button_preproc_erosion)
        self.layout.addWidget(self.button_preproc_opening)
        self.layout.addWidget(self.button_preproc_gradient)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def unactive_buttons(self):
        """ Switches all buttons to inactive style """
        self.button_preproc_contrast.setStyleSheet(unactived_button)
        self.button_preproc_enhance.setStyleSheet(unactived_button)
        self.button_preproc_erosion.setStyleSheet(unactived_button)
        self.button_preproc_opening.setStyleSheet(unactived_button)
        self.button_preproc_gradient.setStyleSheet(unactived_button)

    def menu_action(self):
        """Action performed when a button is clicked."""
        self.unactive_buttons()
        sender = self.sender()
        if sender == self.button_preproc_contrast:
            sender.setStyleSheet(actived_button)
            self.preproc_submenu_changed.emit('preproc_contrast')
        elif sender == self.button_preproc_enhance:
            sender.setStyleSheet(actived_button)
            self.preproc_submenu_changed.emit('preproc_enhance')
        elif sender == self.button_preproc_erosion:
            sender.setStyleSheet(actived_button)
            self.preproc_submenu_changed.emit('preproc_erosion')
        elif sender == self.button_preproc_opening:
            sender.setStyleSheet(actived_button)
            self.preproc_submenu_changed.emit('preproc_opening')
        elif sender == self.button_preproc_gradient:
            sender.setStyleSheet(actived_button)
            self.preproc_submenu_changed.emit('preproc_gradient')



class ContrastWidget(QWidget):

    contrast_clicked = pyqtSignal(str)

    def __init__(self, parent):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent

        # Title
        # -----
        self.label_title_contrast_choice = QLabel(translate('title_contrast_choice'))
        self.label_title_contrast_choice.setStyleSheet(styleH1)

        self.check_diff_image = QCheckBox(translate('diff_image'))

        self.contrast_threshold = QPushButton(translate('button_contrast_threshold'))
        self.contrast_threshold.setStyleSheet(styleH2)
        self.contrast_threshold.setStyleSheet(unactived_button)
        self.contrast_threshold.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.contrast_threshold.clicked.connect(self.clicked_action)

        self.contrast_process = QPushButton(translate('button_contrast_process'))
        self.contrast_process.setStyleSheet(styleH2)
        self.contrast_process.setStyleSheet(unactived_button)
        self.contrast_process.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.contrast_process.clicked.connect(self.clicked_action)

        self.layout.addWidget(self.label_title_contrast_choice)
        self.layout.addWidget(self.check_diff_image)
        self.layout.addWidget(self.contrast_threshold)
        self.layout.addWidget(self.contrast_process)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def clicked_action(self):
        """Action performed when a button is clicked."""
        self.unactive_buttons()
        sender = self.sender()
        sender.setStyleSheet(actived_button)
        '''
        if sender == self.contrast_threshold:
            self.filter_selection = Filter.THRESHOLD
        elif sender == self.contrast_process:
            self.filter_selection = Filter.CONTRAST
        '''
        self.contrast_clicked.emit('new')

    def unactive_buttons(self):
        self.contrast_threshold.setStyleSheet(unactived_button)
        self.contrast_process.setStyleSheet(unactived_button)

    def get_selection(self):
        """Return the kind of filter selected."""
        return 0
        # return self.filter_selection

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

            self.setWindowTitle(translate("test_interface"))
            self.setGeometry(300, 300, 400, 600)

            self.central_widget = PreprocSubMenuWidget(self)
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