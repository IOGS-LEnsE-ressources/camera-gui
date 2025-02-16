# -*- coding: utf-8 -*-
"""*images_widget.py* file.

This file contains graphical elements to display images in a widget.
Image is coming from a file (JPG, PNG...) or an industrial camera (IDS, Basler...).

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : oct/2024
"""
import sys, os
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout,
    QLabel, QComboBox, QPushButton, QFrame,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from lensepy import load_dictionary, translate
from lensepy.css import *
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets


class ImageDisplayGraph(QWidget):
    """
    Widget to display an image in a pyqtgraph widget.
    """

    def __init__(self, parent=None, bg_color:str='white', zoom:bool = True):
        """
        Default Constructor.
        :param parent: Parent widget of this widget.
        :param bg_color: Background color.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.bg_color = bg_color
        self.text = ''
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setStyleSheet("border: none;")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Création d'un GraphicsLayoutWidget contenant un ViewBox
        self.graphics_widget = pg.GraphicsLayoutWidget()
        self.layout.addWidget(self.graphics_widget)

        # Création d'une vue (ViewBox) qui permet le zoom et le déplacement
        self.view_box = self.graphics_widget.addViewBox()
        self.view_box.setAspectLocked(True)  # Garde le ratio de l'image
        self.view_box.setBackgroundColor(self.bg_color)
        if zoom is False:
            self.view_box.setMouseEnabled(x=False, y=False)

        # Création de l'élément ImageItem pour afficher l'image
        self.image_item = pg.ImageItem()
        self.view_box.addItem(self.image_item)

        self.image = None

    def set_image_from_array(self, pixels: np.ndarray, text:str = '') -> None:
        """
        Display a new image from an array (Numpy)
        :param pixels: Array of pixels to display.
        """
        self.image = np.array(pixels, dtype='uint8')
        self.image_item.setImage(self.image)
        self.text = text
        if self.text != '':
            # Ajout du texte avec TextItem
            text_item = pg.TextItem(self.text, color='black', anchor=(0, 0))
            self.view_box.addItem(text_item)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = ImageDisplayGraph(self)
            self.setCentralWidget(self.central_widget)

    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())