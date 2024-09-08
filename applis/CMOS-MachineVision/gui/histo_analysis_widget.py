# -*- coding: utf-8 -*-
"""*histo_analysis_widget.py* file.

This file is attached to a 2nd year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-Detection.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>

"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLineEdit,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

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
class HistoAnalysisWidget(QWidget):

    snap_clicked = pyqtSignal(str)

    def __init__(self, parent):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent

        # Title
        # -----
        self.label_title_spatial_analysis = QLabel(translate('title_histo_analysis'))
        self.label_title_spatial_analysis.setStyleSheet(styleH1)

        self.snap_button = QPushButton('button_acquire_histo')
        self.snap_button.setStyleSheet(styleH2)
        self.snap_button.setStyleSheet(unactived_button)
        self.snap_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.snap_button.clicked.connect(self.clicked_action)

        self.save_histo_button = QPushButton('button_save_histo_spatial')
        self.save_histo_button.setStyleSheet(styleH2)
        self.save_histo_button.setStyleSheet(disabled_button)
        self.save_histo_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.save_histo_button.clicked.connect(self.clicked_action)
        self.save_histo_button.setEnabled(False)

        self.save_raw_image_button = QPushButton('button_save_raw_image_spatial')
        self.save_raw_image_button.setStyleSheet(styleH2)
        self.save_raw_image_button.setStyleSheet(disabled_button)
        self.save_raw_image_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.save_raw_image_button.clicked.connect(self.clicked_action)
        self.save_raw_image_button.setEnabled(False)

        self.save_png_image_button = QPushButton('button_save_png_image_spatial')
        self.save_png_image_button.setStyleSheet(styleH2)
        self.save_png_image_button.setStyleSheet(disabled_button)
        self.save_png_image_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.save_png_image_button.clicked.connect(self.clicked_action)
        self.save_png_image_button.setEnabled(False)

        self.layout.addWidget(self.label_title_spatial_analysis)
        self.layout.addWidget(self.snap_button)
        self.layout.addStretch()
        self.layout.addWidget(self.save_histo_button)
        self.layout.addWidget(self.save_raw_image_button)
        self.layout.addWidget(self.save_png_image_button)

        self.layout.addStretch()
        self.setLayout(self.layout)

    def clicked_action(self):
        sender = self.sender()
        if sender == self.snap_button:
            self.snap_clicked.emit('snap')
            self.save_histo_button.setStyleSheet(unactived_button)
            self.save_histo_button.setEnabled(True)
            self.save_raw_image_button.setStyleSheet(unactived_button)
            self.save_raw_image_button.setEnabled(True)
            self.save_png_image_button.setStyleSheet(unactived_button)
            self.save_png_image_button.setEnabled(True)
        elif sender == self.save_histo_button:
            self.snap_clicked.emit('save_hist')
        elif sender == self.save_raw_image_button:
            self.snap_clicked.emit('save_raw')
        elif sender == self.save_png_image_button:
            self.snap_clicked.emit('save_png')

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

            self.central_widget = HistoAnalysisWidget(self)
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