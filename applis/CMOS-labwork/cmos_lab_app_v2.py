# -*- coding: utf-8 -*-
"""*cmos_lab_app.py* file.

*cmos_lab_app* file that contains :class::CmosLabApp

This file is attached to a 2nd year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-Detection.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/contents/appli_CMOS_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>

"""

from lensepy import load_dictionary, translate
from lensepy.css import *
import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget
from gui.camera_choice_widget import CameraChoice

# -------------------------------

class MainWindow(QMainWindow):
    """
    Our main window.

    Args:
        QMainWindow (class): QMainWindow can contain several widgets.
    """

    def __init__(self):
        """
        Initialisation of the main Window.
        """
        super().__init__()

        # Define Window title
        self.setWindowTitle("LEnsE - CMOS Sensor Labwork")
        # Main Widget
        self.main_widget = QWidget()

        # Main Layout
        self.main_layout = QGridLayout()
        self.title_widget = QWidget()
        self.main_menu_widget = QWidget()
        self.camera_widget = CameraChoice()
        self.params_widget = QWidget()
        self.time_graph = QWidget()
        self.histo_graph = QWidget()

        self.main_layout.addWidget(self.title_widget, 0, 1, 1, 3)
        self.main_layout.addWidget(self.main_menu_widget, 1, 1, 2, 1)
        self.main_layout.addWidget(self.camera_widget, 1, 1)
        self.main_layout.addWidget(self.histo_graph, 1, 2)
        self.main_layout.addWidget(self.params_widget, 2, 1)
        self.main_layout.addWidget(self.time_graph, 2, 2)

        self.main_layout.setColumnStretch(0,1)
        self.main_layout.setColumnStretch(1,3)
        self.main_layout.setColumnStretch(2,3)
        self.main_layout.setRowStretch(0,1)
        self.main_layout.setRowStretch(1,3)
        self.main_layout.setRowStretch(2,2)

        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

# -------------------------------
# Launching as main for tests
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())
