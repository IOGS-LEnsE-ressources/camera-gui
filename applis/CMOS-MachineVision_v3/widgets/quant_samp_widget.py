# -*- coding: utf-8 -*-
"""*quant_samp_widget.py* file.

This file contains graphical elements to show impact of quantization
and sampling on an image in a widget.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : oct/2024
"""
import sys
from lensepy import translate
from lensepy.css import *
from lensepy.pyqt6.widget_slider import SliderBloc
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit,
    QMessageBox, QMainWindow
)
from PyQt6.QtCore import Qt, pyqtSignal
from lensepy.pyqt6.widget_image_histogram import ImageHistogramWidget

class QuantizationOptionsWidget(QWidget):
    """
    Options widget of the Quantization select menu.
    """

    quantized = pyqtSignal(str)

    def __init__(self, parent):
        """
        Default Constructor.
        :param parent: Parent widget of the main widget.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.quantization_factor = 8 # bits

        # Title
        # -----
        self.label_title_quantization = QLabel(translate('title_quantization'))
        self.label_title_quantization.setStyleSheet(styleH1)

        # Quantization factor
        # -------------------
        self.slider_quantization = SliderBloc(translate('slider_quantization'), unit='bits', min_value=1,
                                              max_value=8, integer=True)
        self.slider_quantization.set_value(8)
        self.slider_quantization.slider_changed.connect(self.action_slider_bits_depth_changed)

        self.layout.addWidget(self.label_title_quantization)
        self.layout.addWidget(self.slider_quantization)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def action_slider_bits_depth_changed(self, event):
        """Action performed when the slider changed."""
        self.quantized.emit('quantized')

    def get_bits_depth(self) -> int:
        """Return the selected bits depth.
        :return: Selected bits depth.
        """
        return int(self.slider_quantization.get_value())

class SamplingOptionsWidget(QWidget):
    """
    Options widget of the Quantization select menu.
    """

    resampled = pyqtSignal(str)

    def __init__(self, parent):
        """
        Default Constructor.
        :param parent: Parent widget of the main widget.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.quantization_factor = 8 # bits

        # Title
        # -----
        self.label_title_sampling = QLabel(translate('title_resampling'))
        self.label_title_sampling.setStyleSheet(styleH1)

        # Quantization factor
        # -------------------
        self.slider_sampling = SliderBloc(translate('slider_sampling'), unit='pixels', min_value=1,
                                              max_value=32, integer=True)
        self.slider_sampling.set_value(1)
        self.slider_sampling.slider_changed.connect(self.action_slider_samples_changed)

        self.layout.addWidget(self.label_title_sampling)
        self.layout.addWidget(self.slider_sampling)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def action_slider_samples_changed(self, event):
        """Action performed when the slider changed."""
        self.resampled.emit('resampled')

    def get_sample_factor(self) -> int:
        """Return the selected bits depth.
        :return: Selected bits depth.
        """
        return int(self.slider_sampling.get_value())


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = QuantizationOptionsWidget(self)
            self.setCentralWidget(self.central_widget)


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
