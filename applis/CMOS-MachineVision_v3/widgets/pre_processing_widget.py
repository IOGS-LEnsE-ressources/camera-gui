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
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox,
    QMessageBox,
)
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect
from lensepy.pyqt6.widget_combobox import ComboBoxBloc

# TO LENSEPY
class ButtonSelectionWidget(QWidget):

    clicked = pyqtSignal(str)

    def __init__(self, parent=None, name: str = 'select_button'):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.select_layout = QGridLayout()
        self.setLayout(self.select_layout)
        self.label_select = QLabel(translate(name))
        self.list_options = []
        self.list_buttons = []
        self.selected = -1

    def display_selection(self):
        """Create the widget by inserting graphical elements."""
        self.select_layout.addWidget(self.label_select)
        for i, element in enumerate(self.list_options):
            button = QPushButton(element)
            button.setStyleSheet(styleH2)
            button.setStyleSheet(unactived_button)
            button.clicked.connect(self.action_clicked)
            self.list_buttons.append(button)
            self.select_layout.addWidget(button, 0, i+1)

    def set_list_options(self, list):
        """Update the list of the options to select."""
        self.list_options = list
        nb = len(self.list_options)
        self.select_layout.setColumnStretch(0, 40)
        for i in range(1, nb+1):
            self.select_layout.setColumnStretch(i, 50//nb)
        self.display_selection()

    def action_clicked(self, event):
        """Action performed when an element is clicked."""
        sender = self.sender()
        for i in range(len(self.list_options)):
            if sender == self.list_buttons[i]:
                self.selected = i
                self.list_buttons[i].setStyleSheet(actived_button)
                self.clicked.emit(f'select_{i}')
            else:
                self.list_buttons[i].setStyleSheet(unactived_button)

    def get_selection(self):
        """Return the selected object value."""
        return self.list_options[self.selected]

    def get_selection_index(self):
        """Return the index of the selected object value."""
        return self.selected

    def activate_index(self, index):
        """Set active an object from its index.
        :param index: Index of the object to activate.
        """
        self.selected = index
        self.list_buttons[index-1].setStyleSheet(actived_button)

class ErosionDilationOptionsWidget(QWidget):
    """
    Options widget of the AOI select menu.
    """

    ero_dil_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.check_diff = QCheckBox(text=translate('check_diff_image'))
        self.check_diff.stateChanged.connect(self.action_button_clicked)

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

        self.kernel_size_widget = ButtonSelectionWidget(parent=self, name='label_kernel_size')
        self.list_options = ['15', '9', '5', '3']
        self.size_options = ['10', '15', '20', '20']
        self.selected_size = 0
        self.kernel_size_widget.set_list_options(self.list_options)
        self.kernel_size_widget.clicked.connect(self.action_button_clicked)
        self.kernel_size_widget.activate_index(1)

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
        size = int(self.list_options[self.selected_size])
        pixel_size = int(self.size_options[self.selected_size])
        self.kernel_choice.set_size(size,size)
        self.kernel_choice.set_pixel_size(pixel_size)
        self.kernel_choice.pixel_changed.connect(self.action_button_clicked)
        self.kernel_choice.setMinimumHeight(8*20)

        self.layout.addWidget(self.check_diff)
        self.layout.addWidget(self.select_erosion)
        self.layout.addWidget(self.select_dilation)
        self.layout.addWidget(self.kernel_size_widget)
        self.layout.addWidget(self.kernel_preselect)
        self.layout.addWidget(self.kernel_choice)
        self.layout.addStretch()

    def action_button_clicked(self, event):
        """Action performed when a button is clicked."""
        sender = self.sender()
        if sender == self.check_diff:
            check_ok = 1 if self.check_diff.isChecked() else 0
            self.ero_dil_changed.emit(f'check_diff:{check_ok}')
        elif sender == self.select_erosion:
            self.ero_dil_changed.emit('erosion')
            self.select_erosion.setStyleSheet(actived_button)
            self.select_dilation.setStyleSheet(unactived_button)
        elif sender == self.select_dilation:
            self.ero_dil_changed.emit('dilation')
            self.select_erosion.setStyleSheet(unactived_button)
            self.select_dilation.setStyleSheet(actived_button)

        elif sender == self.kernel_choice:
            self.ero_dil_changed.emit('pixel')

        elif sender == self.kernel_size_widget:
            self.ero_dil_changed.emit('resize')

        elif sender == self.kernel_size_widget:
            k_size = int(self.kernel_size_widget.get_selection())
            self.kernel_choice.set_size(k_size, k_size)
            self.kernel_choice.repaint()
            self.ero_dil_changed.emit('kernel')
        elif sender == self.kernel_cross:
            self.kernel_cross.setStyleSheet(actived_button)
            self.kernel_rect.setStyleSheet(unactived_button)
            self.ero_dil_changed.emit('cross')
        elif sender == self.kernel_rect:
            self.kernel_cross.setStyleSheet(unactived_button)
            self.kernel_rect.setStyleSheet(actived_button)
            self.ero_dil_changed.emit('rect')

    def inactivate_kernel(self):
        """Set cross/rect kernel button style to inactive."""
        self.kernel_cross.setStyleSheet(unactived_button)
        self.kernel_rect.setStyleSheet(unactived_button)

    def get_kernel(self) -> np.ndarray:
        """Return an array containing the kernel."""
        return self.kernel_choice.get_image()

    def set_kernel(self, kernel: np.ndarray):
        """Set a kernel."""
        self.kernel_choice.set_image(kernel)

    def resize_kernel(self):
        """Resize the displayed kernel."""
        self.selected_size = self.kernel_size_widget.get_selection_index()
        size = self.list_options[self.selected_size]
        size_pixel = self.size_options[self.selected_size]
        self.kernel_choice.set_pixel_size(int(size_pixel))
        self.kernel_choice.set_size(int(size), int(size))
        self.kernel_choice.repaint()

class OpeningClosingOptionsWidget(QWidget):
    """
    Options widget of the AOI select menu.
    """

    open_close_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.check_diff = QCheckBox(text=translate('check_diff_image'))
        self.check_diff.stateChanged.connect(self.action_button_clicked)

        self.select_opening = QPushButton(translate('button_select_opening'))
        self.select_opening.setStyleSheet(styleH2)
        self.select_opening.setStyleSheet(unactived_button)
        self.select_opening.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.select_opening.clicked.connect(self.action_button_clicked)
        self.select_closing = QPushButton(translate('button_select_closing'))
        self.select_closing.setStyleSheet(styleH2)
        self.select_closing.setStyleSheet(unactived_button)
        self.select_closing.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.select_closing.clicked.connect(self.action_button_clicked)

        self.kernel_size_widget = ButtonSelectionWidget(parent=self, name='label_kernel_size')
        self.list_options = ['15', '9', '5', '3']
        self.size_options = ['10', '15', '20', '20']
        self.selected_size = 0
        self.kernel_size_widget.set_list_options(self.list_options)
        self.kernel_size_widget.clicked.connect(self.action_button_clicked)
        self.kernel_size_widget.activate_index(1)

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
        size = int(self.list_options[self.selected_size])
        pixel_size = int(self.size_options[self.selected_size])
        self.kernel_choice.set_size(size,size)
        self.kernel_choice.set_pixel_size(pixel_size)
        self.kernel_choice.pixel_changed.connect(self.action_button_clicked)
        self.kernel_choice.setMinimumHeight(8*20)

        self.layout.addWidget(self.check_diff)
        self.layout.addWidget(self.select_opening)
        self.layout.addWidget(self.select_closing)
        self.layout.addWidget(self.kernel_size_widget)
        self.layout.addWidget(self.kernel_preselect)
        self.layout.addWidget(self.kernel_choice)
        self.layout.addStretch()

    def action_button_clicked(self, event):
        """Action performed when a button is clicked."""
        sender = self.sender()
        if sender == self.check_diff:
            check_ok = 1 if self.check_diff.isChecked() else 0
            self.open_close_changed.emit(f'check_diff:{check_ok}')

        elif sender == self.select_opening:
            self.open_close_changed.emit('opening')
            self.select_opening.setStyleSheet(actived_button)
            self.select_closing.setStyleSheet(unactived_button)
        elif sender == self.select_closing:
            self.open_close_changed.emit('closing')
            self.select_opening.setStyleSheet(unactived_button)
            self.select_closing.setStyleSheet(actived_button)
        elif sender == self.kernel_choice:
            self.open_close_changed.emit('pixel')
        elif sender == self.kernel_size_widget:
            k_size = int(self.kernel_size_widget.get_selection())
            self.kernel_choice.set_size(k_size, k_size)
            self.kernel_choice.repaint()
            self.open_close_changed.emit('kernel')
        elif sender == self.kernel_cross:
            self.kernel_cross.setStyleSheet(actived_button)
            self.kernel_rect.setStyleSheet(unactived_button)
            self.open_close_changed.emit('cross')
        elif sender == self.kernel_rect:
            self.kernel_cross.setStyleSheet(unactived_button)
            self.kernel_rect.setStyleSheet(actived_button)
            self.open_close_changed.emit('rect')

    def inactivate_kernel(self):
        """Set cross/rect kernel button style to inactive."""
        self.kernel_cross.setStyleSheet(unactived_button)
        self.kernel_rect.setStyleSheet(unactived_button)

    def get_kernel(self) -> np.ndarray:
        """Return an array containing the kernel."""
        return self.kernel_choice.get_image()

    def set_kernel(self, kernel: np.ndarray):
        """Set a kernel."""
        self.kernel_choice.set_image(kernel)

    def resize_kernel(self):
        """Resize the displayed kernel."""
        self.selected_size = self.kernel_size_widget.get_selection_index()
        size = self.list_options[self.selected_size]
        size_pixel = self.size_options[self.selected_size]
        self.kernel_choice.set_pixel_size(int(size_pixel))
        self.kernel_choice.set_size(int(size), int(size))
        self.kernel_choice.repaint()


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

    def set_pixel_size(self, size: int):
        """
        Set the size of 1 image pixel, in pixels.
        :param size: Size of 1 pixel.
        """
        self.pixel_per_pixel = size

    def get_image(self) -> np.ndarray:
        """
        Return the image.
        :return: Array containing the image.
        """
        return self.image.astype(np.uint8)

    def set_image(self, image: np.ndarray):
        """
        Set a new image.
        """
        self.image = image.T
        self.repaint()