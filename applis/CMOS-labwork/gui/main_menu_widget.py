# -*- coding: utf-8 -*-
"""*main_menu_widget.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

from lensepy import load_dictionary, translate
from lensepy.css import *
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

# %% To add in lensepy librairy
# Styles
# ------
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

# %% Params
BUTTON_HEIGHT = 60 #px
OPTIONS_BUTTON_HEIGHT = 20 #px

# %% Widget
class MainMenuWidget(QWidget):

    camera_settings_clicked = pyqtSignal(str)

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
        
        self.button_aoi_main_menu = QPushButton(translate("button_aoi_main_menu"))
        self.button_aoi_main_menu.setStyleSheet(unactived_button)
        self.button_aoi_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_aoi_main_menu.clicked.connect(self.button_aoi_main_menu_isClicked)
        
        self.button_live_main_menu = QPushButton(translate("button_live_main_menu"))
        self.button_live_main_menu.setStyleSheet(unactived_button)
        self.button_live_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_live_main_menu.clicked.connect(self.button_live_main_menu_isClicked)
        
        self.button_acquisition_main_menu = QPushButton(translate("button_acquisition_main_menu"))
        self.button_acquisition_main_menu.setStyleSheet(unactived_button)
        self.button_acquisition_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_acquisition_main_menu.clicked.connect(self.button_acquisition_main_menu_isClicked)
        
        self.button_options_main_menu = QPushButton(translate("button_options_main_menu"))
        self.button_options_main_menu.setStyleSheet(unactived_button)
        self.button_options_main_menu.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.button_options_main_menu.clicked.connect(self.button_options_main_menu_isClicked)
        
        self.layout.addWidget(self.label_title_main_menu)
        self.layout.addWidget(self.button_camera_settings_main_menu)
        self.layout.addWidget(self.button_aoi_main_menu)
        self.layout.addWidget(self.button_live_main_menu)
        self.layout.addWidget(self.button_acquisition_main_menu)
        self.layout.addStretch()
        self.layout.addWidget(self.button_options_main_menu)
        self.setLayout(self.layout)
        
    def unactive_buttons(self):
        """ Switches all buttons to inactive style """
        self.button_camera_settings_main_menu.setStyleSheet(unactived_button)
        self.button_aoi_main_menu.setStyleSheet(unactived_button)
        self.button_live_main_menu.setStyleSheet(unactived_button)
        self.button_acquisition_main_menu.setStyleSheet(unactived_button)
        self.button_options_main_menu.setStyleSheet(unactived_button)        
        
    def button_camera_settings_main_menu_isClicked(self):
        # Change style
        self.unactive_buttons()
        self.button_camera_settings_main_menu.setStyleSheet(actived_button)
        
        # Action
        self.camera_settings_clicked.emit('camera_settings')
        
    def button_aoi_main_menu_isClicked(self):
        # Change style
        self.unactive_buttons()
        self.button_aoi_main_menu.setStyleSheet(actived_button)
        
        # Action
        print("AOI")
        
    def button_live_main_menu_isClicked(self):
        # Change style
        self.unactive_buttons()
        self.button_live_main_menu.setStyleSheet(actived_button)
        
        # Action
        print("Live")
        
    def button_acquisition_main_menu_isClicked(self):
        # Change style
        self.unactive_buttons()
        self.button_acquisition_main_menu.setStyleSheet(actived_button)
        
        # Action
        print("Acquisition")
        
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

            # Translation
            dictionary = {}
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