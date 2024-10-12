# -*- coding: utf-8 -*-
"""*histo_widget.py* file.

This file contains graphical elements to display histograms of images in a widget.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : oct/2024
"""
from lensepy import translate
from lensepy.css import *
import sys, os
import numpy as np
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal

class HistoSpaceOptionsWidget(QWidget):
    """
    Options widget of the histo space menu.
    """

    snap_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent widget of the histo space options widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.layout = QVBoxLayout()

        # Title
        # -----
        self.label_title_spatial_analysis = QLabel(translate('title_histo_analysis'))
        self.label_title_spatial_analysis.setStyleSheet(styleH1)

        self.snap_button = QPushButton(translate('button_acquire_histo'))
        self.snap_button.setStyleSheet(styleH2)
        self.snap_button.setStyleSheet(unactived_button)
        self.snap_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.snap_button.clicked.connect(self.clicked_action)

        self.save_png_image_button = QPushButton(translate('button_save_png_image_spatial'))
        self.save_png_image_button.setStyleSheet(styleH2)
        self.save_png_image_button.setStyleSheet(disabled_button)
        self.save_png_image_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.save_png_image_button.clicked.connect(self.clicked_action)
        self.save_png_image_button.setEnabled(False)

        self.layout.addWidget(self.label_title_spatial_analysis)
        self.layout.addWidget(self.snap_button)
        self.layout.addStretch()
        self.layout.addWidget(self.save_png_image_button)

        self.layout.addStretch()
        self.setLayout(self.layout)

    def clicked_action(self):
        sender = self.sender()
        if sender == self.snap_button:
            self.snap_clicked.emit('snap')
            self.save_png_image_button.setStyleSheet(unactived_button)
            self.save_png_image_button.setEnabled(True)
        elif sender == self.save_png_image_button:
            self.snap_clicked.emit('save_png')
