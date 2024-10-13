# -*- coding: utf-8 -*-
"""*pre_processing_widget.py* file.

This file contains graphical elements to apply pre processing on images.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : oct/2024
"""
from lensepy import translate
from lensepy.css import *
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox,
    QMessageBox,
)
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect
from lensepy.pyqt6.widget_combobox import ComboBoxBloc


class ErosionDilationOptionsWidget(QWidget):
    """
    Options widget of the AOI select menu.
    """

    ero_dil_changed = pyqtSignal(str)

    def __init__(self, parent):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.select_erosion = QPushButton(translate('button_select_erosion'))
        self.select_erosion.setStyleSheet(styleH2)
        self.select_erosion.setStyleSheet(unactived_button)
        self.select_erosion.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.select_erosion.clicked.connect(self.action_button_clicked)
        self.select_dilation = QPushButton(translate('button_select_dilation'))
        self.select_dilation.setStyleSheet(styleH2)
        self.select_dilation.setStyleSheet(unactived_button)
        self.select_dilation.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.select_dilation.clicked.connect(self.action_button_clicked)

        self.kernel_size = ComboBoxBloc(translate('combo_kernel_size'), list_options=['7', '5', '3'],
                                        default=False)
        self.kernel_size.selection_changed.connect(self.action_button_clicked)

        self.kernel_preselect = QWidget()
        self.kernel_preselect_layout = QHBoxLayout()
        self.kernel_preselect.setLayout(self.kernel_preselect_layout)
        self.kernel_cross = QPushButton(translate('kernel_preselect_cross'))
        self.kernel_cross.setStyleSheet(styleH2)
        self.kernel_cross.setStyleSheet(unactived_button)
        self.kernel_cross.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.kernel_cross.clicked.connect(self.action_button_clicked)
        self.kernel_rect = QPushButton(translate('kernel_preselect_rect'))
        self.kernel_rect.setStyleSheet(styleH2)
        self.kernel_rect.setStyleSheet(unactived_button)
        self.kernel_rect.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.kernel_rect.clicked.connect(self.action_button_clicked)
        self.kernel_preselect_layout.addWidget(self.kernel_cross)
        self.kernel_preselect_layout.addWidget(self.kernel_rect)


        self.kernel_choice = ImagePixelsWidget(self)
        self.kernel_choice.set_size(7,7)
        self.kernel_choice.pixel_changed.connect(self.action_button_clicked)

        self.layout.addWidget(self.select_erosion)
        self.layout.addWidget(self.select_dilation)
        self.layout.addWidget(self.kernel_size)
        self.layout.addWidget(self.kernel_preselect)
        self.layout.addWidget(self.kernel_choice)

    def action_button_clicked(self, event):
        """Action performed when a button is clicked."""
        sender = self.sender()
        if sender == self.select_erosion:
            self.ero_dil_changed.emit('erosion')
            self.select_erosion.setStyleSheet(actived_button)
            self.select_dilation.setStyleSheet(unactived_button)
        elif sender == self.select_dilation:
            self.ero_dil_changed.emit('dilation')
            self.select_erosion.setStyleSheet(unactived_button)
            self.select_dilation.setStyleSheet(actived_button)
        elif sender == self.kernel_choice:
            self.ero_dil_changed.emit('pixel')
        elif sender == self.kernel_size:
            k_size = int(self.kernel_size.get_text())
            self.kernel_choice.set_size(k_size, k_size)
            self.kernel_choice.repaint()
            self.ero_dil_changed.emit('kernel')
        elif sender == self.kernel_cross:
            self.ero_dil_changed.emit('cross')
        elif sender == self.kernel_rect:
            self.ero_dil_changed.emit('rect')

    def get_kernel(self) -> np.ndarray:
        """Return an array containing the kernel."""
        return self.kernel_choice.get_image()



# MOVING TO LENSEPY
class ImagePixelsWidget(QWidget):
    """
    Class to display and create an image (array) in a widget.
    """

    pixel_changed = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        :param parent: Parent widget or window of this widget.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.img_width = 20
        self.img_height = 20
        self.pixel_per_pixel = 20
        self.image = np.zeros((self.img_width, self.img_height))


    def paintEvent(self, event):
        """PaintEvent method."""
        painter = QPainter(self)
        pen = QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        pos_x0 = (self.width() - self.pixel_per_pixel * self.img_width)//2
        pos_y0 = (self.height() - self.pixel_per_pixel * self.img_height)//2
        for i in range(self.img_width):
            for j in range(self.img_height):
                pos_x = pos_x0 + i * self.pixel_per_pixel
                pos_y = pos_y0 + j * self.pixel_per_pixel

                if self.image[i, j] == 0:
                    painter.setBrush(QColor(200, 200, 200))
                    painter.drawRect(QRect(pos_x, pos_y, self.pixel_per_pixel, self.pixel_per_pixel))
                else:
                    painter.setBrush(QColor(0, 0, 0))
                    painter.drawRect(QRect(pos_x, pos_y, self.pixel_per_pixel, self.pixel_per_pixel))

    def mousePressEvent(self, event):
        """Action when a mouse button is pressed."""
        pos_x0 = (self.width() - self.pixel_per_pixel * self.img_width) // 2
        pos_y0 = (self.height() - self.pixel_per_pixel * self.img_height) // 2
        if event.button() == Qt.MouseButton.LeftButton:
            last_point = event.position().toPoint()
            pos_x = (last_point.x()-pos_x0) // self.pixel_per_pixel
            pos_y = (last_point.y()-pos_y0) // self.pixel_per_pixel
            if 0 <= pos_x < self.img_width and 0 <= pos_y < self.img_height:
                self.image[pos_x, pos_y] = 1-self.image[pos_x, pos_y]
                self.repaint()
                self.pixel_changed.emit('pixel_changed')

    def set_size(self, width: int, height: int):
        """
        Set the size of the image.
        :param width: Width of the image.
        :param height: Height of the image.
        """
        self.img_width = width
        self.img_height = height
        self.image = np.zeros((self.img_width, self.img_height))

    def get_image(self) -> np.ndarray:
        """
        Return the image.
        :return: Array containing the image.
        """
        return self.image.astype(np.uint8)