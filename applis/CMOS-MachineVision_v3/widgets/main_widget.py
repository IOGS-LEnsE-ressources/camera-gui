# -*- coding: utf-8 -*-
"""*main_widget.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
"""
import sys, os
import numpy as np
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QPushButton, QCheckBox,
    QMessageBox, QSizePolicy
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from lensepy import load_dictionary, translate, dictionary
from lensepy.pyqt6.widget_image_histogram import *
from lensepy.css import *
from lensepy.images import *
from lensepy.pyqt6.widget_slider import *
from widgets.camera import *
from widgets.images_widget import *
from widgets.histo_widget import *
from widgets.aoi_select_widget import *
from widgets.quant_samp_widget import *
from widgets.pre_processing_widget import *
from widgets.filters_widget import *

BOT_HEIGHT, TOP_HEIGHT = 45, 50
LEFT_WIDTH, RIGHT_WIDTH = 45, 45
TOP_LEFT_ROW, TOP_LEFT_COL = 1, 1
TOP_RIGHT_ROW, TOP_RIGHT_COL = 1, 2
BOT_LEFT_ROW, BOT_LEFT_COL = 2, 1
BOT_RIGHT_ROW, BOT_RIGHT_COL = 2, 2
SUBMENU_ROW, SUBMENU_COL = 0, 0
OPTIONS_ROW, OPTIONS_COL = 0, 1

# Other functions
def load_menu(file_path: str, menu):
    """
    Load parameter from a CSV file.
    """
    if os.path.exists(file_path):
        # Read the CSV file, ignoring lines starting with '//'
        data = np.genfromtxt(file_path, delimiter=';', dtype=str, comments='#', encoding='UTF-8')
        # Populate the dictionary with key-value pairs from the CSV file
        for element, title, signal, _ in data:
            if element == 'B':     # button
                menu.add_button(translate(title), signal)
            elif element == 'O':     # options button
                menu.add_button(translate(title), signal, option=True)
            elif element == 'L':   # label title
                menu.add_label_title(translate(title))
            elif element == 'S':   # blank space
                menu.add_space()
        menu.display_layout()
    else:
        print('MENU File error')

def load_default_parameters() -> dict:
    """
    Load parameter from a CSV file.

    :return: Dict containing 'key_1': 'language_word_1'.

    Notes
    -----
    This function reads a CSV file that contains key-value pairs separated by semicolons (';')
    and stores them in a global dictionary variable. The CSV file may contain comments
    prefixed by '#', which will be ignored.

    The file should have the following format:
        # comment
        # comment
        key_1 ; language_word_1
        key_2 ; language_word_2
    """
    dictionary_loaded = {}
    if os.path.exists('./config/default_config.txt'):
        # Read the CSV file, ignoring lines starting with '//'
        data = np.genfromtxt('./config/default_config.txt', delimiter=';',
                             dtype=str, comments='#', encoding='UTF-8')
        # Populate the dictionary with key-value pairs from the CSV file
        for key, value in data:
            dictionary_loaded[key.strip()] = value.strip()
        return dictionary_loaded
    else:
        print('File error')
        return {}

def load_default_dictionary(language: str) -> bool:
    """Initialize default dictionary from default_config.txt file"""
    file_name_dict = f'./lang/dict_{language}.txt'
    load_dictionary(file_name_dict)


class ExpoSliderWidget(QWidget):
    """
    Slider for exposure time.
    """

    expo_changed = pyqtSignal(str)

    def __init__(self, parent=None, title: str='expo_slider'):
        """
        Default Constructor.
        :param parent: Parent widget of the menu widget.
        :param title: Title of the menu.
        """
        super().__init__(parent=parent)
        self.enabled = False
        # Layout and graphical elements
        self.layout = QHBoxLayout()

        self.check_expo = QCheckBox()
        self.expo_slider = SliderBloc(name=translate('expo_slider'), unit=' ms',
                                      min_value=0, max_value=1)
        self.layout.addWidget(self.expo_slider)
        self.layout.addWidget(self.check_expo)
        self.setLayout(self.layout)
        self.check_expo.stateChanged.connect(self.action_check_changed)
        self.expo_slider.slider_changed.connect(self.action_slider_changed)
        self.__set_enabled(False)

    def set_min_max_values(self, min_value, max_value):
        """Set the minimum and the maximum values of the slider."""
        self.expo_slider.set_min_max_slider_values(min_value, max_value)

    def is_expo_checked(self):
        """Return if the exposure slider is enabled."""
        return self.check_expo.isChecked()

    def __set_enabled(self, value: bool=False):
        """Set enabled the widget."""
        self.enabled = value
        self.expo_slider.set_enabled(self.enabled)

    def set_checkable(self, value: bool=False):
        """Set checkable the widget."""
        self.check_expo.setEnabled(value)

    def action_check_changed(self):
        """Action performed when the expo slider is checked."""
        self.enabled = not self.enabled
        self.__set_enabled(self.enabled)
        print('slider_expo_changed')

    def action_slider_changed(self):
        """Action performed when the expo slider changed."""
        self.expo_changed.emit('slider')
        print('slider_expo_changed')

    def get_value(self):
        """Return the value of the slider."""
        return self.expo_slider.get_value()

    def set_value(self, value: float):
        """
        Return the value of the slider.
        :param value: Value of the exposure time to set.
        """
        self.expo_slider.set_value(value)

# %% Widgets
class MenuWidget(QWidget):
    """
    Main menu of the application
    """

    menu_clicked = pyqtSignal(str)

    def __init__(self, parent=None, title: str='label_title_main_menu', sub: bool=False):
        """
        Default Constructor.
        :param parent: Parent widget of the menu widget.
        :param title: Title of the menu.
        :param sub: True if it is a submenu.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.submenu = sub
        self.title = title
        # Layout and graphical elements
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.buttons_list = []
        self.buttons_signal = []
        self.buttons_enabled = []
        self.zoom_widget = AoiZoomOptionsWidget(self)
        self.expo_widget = ExpoSliderWidget(title=translate('expo_slider'))
        self.actual_button = None

    def display_layout(self):
        """
        Update the layout with all the elements.
        """
        for i, element in enumerate(self.buttons_list):
            if element is not None:
                self.layout.addWidget(element)
            else:
                self.layout.addStretch()
        if self.parent.parent.aoi is not None:
            self.layout.addWidget(self.zoom_widget)
            self.zoom_widget.zoom_changed.connect(self.action_zoom_changed)
        if self.submenu is False:
            self.layout.addWidget(self.expo_widget)

    def add_button(self, title: str, signal: str=None, option: bool=False):
        """
        Add a button into the interface.
        :param title: Title of the button.
        :param signal: Signal triggered by the button.
        :param option: True if the button is an option button (smaller height).
        :return:
        """
        button = QPushButton(translate(title))
        button.setStyleSheet(unactived_button)
        if option:
            button.setFixedHeight(OPTIONS_BUTTON_HEIGHT)
        else:
            button.setFixedHeight(BUTTON_HEIGHT)
        button.clicked.connect(self.menu_is_clicked)
        self.buttons_list.append(button)
        self.buttons_signal.append(signal)
        self.buttons_enabled.append(True)

    def inactive_buttons(self):
        """ Switches all buttons to inactive style """
        for i, element in enumerate(self.buttons_list):
            if element is not None:
                if self.buttons_enabled[i]:
                    element.setStyleSheet(unactived_button)

    def set_button_enabled(self, button_index: int, value: bool):
        """
        Set a button enabled.
        :param button_index: Index of the button to update.
        :param value: True if the button must be enabled.
        """
        self.buttons_enabled[button_index-1] = value
        self.buttons_list[button_index-1].setEnabled(value)
        if value:
            self.buttons_list[button_index-1].setStyleSheet(unactived_button)
        else:
            self.buttons_list[button_index-1].setStyleSheet(disabled_button)

    def add_label_title(self, title):
        """
        Add a space in the menu.
        :param title: Title of the label.
        """
        label = QLabel(title)
        label.setStyleSheet(styleH1)
        self.buttons_list.append(label)
        self.buttons_signal.append(None)
        self.buttons_enabled.append(True)

    def add_space(self):
        """
        Add a space in the menu.
        """
        self.buttons_list.append(None)
        self.buttons_signal.append(None)
        self.buttons_enabled.append(True)

    def menu_is_clicked(self):
        self.inactive_buttons()
        sender = self.sender()
        self.actual_button = sender

        for i, element in enumerate(self.buttons_list):
            if sender == element:
                if self.submenu is False:
                    # Update Sub Menu
                    self.parent.submenu_widget = MenuWidget(self.parent,
                                                            title=f'sub_menu_{self.buttons_signal[i]}',
                                                            sub=True)
                    self.parent.submenu_widget.menu_clicked.connect(self.submenu_is_clicked)
                    file_name = f'./config/{self.buttons_signal[i]}_menu.txt'
                    load_menu(file_name, self.parent.submenu_widget)
                    self.parent.set_sub_menu_widget(self.parent.submenu_widget)
                    self.parent.submenu_widget.display_layout()
                # Change button style
                if self.buttons_enabled[i] is True and sender is not None:
                    sender.setStyleSheet(actived_button)
                # Send signal
                self.menu_clicked.emit(self.buttons_signal[i])
            else:
                if element is not None:
                    if self.buttons_enabled[i] is True:
                        element.setStyleSheet(unactived_button)
                    else:
                        element.setStyleSheet(disabled_button)

    def update_menu_display(self):
        """Update the menu."""
        for i, element in enumerate(self.buttons_list):
            if element is not None:
                if self.actual_button == element:
                    element.setStyleSheet(actived_button)
                    element.setEnabled(True)
                elif self.buttons_enabled[i] is True:
                    element.setStyleSheet(unactived_button)
                    element.setEnabled(True)
                else:
                    element.setStyleSheet(disabled_button)
                    element.setEnabled(False)

    def set_enabled(self, index: int, value:bool=True):
        """
        Set enabled a button.
        :param index:
        :param value:
        """
        menu = self.parent.get_list_menu('off_menu')
        if isinstance(index, list):
            for i in index:
                if i not in menu:
                    self.buttons_enabled[i-1] = value
                else:
                    self.buttons_enabled[i - 1] = False
        else:
            if index not in menu:
                self.buttons_enabled[index - 1] = value
            else:
                self.buttons_enabled[index - 1] = False
        self.update_menu_display()

    def submenu_is_clicked(self, event):
        self.menu_clicked.emit(event)

    def action_zoom_changed(self, event):
        self.zoom_factor = self.zoom_widget.get_zoom()
        print(f'Zoom {self.zoom_factor}')

    def set_expo_enabled(self, value: bool):
        self.expo_widget.set_enabled(value)

    def get_expo_value(self):
        """Return the exposure time value from the slider."""
        return self.expo_widget.expo_slider.get_value()

class TitleWidget(QWidget):
    """
    Widget containing the title of the application and the LEnsE logo.
    """
    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent widget of the title widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.layout = QGridLayout()

        self.label_title = QLabel(translate('label_title'))
        self.label_title.setStyleSheet(styleH1)
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_subtitle = QLabel(translate('label_subtitle'))
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

class MainWidget(QWidget):
    """
    Main central widget of the application.
    """

    main_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent window of the main widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.mode = None
        self.submode = None
        # Parameters
        self.zoom_factor = 1
        # Read default parameters
        self.default_parameters = load_default_parameters()
        if 'language' in self.default_parameters:
            load_default_dictionary(self.default_parameters['language'])
        # GUI Structure
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.title_label = TitleWidget(self)
        self.main_menu = MenuWidget(self)
        self.top_left_widget = ImagesDisplayWidget(self)
        self.top_right_widget = QWidget()
        self.bot_right_widget = QWidget()
        # Submenu and option widgets in the bottom left corner of the GUI
        self.bot_left_widget = QWidget()
        self.bot_left_layout = QGridLayout()
        self.bot_left_widget.setLayout(self.bot_left_layout)
        self.bot_left_layout.setColumnStretch(0, 50)
        self.bot_left_layout.setColumnStretch(1, 50)
        self.submenu_widget = QWidget()
        self.options_widget = QWidget()

        # Adding actions
        self.main_menu.menu_clicked.connect(self.menu_action)
        self.main_menu.expo_widget.expo_changed.connect(self.action_expo_changed)

        # Fixing sizes
        width = self.parent.width()
        height = self.parent.height()
        self.layout.setColumnStretch(0, 10)
        self.layout.setColumnStretch(1, LEFT_WIDTH)
        self.layout.setColumnStretch(2, RIGHT_WIDTH)
        self.layout.setRowStretch(0, 5)
        self.layout.setRowStretch(1, TOP_HEIGHT)
        self.layout.setRowStretch(2, BOT_HEIGHT)

        # Adding elements in the layout
        self.layout.addWidget(self.title_label, 0, 0, 1, 3)
        self.layout.addWidget(self.main_menu, 1, 0, 2, 1)
        self.bot_left_layout.addWidget(self.submenu_widget, SUBMENU_ROW, SUBMENU_COL)
        self.bot_left_layout.addWidget(self.options_widget, OPTIONS_ROW, OPTIONS_COL)
        self.layout.addWidget(self.bot_left_widget, BOT_LEFT_ROW, BOT_LEFT_COL)

        self.layout.addWidget(self.top_left_widget, TOP_LEFT_ROW, TOP_LEFT_COL)
        self.layout.addWidget(self.top_right_widget, TOP_RIGHT_ROW, TOP_RIGHT_COL)
        self.layout.addWidget(self.bot_right_widget, BOT_RIGHT_ROW, BOT_RIGHT_COL)
        self.top_left_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def auto_connect_camera(self):
        """Auto connect a camera, depending on the option in default_config.txt."""
        if 'autoconnect' in self.default_parameters:
            if self.default_parameters['autoconnect'] == 'Yes':
                if 'brandname' in self.default_parameters:
                    camera = cam_from_brands[self.default_parameters['brandname']]()
                    if camera.find_first_camera():
                        self.parent.brand_camera = self.default_parameters['brandname']
                        self.parent.camera = camera
                        self.parent.camera.init_camera()
                        self.parent.camera_thread.set_camera(self.parent.camera)
                        # Update menu exposure time slider
                        min_expo, max_expo = self.parent.camera.get_exposure_range()
                        if max_expo > 400000:
                            max_expo = 400000
                        if min_expo < 100:
                            min_expo = 100
                        self.main_menu.expo_widget.set_min_max_values(min_expo/1000,
                                                                      max_expo/1000)
                        # Init default parameters !
                        self.menu_action('images')
                        self.init_default_camera_params()

                        # Start Thread
                        self.parent.image_bits_depth = get_bits_per_pixel(self.parent.camera.get_color_mode())
                        self.parent.camera_thread.start()
                        self.fast_mode = True
                    return True
            return False

    def init_default_camera_params(self):
        """Initialize a camera with default_config.txt."""
        print('Default Parameters')
        if 'exposure' in self.default_parameters:
            self.parent.camera.set_exposure(int(self.default_parameters['exposure']))
            self.main_menu.expo_widget.set_value(int(self.default_parameters['exposure'])/1000)
        if 'blacklevel' in self.default_parameters:
            self.parent.camera.set_black_level(int(self.default_parameters['blacklevel']))
        if 'framerate' in self.default_parameters:
            self.parent.camera.set_frame_rate(int(self.default_parameters['framerate']))
        if 'colormode' in self.default_parameters:
            self.parent.camera.set_color_mode(self.default_parameters['colormode'])
        camera = self.parent.camera
        print(f'Expo = {camera.get_exposure()}')
        print(f'FPS  = {camera.get_frame_rate()}')
        print(f'Colo = {camera.get_color_mode()}')
        print(f'ExpoRange = {camera.get_exposure_range()}')

    def clear_layout(self, row: int, column: int) -> None:
        """
        Remove widgets from a specific position in the layout.
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

    def clear_sublayout(self, column: int) -> None:
        """
        Remove widgets from a specific position in the layout of the bottom left area.
        :param column: Column index of the layout.
        """
        item = self.bot_left_layout.itemAtPosition(0, column)
        if item is not None:
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.layout.removeItem(item)

    def get_list_menu(self, menu):
        """ """
        if menu in self.default_parameters:
            return [int(x) for x in self.default_parameters[menu].split(',')]

    def set_top_right_widget(self, widget):
        """
        Modify the top right widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(TOP_RIGHT_ROW, TOP_RIGHT_COL)
        self.top_right_widget = widget
        self.layout.addWidget(self.top_right_widget, TOP_RIGHT_ROW, TOP_RIGHT_COL)

    def set_bot_left_widget(self, widget):
        """
        Modify the bottom left widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(BOT_LEFT_ROW, BOT_LEFT_COL)
        self.bot_left_widget = widget
        self.layout.addWidget(self.bot_left_widget, BOT_LEFT_ROW, BOT_LEFT_COL)

    def set_bot_right_widget(self, widget):
        """
        Modify the bottom right widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(BOT_RIGHT_ROW, BOT_RIGHT_COL)
        self.bot_right_widget = widget
        self.layout.addWidget(self.bot_right_widget, BOT_RIGHT_ROW, BOT_RIGHT_COL)

    def set_sub_menu_widget(self, widget):
        """
        Modify the sub menu widget.
        :param widget: Widget of the sub menu.
        """
        self.clear_sublayout(SUBMENU_COL)
        self.submenu_widget = widget
        self.bot_left_layout.addWidget(self.submenu_widget, SUBMENU_ROW, SUBMENU_COL)

    def set_options_widget(self, widget):
        """
        Modify the options widget.
        :param widget: Widget of the options.
        """
        self.clear_sublayout(OPTIONS_COL)
        self.options_widget = widget
        self.bot_left_layout.addWidget(self.options_widget, OPTIONS_ROW, OPTIONS_COL)

    def update_image(self, aoi: bool = False, aoi_disp: bool = False, zoom_factor: int = 1):
        """
        Update image display in the top left widget.
        :param aoi: Only AOI is displayed.
        :param aoi_disp: The whole image is displayed with a rectangle around the AOI.
        """
        if aoi:
            image = get_aoi_array(self.parent.image, self.parent.aoi)
            image = zoom_array(image, self.zoom_factor)
            #print(f'Z = {self.zoom_factor}')
            self.top_left_widget.set_image_from_array(image, aoi)
        else:
            if aoi_disp:
                image = display_aoi(self.parent.image, self.parent.aoi)
                self.top_left_widget.set_image_from_array(image)
            else:
                self.top_left_widget.set_image_from_array(self.parent.raw_image)

    def menu_action(self, event):
        """
        Action performed when a button of the main menu is clicked.
        Only GUI actions are performed in this section.
        :param event: Event that triggered the action.
        """
        print(f'menu_action : event = {event}')
        self.mode = event
        menu = self.get_list_menu('type1')
        self.zoom_factor = 1
        # Reset zoom factor
        self.main_menu.zoom_widget.reset_zoom()
        # Update maximum value of the zoom
        widget_width, widget_height = self.width(), self.height()
        if self.parent.aoi is not None:
            image = get_aoi_array(self.parent.image, self.parent.aoi)
            image_width, image_height = image.shape[1], image.shape[0]
            zoom_max = int(np.min([widget_width/image_width, widget_height/image_height])) - 1
            if zoom_max < 1:
                zoom_max = 1
        else:
            zoom_max = 1
        self.main_menu.zoom_widget.set_zoom_max(zoom_max)
        # Update main menu
        self.main_menu.set_enabled(menu, True)
        if self.parent.raw_image is None and self.parent.camera is None:
            menu = self.get_list_menu('type1')
            self.main_menu.set_enabled(menu, False)
        if self.parent.aoi is None:
            menu = self.get_list_menu('type2')
            self.main_menu.set_enabled(menu, False)
        self.clear_sublayout(OPTIONS_COL)
        self.clear_layout(TOP_RIGHT_ROW, TOP_RIGHT_COL)
        self.clear_layout(BOT_RIGHT_ROW, BOT_RIGHT_COL)

        if self.parent.camera is not None:
            if self.mode != 'images':
                self.set_expo_checkable(True)
                expo = self.parent.camera.get_exposure()
                self.main_menu.expo_widget.set_value(expo/1000)
            else:
                self.set_expo_checkable(False)
        else:
            self.set_expo_checkable(False)

        if self.mode == 'images':
            if self.parent.raw_image is not None:
                self.update_image()
            if self.parent.camera is not None:
                # Open camera settings
                self.bot_right_widget = CameraSettingsWidget(self, self.parent.camera)
                self.set_bot_right_widget(self.bot_right_widget)
                self.options_widget = CameraInfosWidget(self)
                self.set_options_widget(self.options_widget)
                self.top_right_widget = ImageHistogramWidget('Image Histogram')
                self.top_right_widget.set_background('white')
                self.set_top_right_widget(self.top_right_widget)
                self.bot_right_widget.update_parameters(auto_min_max=True)
                # Display expo time setting in main menu

        elif self.mode == 'open_image':
            if self.parent.camera is not None:
                self.parent.camera.stop_acquisition()
                if self.parent.brand_camera == 'IDS':
                    self.parent.camera_thread.stop(timeout=False)
                else:
                    self.parent.camera_thread.stop()
                self.parent.camera.disconnect()
                self.parent.camera_device = None
                self.parent.camera.destroy_camera()
                self.parent.camera = None
            if self.parent.raw_image is not None:
                self.update_image()
            self.options_widget = ImagesFileOpeningWidget(self)
            self.set_options_widget(self.options_widget)

        elif self.mode == 'open_camera':
            if self.parent.camera is not None:
                self.parent.camera.stop_acquisition()
                if self.parent.brand_camera == 'IDS':
                    self.parent.camera_thread.stop(timeout=False)
                else:
                    self.parent.camera_thread.stop()
                self.parent.camera.disconnect()
                self.parent.camera_device = None
                self.parent.camera.destroy_camera()
                self.parent.camera = None
            self.options_widget = ImagesCameraOpeningWidget(self)
            self.set_options_widget(self.options_widget)

        elif self.mode == 'aoi_select':
            self.options_widget = AoiSelectOptionsWidget(self)
            if self.parent.aoi is not None:
                self.update_image(aoi_disp=True)
                self.options_widget.set_aoi(self.parent.aoi)
            self.set_options_widget(self.options_widget)
            self.clear_layout(TOP_RIGHT_ROW, TOP_RIGHT_COL)
            self.top_right_widget = ImageHistogramWidget('Image Histogram')
            self.top_right_widget.set_background('white')
            self.set_top_right_widget(self.top_right_widget)
            self.bot_right_widget = ImageHistogramWidget('AOI Histogram')
            self.bot_right_widget.set_background('lightgray')
            self.set_bot_right_widget(self.bot_right_widget)

        elif self.mode == 'histo':
            # Display a label with definition or what to do in the options view ?
            self.update_image(aoi=True)
            self.top_right_widget = ImageHistogramWidget('Image Histogram')
            self.top_right_widget.set_background('white')
            self.layout.addWidget(self.top_right_widget, TOP_RIGHT_ROW, TOP_RIGHT_COL)
            if self.parent.camera is None:
                self.submenu_widget.set_enabled(2, False)

        elif self.mode == 'histo_space':
            self.update_image(aoi=True)
            self.options_widget = HistoSpaceOptionsWidget(self)
            self.set_options_widget(self.options_widget)
            self.top_right_widget = ImageHistogramWidget('Image Histogram')
            self.top_right_widget.set_background('white')
            self.layout.addWidget(self.top_right_widget, TOP_RIGHT_ROW, TOP_RIGHT_COL)
            if self.parent.camera is None:
                self.submenu_widget.set_enabled(2, False)

        elif self.mode == 'histo_time':
            self.options_widget = HistoTimeOptionsWidget(self)
            self.set_options_widget(self.options_widget)
            pixels_x, pixels_y = rand_pixels(self.parent.aoi)
            self.options_widget.set_pixels_x_y(pixels_x, pixels_y)
            if self.parent.camera is None:
                self.submenu_widget.set_enabled(2, False)
            self.top_right_widget = ImageHistogramWidget('Image Histogram')
            self.top_right_widget.set_background('white')
            self.set_top_right_widget(self.top_right_widget)

        elif self.mode == 'quant_samp':
            self.update_image(aoi=True)
            # Display a label with definition or what to do in the options view ?
            pass

        elif self.mode == 'quantization':
            self.update_image(aoi=True)
            self.options_widget = QuantizationOptionsWidget(self)
            self.set_options_widget(self.options_widget)
            self.top_right_widget = ImagesDisplayWidget(self)
            self.set_top_right_widget(self.top_right_widget)
            self.start_double_histo_widget(name1=translate('histo_original_image'),
                                           name2=translate('histo_quantized_image'))
            self.parent.action_quantize_image('quantized')

        elif self.mode == 'sampling':
            self.update_image(aoi=True)
            self.options_widget = SamplingOptionsWidget(self)
            self.set_options_widget(self.options_widget)
            self.top_right_widget = ImagesDisplayWidget(self)
            self.set_top_right_widget(self.top_right_widget)
            self.start_double_histo_widget(name1=translate('histo_original_image'),
                                           name2=translate('histo_quantized_image'))
            self.parent.action_sampling_image('resampled')

        elif self.mode == 'threshold':
            self.submode = None
            self.update_image(aoi=True)
            self.options_widget = ThresholdOptionsWidget(self)
            self.set_options_widget(self.options_widget)
            self.top_right_widget = ImagesDisplayWidget(self)
            self.set_top_right_widget(self.top_right_widget)
            self.resize_top_right_image()
            self.bot_right_widget = ImageHistogramWidget(self)
            self.bot_right_widget.set_background('white')
            self.set_bot_right_widget(self.bot_right_widget)

        elif self.mode == 'bright_contrast':
            self.update_image(aoi=True)
            self.options_widget = ContrastBrightnessOptionsWidget(self)
            self.set_options_widget(self.options_widget)
            self.top_right_widget = ImagesDisplayWidget(self)
            self.set_top_right_widget(self.top_right_widget)
            self.start_double_histo_widget(name1=translate('histo_original_image'),
                                           name2=translate('histo_contr_bright_image'))

        elif self.mode == 'enhance_contrast':
            # self.submode = 'enhance_contrast'
            self.update_image(aoi=True)
            self.options_widget = ContrastAdjustOptionsWidget(self)
            self.set_options_widget(self.options_widget)
            self.top_right_widget = ImagesDisplayWidget(self)
            self.set_top_right_widget(self.top_right_widget)
            self.start_double_histo_widget(name1=translate('histo_original_image'),
                                           name2=translate('histo_contr_bright_image'))
            print('Enhance OK')

        elif self.mode == 'erosion_dilation':
            self.update_image(aoi=True)
            self.options_widget = ErosionDilationOptionsWidget(self)
            self.set_options_widget(self.options_widget)
            self.top_right_widget = ImagesDisplayWidget(self)
            self.set_top_right_widget(self.top_right_widget)
            self.start_double_histo_widget(name1=translate('histo_original_image'),
                                           name2=translate('histo_eroded_image'))

        elif self.mode == 'opening_closing':
            self.update_image(aoi=True)
            self.options_widget = OpeningClosingOptionsWidget(self)
            self.set_options_widget(self.options_widget)
            self.top_right_widget = ImagesDisplayWidget(self)
            self.set_top_right_widget(self.top_right_widget)
            self.start_double_histo_widget(name1=translate('histo_original_image'),
                                           name2=translate('histo_eroded_image'))

        elif self.mode == 'gradient':
            self.submode = 'gradient'
            self.update_image(aoi=True)
            self.options_widget = GradientOptionsWidget(self)
            self.set_options_widget(self.options_widget)
            self.top_right_widget = ImagesDisplayWidget(self)
            self.set_top_right_widget(self.top_right_widget)
            self.start_double_histo_widget(name1=translate('histo_original_image'),
                                           name2=translate('histo_gradient_image'))

        elif self.mode == 'filters':
            self.update_image(aoi=True)
            self.top_right_widget = ImagesDisplayWidget(self)
            self.set_top_right_widget(self.top_right_widget)

        elif self.mode == 'filter_smooth':
            self.update_image(aoi=True)
            self.options_widget = SmoothFilterOptionsWidget(self)
            self.set_options_widget(self.options_widget)
            self.top_right_widget = ImagesDisplayWidget(self)
            self.set_top_right_widget(self.top_right_widget)

        self.main_signal.emit(event)

    def resize_top_right_image(self):
        """Resize the top right corner widget to adapt image size to window size."""
        new_size = self.parent.size()
        width = new_size.width()
        height = new_size.height()
        wi = (width * RIGHT_WIDTH) // 100
        he = (height * TOP_HEIGHT) // 100
        self.top_right_widget.update_size(wi, he)

    def start_double_histo_widget(self, name1: str = 'Original Image',
                                  name2: str = 'Modified Image'):
        """Start a widget containing a double histogram in the bottom right corner."""
        self.resize_top_right_image()
        self.bot_right_widget = DoubleHistoWidget(self, name_histo_1=name1, name_histo_2=name2)
        self.set_bot_right_widget(self.bot_right_widget)

    def update_size(self, aoi: bool = False):
        """
        Update the size of the main widget.
        """
        new_size = self.parent.size()
        width = new_size.width()
        height = new_size.height()
        wi = (width*LEFT_WIDTH)//100
        he = (height*TOP_HEIGHT)//100
        self.top_left_widget.update_size(wi, he, aoi)

    def set_expo_checkable(self, value: bool=False):
        """Set checkable the exposure time changing slider."""
        self.main_menu.expo_widget.set_checkable(value)

    def action_expo_changed(self, event):
        """Action performed when the exposure value in the main menu slider changed."""
        expo_value = self.main_menu.get_expo_value()*1000
        self.parent.camera.set_exposure(expo_value)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = MainWidget(self)
            self.setCentralWidget(self.central_widget)

        def create_gui(self):
            widget2 = QWidget()
            widget2.setStyleSheet('background-color: blue;')
            self.central_widget.set_top_right_widget(widget2)
            widget3 = QWidget()
            widget3.setStyleSheet('background-color: green;')
            self.central_widget.set_sub_menu_widget(widget3)
            widget4 = QWidget()
            widget4.setStyleSheet('background-color: yellow;')
            self.central_widget.set_bot_right_widget(widget4)

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
    main.create_gui()
    main.show()
    sys.exit(app.exec())
