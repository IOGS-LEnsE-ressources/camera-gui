# -*- coding: utf-8 -*-
"""*time_analysis_widget.py* file.

This file is attached to a 2nd year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-Detection.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>

"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLineEdit,
    QVBoxLayout, QHBoxLayout, QGridLayout, QProgressBar,
    QLabel, QPushButton,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

if __name__ == '__main__':
    from slider_bloc import SliderBloc
else:
    from gui.slider_bloc import SliderBloc

from lensepy import load_dictionary, translate
from lensepy.css import *
from lensecam.ids.camera_ids import CameraIds

# %% To add in lensepy librairy
# Styles
# ------
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

# %% Params
BUTTON_HEIGHT = 60  # px
OPTIONS_BUTTON_HEIGHT = 20  # px


# %% Widget
class TimeAnalysisWidget(QWidget):

    start_acq_clicked = pyqtSignal(str)

    def __init__(self, parent):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.nb_of_points = 0

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

        self.start_button = QPushButton('button_start_time')
        self.start_button.setStyleSheet(styleH2)
        self.start_button.setStyleSheet(unactived_button)
        self.start_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.start_button.clicked.connect(self.clicked_action)

        self.progress_bar = QProgressBar(self)

        self.save_histo_button = QPushButton('button_save_histo_spatial')
        self.save_histo_button.setStyleSheet(styleH2)
        self.save_histo_button.setStyleSheet(disabled_button)
        self.save_histo_button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.save_histo_button.clicked.connect(self.clicked_action)
        self.save_histo_button.setEnabled(False)

        self.layout.addWidget(self.label_title_time_analysis)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.nb_of_points_widget)
        self.layout.addWidget(self.progress_bar)
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
            self.start_acq_clicked.emit('save_hist')

    def get_nb_of_points(self):
        return self.nb_of_points

    def waiting_value(self, value: int):
        # Display time elapsed...
        self.progress_bar.setValue(value)
        # Enable or disable buttons
        if value < self.nb_of_points:
            self.start_button.setStyleSheet(disabled_button)
            self.start_button.setEnabled(False)
            self.save_histo_button.setStyleSheet(disabled_button)
            self.save_histo_button.setEnabled(False)
        else:
            self.start_button.setStyleSheet(unactived_button)
            self.start_button.setEnabled(True)

    def set_enabled_save(self, value: bool = True):
        if value:
            # Save histo is possible
            self.save_histo_button.setStyleSheet(unactived_button)
            self.save_histo_button.setEnabled(True)
        else:
            self.save_histo_button.setStyleSheet(disabled_button)
            self.save_histo_button.setEnabled(False)


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

            self.central_widget = TimeAnalysisWidget(self)
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