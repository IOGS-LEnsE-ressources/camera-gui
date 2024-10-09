# -*- coding: utf-8 -*-
"""*main_menu_widget.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from lensepy import load_dictionary, translate
from lensepy.css import *

if __name__ == '__main__':
    from slider_bloc import SliderBloc
else:
    from gui.slider_bloc import SliderBloc

# %% Widget
class MainMenuWidget(QWidget):

    menu_clicked = pyqtSignal(str)
    settings_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.aoi_selected = False

        self.label_title_main_menu = QLabel(translate("label_title_main_menu"))
        self.label_title_main_menu.setStyleSheet(styleH1)
        self.label_title_main_menu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.button_camera_settings_main_menu = QPushButton(translate("button_camera_settings_main_menu"))
        self.button_camera_settings_main_menu.setStyleSheet(unactived_button)
        self.button_camera_settings_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_camera_settings_main_menu.clicked.connect(self.main_menu_is_clicked)
        
        self.button_aoi_main_menu = QPushButton(translate("button_aoi_main_menu"))
        self.button_aoi_main_menu.setStyleSheet(unactived_button)
        self.button_aoi_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_aoi_main_menu.clicked.connect(self.main_menu_is_clicked)
        
        self.button_histo_analysis_main_menu = QPushButton(translate("button_histo_analysis_main_menu"))
        self.button_histo_analysis_main_menu.setStyleSheet(disabled_button)
        self.button_histo_analysis_main_menu.setEnabled(False)
        self.button_histo_analysis_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_histo_analysis_main_menu.clicked.connect(self.main_menu_is_clicked)

        self.button_preprocessing_main_menu = QPushButton(translate(
            "button_preprocessing_main_menu"))
        self.button_preprocessing_main_menu.setStyleSheet(disabled_button)
        self.button_preprocessing_main_menu.setEnabled(False)
        self.button_preprocessing_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_preprocessing_main_menu.clicked.connect(self.main_menu_is_clicked)

        self.button_filter_analysis_main_menu = QPushButton(translate("button_filter_analysis_main_menu"))
        self.button_filter_analysis_main_menu.setStyleSheet(disabled_button)
        self.button_filter_analysis_main_menu.setEnabled(False)
        self.button_filter_analysis_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_filter_analysis_main_menu.clicked.connect(self.main_menu_is_clicked)

        self.button_edge_analysis_main_menu = QPushButton(translate("button_edge_analysis_main_menu"))
        self.button_edge_analysis_main_menu.setStyleSheet(disabled_button)
        self.button_edge_analysis_main_menu.setEnabled(False)
        self.button_edge_analysis_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_edge_analysis_main_menu.clicked.connect(self.main_menu_is_clicked)

        self.button_segmentation_main_menu = QPushButton(translate("button_segmentation_main_menu"))
        self.button_segmentation_main_menu.setStyleSheet(disabled_button)
        self.button_segmentation_main_menu.setEnabled(False)
        self.button_segmentation_main_menu.setFixedHeight(BUTTON_HEIGHT)
        self.button_segmentation_main_menu.clicked.connect(self.main_menu_is_clicked)

        self.button_options_main_menu = QPushButton(translate("button_options_main_menu"))
        self.button_options_main_menu.setStyleSheet(unactived_button)
        self.button_options_main_menu.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        self.button_options_main_menu.clicked.connect(self.button_options_main_menu_isClicked)

        self.camera_params = MiniParamsWidget(parent=self)
        self.camera_params.settings_changed.connect(self.update_parameters)

        self.layout.addWidget(self.label_title_main_menu)
        self.layout.addWidget(self.button_camera_settings_main_menu)
        self.layout.addWidget(self.button_aoi_main_menu)
        self.layout.addStretch()
        self.layout.addWidget(self.button_histo_analysis_main_menu)
        self.layout.addStretch()
        self.layout.addWidget(self.button_preprocessing_main_menu)
        self.layout.addWidget(self.button_filter_analysis_main_menu)
        self.layout.addWidget(self.button_edge_analysis_main_menu)
        self.layout.addStretch()
        self.layout.addWidget(self.button_segmentation_main_menu)
        self.layout.addStretch()
        self.layout.addWidget(self.camera_params)
        self.layout.addStretch()
        self.layout.addWidget(self.button_options_main_menu)
        self.setLayout(self.layout)

    def update_parameters(self):
        """Update camera settings (exposure time, black_level and size)"""
        self.camera_params.set_parameters(self.parent.camera)
        self.settings_changed.emit('main_menu_changed')

    def set_parameters_enable(self, value):
        """Display the parameters in the menu section (if True)"""
        if value:
            self.camera_params.set_enabled()
        else:
            self.camera_params.set_disabled()


    def unactive_buttons(self):
        """ Switches all buttons to inactive style """
        self.camera_params.set_enabled()
        self.button_camera_settings_main_menu.setStyleSheet(unactived_button)
        self.button_aoi_main_menu.setStyleSheet(unactived_button)
        if self.aoi_selected:
            self.button_histo_analysis_main_menu.setStyleSheet(unactived_button)
            self.button_preprocessing_main_menu.setStyleSheet(unactived_button)
            self.button_filter_analysis_main_menu.setStyleSheet(unactived_button)
            self.button_segmentation_main_menu.setStyleSheet(unactived_button)
            self.button_edge_analysis_main_menu.setStyleSheet(unactived_button)
        self.button_options_main_menu.setStyleSheet(unactived_button)

    def main_menu_is_clicked(self):
        self.unactive_buttons()
        sender = self.sender()
        if sender == self.button_camera_settings_main_menu:
            # Change style
            sender.setStyleSheet(actived_button)
            self.camera_params.set_disabled()
            # Action
            self.menu_clicked.emit('camera_settings')
        elif sender == self.button_preprocessing_main_menu:
            # Change style
            sender.setStyleSheet(actived_button)
            # Action
            self.menu_clicked.emit('pre_processing')
        elif sender == self.button_aoi_main_menu:
            self.unactive_buttons()
            self.aoi_selected = True
            sender.setStyleSheet(actived_button)
            self.button_histo_analysis_main_menu.setStyleSheet(unactived_button)
            self.button_histo_analysis_main_menu.setEnabled(True)
            self.button_preprocessing_main_menu.setStyleSheet(unactived_button)
            self.button_preprocessing_main_menu.setEnabled(True)
            self.button_filter_analysis_main_menu.setStyleSheet(unactived_button)
            self.button_filter_analysis_main_menu.setEnabled(True)
            self.button_edge_analysis_main_menu.setStyleSheet(unactived_button)
            self.button_edge_analysis_main_menu.setEnabled(True)
            self.button_segmentation_main_menu.setStyleSheet(unactived_button)
            self.button_segmentation_main_menu.setEnabled(True)
            # Action
            self.menu_clicked.emit('aoi')
        elif sender == self.button_histo_analysis_main_menu:
            self.unactive_buttons()
            sender.setStyleSheet(actived_button)
            # Action
            self.menu_clicked.emit('histo')
        elif sender == self.button_edge_analysis_main_menu:
            self.unactive_buttons()
            sender.setStyleSheet(actived_button)
            # Action
            self.menu_clicked.emit('edge')
        elif sender == self.button_filter_analysis_main_menu:
            self.unactive_buttons()
            sender.setStyleSheet(actived_button)
            # Action
            self.menu_clicked.emit('filter')
        elif sender == self.button_segmentation_main_menu:
            self.unactive_buttons()
            sender.setStyleSheet(actived_button)
            # Action
            self.menu_clicked.emit('segmentation')

        
    def button_options_main_menu_isClicked(self):
        # Change style
        self.unactive_buttons()
        self.button_options_main_menu.setStyleSheet(actived_button)
        
        # Action
        self.menu_clicked.emit('options')


class MiniParamsWidget(QWidget):

    settings_changed = pyqtSignal(str)

    def __init__(self, parent):
        """

        """
        super().__init__(parent=parent)
        self.parent = parent
        self.layout = QGridLayout()

        self.slider_exposure = SliderBloc('Exposure Time', 'ms', 0, 100)
        self.slider_exposure.set_enabled(False)
        self.slider_exposure.slider_changed.connect(self.action_slider_changing)
        self.slider_exposure_enabling = QCheckBox(parent=self)
        self.slider_exposure_enabling.clicked.connect(self.action_enabling)
        self.layout.addWidget(self.slider_exposure, 0, 0)
        self.layout.addWidget(self.slider_exposure_enabling, 0, 1)

        self.setLayout(self.layout)

    def set_parameters(self, camera):
        """ Update displayed parameters from the sensor."""
        exposure = round(camera.get_exposure() / 1000, 2)
        self.slider_exposure.set_value(exposure)

    def action_enabling(self):
        if self.slider_exposure_enabling.isChecked():
            self.slider_exposure.set_enabled(True)
            min_val, max_val = self.parent.parent.camera.get_exposure_range()
            if self.parent.parent.brand == "Basler":
                if max_val > 400000:
                    max_val = 400000
            self.slider_exposure.set_min_max_slider_values(round(min_val/1000, 1), round(max_val/1000, 1))
            self.settings_changed.emit('changed')
        else:
            self.slider_exposure.set_enabled(False)

    def action_slider_changing(self):
        value = self.slider_exposure.get_value() * 1000
        self.parent.parent.camera.set_exposure(value)
        self.settings_changed.emit('changed')

    def set_enabled(self):
        self.slider_exposure_enabling.setEnabled(True)
        if self.slider_exposure_enabling.isChecked():
            self.slider_exposure.set_enabled(True)

    def set_disabled(self):
        self.slider_exposure.set_enabled(False)
        self.slider_exposure_enabling.setEnabled(False)


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
