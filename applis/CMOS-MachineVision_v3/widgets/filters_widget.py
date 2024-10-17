# -*- coding: utf-8 -*-
"""*filters_widget.py* file.

This file contains graphical elements to process filters on images in a widget.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : oct/2024
"""
from lensepy import *
from lensepy.css import *
import sys, os
import numpy as np
from lensepy.pyqt6.widget_combobox import *
from lensepy.pyqt6.widget_slider import *
from lensepy.pyqt6.widget_image_display import *
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QLineEdit, QProgressBar,
    QMessageBox, QFileDialog, QMainWindow
)
from PyQt6.QtCore import pyqtSignal, QDir
from matplotlib import pyplot as plt


# TO MOVE TO LENSEPY.PYQT6
from lensepy.images.processing import *
from enum import Enum

class Kernel(Enum):
    NOKERNEL = 0
    CROSS = 1
    RECT = 2
    ELLIP = 3

class Smooth(Enum):
    NOFILTER = 0
    BLUR = 1
    GAUSS = 2
    MEDIAN = 3

class KernelChoiceWidget(QWidget):
    """
    Widget containing the kernel choice options.
    """

    kernel_choice_changed = pyqtSignal(str)

    def __init__(self, parent=None, name='label_kernel_size',
                 list_options=['15', '9', '5', '3'],
                 size_options=['10', '15', '20', '20'],
                 choice: bool=True):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.parent = parent
        self.choice = choice

        self.kernel_type = Kernel.NOKERNEL

        self.kernel_size_widget = ButtonSelectionWidget(parent=self, name=name)
        self.list_options = list_options
        self.size_options = size_options
        self.selected_size = 1
        self.kernel_size_widget.set_list_options(self.list_options)
        self.kernel_size_widget.clicked.connect(self.action_button_clicked)
        self.kernel_size_widget.activate_index(self.selected_size)

        if self.choice:
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
            self.kernel_ellip = QPushButton(translate('kernel_preselect_ellip'))
            self.kernel_ellip.setStyleSheet(styleH2)
            self.kernel_ellip.setStyleSheet(unactived_button)
            self.kernel_ellip.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
            self.kernel_ellip.clicked.connect(self.action_button_clicked)
            self.kernel_preselect_layout.addWidget(self.kernel_cross)
            self.kernel_preselect_layout.addWidget(self.kernel_rect)
            self.kernel_preselect_layout.addWidget(self.kernel_ellip)

            self.kernel_choice = ImagePixelsWidget(self)
            size = int(self.list_options[self.selected_size-1])
            pixel_size = int(self.size_options[self.selected_size-1])
            self.kernel_choice.set_size(size, size)
            self.kernel_choice.set_pixel_size(pixel_size)
            self.kernel_choice.pixel_changed.connect(self.action_button_clicked)
            self.kernel_choice.setMinimumHeight(8 * 20)

        self.layout.addWidget(self.kernel_size_widget)
        if self.choice:
            self.layout.addWidget(self.kernel_preselect)
            self.layout.addWidget(self.kernel_choice)

    def set_list_options(self, list, size_list=None):
        """Update the list of options."""
        self.list_options = list
        self.size_options = size_list
        self.selected_size = 0
        self.kernel_size_widget.set_list_options(self.list_options)

    def activate_index(self, index:int):
        """Activate a specific option by index."""
        self.kernel_size_widget.activate_index(index)

    def action_button_clicked(self, event):
        """Action performed when a button is clicked."""
        sender = self.sender()
        k_size = int(self.kernel_size_widget.get_selection())

        if sender == self.kernel_size_widget:
            index = int(self.kernel_size_widget.get_selection_index())
            p_size = int(self.size_options[index])
            if self.choice:
                self.kernel_choice.set_size(k_size, k_size)
                self.kernel_choice.set_pixel_size(p_size)
            self.kernel_choice_changed.emit('kernel')
        elif sender == self.kernel_cross:
            self.kernel_type = Kernel.CROSS
            self.kernel_cross.setStyleSheet(actived_button)
            self.kernel_rect.setStyleSheet(unactived_button)
            self.kernel_ellip.setStyleSheet(unactived_button)
            self.kernel_choice_changed.emit('cross')
        elif sender == self.kernel_rect:
            self.kernel_type = Kernel.RECT
            self.kernel_cross.setStyleSheet(unactived_button)
            self.kernel_rect.setStyleSheet(actived_button)
            self.kernel_ellip.setStyleSheet(unactived_button)
            self.kernel_choice_changed.emit('rect')
        elif sender == self.kernel_ellip:
            self.kernel_type = Kernel.ELLIP
            self.kernel_cross.setStyleSheet(unactived_button)
            self.kernel_rect.setStyleSheet(unactived_button)
            self.kernel_ellip.setStyleSheet(actived_button)
            self.kernel_choice_changed.emit('ellip')

        if self.choice:
            if event == 'pixel_changed':
                self.inactivate_kernel()
            elif self.kernel_type == Kernel.RECT:
                kernel = get_rect_kernel(k_size)
                self.set_kernel(kernel)
            elif self.kernel_type == Kernel.CROSS:
                kernel = get_cross_kernel(k_size)
                self.set_kernel(kernel)
            elif self.kernel_type == Kernel.ELLIP:
                kernel = get_ellip_kernel(k_size)
                self.set_kernel(kernel)
            self.kernel_choice.repaint()

    def inactivate_kernel(self):
        """Set cross/rect kernel button style to inactive."""
        self.kernel_cross.setStyleSheet(unactived_button)
        self.kernel_rect.setStyleSheet(unactived_button)
        self.kernel_ellip.setStyleSheet(unactived_button)

    def get_kernel(self) -> np.ndarray:
        """Return an array containing the kernel."""
        return self.kernel_choice.get_image()

    def get_kernel_size(self) -> int:
        """Return the kernel size."""
        return int(self.kernel_size_widget.get_selection())

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

class SmoothFilterOptionsWidget(QWidget):
    """
    Widget containing the smooth filters options.
    """

    options_changed = pyqtSignal(str)

    def __init__(self, parent):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent

        self.filter = Smooth.NOFILTER

        self.check_diff = QCheckBox(text=translate('check_diff_image'))
        self.check_diff.stateChanged.connect(self.action_button_clicked)

        self.filter_type = ButtonSelectionWidget(parent=self, name=translate('filtre_type'))
        self.list_options = [translate('filter_blur'),
                             translate('filter_gaussian'),
                             translate('filter_median')]
        self.selected_type = 1
        self.filter_type.set_list_options(self.list_options)
        self.filter_type.clicked.connect(self.action_button_clicked)
        self.filter_type.activate_index(self.selected_type)

        self.kernel_choice = KernelChoiceWidget(name='label_kernel_size', choice=False)
        self.kernel_choice.kernel_choice_changed.connect(self.action_button_clicked)

        self.slider_sigma = SliderBloc(name=translate('gaussian_sigma'), unit='',
                                      min_value=0, max_value=5)
        self.slider_sigma.set_value(1)
        self.slider_sigma.set_enabled(False)
        self.slider_sigma.slider_changed.connect(self.action_button_clicked)

        self.layout.addWidget(self.check_diff)
        self.layout.addWidget(self.filter_type)
        self.layout.addWidget(self.kernel_choice)
        self.layout.addStretch()
        self.layout.addWidget(self.slider_sigma)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def action_button_clicked(self, event):
        """Action performed when a button is clicked."""
        sender = self.sender()
        if sender == self.check_diff:
            check_ok = 1 if self.check_diff.isChecked() else 0
            self.options_changed.emit(f'check_diff:{check_ok}')
        elif sender == self.filter_type:
            f_type = self.filter_type.get_selection()
            self.slider_sigma.set_enabled(False)
            if f_type == translate('filter_blur'):
                self.filter = Smooth.BLUR
            elif f_type == translate('filter_gaussian'):
                self.filter = Smooth.GAUSS
                self.slider_sigma.set_enabled(True)
            elif f_type == translate('filter_median'):
                self.filter = Smooth.MEDIAN
        elif sender == self.slider_sigma:
            sigma = self.slider_sigma.get_value()
            print(f'Sigma Changed ! {sigma}')

        self.options_changed.emit('smooth_filter')

    def get_selection(self, image: np.ndarray):
        k_size = self.kernel_choice.get_kernel_size()
        if self.filter == Smooth.BLUR:
            output_image = cv2.blur(image, (k_size, k_size))
        elif self.filter == Smooth.GAUSS:
            sigma_x = self.slider_sigma.get_value()
            output_image = cv2.GaussianBlur(image, (k_size, k_size), sigmaX=sigma_x)
        elif self.filter == Smooth.MEDIAN:
            output_image = cv2.medianBlur(image, k_size)
        else:
            return None
        return output_image


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = SmoothFilterOptionsWidget(self)
            self.setCentralWidget(self.central_widget)


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())