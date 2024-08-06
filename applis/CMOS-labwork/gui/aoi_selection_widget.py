# -*- coding: utf-8 -*-
"""*aoi_selection_widget.py* file.

This file is attached to a 2nd year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-Detection.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>

"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLineEdit,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)

if __name__ == '__main__':
    from slider_bloc import SliderBloc
else:
    from gui.slider_bloc import SliderBloc

from lensepy import load_dictionary, translate
from lensepy.css import *
from lensecam.ids.camera_ids import CameraIds

# %% To add in lensepy librairy
# Styles
# ------
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

# %% Params
BUTTON_HEIGHT = 60  # px
OPTIONS_BUTTON_HEIGHT = 20  # px


# %% Widget
class AoiSelectionWidget(QWidget):
    def __init__(self, parent):
        """

        """
        super().__init__(parent=None)
        self.layout = QVBoxLayout()
        self.x_pos = 0
        self.y_pos = 0
        self.width = 200
        self.height = 200
        self.parent = parent

        # Title
        # -----
        self.label_title_aoi_selection = QLabel(translate('title_aoi_selection'))
        self.label_title_aoi_selection.setStyleSheet(styleH1)

        # X position
        self.x_position_widget = QWidget()
        self.x_position_sublayout = QHBoxLayout()
        self.x_position_label = QLabel('X position (pixel) = ')
        self.x_position_label.setStyleSheet(styleH2)
        self.x_position_value = QLineEdit()
        self.x_position_value.setText(str(self.x_pos))
        self.x_position_value.editingFinished.connect(self.xy_position_changing)
        self.x_position_sublayout.addWidget(self.x_position_label)
        self.x_position_sublayout.addWidget(self.x_position_value)
        self.x_position_widget.setLayout(self.x_position_sublayout)

        # Y position
        self.y_position_widget = QWidget()
        self.y_position_sublayout = QHBoxLayout()
        self.y_position_label = QLabel('Y position (pixel) = ')
        self.y_position_label.setStyleSheet(styleH2)
        self.y_position_value = QLineEdit()
        self.y_position_value.setText(str(self.y_pos))
        self.y_position_value.editingFinished.connect(self.xy_position_changing)
        self.y_position_sublayout.addWidget(self.y_position_label)
        self.y_position_sublayout.addWidget(self.y_position_value)
        self.y_position_widget.setLayout(self.y_position_sublayout)

        # Width
        self.width_widget = QWidget()
        self.width_sublayout = QHBoxLayout()
        self.width_label = QLabel('Width (pixel) = ')
        self.width_label.setStyleSheet(styleH2)
        self.width_value = QLineEdit()
        self.width_value.setText(str(self.width))
        self.width_value.editingFinished.connect(self.size_changing)
        self.width_sublayout.addWidget(self.width_label)
        self.width_sublayout.addWidget(self.width_value)
        self.width_widget.setLayout(self.width_sublayout)

        # Height
        self.height_widget = QWidget()
        self.height_sublayout = QHBoxLayout()
        self.height_label = QLabel('Height (pixel) = ')
        self.height_label.setStyleSheet(styleH2)
        self.height_value = QLineEdit()
        self.height_value.setText(str(self.height))
        self.height_value.editingFinished.connect(self.size_changing)
        self.height_sublayout.addWidget(self.height_label)
        self.height_sublayout.addWidget(self.height_value)
        self.height_widget.setLayout(self.height_sublayout)

        self.layout.addWidget(self.label_title_aoi_selection)
        self.layout.addWidget(self.x_position_widget)
        self.layout.addWidget(self.y_position_widget)
        self.layout.addWidget(self.width_widget)
        self.layout.addWidget(self.height_widget)

        self.layout.addStretch()
        self.setLayout(self.layout)

    def xy_position_changing(self):
        x_max, y_max = self.parent.camera.get_sensor_size()
        # Verify if X and Y position are OK ! (good range of the image)
        if 0 <= int(self.x_position_value.text()) <= x_max:
            self.x_pos = int(self.x_position_value.text())
            # Test size ! and resize if necessary !!
        else:
            self.x_position_value.setText(str(self.x_pos))
            warn = QMessageBox.warning(self, 'Value Error', 'This value is out of range !')
        if 0 <= int(self.y_position_value.text()) <= x_max:
            self.y_pos = int(self.y_position_value.text())
            # Test size ! and resize if necessary !!
        else:
            self.y_position_value.setText(str(self.y_pos))
            warn = QMessageBox.warning(self, 'Value Error', 'This value is out of range !')

    def size_changing(self):
        x_max, y_max = self.parent.camera.get_sensor_size()
        # Verify if X+width and Y+height are OK ! (good range of the image)


# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication


    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Translation
            dictionary = {}
            # Load French dictionary
            # dictionary = load_dictionary('../lang/dict_FR.txt')
            # Load English dictionary
            dictionary = load_dictionary('../lang/dict_EN.txt')

            self.setWindowTitle(translate("window_title_camera_settings"))
            self.setGeometry(300, 300, 400, 600)

            self.central_widget = AoiSelectionWidget()
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