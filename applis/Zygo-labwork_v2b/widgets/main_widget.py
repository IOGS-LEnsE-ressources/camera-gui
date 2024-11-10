# -*- coding: utf-8 -*-
"""*main_widget.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
"""
import sys, os
import threading, time
import numpy as np
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QCheckBox, QTextEdit,
    QMessageBox, QFileDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from lensepy import load_dictionary, translate, dictionary
from lensepy.css import *
from widgets.camera import *
from widgets.images import *
from process.hariharan_algorithm import *
from skimage.restoration import unwrap_phase

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
            elif element == 'O':   # options button
                menu.add_button(translate(title), signal, option=True)
            elif element == 'L':   # label title
                menu.add_label_title(translate(title))
            elif element == 'S':   # blank space
                menu.add_space()
        menu.display_layout()
    else:
        print('MENU File error')

# %% Widgets
class MenuWidget(QWidget):
    """
    Main menu of the application
    """

    menu_clicked = pyqtSignal(str)

    def __init__(self, parent=None, title: str='label_title_main_menu', sub: bool=False):
        """
        Default Constructor.
        :param parent:
        :param title:
        :param sub:
        """
        super().__init__(parent=parent)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.submenu = sub
        self.setLayout(self.layout)
        self.buttons_list = []
        self.buttons_signal = []
        self.buttons_enabled = []
        self.actual_button = None

        self.label_title_main_menu = QLabel(translate(title))
        self.label_title_main_menu.setStyleSheet(styleH1)
        self.label_title_main_menu.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.label_title_main_menu)

    def display_layout(self):
        """
        Update the layout with all the elements.
        """
        for i, element in enumerate(self.buttons_list):
            if element is not None:
                self.layout.addWidget(element)
            else:
                self.layout.addStretch()

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

    def add_space(self):
        """
        Add a space in the menu.
        :param title:
        :param signal:
        :return:
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
                sender.setStyleSheet(actived_button)
                # Send signal
                self.menu_clicked.emit(self.buttons_signal[i])

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
                    self.buttons_enabled[i - 1] = value
                else:
                    self.buttons_enabled[i - 1] = False
        else:
            if index not in menu:
                self.buttons_enabled[index - 1] = value
            else:
                self.buttons_enabled[index - 1] = False
        self.update_menu_display()

    def set_activated(self, index: int):
        """
        Set activated a button.
        :param index:
        """
        self.inactive_buttons()
        if isinstance(index, list):
            for i in index:
                self.buttons_list[i - 1].setStyleSheet(actived_button)
        else:
            self.buttons_list[index - 1].setStyleSheet(actived_button)

    def submenu_is_clicked(self, event):
        self.menu_clicked.emit(event)

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

class HTMLWidget(QWidget):
    """
    Widget displaying an HTML content.
    """
    def __init__(self, url: str='', css: str=''):
        """Default constructor.
        :param url: filepath or url to the HTML page. Default ''.
        """
        super().__init__()
        self.url = url
        self.css = css
        self.html_page = QTextEdit()
        self.html_page.setReadOnly(True)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.html_page)
        self.setLayout(self.layout)
        if url != '':
            self.set_url(self.url, self.css)

    def set_url(self, url: str, css: str = ''):
        """
        Set the URL of the mini browser.
        :param url: filepath or url to the HTML page.
        :param css: filepath to a css file. Default ''.
        """
        self.url = url
        self.css = css

        css_content = ''
        with open(url, "r", encoding="utf-8") as file:
            html_content = file.read()
        if self.css != '':
            with open(css, "r", encoding="utf-8") as file:
                css_content = file.read()

        full_html_content = f"""
        <html>
        <head>
            <style>
            {css_content}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        self.html_page.setHtml(full_html_content)

import pyqtgraph as pg
import pyqtgraph.opengl as gl
class Surface3DWidget(QWidget):
    def __init__(self, wrapped_phase, parent=None):
        super(Surface3DWidget, self).__init__(parent)

        # Configuration de la disposition
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Création du widget GLViewWidget pour l'affichage 3D
        self.view = gl.GLViewWidget()
        layout.addWidget(self.view)
        self.view.setCameraPosition(distance=300)
        self.view.setWindowTitle('Unwrapped surface')

        # Préparation des données pour l'affichage
        self.display_surface(wrapped_phase)

    def display_surface(self, wrapped_phase):
        # Limites de la région à afficher
        Z = wrapped_phase[400:1200, 750:1900]

        # Création des axes X et Y pour les données
        x = np.linspace(0, Z.shape[1], Z.shape[1])
        y = np.linspace(0, Z.shape[0], Z.shape[0])
        X, Y = np.meshgrid(x, y)
        Z = Z  # La profondeur (Z) est la valeur de `wrapped_phase`

        # Conversion des données en un format compatible avec pyqtgraph
        X = X.flatten()
        Y = Y.flatten()
        Z = Z.flatten()

        # Création de l'élément surface
        surface = gl.GLSurfacePlotItem(x=X, y=Y, z=Z, shader='heightColor', computeNormals=False, smooth=True)
        surface.scale(1, 1, 0.1)  # Ajuster l'échelle en profondeur
        surface.setColor((1, 0.5, 0, 1))  # Définir la couleur de la surface

        # Ajout de la surface au widget GLViewWidget
        self.view.addItem(surface)

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
        # GUI Structure
        self.layout = QGridLayout()
        self.title_label = TitleWidget(self)
        self.main_menu = MenuWidget(self)
        self.top_left_widget = QWidget()
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
        self.layout.addWidget(self.title_label, 0, 0, 1, 3)
        self.bot_left_layout.addWidget(self.submenu_widget, SUBMENU_ROW, SUBMENU_COL)
        self.bot_left_layout.addWidget(self.options_widget, OPTIONS_ROW, OPTIONS_COL)
        self.layout.addWidget(self.bot_left_widget, BOT_LEFT_ROW, BOT_LEFT_COL)
        # Add elements to the main layout
        self.layout.addWidget(self.top_left_widget, TOP_LEFT_ROW, TOP_LEFT_COL)
        self.layout.addWidget(self.top_right_widget, TOP_RIGHT_ROW, TOP_RIGHT_COL)
        self.layout.addWidget(self.bot_right_widget, BOT_RIGHT_ROW, BOT_RIGHT_COL)

        self.main_menu.menu_clicked.connect(self.menu_action)

        # Adding elements in the layout
        self.layout.addWidget(self.main_menu, 1, 0, 2, 1)
        self.layout.setColumnStretch(0, 10)
        self.layout.setColumnStretch(1, LEFT_WIDTH)
        self.layout.setColumnStretch(2, RIGHT_WIDTH)
        self.layout.setRowStretch(0, 5)
        self.layout.setRowStretch(1, TOP_HEIGHT)
        self.layout.setRowStretch(2, BOT_HEIGHT)
        self.setLayout(self.layout)

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

    def set_top_left_widget(self, widget):
        """
        Modify the top left widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(TOP_LEFT_ROW, TOP_LEFT_COL)
        self.top_left_widget = widget
        self.layout.addWidget(self.top_left_widget, TOP_LEFT_ROW, TOP_LEFT_COL)

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

    def get_list_menu(self, menu):
        """ """
        if menu in self.parent.default_parameters:
            return [int(x) for x in self.parent.default_parameters[menu].split(',')]

    def update_menu(self):
        """Update menu depending on the actual mode."""
        # Update menu
        menu = self.get_list_menu('all_menu')
        self.main_menu.set_enabled(menu, True)
        menu = []
        if self.parent.mask_created is False:
            menu += self.get_list_menu('nomask')
        if self.parent.acquisition_done is False and self.parent.images_opened is False:
            menu += self.get_list_menu('nodata')
        if self.parent.camera_connected is False:
            menu += self.get_list_menu('nocam')
        if self.parent.piezo_connected is False:
            menu += self.get_list_menu('nopiezo')
        self.main_menu.set_enabled(menu, False)

    def menu_action(self, event):
        """
        Action performed when a button of the main menu is clicked.
        Only GUI actions are performed in this section.
        :param event: Event that triggered the action.
        """
        self.main_signal.emit(event)
        self.clear_sublayout(OPTIONS_COL)
        self.clear_layout(TOP_LEFT_ROW, TOP_LEFT_COL)
        self.clear_layout(TOP_RIGHT_ROW, TOP_RIGHT_COL)
        self.clear_layout(BOT_RIGHT_ROW, BOT_RIGHT_COL)
        # Update menu
        self.update_menu()

        # Manage application
        if event == 'camera':   # Camera menu is clicked
            self.action_camera()

        elif event == 'zoom_camera':
            self.action_zoom_camera()

        elif event == 'images':
            self.parent.stop_thread()
            if self.parent.acquisition_done is False and self.parent.images_opened is False:
                self.submenu_widget.set_button_enabled(2, False)
                self.submenu_widget.set_button_enabled(4, False)
            else:
                self.submenu_widget.set_button_enabled(2, True)
                self.submenu_widget.set_button_enabled(4, True)
            html_page = HTMLWidget('./docs/html/images.html', './docs/html/styles.css')
            self.set_top_right_widget(html_page)

        elif event == 'open_images':
            self.parent.stop_thread()
            if self.parent.images_opened:
                print('WARNING !!')

            self.parent.images, self.parent.masks = self.action_menu_open_images()
            if self.parent.images is not None:
                self.parent.images_opened = True
                self.submenu_widget.set_button_enabled(2, True)
                self.submenu_widget.set_activated(2)
                self.submenu_widget.set_button_enabled(4, True)
            else:
                self.parent.images_opened = False
            if self.parent.masks is not None:
                self.parent.mask_created = True
            else:
                self.parent.mask_created = False
            self.menu_action('display_images')

        elif event == 'display_images':
            self.action_menu_display_images()

        elif event == 'simple_analysis':
            self.action_simple_analysis()

        elif event == 'wrapped_phase':
            self.parent.stop_thread()
            self.set_top_left_widget(ImagesDisplayWidget(self))
            self.update_size()
            self.set_top_right_widget(Surface3DWidget(self.parent.wrapped_phase, self))

            display_wrapped_phase(self.parent.wrapped_phase)

        elif event == 'unwrapped_phase':
            self.parent.stop_thread()
            self.set_top_left_widget(ImagesDisplayWidget(self))
            self.update_size()
            display_wrapped_phase(self.parent.unwrapped_phase)

    def action_camera(self):
        camera_setting = CameraSettingsWidget(self, self.parent.camera)
        self.set_options_widget(camera_setting)
        if 'Max Expo Time' in self.parent.default_parameters:
            self.options_widget.set_maximum_exposure_time(
                float(self.parent.default_parameters['Max Expo Time']))  # in ms
        self.options_widget.update_parameters(auto_min_max=True)
        html_page = HTMLWidget('./docs/html/camera.html', './docs/html/styles.css')
        self.set_top_right_widget(html_page)
        self.set_top_left_widget(ImagesDisplayWidget(self))
        self.update_size()
        self.parent.camera_thread.start()

    def action_zoom_camera(self):
        camera_setting = CameraSettingsWidget(self, self.parent.camera)
        self.set_options_widget(camera_setting)
        if 'Max Expo Time' in self.parent.default_parameters:
            self.options_widget.set_maximum_exposure_time(
                float(self.parent.default_parameters['Max Expo Time']))  # in ms
        self.options_widget.update_parameters(auto_min_max=True)
        html_page = HTMLWidget('./docs/html/camera.html', './docs/html/styles.css')
        self.set_top_right_widget(html_page)
        self.set_top_left_widget(ImagesDisplayWidget(self))
        self.update_size()
        self.parent.camera_thread.start()


    def action_menu_open_images(self):
        """Action performed when a MAT file has to be loaded."""
        file_dialog = QFileDialog()
        if 'Dir Images' in self.parent.default_parameters:
            default_path = self.parent.default_parameters['Dir Images']
        else:
            default_path = os.path.expanduser("~") + '/Images/'
        file_path, _ = file_dialog.getOpenFileName(self, translate('dialog_open_image'),
                                                   default_path, "Matlab (*.mat)")
        if file_path != '':
            data = read_mat_file(file_path)
            images_mat = data['Images']
            images = split_3d_array(images_mat)
            if 'Masks' in data:
                mask = data['Masks']  # TO DO : add a test on the size of 'Masks'
            else:
                mask = None
            if isinstance(images, list):
                if len(images)%5 == 0 and len(images) > 1:
                    self.parent.wrapped_phase_done = False
                    self.parent.unwrapped_phase_done = False
                    return images, mask
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No File Loaded")
            dlg.setText("Number of images in this file is not adapted to Hariharan algorithm.")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            return None, None
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No File Loaded")
            dlg.setText("No Image File was loaded...")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()
            html_page = HTMLWidget('./docs/images.html')
            self.set_top_right_widget(html_page)
            return None, None

    def action_menu_display_images(self):
        """Action performed when images are displayed."""
        self.parent.stop_thread()
        self.set_top_left_widget(ImagesDisplayWidget(self))
        self.update_size()
        self.set_options_widget(ImagesChoice(self))
        if self.parent.images_opened:
            self.options_widget.set_images_status(True, index=1)
            self.top_left_widget.set_image_from_array(self.parent.images[0])
        else:
            self.options_widget.set_images_status(False)
        if self.parent.mask_created:
            number = 0
            if isinstance(self.parent.masks, list):
                number = len(self.parent.masks)
            elif isinstance(self.parent.masks, np.ndarray):
                number = 1
            self.options_widget.set_masks_status(True, number)
        else:
            self.options_widget.set_masks_status(False)
        html_page = HTMLWidget('./docs/html/images.html', './docs/html/styles.css')
        self.set_top_right_widget(html_page)

    def action_simple_analysis(self):
        """Action performed when a simple analysis is required.
        Wrapped, then unwrapped phase processes are started in a thread.
        """
        self.parent.stop_thread()
        try:
            if self.parent.wrapped_phase_done is False:
                self.submenu_widget.set_button_enabled(1, False)
                self.submenu_widget.set_button_enabled(2, False)
                thread = threading.Thread(target=self.thread_wrapped_phase_calculation)
                thread.start()
            else:
                if self.parent.unwrapped_phase_done is False:
                    self.submenu_widget.set_button_enabled(2, False)
                    thread = threading.Thread(target=self.thread_unwrapped_phase_calculation)
                    thread.start()

            self.set_top_left_widget(ImagesDisplayWidget(self))
            self.update_size()
            if self.parent.images_opened:
                self.top_left_widget.set_image_from_array(self.parent.images[0])
            html_page = HTMLWidget('./docs/html/simple_analysis.html', './docs/html/styles.css')
            self.set_top_right_widget(html_page)
        except Exception as e:
            print(f'Simple Analysis - {e}')

    def thread_wrapped_phase_calculation(self):
        """"""
        # TO DO : select the good set of images if multiple acquisition
        k = 0
        images = self.parent.images[0+k:5+k]
        self.parent.wrapped_phase = hariharan_algorithm(images)
        self.parent.wrapped_phase_done = True
        if self.parent.main_mode == 'simple_analysis':
            self.submenu_widget.set_button_enabled(1, True)
        thread = threading.Thread(target=self.thread_unwrapped_phase_calculation)
        thread.start()

    def thread_unwrapped_phase_calculation(self):
        """"""
        self.parent.unwrapped_phase = unwrap_phase(self.parent.wrapped_phase) / (2 * np.pi)
        if self.parent.main_mode == 'simple_analysis' or self.parent.main_mode == 'wrapped_phase':
            self.submenu_widget.set_button_enabled(2, True)

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
            widget1 = QWidget()
            widget1.setStyleSheet('background-color: red;')
            self.central_widget.set_top_left_widget(widget1)
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
