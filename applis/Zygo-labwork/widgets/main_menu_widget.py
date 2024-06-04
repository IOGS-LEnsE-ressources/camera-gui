# -*- coding: utf-8 -*-
"""*main_menu_widget.py* file.

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
import numpy as np
from lensepy import load_dictionary, translate

# %% To add in lensepy librairy
# Colors
# ------
BLUE_IOGS = '#0A3250'
ORANGE_IOGS = '#FF960A'
WHITE = '#000000'
GRAY = '#727272'
BLACK = '#FFFFFF'

# Styles
# ------
styleH1 = f"font-size:20px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
no_style = f"background-color:{GRAY}; color:{BLACK}; font-size:15px;"

unactived_button = f"background-color:{BLUE_IOGS}; color:white; font-size:15px; font-weight:bold; border-radius: 10px;"
actived_button = f"background-color:{ORANGE_IOGS}; color:white; font-size:15px; font-weight:bold; border-radius: 10px;"

# Translation
# -----------
dictionary = {}

def load_dictionary(language_path: str) -> None:
    """
    Load a dictionary from a CSV file based on the specified language.

    Parameters
    ----------
    language : str
        The language path to specify which CSV file to load.

    Returns
    -------
    None

    Notes
    -----
    This function reads a CSV file that contains key-value pairs separated by semicolons (';')
    and stores them in a global dictionary variable. The CSV file may contain comments
    prefixed by '//', which will be ignored.

    The file should have the following format:
        // comment
        // comment
        key_1 ; language_word_1
        key_2 ; language_word_2

    The function will strip any leading or trailing whitespace from the keys and values.

    See Also
    --------
    numpy.genfromtxt : Load data from a text file, with missing values handled as specified.
    """
    global dictionary
    dictionary = {}

    # Read the CSV file, ignoring lines starting with '//'
    data = np.genfromtxt(
        language_path, delimiter=';', dtype=str, comments='#', encoding='UTF-8')

    # Populate the dictionary with key-value pairs from the CSV file
    for key, value in data:
        dictionary[key.strip()] = value.strip()

def translate(key: str) -> str:
    """
    Translate a given key to its corresponding value.

    Parameters
    ----------
    key : str
        The key to translate.

    Returns
    -------
    str
        The translated value corresponding to the key. If the key does not exist, it returns the key itself.

    """    
    if ('dictionary' in globals()) and (key in dictionary):
        return dictionary[key]
    else:
        return key

# %% Params
BUTTON_HEIGHT = 60 #px
OPTIONS_BUTTON_HEIGHT = 20 #px

# %% Widget
class MainMenuWidget(QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        
        self.label_title_main_menu = QLabel(translate("label_title_main_menu"))
        self.label_title_main_menu.setStyleSheet(styleH1)
        self.label_title_main_menu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.button_camera_settings_main_menu = QPushButton(translate("button_camera_settings_main_menu"))
        self.button_camera_settings_main_menu.setStyleSheet(unactived_button)
        self.button_camera_settings_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_camera_settings_main_menu.clicked.connect(self.button_camera_settings_main_menu_isClicked)
        
        self.button_masks_main_menu = QPushButton(translate("button_masks_main_menu"))
        self.button_masks_main_menu.setStyleSheet(unactived_button)
        self.button_masks_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_masks_main_menu.clicked.connect(self.button_masks_main_menu_isClicked)
        
        self.button_acquisition_main_menu = QPushButton(translate("button_acquisition_main_menu"))
        self.button_acquisition_main_menu.setStyleSheet(unactived_button)
        self.button_acquisition_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_acquisition_main_menu.clicked.connect(self.button_acquisition_main_menu_isClicked)
        
        self.button_analyzes_main_menu = QPushButton(translate("button_analyzes_main_menu"))
        self.button_analyzes_main_menu.setStyleSheet(unactived_button)
        self.button_analyzes_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_analyzes_main_menu.clicked.connect(self.button_analyzes_main_menu_isClicked)
        
        self.button_options_main_menu = QPushButton(translate("button_options_main_menu"))
        self.button_options_main_menu.setStyleSheet(unactived_button)
        self.button_options_main_menu.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.button_options_main_menu.clicked.connect(self.button_options_main_menu_isClicked)
        
        self.layout.addWidget(self.label_title_main_menu)
        self.layout.addWidget(self.button_camera_settings_main_menu)
        self.layout.addWidget(self.button_masks_main_menu)
        self.layout.addWidget(self.button_acquisition_main_menu)
        self.layout.addWidget(self.button_analyzes_main_menu)
        self.layout.addStretch()
        self.layout.addWidget(self.button_options_main_menu)
        self.setLayout(self.layout)
        
    def unactive_buttons(self):
        """ Switches all buttons to inactive style """
        self.button_camera_settings_main_menu.setStyleSheet(unactived_button)
        self.button_masks_main_menu.setStyleSheet(unactived_button)
        self.button_acquisition_main_menu.setStyleSheet(unactived_button)
        self.button_analyzes_main_menu.setStyleSheet(unactived_button)
        self.button_options_main_menu.setStyleSheet(unactived_button)        
        
    def button_camera_settings_main_menu_isClicked(self):
        # Change style
        self.unactive_buttons()
        self.button_camera_settings_main_menu.setStyleSheet(actived_button)
        
        # Action
        print("Camera Settings")
        
    def button_masks_main_menu_isClicked(self):
        # Change style
        self.unactive_buttons()
        self.button_masks_main_menu.setStyleSheet(actived_button)
        
        # Action
        print("Masks")
        
    def button_acquisition_main_menu_isClicked(self):
        # Change style
        self.unactive_buttons()
        self.button_acquisition_main_menu.setStyleSheet(actived_button)
        
        # Action
        print("Acquisition")
        
    def button_analyzes_main_menu_isClicked(self):
        # Change style
        self.unactive_buttons()
        self.button_analyzes_main_menu.setStyleSheet(actived_button)
        
        # Action
        print("Analyzes")
        
    def button_options_main_menu_isClicked(self):
        # Change style
        self.unactive_buttons()
        self.button_options_main_menu.setStyleSheet(actived_button)
        
        # Action
        print("Options")
        
# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            
            # Load French dictionary
            #dictionary = load_dictionary('../lang/dict_FR.txt')
            # Load English dictionary
            dictionary = load_dictionary('../lang/dict_EN.txt')

            self.setWindowTitle(translate("window_title_main_menu_widget"))
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
                event.accept()
            else:
                event.ignore()


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
