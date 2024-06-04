# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 09:52:38 2024

@author: LEnsE
"""

# -*- coding: utf-8 -*-
"""*menu_widget.py* file.

...

This file is attached to a 1st year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/contents/appli_CMOS_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>

"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QPixmap

# %% To add in lensepy librairy
# Colors
BLUE_LENSE = '#0A3250'
BLACK = '#FFFFFF'

ACTIVE_COLOR = '#000000'
INACTIVE_COLOR = '#FFFFFF'

styleH1 = "font-size:16px; padding:7px; color:Navy; border-top: 1px solid Navy;"
no_style = "background:darkgray; color:white; font-size:15px; font-weight:bold;"

# %% Test
translate = lambda x: x

# %% Widget
class MainMenuWidget(QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        
        self.label_title_menu = QLabel(translate("label_title_menu"))
        self.label_title_menu.setStyleSheet(styleH1)
        self.label_title_menu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.button_camera_settings_menu = QPushButton(translate("button_camera_settings_menu"))
        self.button_camera_settings_menu.setStyleSheet(no_style)
        self.button_camera_settings_menu.clicked.connect(self.button_camera_settings_menu_isClicked)
        
        self.button_masks_menu = QPushButton(translate("button_masks_menu"))
        self.button_masks_menu.setStyleSheet(no_style)
        self.button_masks_menu.clicked.connect(self.button_masks_menu_isClicked)
        
        self.button_acquisition_menu = QPushButton(translate("button_acquisition_menu"))
        self.button_acquisition_menu.setStyleSheet(no_style)
        self.button_acquisition_menu.clicked.connect(self.button_acquisition_menu_isClicked)
        
        self.button_analyzes_menu = QPushButton(translate("button_analyzes_menu"))
        self.button_analyzes_menu.setStyleSheet(no_style)
        self.button_analyzes_menu.clicked.connect(self.button_analyzes_menu_isClicked)
        
        self.layout.addWidget(self.label_title_menu)
        self.layout.addWidget(self.button_camera_settings_menu)
        self.layout.addWidget(self.button_masks_menu)
        self.layout.addWidget(self.button_acquisition_menu)
        self.layout.addWidget(self.button_analyzes_menu)
        self.layout.addStretch()
        self.setLayout(self.layout)
        
    def button_camera_settings_menu_isClicked(self):
        print("Camera Settings")
        
    def button_masks_menu_isClicked(self):
        print("Masks")
        
    def button_acquisition_menu_isClicked(self):
        print("Acquisition")
        
    def button_analyzes_menu_isClicked(self):
        print("Analyzes")
        
# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("Zygo Main Menu Widget")
            self.setGeometry(300, 300, 200, 600)

            self.central_widget = MainMenuWidget()
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
                if self.central_widget.camera is not None:
                    self.central_widget.camera.disconnect()
                event.accept()
            else:
                event.ignore()


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
