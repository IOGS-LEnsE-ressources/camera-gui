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
from lensepy.css import *


# %% Widget
class MainMenuWidget(QWidget):
    # Signals definition
    # ------------------
    signal_menu_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__(parent=None)
        self.setStyleSheet("background-color: white;")

        # Widgets
        # -------
        self.layout = QVBoxLayout()

        self.subwidget = QWidget()
        self.sublayout = QVBoxLayout()
        
        self.label_title_main_menu = QLabel('Menu')
        self.label_title_main_menu.setStyleSheet(styleH1)
        self.label_title_main_menu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sublayout.addWidget(self.label_title_main_menu)

        self.button_list = []   # List of the buttons of the menu
        self.button_signal_list = []    # List of the signal emitted value for each button
        self.button_option_list = []    # List of the option buttons of the menu
        self.button_signal_option_list = [] # List of the signal emitted value for option buttons

        self.subwidget.setLayout(self.sublayout)
        self.layout.addWidget(self.subwidget)
        self.setLayout(self.layout)

    def add_item_menu(self, name: str, disabled: bool=False, signal_value: str=''):
        button = QPushButton(name)
        button.setStyleSheet(unactived_button)
        button.setFixedHeight(BUTTON_HEIGHT)
        button.clicked.connect(self.button_main_menu_isClicked)
        self.button_list.append(button)
        if signal_value == '':
            self.button_signal_list.append(name)
        else:
            self.button_signal_list.append(signal_value)
        if disabled:
            self.disable_button(name)

    def add_option_item_menu(self, name: str, disabled: bool=False, signal_value: str=''):
        button = QPushButton(name)
        button.setStyleSheet(unactived_button)
        button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        button.clicked.connect(self.button_main_menu_isClicked)
        self.button_option_list.append(button)
        if signal_value == '':
            self.button_signal_option_list.append(name)
        else:
            self.button_signal_option_list.append(signal_value)
        if disabled:
            self.disable_button(name)

    def refresh_menu(self):
        for i, button in enumerate(self.button_list):
            self.sublayout.addWidget(button)
        self.sublayout.addStretch()
        for i, button_o in enumerate(self.button_option_list):
            self.sublayout.addWidget(button_o)

    def disable_button(self, name:str):
        index_button = self.find_button_index_by_text(name, self.button_list)
        if index_button != -1:
            self.button_list[index_button].setEnabled(False)
            self.button_list[index_button].setStyleSheet(disabled_button)
        else:
            index_button = self.find_button_index_by_text(name, self.button_option_list)
            if index_button != -1:
                self.button_option_list[index_button].setEnabled(False)
                self.button_option_list[index_button].setStyleSheet(disabled_button)

    def enable_button(self, name:str):
        index_button = self.find_button_index_by_text(name, self.button_list)
        if index_button != -1:
            self.button_list[index_button].setEnabled(True)
            self.button_list[index_button].setStyleSheet(unactived_button)
        else:
            index_button = self.find_button_index_by_text(name, self.button_option_list)
            if index_button != -1:
                self.button_option_list[index_button].setEnabled(True)
                self.button_option_list[index_button].setStyleSheet(unactived_button)

    def unactive_buttons(self):
        for i, button in enumerate(self.button_list):
            if button.isEnabled():
                button.setStyleSheet(unactived_button)
        for i, button_o in enumerate(self.button_option_list):
            if button_o.isEnabled():
                button_o.setStyleSheet(unactived_button)
        
    def button_main_menu_isClicked(self):
        button = self.sender()
        # Change style
        self.unactive_buttons()
        button.setStyleSheet(actived_button)
        # Finding button in main menu
        index = self.find_button_index_by_text(button.text(), self.button_list)
        if index != -1:
            self.signal_menu_selected.emit(self.button_signal_list[index])
        else:
            # Finding button in options item
            index = self.find_button_index_by_text(button.text(), self.button_option_list)
            if index != -1:
                self.signal_menu_selected.emit(self.button_signal_option_list[index])
            else:
                self.signal_menu_selected.emit('bad_signal')

    def find_button_index_by_text(self, text, list_):
        for index, button in enumerate(list_):
            if button.text() == text:
                return index
        return -1

    def reset_menu(self):
        # Change style
        self.unactive_buttons()

        
# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Translation
            dictionary = {}

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(300, 300, 200, 600)

            self.central_widget = MainMenuWidget()
            self.central_widget.add_item_menu('Test 1')
            self.central_widget.add_item_menu('Test 2')
            self.central_widget.add_option_item_menu('Option 1')
            self.central_widget.add_option_item_menu('Option 2')
            self.central_widget.refresh_menu()
            self.central_widget.disable_button('Test 2')
            self.central_widget.signal_menu_selected.connect(self.print_signal)
            self.setCentralWidget(self.central_widget)

        def print_signal(self, event):
            print(event)

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
