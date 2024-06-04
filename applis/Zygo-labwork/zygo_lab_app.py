# -*- coding: utf-8 -*-
"""*zygo_lab_app.py* file.

*zygo_lab_app* file that contains :class::ZygoLabApp

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
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap

from lensepy.pyqt6.widget_image_display import WidgetImageDisplay
from gui.camera_choice_zygo import CameraChoice, dict_of_brands, cam_from_brands


class ZygoLabApp(QWidget):

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

        self.brand_choice = None
        self.cameras_list_widget = None
        self.camera = None

        self.camera_display_widget = WidgetImageDisplay()

    def action_choice(self, event):
        """Action performed when a camera brand is selected."""
        self.brand_choice = event
        if event != 'None':
            self.clearLayout(1)
            self.cameras_list_widget = dict_of_brands[event]()
            self.cameras_list_widget.connected.connect(self.action_camera_connected)
            self.layout.addWidget(self.cameras_list_widget)
            self.layout.addStretch()
        else:
            self.clearLayout(1)

    def action_camera_connected(self, event):
        """Action performed when a camera is selected."""
        print(event)
        cam_dev = self.cameras_list_widget.get_selected_camera_dev()
        self.camera = cam_from_brands[self.brand_choice](cam_dev)

    def refresh_app(self):
        """Action performed for refreshing the display of the app."""
        pass

    def clearLayout(self, num: int = 1) -> None:
        """Remove widgets from layout.

        :param num: Number of elements to remove. Default: 1.
        :type num: int

        """
        # Remove the specified number of widgets from the layout
        for idx in range(num):
            item = self.layout.takeAt(num - idx)
            if item.widget():
                item.widget().deleteLater()


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication


    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("Zygo-IDS Labwork APP")
            self.setGeometry(300, 300, 400, 600)

            self.central_widget = ZygoLabApp()
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
