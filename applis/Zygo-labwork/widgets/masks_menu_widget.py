# -*- coding: utf-8 -*-
"""*masks_widget.py* file.

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
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QPixmap
import numpy as np
from lensepy import load_dictionary, translate
from lensepy.css import *

styleCheckbox = f"font-size: 12px; padding: 7px; color: {BLUE_IOGS}; font-weight: normal;"

# %% Params
BUTTON_HEIGHT = 30 #px

# %% Widget
class MasksMenu(QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.setStyleSheet("background-color: white;")
        self.layout = QVBoxLayout()

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        
        self.label_title_masks_menu = QLabel(translate('label_title_masks_menu'))
        self.label_title_masks_menu.setStyleSheet(styleH1)
        
        self.subwidget_masks = QWidget()
        self.sublayout_masks = QHBoxLayout()
        # First col
        # ---------
        self.subwidget_left = QWidget()
        self.sublayout_left = QVBoxLayout()
        
        self.button_circle_mask = QPushButton(translate('button_circle_mask'))
        self.button_circle_mask.setStyleSheet(unactived_button)
        self.button_circle_mask.setFixedHeight(BUTTON_HEIGHT)
        
        self.button_rectangle_mask = QPushButton(translate('button_rectangle_mask'))
        self.button_rectangle_mask.setStyleSheet(unactived_button)
        self.button_rectangle_mask.setFixedHeight(BUTTON_HEIGHT)
        
        self.button_polygon_mask = QPushButton(translate('button_polygon_mask'))
        self.button_polygon_mask.setStyleSheet(unactived_button)
        self.button_polygon_mask.setFixedHeight(BUTTON_HEIGHT)
        
        self.checkbox_apply_mask = QCheckBox(translate('checkbox_apply_mask'))
        self.checkbox_apply_mask.setStyleSheet(styleCheckbox)
        
        self.sublayout_left.addWidget(self.button_circle_mask)
        self.sublayout_left.addWidget(self.button_rectangle_mask)
        self.sublayout_left.addWidget(self.button_polygon_mask)
        self.sublayout_left.addWidget(self.checkbox_apply_mask)
        self.sublayout_left.setContentsMargins(0, 0, 0, 0)
        self.subwidget_left.setLayout(self.sublayout_left)
        
        # Second col
        # ----------
        self.subwidget_right = QWidget()
        self.sublayout_right = QVBoxLayout()
        
        self.button_move_mask = QPushButton(translate('button_move_mask'))
        self.button_move_mask.setStyleSheet(unactived_button)
        self.button_move_mask.setFixedHeight(BUTTON_HEIGHT)
        
        self.button_resize_mask = QPushButton(translate('button_resize_mask'))
        self.button_resize_mask.setStyleSheet(unactived_button)
        self.button_resize_mask.setFixedHeight(BUTTON_HEIGHT)
        
        self.button_erase_mask = QPushButton(translate('button_erase_mask'))
        self.button_erase_mask.setStyleSheet(unactived_button)
        self.button_erase_mask.setFixedHeight(BUTTON_HEIGHT)
        
        self.checkbox_inverse_mask = QCheckBox(translate('checkbox_inverse_mask'))
        self.checkbox_inverse_mask.setStyleSheet(styleCheckbox)
        
        self.sublayout_right.addWidget(self.button_move_mask)
        self.sublayout_right.addWidget(self.button_resize_mask)
        self.sublayout_right.addWidget(self.button_erase_mask)
        self.sublayout_right.addWidget(self.checkbox_inverse_mask)
        self.sublayout_right.setContentsMargins(0, 0, 0, 0)
        self.subwidget_right.setLayout(self.sublayout_right)
        
        # Combined
        # --------
        self.sublayout_masks.addWidget(self.subwidget_left)
        self.sublayout_masks.addWidget(self.subwidget_right)
        self.sublayout_masks.setContentsMargins(0, 0, 0, 0)
        self.subwidget_masks.setLayout(self.sublayout_masks)
        
        self.layout.addWidget(self.label_title_masks_menu)
        self.layout.addWidget(self.subwidget_masks)

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)
        
# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Translation
            dictionary = {}
            # Load French dictionary
            #dictionary = load_dictionary('../lang/dict_FR.txt')
            # Load English dictionary
            dictionary = load_dictionary('../lang/dict_EN.txt')

            self.setWindowTitle(translate("window_title_masks_widget"))
            self.setGeometry(300, 300, 600, 600)

            self.central_widget = MasksMenu()
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
