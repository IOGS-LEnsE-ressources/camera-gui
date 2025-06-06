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
import cv2
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from lensepy import load_dictionary, translate
from lensepy.css import *
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets

import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow,
                             QGraphicsView, QGraphicsScene,
                             QGraphicsPixmapItem, QGraphicsTextItem,
                             QVBoxLayout, QWidget)
from PyQt6.QtGui import QPixmap, QColor, QImage, QWheelEvent
from PyQt6.QtCore import Qt


class ImageDisplayGraph(QWidget):
    """
    Widget to display an image in a pyqtgraph widget.
    """

    def __init__(self, parent=None, bg_color='white', zoom:bool = True):
        """
        Default Constructor.
        :param parent: Parent widget of this widget.
        :param bg_color: Background color.
        """
        super().__init__(parent)
        self.parent = parent
        self.bg_color = bg_color
        self.text = ''
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.bits_depth = 8

        # Create a QGraphicsView and Scene
        self.scene = QGraphicsScene(self)
        self.graphics_view = QGraphicsView(self.scene)
        self.layout.addWidget(self.graphics_view)

        self.graphics_view.setStyleSheet("border: none;")  # Remove border from the QGraphicsView
        self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)


        # Background color of the scene
        self.scene.setBackgroundBrush(QColor(self.bg_color))
        self.zoom = zoom
        self.zoom_factor = 1.1


    def set_bits_depth(self, depth_value: int = 8):
        """
        Set the bits depth for pixel.
        :param depth_value: Bits depth of each pixel.
        """
        self.bits_depth = depth_value

    def set_image_from_array(self, pixels: np.ndarray, text: str = ''):
        """
        Display a new image from a numpy array.
        :param pixels: Array of pixels to display.
        :param text: Text to display in the bottom left corner of the widget.
        """
        self.scene.clear()
        if pixels is None:
            return  # Ne rien faire si aucun tableau fourni

        if text:
            self.text = text
        # Convert pixels
        if self.bits_depth > 8:
            raw_image = pixels.view(np.uint16)
            image = (raw_image >> (self.bits_depth - 8)).astype(np.uint8)
        else:
            image = pixels.view(np.uint8)

        # Copy of the image
        image_copy = image.copy()
        # QtImage creation
        height, width = image_copy.shape
        qimage = QImage(image_copy.data, width, height, QImage.Format.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)

        # Adjust size view
        self.graphics_view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

        # Add text in the bottom left corner
        '''
        if self.text:
            font = QFont('Arial', 3)
            text_item = QGraphicsTextItem(self.text)
            text_item.setFont(font)
            text_item.setDefaultTextColor(QColor(0, 0, 0))
            text_item.setPos(0, pixmap.height() - 10)  # Décaler un peu plus pour éviter d'être coupé
            self.scene.addItem(text_item)
        '''

    def wheelEvent(self, event: QWheelEvent):
        """
        Handle mouse wheel event for zooming.
        """
        if self.zoom:
            if event.angleDelta().y() > 0:
                self.graphics_view.scale(self.zoom_factor, self.zoom_factor)
            else:
                self.graphics_view.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
"""
    def set_image_from_uint8(self, image : bytes, text: str = ''):
        '''Permet d'effectuer le même fonction que set_image_from_array, mais avec une image uint8, ce qui
        est le format des images de la caméra après conversion'''

        if image.ndim != 2 or image.dtype != np.uint8:
            raise ValueError("L'image doit être un tableau 2D en uint8 (grayscale).")

        h, w = image.shape
        qimage = QImage(image.data, w, h, w, QImage.Format.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)

        self.image_label.setPixmap(pixmap)
        self.graphics_view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setScaledContents(True)"""


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = ImageDisplayGraph(self, bg_color='white')
        self.setCentralWidget(self.central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    image = np.random.normal(size=(100, 100))
    window.central_widget.set_image_from_array(image, "Test")
    window.show()
    sys.exit(app.exec())

'''
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

        # Create a GraphicsLayoutWidget containing a ViewBox
        self.graphics_widget = pg.GraphicsLayoutWidget()
        self.graphics_widget.setFrameShape(QFrame.Shape.NoFrame)
        self.graphics_widget.setFrameShadow(QFrame.Shadow.Plain)
        self.layout.addWidget(self.graphics_widget)
        # Create a ViewBox for zoom
        self.view_box = self.graphics_widget.addViewBox()
        self.view_box.setAspectLocked(True)  # Keep image ratio
        self.view_box.setBackgroundColor(pg.mkColor(self.bg_color))
        if zoom is False:
            self.view_box.setMouseEnabled(x=False, y=False)

        # Create image item to display an image
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
        self.view_box.autoRange()
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
'''