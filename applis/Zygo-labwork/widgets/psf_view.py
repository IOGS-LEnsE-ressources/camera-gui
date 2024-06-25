# -*- coding: utf-8 -*-
"""*psf_view.py* file.

*psf_view* file that contains :class::AnalysisApp

This file is attached to a 2nd year of engineer training labwork in photonics.
Subject : https://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-PolyAberrations.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""
import sys, os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(parent_dir)

import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QCheckBox, QDialog,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt, QSignalMapper
from PyQt6.QtGui import QPixmap, QIcon, QCloseEvent

from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *

from process.compute_psf_ftm import *

if __name__ == '__main__':
    from lineedit_bloc import LineEditBloc
    from imshow_pyqtgraph import ImageWidget
else:
    from widgets.lineedit_bloc import LineEditBloc
    from widgets.imshow_pyqtgraph import ImageWidget


# %% To add in lensepy librairy
# Styles
# ------
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

# %% Params
BUTTON_HEIGHT = 60 #px
OPTIONS_BUTTON_HEIGHT = 20 #px

x = y = np.linspace(-5, 5, 500)
X, Y = np.meshgrid(x, y)
phase_test = np.ones_like(X)
phase_test[X**2 + Y**2 > 4**2] = 0
phase_test = phase_test*np.exp(2*I*PI*(np.sqrt(8)*X*(X**2+Y**2)-2)*0.007) # Coma

class PointspreadFunctionDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)
        
        if parent is None:
            self.phase = phase_test
        else:
            self.phase = self.parent.phase

        self.grid_size = 1024
        self.zoom = 4

        self.setStyleSheet("background-color: white;")
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        self.master_widget.setStyleSheet("background-color: white;")

        # Title
        # -----
        self.label_title = QLabel('PSF')
        self.label_title.setStyleSheet(styleH1)

        # Zero-padding selectors
        # ----------------------
        self.lineedit_grid_size = LineEditBloc(title='Ne', txt=str(self.grid_size))
        self.lineedit_grid_size.editing_finished_signal().connect(self.on_grid_size_change)
        self.lineedit_zoom = LineEditBloc(title='Zoom', txt=str(self.zoom))
        self.lineedit_zoom.editing_finished_signal().connect(self.on_zoom_change)
        self.sublayout = QHBoxLayout()
        self.sublayout.addWidget(self.lineedit_grid_size)
        self.sublayout.addWidget(self.lineedit_zoom)

        # PSF
        # ---
        self.psf_display = ImageWidget()

        self.layout.addWidget(self.label_title)
        self.layout.addLayout(self.sublayout)
        self.layout.addWidget(self.psf_display)

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

    def on_grid_size_change(self):
        self.grid_size = int(self.lineedit_grid_size.text())
        self.update_psf()

    def on_zoom_change(self):
        self.zoom = float(self.lineedit_zoom.text())
        self.update_psf()

    def update_psf(self):
        psf = get_psf(self.phase, self.zoom, self.grid_size)
        #psf = get_psf(self.phase, 4, 1024)

        psf-=psf.min()
        psf/=psf.max()

        # print(psf.min(), psf.max())

        self.psf_display.set_image_data(psf, 'gray')












if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Define Window title
            self.setWindowTitle(translate("Zygo-IDS Labwork APP"))
            self.setWindowIcon(QIcon('assets\IOGS-LEnsE-icon.jpg'))
            self.setGeometry(50, 50, 500, 500)

            self.central_widget = PointspreadFunctionDisplay()
            self.setCentralWidget(self.central_widget)

        def closeEvent(self, event):
            """
            closeEvent redefinition. Use when the user clicks
            on the red cross to close the window
            """
            pass
            """reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                if self.central_widget.camera is not None:
                    self.central_widget.camera_widget.disconnect()
                event.accept()
            else:
                event.ignore()"""


    app = QApplication(sys.argv)
    main = MyWindow()
    main.showMaximized()
    sys.exit(app.exec())