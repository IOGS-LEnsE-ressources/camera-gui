# -*- coding: utf-8 -*-
"""*camera_choice.py* file.

*camera_choice* file that contains :class::CameraChoice

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel, QComboBox, QPushButton
)
from PyQt6.QtCore import pyqtSignal

from basler.camera_basler_widget import CameraBaslerListWidget
from basler.camera_basler import CameraBasler
from ids.camera_ids_widget import CameraIdsListWidget
from ids.camera_ids import CameraIds


dict_of_brands = {
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

        self.selected_label = QLabel()
        self.return_button = QPushButton('Back to Brand selection')
        self.return_button.clicked.connect(self.action_return_button)

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
        self.clearLayout(2)
        self.selected_label = QLabel()
        self.return_button = QPushButton('Back to Brand selection')
        self.return_button.clicked.connect(self.action_return_button)
        self.selected_label.setText(brand_choice)
        self.layout.addWidget(self.selected_label)
        self.layout.addWidget(self.return_button)
        self.selected.emit(brand_choice)

    def action_return_button(self, event) -> None:
        """Action performed when the 'Back to Brand' button is clicked."""
        self.clearLayout(2)
        self.choice_list = QComboBox()
        # create list from dict dict_of_brands
        self.choice_list.clear()
        for item, (brand, camera_widget) in enumerate(dict_of_brands.items()):
            self.choice_list.addItem(brand)
        self.layout.addWidget(self.choice_list)
        self.choice_list.currentIndexChanged.connect(self.action_choice_list)
        self.select_button = QPushButton('Select')
        self.select_button.clicked.connect(self.action_select_button)
        self.select_button.setEnabled(False)
        self.layout.addWidget(self.select_button)
        self.selected.emit('None')

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
        for idx in range(num):
            item = self.layout.takeAt(num-idx)
            if item.widget():
                item.widget().deleteLater()
