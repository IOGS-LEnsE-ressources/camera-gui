# -*- coding: utf-8 -*-
"""*cmos_lab_app.py* file.

*cmos_lab_app* file that contains :class::CmosLabApp

This file is attached to a 2nd year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-Detection.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/contents/appli_CMOS_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>

*****************
*  CameraChoice
*****************
* Mode
* FPS
* Exposure
*****************
* AOI   - DRAW
*  x0   w
*  y0   h
*       Params
*****************
* Hist AOI
* X Zoom    Start
*****************
* Hist Pixel(s)
* Params    Start
* X Hist    X Time
*****************

"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap

from supoptools.pyqt6 import *

from basler.camera_list import *

class CmosLabApp(QWidget):
    """Main interface of the CMOS sensor study labwork."""

    def __init__(self):
        """Default constructor of the class.
        """
        super().__init__(parent=None)

        self.basler_button = QPushButton('Basler')


class CameraChoice(QWidget):
    """Camera Choice."""

    def __init__(self):
        """Default constructor of the class.
        """
        super().__init__(parent=None)


        self.basler_button = QPushButton('Basler')


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("Widget Slider test")
            self.setGeometry(300, 300, 400, 600)

            self.central_widget = CmosLabApp()
            self.setCentralWidget(self.central_widget)


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())