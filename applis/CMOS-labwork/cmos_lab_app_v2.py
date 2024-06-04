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
from PyQt6.QtWidgets import (QApplication, QMainWindow,
                             QGridLayout, QWidget,
                             QMessageBox)
from gui.camera_choice_widget import CameraChoice
from gui.main_menu_widget import MainMenuWidget
from gui.title_widget import TitleWidget

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
        self.camera = None

        # Define Window title
        self.setWindowTitle("LEnsE - CMOS Sensor Labwork")
        # Main Widget
        self.main_widget = QWidget()

        # Main Layout
        self.main_layout = QGridLayout()
        self.title_widget = TitleWidget()
        self.main_menu_widget = MainMenuWidget()
        self.camera_widget = QWidget()
        self.camera_widget.setStyleSheet("background-color: lightblue;")
        self.params_widget = QWidget()
        self.time_graph = QWidget()
        self.time_graph.setStyleSheet("background-color: lightblue;")
        self.histo_graph = QWidget()

        self.main_layout.addWidget(self.title_widget, 0, 0, 1, 3)
        self.main_layout.addWidget(self.main_menu_widget, 1, 0, 2, 1)
        self.main_layout.addWidget(self.camera_widget, 1, 1)
        self.main_layout.addWidget(self.histo_graph, 1, 2)
        self.main_layout.addWidget(self.params_widget, 2, 1)
        self.main_layout.addWidget(self.time_graph, 2, 2)

        self.main_layout.setColumnStretch(0,1)
        self.main_layout.setColumnStretch(1,3)
        self.main_layout.setColumnStretch(2,3)
        self.main_layout.setRowStretch(0,1)
        self.main_layout.setRowStretch(1,5)
        self.main_layout.setRowStretch(2,4)

        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Events
        self.main_menu_widget.camera_settings_clicked.connect(self.camera_settings_action)

    def camera_settings_action(self, event) -> None:
        if self.camera is None:
            print('No Camera')
        print(f'Camera Settings {event}')
        self.params_widget = CameraChoice()
        self.main_layout.addWidget(self.params_widget, 2, 1)

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

# -------------------------------
# Launching as main for tests
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())
