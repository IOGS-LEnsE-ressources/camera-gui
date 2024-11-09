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


class ImagesChoice(QWidget):
    """Images Choice."""

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.layout = QVBoxLayout()

        self.label_images_choice_title = QLabel(translate("label_images_choice_title"))
        self.label_images_choice_title.setStyleSheet(styleH1)
        self.label_images_choice_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_status_images = QLabel(translate("label_status_images"))
        self.label_status_images.setStyleSheet(styleH2)
        self.label_status_images.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_status_masks = QLabel(translate("label_status_masks"))
        self.label_status_masks.setStyleSheet(styleH2)
        self.label_status_masks.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.label_images_choice_title)
        self.layout.addWidget(self.label_status_images)
        self.layout.addWidget(self.label_status_masks)

        self.setLayout(self.layout)

    def set_images_status(self, value: bool):
        """Update images status."""
        if value:
            self.label_status_images.setText('Images OK')
        else:
            self.label_status_images.setText('No Images')

    def set_masks_status(self, value: bool, number: int=0):
        """Update images status."""
        if value:
            self.label_status_masks.setText(f'Masks OK {number}')
        else:
            self.label_status_masks.setText('No Masks')

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