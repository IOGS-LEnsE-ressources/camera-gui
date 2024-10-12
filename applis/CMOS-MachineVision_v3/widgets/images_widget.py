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
import cv2
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox, QFileDialog, QSizePolicy
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from lensepy import load_dictionary, translate
from lensepy.css import *
from lensepy.images.conversion import *


class ImagesFileOpeningWidget(QWidget):
    """
    Options widget of the image opening menu.
    """

    image_opened = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent widget of this widget.
        """
        super().__init__(parent=parent)
        # GUI Structure
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label_title_images_options = QLabel(translate('title_images_opening'))
        self.label_title_images_options.setStyleSheet(styleH1)
        self.label_title_images_options.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.button_open_image = QPushButton(translate('button_open_image_from_file'))
        self.button_open_image.setStyleSheet(unactived_button)
        self.button_open_image.setFixedHeight(BUTTON_HEIGHT)
        self.button_open_image.clicked.connect(self.action_open_image)

        self.layout.addWidget(self.label_title_images_options)
        self.layout.addWidget(self.button_open_image)
        self.layout.addStretch()

    def action_open_image(self, event, gray: bool=True):
        """
        Open an image from a file.
        """
        self.button_open_image.setStyleSheet(actived_button)
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, translate('dialog_open_image'),
                                                   "", "Images (*.png *.jpg *.jpeg)")
        if file_path != '':
            if gray:
                image_array = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            else:
                image_array = cv2.imread(file_path)
            self.image_opened.emit(image_array)
        else:
            self.button_open_image.setStyleSheet(unactived_button)
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No File Loaded")
            dlg.setText("No Image File was loaded...")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()

class ImagesCameraOpeningWidget(QWidget):
    """
    Options widget of the image opening menu.
    """

    camera_opening = pyqtSignal(str)
    camera_opened = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent widget of this widget.
        """
        super().__init__(parent=parent)
        # GUI Structure
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label_title_camera_options = QLabel(translate('title_camera_opening'))
        self.label_title_camera_options.setStyleSheet(styleH1)
        self.label_title_camera_options.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.button_open_camera = QPushButton(translate('button_open_camera'))
        self.button_open_camera.setStyleSheet(unactived_button)
        self.button_open_camera.setFixedHeight(BUTTON_HEIGHT)
        self.button_open_camera.clicked.connect(self.action_open_camera)

        self.button_open_webcam = QPushButton(translate('button_open_webcam'))
        self.button_open_webcam.setStyleSheet(disabled_button)
        self.button_open_webcam.setFixedHeight(BUTTON_HEIGHT)
        self.button_open_webcam.clicked.connect(self.action_open_webcam)
        self.button_open_webcam.setEnabled(False)

        self.layout.addWidget(self.label_title_camera_options)
        self.layout.addWidget(self.button_open_camera)
        self.layout.addWidget(self.button_open_webcam)
        self.layout.addStretch()

    def action_open_camera(self):
        """
        Open an industrial camera.
        """
        self.camera_opening.emit('camera_opening')
        self.button_open_camera.setStyleSheet(actived_button)

    def action_open_webcam(self):
        """
        Open an industrial camera.
        """
        self.camera_opening.emit('webcam_opening')

class ImagesDisplayWidget(QWidget):
    """
    Widget to display an image.
    """

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent widget of this widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.width = 0
        self.height = 0
        # GUI Structure
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        # Objects
        self.image = None
        # GUI Elements
        self.image_display = QLabel('Image to display')
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display.setScaledContents(False)
        self.layout.addWidget(self.image_display)

    def update_size(self, width, height):
        """
        Update the size of this widget.
        """
        self.width = width
        self.height = height
        if self.image is not None:
            image_to_display = self.image
            if self.image.shape[1] > self.width or self.image.shape[0] > self.height:
                image_to_display = resize_image_ratio(self.image, self.height-30, self.width-20)
            qimage = array_to_qimage(image_to_display)
            pmap = QPixmap.fromImage(qimage)
            self.image_display.setPixmap(pmap)

    def set_image_from_array(self, pixels: np.ndarray) -> None:
        """
        Display a new image from an array (Numpy)
        :param pixels: Array of pixels to display.
        """
        self.image = np.array(pixels, dtype='uint8')
        image_to_display = self.image
        if self.image.shape[1] > self.width or self.image.shape[0] > self.height:
            image_to_display = resize_image_ratio(self.image, self.height-30, self.width-20)
        qimage = array_to_qimage(image_to_display)
        pmap = QPixmap.fromImage(qimage)
        self.image_display.setPixmap(pmap)
