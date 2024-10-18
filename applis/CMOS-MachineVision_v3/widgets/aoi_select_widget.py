# -*- coding: utf-8 -*-
"""*aoi_select_widget.py* file.

This file contains graphical elements to select an area of interest (AOI)
in the image in a widget.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : oct/2024
"""
from lensepy import translate
from lensepy.css import *
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal

def get_aoi_array(array: np.ndarray, aoi: (int, int, int, int)) -> np.ndarray:
    """Get an AOI from an array.
    :param array: Array to process.
    :param aoi: X,Y position and W,H size of the AOI.
    """
    x, y, w, h = aoi
    return array[y:y + h, x:x + w].copy()

def display_aoi(array: np.ndarray, aoi: (int, int, int, int)) -> np.ndarray:
    """Return an array with the AOI.
    :param array: Array to process.
    :param aoi: X,Y position and W,H size of the AOI.
    """
    x, y, w, h = aoi
    # Choose the color of the rectangle depending on the intensity average.
    mean_image = np.mean(array)
    if mean_image > 128:
        color = 0
    else:
        color = 255
    # Size of the rectangle edge
    min_size = np.min([array.shape[0], array.shape[1]])
    rect_size = int(min_size // 45)
    if rect_size > 20:
        rect_size = 20
    # Add a rectangle - Change Size ??
    image = array.copy()
    for i in range(rect_size):
        # Horizontal edges
        image[y + i, x:x + w] = color
        image[y - i + h - 1, x:x + w] = color
        # Vertical edges
        image[y:y + h, x + i] = color
        image[y:y + h, x - i + w - 1] = color
    return image

class AoiSelectOptionsWidget(QWidget):
    """
    Options widget of the AOI select menu.
    """

    aoi_selected = pyqtSignal(str)

    def __init__(self, parent):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.x_pos = 0
        self.y_pos = 0
        self.width = 0
        self.height = 0

        # Title
        # -----
        self.label_title_aoi_selection = QLabel(translate('title_aoi_selection'))
        self.label_title_aoi_selection.setStyleSheet(styleH1)

        # X position
        self.x_position_widget = QWidget()
        self.x_position_sublayout = QHBoxLayout()
        self.x_position_label = QLabel('X position (pixel) = ')
        self.x_position_label.setStyleSheet(styleH2)
        self.x_position_value = QLineEdit()
        self.x_position_value.setText(str(self.x_pos))
        self.x_position_value.editingFinished.connect(self.xy_position_changing)
        self.x_position_sublayout.addWidget(self.x_position_label)
        self.x_position_sublayout.addWidget(self.x_position_value)
        self.x_position_widget.setLayout(self.x_position_sublayout)

        # Y position
        self.y_position_widget = QWidget()
        self.y_position_sublayout = QHBoxLayout()
        self.y_position_label = QLabel('Y position (pixel) = ')
        self.y_position_label.setStyleSheet(styleH2)
        self.y_position_value = QLineEdit()
        self.y_position_value.setText(str(self.y_pos))
        self.y_position_value.editingFinished.connect(self.xy_position_changing)
        self.y_position_sublayout.addWidget(self.y_position_label)
        self.y_position_sublayout.addWidget(self.y_position_value)
        self.y_position_widget.setLayout(self.y_position_sublayout)

        # Width
        self.width_widget = QWidget()
        self.width_sublayout = QHBoxLayout()
        self.width_label = QLabel('Width (pixel) = ')
        self.width_label.setStyleSheet(styleH2)
        self.width_value = QLineEdit()
        self.width_value.setText(str(self.width))
        self.width_value.editingFinished.connect(self.size_changing)
        self.width_sublayout.addWidget(self.width_label)
        self.width_sublayout.addWidget(self.width_value)
        self.width_widget.setLayout(self.width_sublayout)

        # Height
        self.height_widget = QWidget()
        self.height_sublayout = QHBoxLayout()
        self.height_label = QLabel('Height (pixel) = ')
        self.height_label.setStyleSheet(styleH2)
        self.height_value = QLineEdit()
        self.height_value.setText(str(self.height))
        self.height_value.editingFinished.connect(self.size_changing)
        self.height_sublayout.addWidget(self.height_label)
        self.height_sublayout.addWidget(self.height_value)
        self.height_widget.setLayout(self.height_sublayout)

        # Center button
        self.center_aoi_button = QPushButton(translate('button_center_aoi'))
        self.center_aoi_button.setStyleSheet(styleH2)
        self.center_aoi_button.setStyleSheet(unactived_button)
        self.center_aoi_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.center_aoi_button.clicked.connect(self.centered_action)

        # All image
        self.full_image_button = QPushButton(translate('button_full_image'))
        self.full_image_button.setStyleSheet(styleH2)
        self.full_image_button.setStyleSheet(unactived_button)
        self.full_image_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.full_image_button.clicked.connect(self.full_image_action)

        self.layout.addWidget(self.label_title_aoi_selection)
        self.layout.addWidget(self.x_position_widget)
        self.layout.addWidget(self.y_position_widget)
        self.layout.addWidget(self.width_widget)
        self.layout.addWidget(self.height_widget)
        self.layout.addStretch()
        self.layout.addStretch()
        self.layout.addWidget(self.center_aoi_button)
        self.layout.addStretch()
        self.layout.addWidget(self.full_image_button)
        self.layout.addStretch()
        self.setLayout(self.layout)
        self.full_image_action()

    def centered_action(self):
        if self.parent.parent.raw_image is not None:
            x_max, y_max = self.parent.parent.raw_image.shape[1], self.parent.parent.raw_image.shape[0]
            self.x_pos = x_max // 2 - self.width // 2
            self.y_pos = y_max // 2 - self.height // 2
            self.update_aoi()
            self.aoi_selected.emit('aoi_selected')

    def full_image_action(self):
        if self.parent.parent.raw_image is not None:
            x_max, y_max = self.parent.parent.raw_image.shape[1], self.parent.parent.raw_image.shape[0]
            self.x_pos = 0
            self.y_pos = 0
            self.width = x_max
            self.height = y_max
            self.update_aoi()
            self.aoi_selected.emit('aoi_selected')

    def set_aoi(self, aoi_values: list):
        self.x_pos = int(aoi_values[0])
        self.y_pos = int(aoi_values[1])
        self.width = int(aoi_values[2])
        self.height = int(aoi_values[3])
        self.update_aoi()

    def update_aoi(self):
        self.x_position_value.setText(str(self.x_pos))
        self.y_position_value.setText(str(self.y_pos))
        self.width_value.setText(str(self.width))
        self.height_value.setText(str(self.height))

    def xy_position_changing(self):
        if self.parent.parent.raw_image is not None:
            x_max, y_max = self.parent.parent.raw_image.shape[1], self.parent.parent.raw_image.shape[0]
        elif self.parent.parent.camera is not None:
            x_max, y_max = self.parent.parent.camera.get_sensor_size()
        # Verify if X and Y position are OK ! (good range of the image)
        if 0 <= int(self.x_position_value.text()) < x_max:
            self.x_pos = int(self.x_position_value.text())
            # Test size ! and resize if necessary !!
            if self.x_pos + int(self.width) > x_max:
                self.width = x_max - self.x_pos - 1
                warn = QMessageBox.warning(self, 'Resizing', 'Resizing the AOI')
                self.width_value.setText(str(self.width))
        else:
            self.x_position_value.setText(str(self.x_pos))
            warn = QMessageBox.warning(self, 'Value Error', 'This value is out of range !')
        if 0 <= int(self.y_position_value.text()) < y_max:
            self.y_pos = int(self.y_position_value.text())
            # Test size ! and resize if necessary !!
            if self.y_pos + int(self.height) > y_max:
                self.height = y_max - self.y_pos - 1
                warn = QMessageBox.warning(self, 'Resizing', 'Resizing the AOI')
                self.height_value.setText(str(self.height))
        else:
            self.y_position_value.setText(str(self.y_pos))
            warn = QMessageBox.warning(self, 'Value Error', 'This value is out of range !')
        self.aoi_selected.emit('aoi_selected')

    def size_changing(self):
        if self.parent.parent.raw_image is not None:
            x_max, y_max = self.parent.parent.raw_image.shape[1], self.parent.parent.raw_image.shape[0]
        elif self.parent.parent.camera is not None:
            x_max, y_max = self.parent.parent.camera.get_sensor_size()
        # Verify if X+width and Y+height are OK ! (good range of the image)
        if self.x_pos + int(self.width_value.text()) <= x_max:
            self.width = int(self.width_value.text())
        else:
            self.width_value.setText(str(self.width))
            warn = QMessageBox.warning(self, 'Value Error', 'This value is out of range !')

        if self.y_pos + int(self.height_value.text()) <= y_max:
            self.height = int(self.height_value.text())
        else:
            self.height_value.setText(str(self.height))
            warn = QMessageBox.warning(self, 'Value Error', 'This value is out of range !')
        self.aoi_selected.emit('aoi_selected')

    def get_position(self):
        return self.x_pos, self.y_pos

    def get_size(self):
        return self.width, self.height


class AoiZoomOptionsWidget(QWidget):
    """
    Options widget of the AOI Zoom menu.
    """

    zoom_changed = pyqtSignal(str)

    def __init__(self, parent):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.zoom_max = 4
        self.zoom = 1

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.label_zoom = QLabel('')
        self.label_zoom.setStyleSheet(styleH3)
        self.label_zoom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_zoom.setText(str(self.zoom))
        self.label_zoom.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.zoom_more = QPushButton('Zoom +')
        self.zoom_more.setStyleSheet(styleH3)
        self.zoom_more.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.zoom_more.clicked.connect(self.action_zoom_changing)
        self.zoom_less = QPushButton('Zoom -')
        self.zoom_less.setStyleSheet(styleH3)
        self.zoom_less.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.zoom_less.clicked.connect(self.action_zoom_changing)
        self.button_reset_zoom = QPushButton('Reset')
        self.button_reset_zoom.setStyleSheet(styleH3)
        self.button_reset_zoom.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.button_reset_zoom.clicked.connect(self.action_zoom_changing)
        self.layout.addWidget(self.zoom_less, 0, 0)
        self.layout.addWidget(self.label_zoom, 0, 1)
        self.layout.addWidget(self.button_reset_zoom, 0, 2)
        self.layout.addWidget(self.zoom_more, 0, 3)
        self.layout.setColumnStretch(0, 2)
        self.layout.setColumnStretch(1, 3)
        self.layout.setColumnStretch(2, 2)
        self.layout.setColumnStretch(3, 2)

    def action_zoom_changing(self, event):

        sender = self.sender()
        if sender == self.zoom_more:
            if self.inc_zoom():
                self.zoom_changed.emit('zoom_more')
        elif sender == self.zoom_less:
            if self.dec_zoom():
                self.zoom_changed.emit('zoom_less')
        elif sender == self.button_reset_zoom:
            self.reset_zoom()
            self.zoom_changed.emit('zoom_reset')

    def set_zoom_max(self, value):
        """Set the maximum value for the zoom in the AOI."""
        self.zoom_max = value
        #print(f'ZMax = {self.zoom_max}')

    def get_zoom(self):
        """Return the value of the zoom."""
        #print('GET_ZOOM')
        return self.zoom

    def reset_zoom(self):
        """Reset the zoom value to 1."""
        self.zoom = 1

    def inc_zoom(self):
        """Increase the zoom value of 1."""
        #print(f'INC - ZMax = {self.zoom_max}')
        if self.zoom + 1 <= self.zoom_max:
            self.zoom += 1
            return True
        else:
            return False

    def dec_zoom(self):
        """Decrease the zoom value of 1."""
        if self.zoom - 1 >= 1:
            self.zoom -= 1
            return True
        else:
            return False