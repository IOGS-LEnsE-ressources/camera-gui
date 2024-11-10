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
import scipy
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout,
    QLabel, QComboBox, QPushButton,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from lensepy import load_dictionary, translate
from lensepy.css import *
from lensepy.images.conversion import *


def read_mat_file(file_path: str) -> dict:
    """
    Load data and masks from a .mat file.
    The file must contain a set of 5 images (Hariharan algorithm) in a dictionary key called "Images".
    Additional masks can be included in a dictionary key called "Masks".

    :param file_path: Path and name of the file to load.
    :return: Dictionary containing at least np.ndarray including in the "Images"-key object.
    """
    data = scipy.io.loadmat(file_path)
    return data

def write_mat_file(file_path, images: np.ndarray, masks: np.ndarray = None):
    """
    Load data and masks from a .mat file.
    The file must contain a set of 5 images (Hariharan algorithm) in a dictionary key called "Images".
    Additional masks can be included in a dictionary key called "Masks".

    :param file_path: Path and name of the file to write.
    :param images: Set of images to save.
    :param masks: Set of masks to save. Default None.
    """
    data = {
        'Images': images
    }
    if masks is not None:
        data['Masks'] = masks
    scipy.io.savemat(file_path, data)


def split_3d_array(array_3d):
    # Ensure the array has the expected shape
    if array_3d.shape[2] != 5:
        raise ValueError("The loaded array does not have the expected third dimension size of 5.")

    # Extract the 2D arrays
    arrays = [array_3d[:, :, i].astype(np.float32) for i in range(5)]
    return arrays


def generate_images_grid(images: list[np.ndarray]):
    """Generate a grid with 5 images.
    :param images: List of 5 images.
    """
    img_height, img_width = images[0].shape
    separator_size = 5
    # Global size
    total_height = 2 * img_height + separator_size  # 2 rows of images
    total_width = 3 * img_width + 2 * separator_size  # 3 columns of images
    # Empty image
    result = np.ones((total_height, total_width), dtype=np.uint8) * 255
    # Add each images
    result[0:img_height, 0:img_width] = images[0]
    result[0:img_height, img_width + separator_size:2 * img_width + separator_size] = images[1]
    result[0:img_height, 2 * img_width + 2 * separator_size:] = images[2]
    result[img_height + separator_size:, 0:img_width] = images[3]
    result[img_height + separator_size:, img_width + separator_size:2 * img_width + separator_size] = images[4]
    return result

class ImagesChoice(QWidget):
    """Images Choice."""

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label_images_choice_title = QLabel(translate("label_images_choice_title"))
        self.label_images_choice_title.setStyleSheet(styleH1)
        self.label_images_choice_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_set_of_images = QLabel()
        self.label_set_of_images.setStyleSheet(styleH2)
        self.label_set_of_images.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_status_images = QLabel(translate("label_status_images"))
        self.label_status_images.setStyleSheet(styleH2)
        self.label_status_images.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_status_masks = QLabel(translate("label_status_masks"))
        self.label_status_masks.setStyleSheet(styleH2)
        self.label_status_masks.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Widget set of images
        self.sets_of_images_number = 0
        self.sets_of_images_widget = QWidget()
        self.layout_set = QHBoxLayout()
        self.sets_of_images_widget.setLayout(self.layout_set)
        self.sets_button_list = []

        # Widget images selection
        self.images_select_widget = QWidget()
        self.layout_images = QHBoxLayout()
        self.images_select_widget.setLayout(self.layout_images)
        self.images_button_select = []
        for i in range(5):
            button = QPushButton(str(i+1))
            button.setFixedWidth(40)
            button.setStyleSheet(unactived_button)
            button.clicked.connect(self.display_image)
            self.images_button_select.append(button)
        button = QPushButton('ALL')
        button.setFixedWidth(40)
        button.clicked.connect(self.display_image)
        button.setStyleSheet(unactived_button)
        self.images_button_select.append(button)
        # Widget masks selection
        self.masks_number = 0
        self.masks_select_widget = QWidget()
        self.layout_masks = QHBoxLayout()
        self.masks_select_widget.setLayout(self.layout_masks)
        self.masks_button_select = []

        # Add graphical elements in the layout
        self.layout.addWidget(self.label_images_choice_title)
        self.layout.addWidget(self.label_set_of_images)
        self.layout.addWidget(self.images_select_widget)
        self.layout.addWidget(self.label_status_images)
        self.layout.addWidget(self.images_select_widget)
        self.layout.addWidget(self.label_status_masks)
        self.layout.addWidget(self.masks_select_widget)


    def set_images_status(self, value: bool, index: int = 0):
        """Update images status.
        :param value: True if images are opened.
        :param index: Index of the image selected for display.
        """
        if value:
            self.sets_of_images_number = len(self.parent.parent.images)%5
            if self.sets_of_images_number > 1:
                self.label_set_of_images.setText(f'{self.sets_of_images_number} set(s) of images')
                for i in range(self.sets_of_images_number):
                    button = QPushButton(f'S{i + 1}')
                    button.setFixedWidth(40)
                    if i == 0:
                        button.setStyleSheet(actived_button)
                    else:
                        button.setStyleSheet(unactived_button)
                    button.clicked.connect(self.display_mask)
                    self.sets_button_list.append(button)
                    self.layout_set.addWidget(self.sets_button_list[i])
            self.label_status_images.setText('Display image ?')
            for i in range(6):
                self.layout_images.addWidget(self.images_button_select[i])
            self.images_button_select[index-1].setStyleSheet(actived_button)
        else:
            self.label_status_images.setText('No Image')

    def set_masks_status(self, value: bool, number: int=0):
        """Update images status."""
        if value:
            self.label_status_masks.setText(f'{number} Mask(s) / Display ?')
            self.masks_number = number
            for i in range(number):
                button = QPushButton(str(i + 1))
                button.setFixedWidth(40)
                button.setStyleSheet(unactived_button)
                button.clicked.connect(self.display_mask)
                self.masks_button_select.append(button)
                self.layout_masks.addWidget(self.masks_button_select[i])
        else:
            self.label_status_masks.setText('No Mask')
            self.masks_number = 0

    def unactivate_buttons(self):
        """Set unactivated all the buttons."""
        for i in range(6):
            self.images_button_select[i].setStyleSheet(unactived_button)
        for i in range(self.masks_number):
            self.masks_button_select[i].setStyleSheet(unactived_button)

    def display_image(self, event):
        """Action performed when an image is selected to be displayed."""
        self.unactivate_buttons()
        sender = self.sender()
        sender.setStyleSheet(actived_button)
        for i in range(6):
            if sender == self.images_button_select[i]:
                if i != 5:
                    self.parent.top_left_widget.set_image_from_array(self.parent.parent.images[i])
                else:
                    image = generate_images_grid(self.parent.parent.images)
                    self.parent.top_left_widget.set_image_from_array(image)

    def display_mask(self, event):
        """Action performed when an image is selected to be displayed."""
        self.unactivate_buttons()
        sender = self.sender()
        sender.setStyleSheet(actived_button)
        for i in range(self.masks_number):
            if sender == self.masks_button_select[i]:
                image = self.parent.parent.images[0]
                if self.masks_number == 1:
                    self.parent.top_left_widget.set_image_from_array(self.parent.parent.masks*image)
                else:
                    self.parent.top_left_widget.set_image_from_array(self.parent.parent.masks[i]*image)


    def clear_layout(self, row: int, column: int) -> None:
        """Remove widgets from a specific position in the layout.

        :param row: Row index of the layout.
        :type row: int
        :param column: Column index of the layout.
        :type column: int

        """
        item = self.layout.itemAtPosition(row, column)
        if item is not None:
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.layout.removeItem(item)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = ImagesChoice(self)
            self.setCentralWidget(self.central_widget)

    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())