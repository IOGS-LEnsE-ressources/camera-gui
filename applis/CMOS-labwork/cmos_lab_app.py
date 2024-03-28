# -*- coding: utf-8 -*-
"""*cmos_lab_app.py* file.

*cmos_lab_app* file that contains :class::CmosLabApp

This file is attached to a 2nd year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-Detection.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/contents/appli_CMOS_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>

*****************
*  CameraChoice
*****************
* Mode
* FPS
* Exposure
*****************
* AOI   - DRAW
*  x0   w
*  y0   h
*       Params
*****************
* Hist AOI
* X Zoom    Start
*****************
* Hist Pixel(s)
* Params    Start
* X Hist    X Time
*****************

"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap

from supoptools.pyqt6 import *

from basler.camera_basler_widget import CameraBaslerParamsWidget
from ids.camera_ids_widget import CameraIdsParamsWidget

dict_of_brands = {
    'Select...': 'None',
    'Basler': CameraBaslerParamsWidget,
    'IDS': CameraIdsParamsWidget,
}


class CmosLabApp(QWidget):
    """Main interface of the CMOS sensor study labwork."""

    def __init__(self):
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()

        self.choice_widget = CameraChoice()
        self.choice_widget.selected.connect(self.action_choice)

        self.layout.addWidget(self.choice_widget)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def action_choice(self, event):
        """Action performed when a camera brand is selected."""
        print(event)
        camera_window = dict_of_brands[event]()
        camera_window.show()


class CameraChoice(QWidget):
    """Camera Choice."""

    selected = pyqtSignal(str)

    def __init__(self) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)

        self.layout = QVBoxLayout()
        self.choice_label = QLabel('Sensor Brand')
        self.choice_list = QComboBox()
        self.choice_list.currentIndexChanged.connect(self.action_choice_list)
        self.select_button = QPushButton('Select')
        self.select_button.clicked.connect(self.action_select_button)

        # create list from dict dict_of_brands
        self.choice_list.clear()
        for item, (brand, camera_widget) in enumerate(dict_of_brands.items()):
            self.choice_list.addItem(brand)

        self.layout.addWidget(self.choice_label)
        self.layout.addWidget(self.choice_list)
        self.layout.addWidget(self.select_button)
        self.select_button.setEnabled(False)
        self.setLayout(self.layout)

    def action_select_button(self, event) -> None:
        """Action performed when the 'Select' button is clicked."""
        brand_choice = self.choice_list.currentText()
        self.clearLayout(3)
        self.selected.emit(brand_choice)

    def action_choice_list(self, event) -> None:
        """Action performed when the combo 'Choice List' item is changed."""
        selected_item = self.choice_list.currentText()
        if dict_of_brands[selected_item] == 'None':
            self.select_button.setEnabled(False)
        else:
            self.select_button.setEnabled(True)

    def clearLayout(self, num: int = 1) -> None:
        """Remove widgets from layout.

        :param num: Number of elements to remove. Default: 1.
        :type num: int

        """
        # Remove the specified number of widgets from the layout
        for _ in range(num):
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication


    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("Widget Slider test")
            self.setGeometry(300, 300, 400, 600)

            self.central_widget = CmosLabApp()
            self.setCentralWidget(self.central_widget)


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
