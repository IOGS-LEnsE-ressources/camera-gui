# -*- coding: utf-8 -*-
"""*camera_choice.py* file.

*camera_choice* file that contains :class::CameraChoice

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>
"""

from lensepy import load_dictionary, translate
from lensepy.css import *

# %% To add in lensepy librairy
# Styles
# ------
styleH2 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

from PyQt6.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel, QComboBox, QPushButton,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from lensecam.basler.camera_basler_widget import CameraBaslerListWidget
from lensecam.basler.camera_basler import CameraBasler
from lensecam.ids.camera_ids_widget import CameraIdsListWidget
from lensecam.ids.camera_ids import CameraIds
from lensecam.ids.camera_list import CameraList as CameraIdsList
from lensecam.basler.camera_list import CameraList as CameraBaslerList


cam_list_brands = {
    'Basler': CameraBaslerList,
    'IDS': CameraIdsList,
}
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

        self.layout.addWidget(self.label_camera_choice_title, 0, 0)
        self.layout.addWidget(self.brand_choice_label, 1, 0)
        self.layout.addWidget(self.brand_refresh_button, 2, 0)
        self.layout.addWidget(self.brand_choice_list, 3, 0)
        self.layout.addWidget(self.brand_select_button, 4, 0)
        # Add a blank space at the end (spacer)
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layout.addItem(spacer, 5, 0)

        self.brand_select_button.setEnabled(False)
        self.setLayout(self.layout)
        self.init_brand_choice_list()

    def init_brand_choice_list(self):
        """Action ..."""
        # create list from dict dict_of_brands
        self.brand_choice_list.clear()
        for item, (brand, camera_widget) in enumerate(dict_of_brands.items()):
            if brand != 'Select...':
                number_of_cameras = cam_list_brands[brand]().get_nb_of_cam()
                if number_of_cameras != 0:
                    text_value = f'{brand}-{number_of_cameras}'
                    self.brand_choice_list.addItem(text_value)
            else:
                self.brand_choice_list.addItem(brand)
        self.brand_choice_list.currentIndexChanged.connect(self.action_brand_choice_list)
        self.brand_select_button.clicked.connect(self.action_brand_select_button)
        self.brand_select_button.setEnabled(False)

    def action_brand_select_button(self, event) -> None:
        """Action performed when the brand_select button is clicked."""
        brand_choice = self.brand_choice_list.currentText()
        brand_choice = brand_choice.split('-')[0]
        self.clear_layout(3, 0)
        self.clear_layout(4, 0)
        self.selected_label = QLabel()
        self.brand_return_button = QPushButton(translate('brand_return_button'))
        self.brand_return_button.clicked.connect(self.action_brand_return_button)
        self.selected_label.setText(brand_choice)
        self.layout.addWidget(self.selected_label, 3, 0)
        self.layout.addWidget(self.brand_return_button, 4, 0)
        self.layout.addStretch()
        # self.camera dict_of_brands
        self.layout.addStretch()

        self.selected.emit(brand_choice)

    def action_brand_return_button(self, event) -> None:
        """Action performed when the brand_return button is clicked."""
        try:
            self.clear_layout(3, 0)
            self.clear_layout(4, 0)
            # create list from dict dict_of_brands
            self.brand_choice_list = QComboBox()
            self.brand_choice_list.clear()
            for item, (brand, camera_widget) in enumerate(dict_of_brands.items()):
                if brand != 'Select...':
                    number_of_cameras = cam_list_brands[brand]().get_nb_of_cam()
                    if number_of_cameras != 0:
                        text_value = f'{brand}-{number_of_cameras}'
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
            self.selected.emit('None')
        except Exception as e:
            print(f'Exception - action_brand_return {e}')

    def action_brand_choice_list(self, event) -> None:
        """Action performed when the combo 'Choice List' item is changed."""
        try:
            selected_item = self.brand_choice_list.currentText()
            selected_item = selected_item.split('-')[0]
            if dict_of_brands[selected_item] == 'None':
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


# -------------------------------
# Launching as main for tests
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow

    class MainWindow(QMainWindow):
        """
        Our main window.

        Args:
            QMainWindow (class): QMainWindow can contain several widgets.
        """

        def __init__(self):
            """
            Initialisation of the main Window.
            """
            super().__init__()
            # Define Window title
            self.setWindowTitle("LEnsE - Test")
            # Main Widget
            self.main_widget = CameraChoice()
            self.setCentralWidget(self.main_widget)

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
