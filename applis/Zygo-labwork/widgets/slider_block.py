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
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox, QSlider, QLineEdit,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QPixmap
import numpy as np

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
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"
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
class SliderBlock(QWidget):
    def __init__(self, name:str, unit:str, min_value:float, max_value:float) -> None: 
        super().__init__(parent=None)
        self.min_value = min_value
        self.max_value = max_value
        self.value = self.min_value + (self.max_value - self.min_value)/3
        self.ratio = 100
        
        self.layout = QVBoxLayout()
        
        # First line: name, value and unit
        # --------------------------------
        self.subwidget_texts = QWidget()
        self.sublayout_texts = QHBoxLayout()
        
        self.label_name = QLabel(translate(name)+':')
        self.label_name.setStyleSheet(styleH2)
        
        self.lineedit_value = QLineEdit()
        self.lineedit_value.setText(str(self.value))
        self.lineedit_value.textChanged.connect(self.input_changed)
        
        self.label_unit = QLabel(unit)
        self.label_unit.setStyleSheet(styleH3)
        
        self.sublayout_texts.addWidget(self.label_name)
        self.sublayout_texts.addWidget(self.lineedit_value)
        self.sublayout_texts.addWidget(self.label_unit)
        
        self.subwidget_texts.setLayout(self.sublayout_texts)
        
        # Second line: slider and min/max
        # -------------------------------
        self.subwidget_slider = QWidget()
        self.sublayout_slider = QHBoxLayout()
        
        self.label_min_value = QLabel(str(self.min_value)+' '+unit)
        self.label_min_value.setStyleSheet(styleH3)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(int(self.min_value*self.ratio))
        self.slider.setMaximum(int(self.max_value*self.ratio))
        self.slider.valueChanged.connect(self.slider_position_changed)
        
        self.label_max_value = QLabel(str(self.max_value)+' '+unit)
        self.label_max_value.setStyleSheet(styleH3)
        
        self.sublayout_slider.addWidget(self.label_min_value)
        self.sublayout_slider.addWidget(self.slider)
        self.sublayout_slider.addWidget(self.label_max_value)
        
        self.subwidget_slider.setLayout(self.sublayout_slider)
        
        # All combined
        # ------------
        self.layout.addWidget(self.subwidget_texts)
        self.layout.addWidget(self.subwidget_slider)
        self.setLayout(self.layout)
        
    def slider_position_changed(self):
        self.value = self.slider.value()/self.ratio
        self.update_block()
    
    def input_changed(self):
        print("")
        self.value = max(self.min_value, min(self.max_value,float(self.lineedit_value.text())))
        self.update_block()
    
    def update_block(self):
        self.lineedit_value.setText(str(self.value))
        self.slider.setValue(int(self.value*self.ratio))
        
# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            
            # Load French dictionary
            #dictionary = load_dictionary('C:/Users/LEnsE/Documents/GitHub/camera-gui/applis/Zygo-labwork/lang/dict_FR.txt')
            # Load English dictionary
            dictionary = load_dictionary('C:/Users/LEnsE/Documents/GitHub/camera-gui/applis/Zygo-labwork/lang/dict_EN.txt')

            self.setWindowTitle(translate("window_title_slider_block"))
            self.setGeometry(300, 300, 600, 600)

            self.central_widget = SliderBlock(name='name', unit='unit', min_value=4.2, max_value=7.8)
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
