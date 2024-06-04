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
    QVBoxLayout,
    QLabel, QComboBox, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from lensecam.basler.camera_basler_widget import CameraBaslerListWidget
from lensecam.basler.camera_basler import CameraBasler
from lensecam.ids.camera_ids_widget import CameraIdsListWidget
from lensecam.ids.camera_ids import CameraIds


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
        self.return_button = QPushButton('Back to Brand selection')
        self.return_button.clicked.connect(self.action_return_button)

        # create list from dict dict_of_brands
        self.brand_choice_list.clear()
        for item, (brand, camera_widget) in enumerate(dict_of_brands.items()):
            self.brand_choice_list.addItem(brand)

        self.layout.addWidget(self.label_camera_choice_title)
        self.layout.addWidget(self.brand_choice_label)
        self.layout.addWidget(self.brand_choice_list)
        self.layout.addWidget(self.brand_select_button)
        self.layout.addStretch()
        self.brand_select_button.setEnabled(False)
        self.setLayout(self.layout)

    def action_brand_select_button(self, event) -> None:
        """Action performed when the 'Select' button is clicked."""
        brand_choice = self.brand_choice_list.currentText()
        self.clearLayout(3)
        self.selected_label = QLabel()
        self.return_button = QPushButton('Back to Brand selection')
        self.return_button.clicked.connect(self.action_return_button)
        self.selected_label.setText(brand_choice)
        self.layout.addWidget(self.selected_label)
        self.layout.addWidget(self.return_button)
        self.layout.addStretch()

        self.selected.emit(brand_choice)

    def action_return_button(self, event) -> None:
        """Action performed when the 'Back to Brand' button is clicked."""
        self.clearLayout(3)
        self.brand_choice_list = QComboBox()
        # create list from dict dict_of_brands
        self.brand_choice_list.clear()
        for item, (brand, camera_widget) in enumerate(dict_of_brands.items()):
            self.brand_choice_list.addItem(brand)
        self.layout.addWidget(self.brand_choice_list)
        self.brand_choice_list.currentIndexChanged.connect(self.action_brand_choice_list)
        self.brand_select_button = QPushButton('Select')
        self.brand_select_button.clicked.connect(self.action_brand_select_button)
        self.brand_select_button.setEnabled(False)
        self.layout.addWidget(self.brand_select_button)
        self.layout.addStretch()
        self.selected.emit('None')

    def action_brand_choice_list(self, event) -> None:
        """Action performed when the combo 'Choice List' item is changed."""
        selected_item = self.brand_choice_list.currentText()
        if dict_of_brands[selected_item] == 'None':
            self.brand_select_button.setEnabled(False)
        else:
            self.brand_select_button.setEnabled(True)

    def action_camera_select(self, event) -> None:
        print('Camera')

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
