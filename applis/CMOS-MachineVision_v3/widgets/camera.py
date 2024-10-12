# -*- coding: utf-8 -*-
"""*images_widget.py* file.

This file contains graphical elements to display images in a widget.
Image is coming from a file (JPG, PNG...) or an industrial camera (IDS, Basler...).

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : oct/2024
"""
import sys, os
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QGridLayout,
    QLabel, QComboBox, QPushButton,
    QSizePolicy, QSpacerItem, QMainWindow
)
from PyQt6.QtCore import Qt, pyqtSignal
from lensepy import load_dictionary, translate
from lensepy.css import *
from lensepy.images.conversion import *
from lensecam.basler.camera_basler_widget import CameraBaslerListWidget
from lensecam.basler.camera_basler import CameraBasler
from lensecam.ids.camera_ids_widget import CameraIdsListWidget
from lensecam.ids.camera_ids import CameraIds, get_bits_per_pixel
from lensecam.ids.camera_list import CameraList as CameraIdsList
from lensecam.basler.camera_list import CameraList as CameraBaslerList


cam_list_brands = {
    'Basler': CameraBaslerList,
    'IDS': CameraIdsList,
}
cam_list_widget_brands = {
    'Select...': 'None',
    'Basler': CameraBaslerListWidget,
    'IDS': CameraIdsListWidget,
}
cam_from_brands = {
    'Basler': CameraBasler,
    'IDS': CameraIds,
}


class CameraChoice(QWidget):
    """Camera Choice."""

    brand_selected = pyqtSignal(str)
    camera_selected = pyqtSignal(dict)

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        self.parent = parent
        self.layout = QGridLayout()

        self.label_camera_choice_title = QLabel(translate("label_camera_choice_title"))
        self.label_camera_choice_title.setStyleSheet(styleH1)
        self.label_camera_choice_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.brand_choice_label = QLabel(translate('brand_choice_label'))
        self.brand_choice_label.setStyleSheet(styleH2)
        self.brand_choice_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.brand_choice_list = QComboBox()
        self.brand_choice_list.currentIndexChanged.connect(self.action_brand_choice_list)
        self.brand_select_button = QPushButton(translate('brand_select_button'))
        self.brand_select_button.clicked.connect(self.action_brand_select_button)

        self.selected_label = QLabel()
        self.brand_return_button = QPushButton(translate('brand_return_button'))
        self.brand_return_button.clicked.connect(self.action_brand_return_button)

        self.brand_refresh_button = QPushButton(translate('brand_refresh_button'))
        self.brand_refresh_button.clicked.connect(self.action_brand_return_button)

        self.cam_choice_widget = QWidget()
        self.brand_choice = None
        self.selected_camera = None

        self.layout.addWidget(self.label_camera_choice_title, 0, 0)
        self.layout.addWidget(self.brand_choice_label, 1, 0)
        self.layout.addWidget(self.brand_refresh_button, 2, 0)
        self.layout.addWidget(self.brand_choice_list, 3, 0) # 3,0 choice_list
        self.layout.addWidget(self.brand_select_button, 4, 0) # 4,0 brand_select_button
        # Add a blank space at the end (spacer)
        self.spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layout.addItem(self.spacer, 5, 0)

        self.brand_select_button.setEnabled(False)
        self.setLayout(self.layout)
        self.init_brand_choice_list()
        self.action_brand_return_button(None)

    def init_brand_choice_list(self):
        """Action ..."""
        # create list from dict cam_list_widget_brands
        self.brand_choice_list.clear()
        for item, (brand, camera_widget) in enumerate(cam_list_widget_brands.items()):
            if brand != 'Select...':
                number_of_cameras = cam_list_brands[brand]().get_nb_of_cam()
                if number_of_cameras != 0:
                    text_value = f'{brand} ({number_of_cameras})'
                    self.brand_choice_list.addItem(text_value)
            else:
                self.brand_choice_list.addItem(brand)
        self.brand_choice_list.currentIndexChanged.connect(self.action_brand_choice_list)
        self.brand_select_button.setEnabled(False)
        self.brand_select_button.clicked.connect(self.action_brand_select_button)

    def action_brand_select_button(self, event) -> None:
        """Action performed when the brand_select button is clicked."""
        self.clear_layout(5, 0)
        self.clear_layout(4, 0)
        self.clear_layout(3, 0)
        self.brand_choice = self.brand_choice_list.currentText()
        self.brand_choice = self.brand_choice.split(' (')[0]
        self.selected_label = QLabel()
        self.brand_return_button = QPushButton(translate('brand_return_button'))
        self.brand_return_button.clicked.connect(self.action_brand_return_button)
        self.selected_label.setText(self.brand_choice)
        self.layout.addWidget(self.selected_label, 3, 0) # 3,0 choice_list
        self.layout.addWidget(self.brand_return_button, 4, 0) # 4,0 brand_select_button
        self.brand_refresh_button.setEnabled(False)
        self.layout.addItem(self.spacer, 5, 0)
        self.brand_selected.emit('brand:'+self.brand_choice)
        self.cam_choice_widget = cam_list_widget_brands[self.brand_choice]()
        self.cam_choice_widget.connected.connect(self.action_camera_selected)
        self.layout.addWidget(self.cam_choice_widget, 5, 0)

    def action_camera_selected(self, event):
        selected_camera = self.cam_choice_widget.get_selected_camera_index()
        self.brand_return_button.setEnabled(False)
        dict_brand = {'brand': self.brand_choice, 'cam_dev': selected_camera}
        self.camera_selected.emit(dict_brand)

    def action_brand_return_button(self, event) -> None:
        """Action performed when the brand_return button is clicked."""
        try:
            self.clear_layout(6, 0)
            self.clear_layout(5, 0)
            self.clear_layout(4, 0)
            self.clear_layout(3, 0)
            # create list from dict cam_list_widget_brands
            self.brand_choice_list = QComboBox()
            self.brand_choice_list.clear()
            for item, (brand, camera_widget) in enumerate(cam_list_widget_brands.items()):
                if brand != 'Select...':
                    number_of_cameras = cam_list_brands[brand]().get_nb_of_cam()
                    if number_of_cameras != 0:
                        text_value = f'{brand} ({number_of_cameras})'
                        self.brand_choice_list.addItem(text_value)
                else:
                    self.brand_choice_list.addItem(brand)
            self.layout.addWidget(self.brand_choice_list)
            self.brand_choice_list.currentIndexChanged.connect(self.action_brand_choice_list)
            self.brand_select_button = QPushButton(translate('brand_select_button'))
            self.brand_select_button.clicked.connect(self.action_brand_select_button)
            self.brand_select_button.setEnabled(False)
            self.layout.addWidget(self.brand_choice_list, 3, 0)
            self.layout.addWidget(self.brand_select_button, 4, 0)
            self.layout.addItem(self.spacer, 5, 0)
            self.brand_refresh_button.setEnabled(True)
            self.brand_selected.emit('nobrand:')
        except Exception as e:
            print(f'Exception - action_brand_return {e}')

    def action_brand_choice_list(self, event) -> None:
        """Action performed when the combo 'Choice List' item is changed."""
        try:
            selected_item = self.brand_choice_list.currentText()
            selected_item = selected_item.split(' (')[0]
            if cam_list_widget_brands[selected_item] == 'None':
                self.brand_select_button.setEnabled(False)
            else:
                self.brand_select_button.setEnabled(True)
        except Exception as e:
            print(f'Exception - list {e}')

    def clear_layout(self, row: int, column: int) -> None:
        """Remove widgets from a specific position in the layout.

        :param row: Row index of the layout.
        :type row: int
        :param column: Column index of the layout.
        :type column: int

        """
        item = self.layout.itemAtPosition(row, column)
        if item is not None:
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.layout.removeItem(item)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = CameraChoice(self)
            self.setCentralWidget(self.central_widget)

    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())