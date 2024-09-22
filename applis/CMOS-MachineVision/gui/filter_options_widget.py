# -*- coding: utf-8 -*-
"""*filter_options_widget.py* file.

This file is attached to a 2nd year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-Detection.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>

"""

import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLineEdit, QComboBox,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from lensepy import load_dictionary, translate
from lensepy.css import *

if __name__ == '__main__':
    from combobox_bloc import ComboBoxBloc
    from lineedit_bloc import LineEditBloc
    from slider_bloc import SliderBloc
else:
    from gui.combobox_bloc import ComboBoxBloc
    from gui.lineedit_bloc import LineEditBloc
    from gui.slider_bloc import SliderBloc

# %% To add in lensepy librairy
# Styles
# ------
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

# %% Params
BUTTON_HEIGHT = 60  # px
OPTIONS_BUTTON_HEIGHT = 20  # px

blur_list = [translate('blur_averaging'), translate('blur_gaussian'),
             translate('blur_median'), translate('blur_bilateral')]
size_list = ['1', '3', '5', '9', '15', '21', '31']
threshold_list = [translate('th_classic'), translate('th_inverted'), translate('th_hat')]


class ThresholdWidget(QWidget):

    options_clicked = pyqtSignal(str)

    def __init__(self, parent):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent

        # Title
        # -----
        self.label_title_threshold_options = QLabel(translate('title_threshold'))
        self.label_title_threshold_options.setStyleSheet(styleH1)

        self.combobox_threshold_type = ComboBoxBloc(title=translate('threshold_type'),
                                                       list_options=threshold_list)
        self.combobox_threshold_type.selection_changed.connect(self.text_changed)
        max_value = (2**self.parent.bits_depth - 1)
        self.slider_threshold_value = SliderBloc(title=translate('threshold_value'), unit='',
                                       min_value=0, max_value=max_value, is_integer=True)
        self.slider_threshold_value.set_value(max_value//4)
        self.slider_threshold_value.set_enabled(False)
        self.slider_threshold_value.slider_changed.connect(self.action_slider_changing)
        self.slider_threshold_value_hat = SliderBloc(title=translate('threshold_value_hat'), unit='',
                                       min_value=0, max_value=max_value, is_integer=True)
        self.slider_threshold_value_hat.set_enabled(False)
        self.slider_threshold_value_hat.slider_changed.connect(self.action_slider_changing)
        self.slider_threshold_value_hat.set_value(3*max_value//4)

        self.layout.addWidget(self.label_title_threshold_options)
        self.layout.addWidget(self.combobox_threshold_type)
        self.layout.addWidget(self.slider_threshold_value)
        self.layout.addWidget(self.slider_threshold_value_hat)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def text_changed(self):
        if (self.combobox_threshold_type.get_text() == translate('th_classic') or
            self.combobox_threshold_type.get_text() == translate('th_inverted')):
            self.slider_threshold_value.set_enabled(True)
            self.slider_threshold_value_hat.set_enabled(False)
        elif self.combobox_threshold_type.get_text() == translate('th_hat'):
            self.slider_threshold_value.set_enabled(True)
            self.slider_threshold_value_hat.set_enabled(True)

    def action_slider_changing(self):
        threshold_value = int(self.slider_threshold_value.get_value())
        threshold_value_hat = int(self.slider_threshold_value_hat.get_value())
        if threshold_value >= threshold_value_hat:
            threshold_value_hat = threshold_value + 1
            self.slider_threshold_value_hat.set_value(threshold_value_hat)

    def get_selection(self, image: np.ndarray, inverted: bool=False):
        """Process image in 8bits mode - for faster process"""
        delta_image_depth = (self.parent.bits_depth - 8)  # Power of 2 for depth conversion
        threshold_index = self.combobox_threshold_type.get_index()
        threshold_value = int(self.slider_threshold_value.get_value() // 2**delta_image_depth)
        threshold_value_hat = int(self.slider_threshold_value_hat.get_value() // 2**delta_image_depth)
        # Process image
        if threshold_index == 1: # classic
            ret, output_image = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)
        elif threshold_index == 2: # inverted
            ret, output_image = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY_INV)
        elif threshold_index == 3: # hat / in range
            output_image = cv2.inRange(image, threshold_value, threshold_value_hat)


        else:
            return None
        if inverted:
            return output_image - image
        else:
            return output_image


class ContrastAdjustWidget(QWidget):

    options_clicked = pyqtSignal(str)

    def __init__(self, parent):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent

        # Title
        # -----
        self.label_title_contrast_adjust = QLabel(translate('title_contrast_adjust'))
        self.label_title_contrast_adjust.setStyleSheet(styleH1)

        max_value = (2**self.parent.bits_depth - 1)

        self.slider_threshold_min = SliderBloc(title=translate('threshold_value_min'), unit='',
                                       min_value=0, max_value=max_value, is_integer=True)
        self.slider_threshold_min.set_value(0)
        self.slider_threshold_min.slider_changed.connect(self.action_slider_changing)

        self.slider_threshold_max = SliderBloc(title=translate('threshold_value_max'), unit='',
                                       min_value=0, max_value=max_value, is_integer=True)
        self.slider_threshold_max.set_value(max_value)
        self.slider_threshold_max.slider_changed.connect(self.action_slider_changing)

        self.layout.addWidget(self.label_title_contrast_adjust)
        self.layout.addWidget(self.slider_threshold_min)
        self.layout.addWidget(self.slider_threshold_max)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def text_changed(self):
        pass

    def action_slider_changing(self):
        min_value = int(self.slider_threshold_min.get_value())
        max_value = int(self.slider_threshold_max.get_value())
        if min_value >= max_value:
            self.slider_threshold_max.set_value(min_value+1)

    def get_selection(self, image: np.ndarray, inverted: bool=False):
        """Process image in 8bits mode - for faster process"""
        delta_image_depth = (self.parent.bits_depth - 8)  # Power of 2 for depth conversion
        min_value = int(self.slider_threshold_min.get_value() // 2**delta_image_depth)
        max_value = int(self.slider_threshold_max.get_value() // 2**delta_image_depth)
        max_range = 255
        gain = max_range/(max_value-min_value)
        print(f'gain = {gain}')
        output_image = ((image.astype(np.int16)-min_value+1) * gain).astype(np.int16)
        output_image[output_image > max_range] = 255
        output_image[output_image <= 1] = 0
        return output_image.astype(np.uint8)


# %% Widget
class FilterBlurWidget(QWidget):

    options_clicked = pyqtSignal(str)

    def __init__(self, parent):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent

        # Title
        # -----
        self.label_title_filter_options = QLabel(translate('title_filter_blur'))
        self.label_title_filter_options.setStyleSheet(styleH1)

        self.combobox_blur = ComboBoxBloc(title=translate('blur_type'), list_options=blur_list)
        self.combobox_blur.selection_changed.connect(self.text_changed)

        self.combobox_size = ComboBoxBloc(title=translate('kernel_size'), list_options=size_list)
        self.combobox_size.selection_changed.connect(self.text_changed)

        self.slider_sigma = SliderBloc(title=translate('gaussian_sigma'), unit='',
                                      min_value=0, max_value=5)
        self.slider_sigma.set_value(0)
        self.slider_sigma.set_enabled(False)

        self.slider_sigma_space = SliderBloc(title=translate('sigma_space'), unit='px',
                                             min_value=0, max_value=100)#0 , is_integer=True)
        self.slider_sigma_space.set_value(10)
        self.slider_sigma_space.set_enabled(False)

        self.slider_sigma_color = SliderBloc(title=translate('sigma_color'), unit='gray',
                                             min_value=0, max_value=100)# 0, is_integer=True)
        self.slider_sigma_color.set_value(10)
        self.slider_sigma_color.set_enabled(False)

        self.layout.addWidget(self.label_title_filter_options)
        self.layout.addWidget(self.combobox_blur)
        self.layout.addWidget(self.combobox_size)
        self.layout.addStretch()
        self.layout.addWidget(self.slider_sigma)
        self.layout.addWidget(self.slider_sigma_space)
        self.layout.addWidget(self.slider_sigma_color)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def text_changed(self, s):
        self.slider_sigma.set_enabled(False)
        self.slider_sigma_space.set_enabled(False)
        self.slider_sigma_color.set_enabled(False)
        if self.combobox_blur.get_text() == translate('blur_gaussian'):
            self.slider_sigma.set_enabled(True)
        if self.combobox_blur.get_text() == translate('blur_bilateral'):
            self.slider_sigma_space.set_enabled(True)
            self.slider_sigma_color.set_enabled(True)

    def get_selection(self, image: np.ndarray, inverted: bool=False):
        filter_index = self.combobox_blur.get_index()
        kernel_size = self.combobox_size.get_text()
        if kernel_size.isnumeric() is False:
            return None
        if filter_index == 0:
            return None
        kernel_size = int(kernel_size)
        # Process image
        if filter_index == 1: # averaging
            output_image = cv2.blur(image, (kernel_size, kernel_size))
        elif filter_index == 2: # gaussian
            sigma_x = self.slider_sigma.get_value()
            output_image = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigmaX=sigma_x)
        elif filter_index == 3: # median
            output_image = cv2.medianBlur(image, kernel_size)
        elif filter_index == 4: # bilateral
            sigma_space = self.slider_sigma_space.get_value()
            sigma_color = self.slider_sigma_color.get_value()
            output_image = cv2.bilateralFilter(image, kernel_size, sigmaSpace=sigma_space, sigmaColor=sigma_color)
        else:
            return None
        if inverted:
            return output_image - image
        else:
            return output_image

edge_list = [translate('edge_sobel_x'), translate('edge_sobel_y'), translate('edge_sobel_xy'),
             translate('edge_canny')]
class FilterEdgeWidget(QWidget):

    options_clicked = pyqtSignal(str)

    def __init__(self, parent):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent

        # Title
        # -----
        self.label_title_filter_options = QLabel(translate('title_filter_blur'))
        self.label_title_filter_options.setStyleSheet(styleH1)

        self.combobox_edge = ComboBoxBloc(title=translate('edge_type'), list_options=edge_list)
        self.combobox_edge.selection_changed.connect(self.text_changed)

        self.combobox_size = ComboBoxBloc(title=translate('kernel_size'), list_options=size_list)
        self.combobox_size.selection_changed.connect(self.text_changed)


        self.layout.addWidget(self.label_title_filter_options)
        self.layout.addWidget(self.combobox_edge)
        self.layout.addWidget(self.combobox_size)
        self.layout.addStretch()
        self.layout.addStretch()
        self.setLayout(self.layout)

    def text_changed(self, s):
        pass

    def get_selection(self, image: np.ndarray, inverted: bool=False):
        filter_index = self.combobox_edge.get_index()
        kernel_size = self.combobox_size.get_text()
        if kernel_size.isnumeric() is False:
            return None
        if filter_index == 0:
            return None
        kernel_size = int(kernel_size)
        # Process image
        if filter_index == 1: # sobel X
            output_image = cv2.Sobel(src=image, ddepth=cv2.CV_8U, dx=1, dy=0, ksize=kernel_size)
        elif filter_index == 2: # sobel Y
            output_image = cv2.Sobel(src=image, ddepth=cv2.CV_8U, dx=0, dy=1, ksize=kernel_size)
        elif filter_index == 3: # sobel XY
            output_image = cv2.Sobel(src=image, ddepth=cv2.CV_8U, dx=1, dy=1, ksize=kernel_size)
        elif filter_index == 4: # canny
            # Add threshold
            output_image = edges = cv2.Canny(image=image, threshold1=100, threshold2=200)
        else:
            return None
        if inverted:
            return output_image - image
        else:
            return output_image



# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication


    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Translation
            dictionary = {}
            # Load French dictionary
            # dictionary = load_dictionary('../lang/dict_FR.txt')
            # Load English dictionary
            dictionary = load_dictionary('../lang/dict_EN.txt')

            self.setWindowTitle(translate("window_title_camera_settings"))
            self.setGeometry(300, 300, 400, 600)

            self.central_widget = FilterBlurWidget(self)
            self.setCentralWidget(self.central_widget)

        def closeEvent(self, event):
            """
            closeEvent redefinition. Use when the user clicks
            on the red cross to close the window
            """
            reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())