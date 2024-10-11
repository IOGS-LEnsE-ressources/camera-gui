# -*- coding: utf-8 -*-
"""*cmos_lab_app.py* file.

*cmos_lab_app* file that contains :class::CmosLabApp

This file is attached to engineer training labworks in photonics.
- 1st year subject :
- 2nd year subject : http://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-Detection.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/contents/appli_CMOS_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>

Creation : sept/2023
Modification : oct/2024
"""
# -*- coding: utf-8 -*-
"""*base_gui_main.py* file.

*base_gui_main* file that contains :class::BaseGUI, an example of a
complete 5 areas GUI: 1 main menu on the left and 4 equivalent area on the right.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>

Creation : oct/2024
"""
from lensepy import load_dictionary, translate, dictionary
import sys
import numpy as np
from lensepy.css import *
from PyQt6.QtWidgets import (
    QWidget, QPushButton,
    QMainWindow, QApplication, QMessageBox)
from widgets.main_widget import *


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
        self.setWindowTitle("LEnsE - CMOS Sensor / Machine Vision / Labwork")
        # GUI structure
        self.central_widget = MainWidget(self)
        self.setCentralWidget(self.central_widget)
        load_menu('./config/menu.txt', self.central_widget.main_menu)
        self.central_widget.main_signal.connect(self.main_action)
        # Objects
        self.camera = None
        self.image = None

    def main_action(self, event):
        """
        Action performed by an event in the main widget.
        :param event: Event that triggered the action.
        """
        print(f'Main {event}')
        if event == 'open_image':
            self.central_widget.options_widget.image_opened.connect(self.action_image_from_file)

    def action_image_from_file(self, event: np.ndarray):
        """
        Action performed when an image file is opened.
        :param event: Event that triggered the action - np.ndarray.
        """
        self.image = event.copy()
        self.central_widget.top_left_widget.set_image_from_array(self.image)
        self.central_widget.options_widget.button_open_image.setStyleSheet(unactived_button)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())