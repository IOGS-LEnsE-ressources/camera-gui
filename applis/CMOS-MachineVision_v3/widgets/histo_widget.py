# -*- coding: utf-8 -*-
"""*histo_widget.py* file.

This file contains graphical elements to display histograms of images in a widget.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : oct/2024
"""
from lensepy import *
from lensepy.css import *
import sys, os
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QLineEdit, QProgressBar,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import pyqtSignal, QDir
from matplotlib import pyplot as plt


def process_hist_from_array(array: np.ndarray, bins: list) -> (np.ndarray, np.ndarray):
    """
    Calculate a histogram from an array and bins definition.
    :param array: Array containing data.
    :param bins: Bins to calculate the histogram.
    :return: Tuple of np.ndarray: bins and hist data.
    """
    plot_hist, plot_bins_data = np.histogram(array, bins=bins)
    return plot_bins_data, plot_hist

def save_hist(data: np.ndarray, data_hist: np.ndarray, bins: np.ndarray,
              title: str = 'Image Histogram', file_name: str = 'histogram.png',
              informations: str = ''):
    """
    Create a PNG from histogram data.
    :param data: Data to process.
    :param data_hist: Histogram data from np.histogram function.
    :param bins: Bins of the histogram.
    :param title: Title of the figure. Default: Image Histogram.
    :param file_name: Name of the file to store the PNG image. Default: histogram.png.
    :param informations: Informations to display in the graph.
    """
    # Create histogram graph
    n = len(bins)
    mean_data = np.mean(data)
    if mean_data > bins[n//2]:
        x_text_pos = 0.30  # text on the left
    else:
        x_text_pos = 0.95  # text on the right
    plt.figure(figsize=(10, 8), dpi=150)
    plt.bar(bins[:-1], data_hist, width=np.diff(bins),
            edgecolor='black', alpha=0.75, color='blue')
    plt.title(title)
    text_str = f'Mean = {mean_data:.2f}\nStdDev = {np.std(data):.2f}'
    plt.text(x_text_pos, 0.95, text_str, fontsize=10, verticalalignment='top',
             horizontalalignment='right',
             transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.5))
    text_str = (informations)
    plt.text(x_text_pos, 0.25, text_str, fontsize=8, verticalalignment='top',
             horizontalalignment='right',
             transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.5))

    # histogram to store in a png file - and a txt file (array) ??
    default_dir = QDir.homePath()
    file_path, _ = QFileDialog.getSaveFileName(None, translate('save_histogram_title_window'),
                                               f'{default_dir}/{file_name}',
                                               "Images PNG (*.png)")
    if file_path:
        # create an image of the histogram of the saved_image
        plt.savefig(file_path)
        info = QMessageBox.information(None, 'Histogram Saved', f'File saved to {file_path}')
    else:
        warn = QMessageBox.warning(None, 'Saving Error', 'No file saved !')

def rand_pixels(aoi: list) -> (list, list):
    """Selection of 4 pixels in the area of interest."""
    x, y, h, w = aoi
    # Reset old coordinates
    image_x = []
    image_y = []
    for i in range(4):
        image_x.append(np.random.randint(x, x+h))
        image_y.append(np.random.randint(y, y+w))
    return image_x, image_y

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

class HistoTimeOptionsWidget(QWidget):

    start_acq_clicked = pyqtSignal(str)

    def __init__(self, parent):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.nb_of_points = 0
        self.image_x = []
        self.image_y = []
        self.pixels_value = [[], [], [], []]
        self.counter = 0
        self.acquiring = False

        # Title
        # -----
        self.label_title_time_analysis = QLabel(translate('title_time_analysis'))
        self.label_title_time_analysis.setStyleSheet(styleH1)

        # Number of points
        self.nb_of_points_widget = QWidget()
        self.nb_of_points_sublayout = QHBoxLayout()
        self.nb_of_points_label = QLabel('Number of points (2 to 2000) = ')
        self.nb_of_points_label.setStyleSheet(styleH2)
        self.nb_of_points_value = QLineEdit()
        self.nb_of_points_value.setText(str(self.nb_of_points))
        self.nb_of_points_value.editingFinished.connect(self.clicked_action)
        self.nb_of_points_sublayout.addWidget(self.nb_of_points_label)
        self.nb_of_points_sublayout.addWidget(self.nb_of_points_value)
        self.nb_of_points_widget.setLayout(self.nb_of_points_sublayout)

        self.start_button = QPushButton(translate('button_start_time'))
        self.start_button.setStyleSheet(styleH2)
        self.start_button.setStyleSheet(unactived_button)
        self.start_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.start_button.clicked.connect(self.clicked_action)

        self.progress_bar = QProgressBar(self, objectName="IOGSProgressBar")


        self.save_histo_button = QPushButton(translate('button_save_histo_spatial'))
        self.save_histo_button.setStyleSheet(styleH2)
        self.save_histo_button.setStyleSheet(disabled_button)
        self.save_histo_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.save_histo_button.clicked.connect(self.clicked_action)
        self.save_histo_button.setEnabled(False)

        self.pixel_select_widget = QWidget()
        self.pixel_select_layout = QHBoxLayout()
        self.pixel_select_widget.setLayout(self.pixel_select_layout)
        self.pixel_select_label = QLabel(translate('label_pixel_select'))
        self.pixel_select_layout.addWidget(self.pixel_select_label)
        self.pixel_select = QComboBox()
        self.pixel_select.addItems(['Pixel 1', 'Pixel 2', 'Pixel 3', 'Pixel 4'])
        self.pixel_select.setStyleSheet(styleH2)
        self.pixel_select.setStyleSheet(disabled_button)
        self.pixel_select.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.pixel_select.currentTextChanged.connect(self.clicked_action)
        self.pixel_select.setEnabled(False)
        self.pixel_select_layout.addWidget(self.pixel_select)

        self.layout.addWidget(self.label_title_time_analysis)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.nb_of_points_widget)
        self.layout.addWidget(self.progress_bar)
        self.layout.addStretch()
        self.layout.addWidget(self.pixel_select_widget)
        self.layout.addStretch()
        self.layout.addWidget(self.save_histo_button)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def clicked_action(self):
        sender = self.sender()
        if sender == self.start_button:
            if 1 < int(self.nb_of_points_value.text()) <= 2000:
                self.nb_of_points = int(self.nb_of_points_value.text())
                self.start_acq_clicked.emit('start')
                self.progress_bar.setMinimum(0)
                self.progress_bar.setMaximum(self.nb_of_points)
            else:
                warn = QMessageBox.warning(self, 'Wrong value', 'The value is not in the range 1 to 2000')
        elif sender == self.save_histo_button:
            self.start_acq_clicked.emit('save_hist_time')
        elif sender == self.pixel_select:
            self.start_acq_clicked.emit('pixel_changed')

    def is_acquiring(self):
        """Return true if the acquisition is running."""
        return self.acquiring

    def start_acquisition(self):
        """
        Start a new time acquisition for 4 pixels.
        """
        self.pixels_value = [[], [], [], []]
        self.acquiring = True
        self.counter = 0

    def increase_counter(self, image_array: np.ndarray):
        """
        Increase the counter of acquisition and add the data to the list of each pixel.
        :param image_array: Array containing the image.
        """
        for i in range(4):
            self.pixels_value[i].append(image_array[self.image_y[i], self.image_x[i]])
        self.counter += 1
        self.waiting_value()

    def get_pixels(self, index: int):
        """
        Return data for 1 pixel.
        :param index: Index of the pixel to return.
        :return: List of the data.
        """
        return self.pixels_value[index]

    def waiting_value(self):
        # Display time elapsed...
        self.progress_bar.setValue(self.counter)
        # Enable or disable buttons
        if self.counter < self.nb_of_points:
            self.start_button.setStyleSheet(disabled_button)
            self.start_button.setEnabled(False)
            self.save_histo_button.setStyleSheet(disabled_button)
            self.save_histo_button.setEnabled(False)
        else:
            self.acquiring = False
            self.start_acq_clicked.emit('acq_end')
            self.start_button.setStyleSheet(unactived_button)
            self.start_button.setEnabled(True)

    def set_enabled_save(self, value: bool = True):
        if value:
            # Save histo is possible
            self.save_histo_button.setStyleSheet(unactived_button)
            self.save_histo_button.setEnabled(True)
            self.pixel_select.setEnabled(True)
            self.pixel_select.setCurrentIndex(0)
        else:
            self.save_histo_button.setStyleSheet(disabled_button)
            self.save_histo_button.setEnabled(False)
            self.pixel_select.setEnabled(False)

    def get_pixel_index(self):
        """Return the selected pixel index."""
        return self.pixel_select.currentIndex()

    def set_pixels_x_y(self, pixels_x: list, pixels_y: list):
        """Set random pixels X and Y coordinates."""
        self.image_x = pixels_x
        self.image_y = pixels_y