# -*- coding: utf-8 -*-
"""*title_widget.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout,
    QLabel,
    QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *

# %% To add in lensepy librairy
# Styles
# ------
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

# %% Params
BUTTON_HEIGHT = 60 #px
OPTIONS_BUTTON_HEIGHT = 20 #px

# %% Widget
class TitleWidget(QWidget):
    def __init__(self, dictionary_in=None):
        super().__init__(parent=None)
        self.layout = QGridLayout()

        self.label_title = QLabel(translate('label_title'))
        self.label_title.setStyleSheet(styleH1)
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_subtitle = QLabel(translate("label_subtitle"))
        self.label_subtitle.setStyleSheet(styleH3)
        self.label_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lense_logo = QLabel('Logo')
        self.lense_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo = QPixmap("./assets/IOGS-LEnsE-logo_small.jpg")
        # logo = logo_.scaled(imageSize.width()//4, imageSize.height()//4, Qt.AspectRatioMode.KeepAspectRatio)
        self.lense_logo.setPixmap(logo)

        self.layout.addWidget(self.label_title, 0, 0)
        self.layout.addWidget(self.label_subtitle, 1, 0)
        self.layout.setColumnStretch(0, 10)
        self.layout.setColumnStretch(1, 5)
        self.layout.addWidget(self.lense_logo, 0, 1, 2, 1)

        self.setLayout(self.layout)

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
            self.setGeometry(300, 300, 800, 200)

            self.central_widget = TitleWidget()
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
