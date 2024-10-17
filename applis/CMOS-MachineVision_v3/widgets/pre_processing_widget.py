# -*- coding: utf-8 -*-
"""*pre_processing_widget.py* file.

This file contains graphical elements to apply pre processing on images.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : oct/2024
"""
from lensepy import translate
from lensepy.css import *
from lensepy.pyqt6.widget_combobox import *
from lensepy.pyqt6.widget_image_display import *
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox,
    QMessageBox,
)
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect
from lensepy.pyqt6.widget_combobox import *
from lensepy.pyqt6.widget_slider import *

class ThresholdOptionsWidget(QWidget):
    """
    Widget containing the threshold options.
    """

    threshold_changed = pyqtSignal(str)

    def __init__(self, parent):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent

        self.buttons_choice = ButtonSelectionWidget(parent=self, name=translate('label_threshold_type'))
        self.list_options = [translate('threshold_normal'),
                             translate('threshold_inverted'),
                             translate('threshold_hat')]
        #self.list_options = ['1', '2', '3']
        self.buttons_choice.set_list_options(self.list_options)
        self.buttons_choice.clicked.connect(self.action_type_changing)

        max_value = (2**self.parent.parent.image_bits_depth - 1)
        self.slider_threshold_value = SliderBloc(name=translate('threshold_value'), unit='',
                                       min_value=0, max_value=max_value, integer=True)
        self.slider_threshold_value.set_value(max_value//4)
        self.slider_threshold_value.set_enabled(False)
        self.slider_threshold_value.slider_changed.connect(self.action_slider_changing)
        self.slider_threshold_value_hat = SliderBloc(name=translate('threshold_value_hat'), unit='',
                                       min_value=0, max_value=max_value, integer=True)
        self.slider_threshold_value_hat.set_enabled(False)
        self.slider_threshold_value_hat.slider_changed.connect(self.action_slider2_changing)
        self.slider_threshold_value_hat.set_value(3*max_value//4)

        self.layout.addWidget(self.buttons_choice)
        self.layout.addWidget(self.slider_threshold_value)
        self.layout.addWidget(self.slider_threshold_value_hat)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def action_type_changing(self):
        choice = self.buttons_choice.get_selection()
        if choice == translate('threshold_normal'):
            self.slider_threshold_value.set_enabled(True)
            self.slider_threshold_value_hat.set_enabled(False)
        elif choice == translate('threshold_inverted'):
            self.slider_threshold_value.set_enabled(True)
            self.slider_threshold_value_hat.set_enabled(False)
        elif choice == translate('threshold_hat'):
            self.slider_threshold_value.set_enabled(True)
            self.slider_threshold_value_hat.set_enabled(True)
        self.threshold_changed.emit('threshold_type')

    def action_slider_changing(self):
        threshold_value = int(self.slider_threshold_value.get_value())
        threshold_value_hat = int(self.slider_threshold_value_hat.get_value())
        if threshold_value >= threshold_value_hat:
            threshold_value_hat = threshold_value + 1
            self.slider_threshold_value_hat.set_value(threshold_value_hat)
        self.threshold_changed.emit('threshold_change')

    def action_slider2_changing(self):
        threshold_value = int(self.slider_threshold_value.get_value())
        threshold_value_hat = int(self.slider_threshold_value_hat.get_value())
        if threshold_value_hat <= threshold_value:
            threshold_value = threshold_value_hat - 1
            self.slider_threshold_value.set_value(threshold_value)
        self.threshold_changed.emit('threshold_change')

    def get_threshold_value(self):
        """Return the value of the threshold."""
        return int(self.slider_threshold_value.get_value())

    def get_threshold_hat_value(self):
        """Return the value of the hat threshold."""
        return int(self.slider_threshold_value_hat.get_value())

    def get_threshold_type_index(self):
        """Return the selected type of threshold."""
        return int(self.buttons_choice.get_selection_index()+1)


class ContrastAdjustOptionsWidget(QWidget):
    """
    Widget containing the adjusting contrast options.
    # TO DO
    """

    options_clicked = pyqtSignal(str)

    def __init__(self, parent):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent

        max_value = (2**self.parent.parent.image_bits_depth - 1)

        self.slider_threshold_min = SliderBloc(name=translate('threshold_value_min'), unit='',
                                       min_value=0, max_value=max_value, integer=True)
        self.slider_threshold_min.set_value(0)
        self.slider_threshold_min.slider_changed.connect(self.action_slider_changing)

        self.slider_threshold_max = SliderBloc(name=translate('threshold_value_max'), unit='',
                                       min_value=0, max_value=max_value, integer=True)
        self.slider_threshold_max.set_value(max_value)
        self.slider_threshold_max.slider_changed.connect(self.action_slider_changing)

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
            max_value += 1
            self.slider_threshold_max.set_value(min_value+1)

    def get_max(self):
        """Return the value of the maximum slider."""
        return self.slider_threshold_max.get_value()

    def get_min(self):
        """Return the value of the minimum slider."""
        return self.slider_threshold_min.get_value()

    def get_selection(self, image: np.ndarray, inverted: bool=False):
        """Process image in 8bits mode - for faster process"""
        delta_image_depth = (self.parent.bits_depth - 8)  # Power of 2 for depth conversion
        min_value = int(self.slider_threshold_min.get_value() // 2**delta_image_depth)
        max_value = int(self.slider_threshold_max.get_value() // 2**delta_image_depth)
        max_range = 255
        gain = max_range/(max_value-min_value)
        output_image = ((image.astype(np.int16)-min_value+1) * gain).astype(np.int16)
        output_image[output_image > max_range] = 255
        output_image[output_image <= 1] = 0
        return output_image.astype(np.uint8)


class ErosionDilationOptionsWidget(QWidget):
    """
    Widget containing the erosion/dilation options.
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
        self.kernel_ellip = QPushButton(translate('kernel_preselect_ellip'))
        self.kernel_ellip.setStyleSheet(styleH2)
        self.kernel_ellip.setStyleSheet(unactived_button)
        self.kernel_ellip.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.kernel_ellip.clicked.connect(self.action_button_clicked)
        self.kernel_preselect_layout.addWidget(self.kernel_cross)
        self.kernel_preselect_layout.addWidget(self.kernel_rect)
        self.kernel_preselect_layout.addWidget(self.kernel_ellip)

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
            self.kernel_ellip.setStyleSheet(unactived_button)
            self.ero_dil_changed.emit('cross')
        elif sender == self.kernel_rect:
            self.kernel_cross.setStyleSheet(unactived_button)
            self.kernel_rect.setStyleSheet(actived_button)
            self.kernel_ellip.setStyleSheet(unactived_button)
            self.ero_dil_changed.emit('rect')
        elif sender == self.kernel_ellip:
            self.kernel_cross.setStyleSheet(unactived_button)
            self.kernel_rect.setStyleSheet(unactived_button)
            self.kernel_ellip.setStyleSheet(actived_button)
            self.ero_dil_changed.emit('ellip')

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
    Widget containing the opening/closing options.
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
        self.kernel_ellip = QPushButton(translate('kernel_preselect_ellip'))
        self.kernel_ellip.setStyleSheet(styleH2)
        self.kernel_ellip.setStyleSheet(unactived_button)
        self.kernel_ellip.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.kernel_ellip.clicked.connect(self.action_button_clicked)
        self.kernel_preselect_layout.addWidget(self.kernel_cross)
        self.kernel_preselect_layout.addWidget(self.kernel_rect)
        self.kernel_preselect_layout.addWidget(self.kernel_ellip)

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
            self.kernel_ellip.setStyleSheet(unactived_button)
            self.open_close_changed.emit('cross')
        elif sender == self.kernel_rect:
            self.kernel_cross.setStyleSheet(unactived_button)
            self.kernel_rect.setStyleSheet(actived_button)
            self.kernel_ellip.setStyleSheet(unactived_button)
            self.open_close_changed.emit('rect')
        elif sender == self.kernel_ellip:
            self.kernel_cross.setStyleSheet(unactived_button)
            self.kernel_rect.setStyleSheet(unactived_button)
            self.kernel_ellip.setStyleSheet(actived_button)
            self.open_close_changed.emit('ellip')

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


class ContrastBrightnessOptionsWidget(QWidget):
    """
    Widget containing the contrast/brightness options.
    """

    contrast_brithtness_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.slider_contrast = SliderBloc(translate('slider_contrast'), '', 0, 2)
        self.slider_contrast.set_value(1)
        self.slider_contrast.slider_changed.connect(self.action_slider_changed)

        self.slider_brightness = SliderBloc(translate('slider_brightness'), '', -100, 100, integer=True)
        self.slider_brightness.set_value(0)
        self.slider_brightness.slider_changed.connect(self.action_slider_changed)

        self.button_reset = QPushButton('Reset')
        self.button_reset.clicked.connect(self.action_slider_changed)
        self.button_reset.setStyleSheet(unactived_button)
        self.button_reset.setFixedHeight(OPTIONS_BUTTON_HEIGHT)

        self.layout.addWidget(self.slider_contrast)
        self.layout.addWidget(self.slider_brightness)
        self.layout.addWidget(self.button_reset)
        self.layout.addStretch()

    def action_slider_changed(self, event):

        sender = self.sender()
        if sender == self.slider_contrast or sender == self.slider_brightness:
            self.contrast_brithtness_changed.emit('contrast_brightness')
        elif sender == self.button_reset:
            self.slider_contrast.set_value(1)
            self.slider_brightness.set_value(0)
            self.repaint()

    def get_contrast(self):
        """Return the value of the contrast slider."""
        return float(self.slider_contrast.get_value())

    def get_brightness(self):
        """Return the value of the contrast slider."""
        return float(self.slider_brightness.get_value())


class GradientOptionsWidget(QWidget):
    """
    Widget containing the gradient options.
    """

    gradient_changed = pyqtSignal(str)

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
        self.kernel_ellip = QPushButton(translate('kernel_preselect_ellip'))
        self.kernel_ellip.setStyleSheet(styleH2)
        self.kernel_ellip.setStyleSheet(unactived_button)
        self.kernel_ellip.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.kernel_ellip.clicked.connect(self.action_button_clicked)
        self.kernel_preselect_layout.addWidget(self.kernel_cross)
        self.kernel_preselect_layout.addWidget(self.kernel_rect)
        self.kernel_preselect_layout.addWidget(self.kernel_ellip)

        self.kernel_choice = ImagePixelsWidget(self)
        size = int(self.list_options[self.selected_size])
        pixel_size = int(self.size_options[self.selected_size])
        self.kernel_choice.set_size(size,size)
        self.kernel_choice.set_pixel_size(pixel_size)
        self.kernel_choice.pixel_changed.connect(self.action_button_clicked)
        self.kernel_choice.setMinimumHeight(8*20)

        self.layout.addWidget(self.check_diff)
        self.layout.addWidget(self.kernel_size_widget)
        self.layout.addWidget(self.kernel_preselect)
        self.layout.addWidget(self.kernel_choice)
        self.layout.addStretch()

    def action_button_clicked(self, event):
        """Action performed when a button is clicked."""
        sender = self.sender()
        if sender == self.check_diff:
            check_ok = 1 if self.check_diff.isChecked() else 0
            self.gradient_changed.emit(f'check_diff:{check_ok}')
        elif sender == self.kernel_choice:
            self.gradient_changed.emit('pixel')
        elif sender == self.kernel_size_widget:
            k_size = int(self.kernel_size_widget.get_selection())
            self.kernel_choice.set_size(k_size, k_size)
            self.kernel_choice.repaint()
            self.gradient_changed.emit('kernel')
        elif sender == self.kernel_cross:
            self.kernel_cross.setStyleSheet(actived_button)
            self.kernel_rect.setStyleSheet(unactived_button)
            self.kernel_ellip.setStyleSheet(unactived_button)
            self.gradient_changed.emit('cross')
        elif sender == self.kernel_rect:
            self.kernel_cross.setStyleSheet(unactived_button)
            self.kernel_rect.setStyleSheet(actived_button)
            self.kernel_ellip.setStyleSheet(unactived_button)
            self.gradient_changed.emit('rect')
        elif sender == self.kernel_ellip:
            self.kernel_cross.setStyleSheet(unactived_button)
            self.kernel_rect.setStyleSheet(unactived_button)
            self.kernel_ellip.setStyleSheet(actived_button)
            self.gradient_changed.emit('ellip')

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


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = ThresholdOptionsWidget(self)
            self.setCentralWidget(self.central_widget)


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())