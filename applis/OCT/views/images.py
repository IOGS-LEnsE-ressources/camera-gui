# -*- coding: utf-8 -*-
"""*images_widget.py* file.

This file contains graphical elements to display images in a widget.
Image is coming from a file (JPG, PNG...) or an industrial camera (IDS, Basler...).

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : oct/2024
"""

import sys
import time
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsView,
                             QGraphicsScene, QGraphicsPixmapItem,
                             QVBoxLayout, QWidget)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor, QWheelEvent
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject


class ImageDisplayGraph(QWidget):
    def __init__(self, parent=None, bg_color='white', zoom: bool = True):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.scene = QGraphicsScene(self)
        self.graphics_view = QGraphicsView(self.scene)
        self.layout.addWidget(self.graphics_view)

        self.scene.setBackgroundBrush(QColor(bg_color))
        self.zoom = zoom
        self.zoom_factor = 1.1

    def set_image_from_array(self, pixels: np.ndarray, text: str = ''):
        self.scene.clear()
        if pixels is None:
            return
        image = pixels.astype(np.uint8)  # assumes 8-bit depth
        h, w = image.shape
        qimage = QImage(image.data, w, h, QImage.Format.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)
        self.graphics_view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event: QWheelEvent):
        """
        Handle mouse wheel event for zooming.
        """
        if self.zoom:
            if event.angleDelta().y() > 0:
                self.graphics_view.scale(self.zoom_factor, self.zoom_factor)
            else:
                self.graphics_view.scale(1 / self.zoom_factor, 1 / self.zoom_factor)

