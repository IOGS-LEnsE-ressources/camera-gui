# -*- coding: utf-8 -*-
"""*acquisition.py* file.

This file contains graphical elements to manage acquisition of images.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : oct/2024
"""
import sys, os
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout,
    QLabel, QComboBox, QPushButton,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from lensepy import load_dictionary, translate
from lensepy.css import *
from lensepy.pyqt6.widget_slider import *
from lensepy.images.conversion import *


class AcquisitionOptionsWidget(QWidget):
    """Acquisition Options."""

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.label_acquisition_title = QLabel(translate("label_acquisition_title"))
        self.label_acquisition_title.setStyleSheet(styleH1)
        self.label_acquisition_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add graphical elements to the layout
        self.layout.addWidget(self.label_acquisition_title, 0, 0)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = AcquisitionOptionsWidget(self)
            self.setCentralWidget(self.central_widget)

    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())