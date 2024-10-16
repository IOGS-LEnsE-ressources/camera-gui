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
    QMessageBox, QFileDialog, QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, pyqtSignal
from lensepy import load_dictionary, translate
from lensepy.css import *
from widgets.camera import *


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

        self.button_open_image = QPushButton(translate('button_open_image_from_file'))
        self.button_open_image.setStyleSheet(unactived_button)
        self.button_open_image.setFixedHeight(BUTTON_HEIGHT)
        self.button_open_image.clicked.connect(self.action_open_image)

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

    camera_opened = pyqtSignal(dict)

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent widget of this widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        # GUI Structure
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.button_open_camera = QPushButton(translate('button_open_camera_indus'))
        self.button_open_camera.setStyleSheet(unactived_button)
        self.button_open_camera.setFixedHeight(BUTTON_HEIGHT)
        self.button_open_camera.clicked.connect(self.action_open_camera)

        self.button_open_webcam = QPushButton(translate('button_open_webcam'))
        self.button_open_webcam.setStyleSheet(disabled_button)
        self.button_open_webcam.setFixedHeight(BUTTON_HEIGHT)
        self.button_open_webcam.clicked.connect(self.action_open_webcam)
        self.button_open_webcam.setEnabled(False)

        self.button_open_brand_cam = QLabel('')
        default_brand = 'brandname' in self.parent.default_parameters
        if default_brand:
            self.button_open_brand_cam = QPushButton(translate('button_open_brand_cam'))
            self.button_open_brand_cam.setStyleSheet(unactived_button)
            self.button_open_brand_cam.setFixedHeight(BUTTON_HEIGHT)
            self.button_open_camera.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
            self.button_open_brand_cam.clicked.connect(self.action_open_brand_cam)
            self.layout.addWidget(self.button_open_brand_cam)
            self.layout.addStretch()

        self.layout.addWidget(self.button_open_camera)
        self.layout.addWidget(self.button_open_webcam)
        self.layout.addStretch()

    def action_open_camera(self):
        """
        Open an industrial camera.
        """
        self.button_open_camera.setStyleSheet(actived_button)
        self.repaint()
        self.parent.bot_right_widget = CameraChoice()
        self.parent.bot_right_widget.camera_selected.connect(self.action_camera_selected)
        self.parent.set_bot_right_widget(self.parent.bot_right_widget)

    def action_open_brand_cam(self):
        """
        Open an industrial camera.
        """
        if 'brandname' in self.parent.default_parameters:
            camera = cam_from_brands[self.parent.default_parameters['brandname']]()
            if camera.find_first_camera():
                self.parent.parent.camera = camera
                self.parent.parent.camera.init_camera()
                self.parent.parent.camera_thread.set_camera(self.parent.parent.camera)
                # Init default parameters !
                self.parent.menu_action('images')
                self.parent.init_default_camera_params()
                self.parent.bot_right_widget.update_parameters(auto_min_max=True)

                print(f'Expo = {self.parent.parent.camera.get_exposure()}')
                print(f'FPS  = {self.parent.parent.camera.get_frame_rate()}')
                print(f'Colo = {self.parent.parent.camera.get_color_mode()}')
                print(f'ExpoRange = {self.parent.parent.camera.get_exposure_range()}')

                # Start Thread
                self.parent.parent.image_bits_depth = get_bits_per_pixel(
                    self.parent.parent.camera.get_color_mode())
                self.parent.parent.camera_thread.start()
            else:
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Warning - No Camera")
                dlg.setText("No camera is connected to this computer...")
                dlg.setStandardButtons(
                    QMessageBox.StandardButton.Ok
                )
                dlg.setIcon(QMessageBox.Icon.Warning)
                button = dlg.exec()

    def action_camera_selected(self, event):
        """Action performed when a camera is selected."""
        self.camera_opened.emit(event)

    def action_open_webcam(self, event):
        """
        Open an industrial camera.
        """
        print(event)
        self.camera_opening.emit('webcam_opening')


class ImagesCreateWidget(QWidget):
    """
    Options widget of the image creating menu.
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

    def update_size(self, width, height, aoi: bool = False):
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

    def set_image_from_array(self, pixels: np.ndarray, aoi: bool = False) -> None:
        """
        Display a new image from an array (Numpy)
        :param pixels: Array of pixels to display.
        :param aoi: If True, print 'AOI' on the image.
        """
        self.image = np.array(pixels, dtype='uint8')
        image_to_display = self.image
        if self.image.shape[1] > self.width or self.image.shape[0] > self.height:
            image_to_display = resize_image_ratio(self.image, self.height-50, self.width-50)
        qimage = array_to_qimage(image_to_display)
        if aoi:
            painter = QPainter(qimage)
            painter.setPen(QColor(255, 255, 255))  # Couleur blanche pour le texte
            painter.setFont(QFont("Arial", 15))  # Police et taille
            painter.drawText(20, 20, 'AOI')
            painter.end()
        pmap = QPixmap.fromImage(qimage)
        self.image_display.setPixmap(pmap)

