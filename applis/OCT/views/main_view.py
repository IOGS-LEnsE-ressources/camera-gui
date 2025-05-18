# -*- coding: utf-8 -*-
"""*main_view.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QCheckBox, QTextEdit,
    QMessageBox, QFileDialog, QDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from lensepy import load_dictionary, translate, dictionary
from lensepy.pyqt6.widget_image_display import ImageDisplayWidget
from lensepy.css import *
from views.images import ImageDisplayGraph
from views.title_view import TitleView


class CameraParamsWidget(QWidget):
    """
    Widget containing camera parameters.
    """
    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent widget of the camera parameters widget.
        """
        super().__init__(parent=parent)
        self.parent = parent

        layout = QHBoxLayout()
        label = QLabel('Test Camera')
        layout.addWidget(label)
        self.setLayout(layout)


class MiniCameraWidget(QWidget):
    """
    Widget containing the title and the camera parameters.
    """

    def __init__(self, parent=None):
        """
        Default Constructor.
        :param parent: Parent widget of the title widget.
        """
        super().__init__(parent=parent)
        self.parent = parent
        self.layout = QGridLayout()

        self.title_widget = TitleView(self.parent)
        self.camera_params_widget = CameraParamsWidget(self.parent)

        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 2)

        self.layout.addWidget(self.title_widget, 0, 0)
        self.layout.addWidget(self.camera_params_widget, 1, 0)
        self.setLayout(self.layout)



class MainView(QWidget):
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
        # Set size of cols and rows
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)
        self.layout.setRowStretch(2, 1)
        # Adding elements in the layout
        self.mini_camera = MiniCameraWidget(self.parent)
        self.layout.addWidget(self.mini_camera, 0, 0)
        self.image1_widget = ImageDisplayGraph(self, '#90EE90', zoom=False)
        self.layout.addWidget(self.image1_widget, 0, 1)
        self.image2_widget = ImageDisplayGraph(self, '#90EE90', zoom=False)
        self.layout.addWidget(self.image2_widget, 0, 2)

        self.image_graph = ImageDisplayGraph(self, '#48D1CC')
        self.layout.addWidget(self.image_graph, 1, 1, 2, 2)

        # TO DELETE
        image = np.random.normal(size=(100, 100))
        #self.image1_widget.set_image_from_array(image, 'Image1')
        self.image2_widget.set_image_from_array(image, 'Image2')
        self.image_graph.set_image_from_array(image, 'OCT')

        self.setLayout(self.layout)


    def menu_action(self, event):
        """
        Action performed when a button of the main menu is clicked.
        Only GUI actions are performed in this section.
        :param event: Event that triggered the action.
        """
        pass

    def display_right(self):
        # Display image with mask in the top right widget
        self.set_top_right_widget(ImagesDisplayWidget(self))
        new_size = self.parent.size()
        width = new_size.width()
        height = new_size.height()
        wi = (width * RIGHT_WIDTH) // 100
        he = (height * TOP_HEIGHT) // 100
        self.top_right_widget.update_size(wi, he)

        images = self.parent.images.get_images_set(0)
        mask = self.parent.masks.get_global_mask()
        if mask is not None:
            # Crop images around the mask
            top_left, bottom_right = find_mask_limits(mask)
            height, width = bottom_right[1] - top_left[1], bottom_right[0] - top_left[0]
            pos_x, pos_y = top_left[1], top_left[0]
            self.parent.cropped_mask_phase = crop_images([mask], (height, width), (pos_x, pos_y))[0]
            images_c = crop_images(images, (height, width), (pos_x, pos_y))
        else:
            images_c = images
        self.top_right_widget.set_image_from_array(images_c[0])

    def update_size(self, aoi: bool = False):
        """
        Update the size of the main widget.
        """
        new_size = self.parent.size()
        width = new_size.width()
        height = new_size.height()
        wi = width//3
        he = height//3
        self.top_left_widget.update_size(wi, he, aoi)

    def set_top_left_widget(self, widget):
        """
        Modify the top left widget.
        :param widget: Widget to include inside the application.
        """
        self.clear_layout(TOP_LEFT_ROW, TOP_LEFT_COL)
        self.top_left_widget = widget
        self.layout.addWidget(self.top_left_widget, TOP_LEFT_ROW, TOP_LEFT_COL)

    def action_camera(self):
        """Action performed when Camera is clicked in the menu."""
        camera_setting = CameraSettingsWidget(self, self.parent.camera)
        self.set_options_widget(camera_setting)
        if 'Max Expo Time' in self.parent.default_parameters:
            self.options_widget.set_maximum_exposure_time(
                float(self.parent.default_parameters['Max Expo Time']))  # in ms
        self.options_widget.update_parameters(auto_min_max=True)
        self.parent.camera_thread.start()

    def open_images(self):
        """Action performed when a MAT file has to be loaded."""
        file_dialog = QFileDialog()
        if 'Dir Images' in self.parent.default_parameters:
            default_path = self.parent.default_parameters['Dir Images']
        else:
            default_path = os.path.expanduser("~") + '/Images/'
        file_path, _ = file_dialog.getOpenFileName(self, translate('dialog_open_image'),
                                                   default_path, "Matlab (*.mat)")

        if file_path != '':
            masks = Masks()
            images = Images()
            data = read_mat_file(file_path)
            images_mat = data['Images']
            images_d = split_3d_array(images_mat)
            if 'Masks' in data:
                mask_mat = data['Masks']
                mask_d = split_3d_array(mask_mat, size=1)
                if isinstance(mask_d, list):
                    for i, maskk in enumerate(mask_d):
                        masks.add_mask(maskk.squeeze())
            if isinstance(images_d, list):
                if len(images_d) % 5 == 0 and len(images_d) > 1:
                    self.parent.wrapped_phase_done = False
                    self.parent.unwrapped_phase_done = False
                    for i in range(int(len(images_d) / 5)):
                        images.add_set_images(images_d[i:i + 5])
                    return images, masks
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
            return None, None


    def thread_wrapped_phase_calculation(self):
        """Thread to calculate wrapped phase from 5 images."""
        # TO DO : select the good set of images if multiple acquisition
        k = 0
        images = self.parent.images.get_images_set(k)
        mask = self.parent.masks.get_global_mask()
        if mask is not None:
            # Crop images around the mask
            top_left, bottom_right = find_mask_limits(mask)
            print(f"Mask Limits : {top_left} / {bottom_right}")
            height, width = bottom_right[1] - top_left[1], bottom_right[0] - top_left[0]
            pos_x, pos_y = top_left[1], top_left[0]
            self.parent.cropped_mask_phase = crop_images([mask], (height, width), (pos_x, pos_y))[0]
            images_c = crop_images(images, (height, width), (pos_x, pos_y))
            # Filtering images to avoid noise
            images_f = list(map(lambda x: gaussian_filter(x, 10), images_c))

            # Process Phase
            wrapped_phase = hariharan_algorithm(images_f, self.parent.cropped_mask_phase)


            print(f'Image = {images[0].shape} / {images[0].dtype}')
            print(f'Image C = {images_c[0].shape} / {images_c[0].dtype}')
            print(f'Image F = {images_f[0].shape} / {images_f[0].dtype}')
            print(f'Cropped Mask Type = {type(self.parent.cropped_mask_phase)} / {self.parent.cropped_mask_phase.dtype}')
            print(f'Phase Type = {type(wrapped_phase)} / {wrapped_phase.dtype}')
            self.parent.wrapped_phase = wrapped_phase
            # self.parent.wrapped_phase = np.ma.masked_where(np.logical_not(self.parent.cropped_mask_phase), wrapped_phase)
            # End of process
            self.parent.wrapped_phase_done = True
            if self.parent.main_mode == 'simpleanalysis':
                self.submenu_widget.set_button_enabled(1, True)
            thread = threading.Thread(target=self.thread_unwrapped_phase_calculation)
            thread.start()

    def thread_unwrapped_phase_calculation(self):
        """"""
        # Process unwrapping phase
        self.parent.unwrapped_phase = unwrap_phase(self.parent.wrapped_phase)/(2*np.pi)

        self.parent.unwrapped_phase = np.ma.masked_where(np.logical_not(self.parent.cropped_mask_phase),
                                                         self.parent.unwrapped_phase)

        self.parent.unwrapped_phase_done = True
        if self.parent.main_mode == 'simpleanalysis' or self.parent.main_submode == 'wrappedphase':
            self.submenu_widget.set_button_enabled(2, True)

        thread = threading.Thread(target=self.thread_statistics_calculation)
        thread.start()

    def thread_statistics_calculation(self):
        """Process PeakValley and RMS statistics on Unwrapped phase."""
        try:
            self.parent.pv = []
            self.parent.rms = []
            if self.parent.unwrapped_phase_done:
                for i in range(self.parent.acquisition_number):
                    pv, rms = surface_statistics(self.parent.unwrapped_phase)
                    self.parent.pv_stats.append(np.round(pv, 2))
                    self.parent.rms_stats.append(np.round(rms, 2))
                if self.parent.main_mode == 'simpleanalysis':
                    #self.options_widget.set_values(self.parent.pv_stats, self.parent.rms_stats)
                    print(self.parent.pv_stats)
        except Exception as e:
            print(f'Thread PV : {e}')

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = MainView(self)
            self.setCentralWidget(self.central_widget)

        def create_gui(self):
            pass

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
