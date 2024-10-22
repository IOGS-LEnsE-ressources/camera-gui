# -*- coding: utf-8 -*-
"""*cmos_lab_app.py* file.

*cmos_lab_app* file that contains :class::CmosLabApp

This file is attached to engineer training lab works in photonics.
- 1st year subject :
- 2nd year subject : http://lense.institutoptique.fr/ressources/Annee2/TP_Photonique/S8-2324-Detection.EN.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/contents/appli_CMOS_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE <julien.villemejane@institutoptique.fr>

Creation : sept/2023
Modification : oct/2024
"""
import cv2
import numpy as np
from lensepy.images.conversion import quantize_image

from widgets.main_widget import *
from lensecam.camera_thread import CameraThread
from lensecam.ids.camera_ids import get_bits_per_pixel
from PyQt6.QtWidgets import QMainWindow, QApplication
from lensepy.images.processing import *

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
        self.setWindowTitle("LEnsE - CMOS Sensor / Machine Vision / Lab work")
        # Objects
        self.image = None
        self.raw_image = None
        self.saved_image = None
        self.aoi = None
        self.fast_mode = False
        self.image_bits_depth = 8
        # Displayed image
        self.check_diff = False
        self.kernel_type = None
        # Camera
        self.brand_camera = None
        self.camera_device = None
        self.camera = None
        self.camera_index = 0  # TO UPDATE !! when a new camera is selected with a camera_list object
        self.camera_thread = CameraThread()
        self.camera_thread.image_acquired.connect(self.thread_update_image)
        # GUI structure
        self.central_widget = MainWidget(self)
        self.setCentralWidget(self.central_widget)
        load_menu('./config/menu.txt', self.central_widget.main_menu)
        if self.central_widget.auto_connect_camera():
            self.main_action('images')
        self.central_widget.main_signal.connect(self.main_action)
        menu1 = self.central_widget.get_list_menu('type1')
        self.central_widget.main_menu.set_enabled(menu1, False)

    def main_action(self, event):
        """
        Action performed by an event in the main widget.
        :param event: Event that triggered the action.
        """
        if self.raw_image is not None:
            size = self.raw_image.shape[1] * self.raw_image.shape[0]
            self.fast_mode = size > 1e5 # Fast mode if number of pixels > 1e5

        if self.central_widget.mode == 'open_image':
            self.aoi = None
            if self.camera is not None:
                self.camera_thread.stop()
                self.camera.stop_acquisition()
                self.camera.disconnect()
                menu1 = self.central_widget.get_list_menu('type1')
                self.central_widget.main_menu.set_enabled(menu1, False)
            self.central_widget.options_widget.image_opened.connect(self.action_image_from_file)
            self.image_bits_depth = 8

        elif self.central_widget.mode == 'open_camera':
            self.aoi = None
            if self.camera is not None:
                self.camera_thread.stop()
                self.camera.stop_acquisition()
                self.camera.disconnect()
                menu1 = self.central_widget.get_list_menu('type1')
                self.central_widget.main_menu.set_enabled(menu1, False)
            self.central_widget.options_widget.camera_opened.connect(self.action_camera_selected)

        elif self.central_widget.mode == 'aoi_select':
            # Histogram of the global image.
            self.central_widget.top_right_widget.set_bit_depth(self.image_bits_depth)
            self.central_widget.top_right_widget.set_image(self.raw_image, fast_mode=self.fast_mode)
            self.central_widget.top_right_widget.update_info()
            # Histogram of the AOI.
            if self.aoi is not None:
                aoi_array = get_aoi_array(self.raw_image, self.aoi)
                self.central_widget.bot_right_widget.set_bit_depth(self.image_bits_depth)
                self.central_widget.bot_right_widget.set_image(aoi_array, fast_mode=self.fast_mode)
                self.central_widget.bot_right_widget.update_info()
            # Connect signal.
            self.central_widget.options_widget.aoi_selected.connect(self.action_aoi_selected)

        elif self.central_widget.mode == 'histo':
            aoi_array = get_aoi_array(self.raw_image, self.aoi)
            fast = (aoi_array.shape[0] * aoi_array.shape[1]) < 1000
            self.central_widget.top_right_widget.set_bit_depth(self.image_bits_depth)
            self.central_widget.top_right_widget.set_image(aoi_array, fast_mode=fast)
            self.central_widget.top_right_widget.update_info()

        elif self.central_widget.mode == 'histo_space':
            self.central_widget.options_widget.snap_clicked.connect(self.action_histo_space)
            aoi_array = get_aoi_array(self.raw_image, self.aoi)
            if aoi_array.shape[0] * aoi_array.shape[1] < 1000:
                fast = False
            else:
                fast = True
            self.central_widget.top_right_widget.set_bit_depth(self.image_bits_depth)
            self.central_widget.top_right_widget.set_image(aoi_array, fast_mode=fast)
            self.central_widget.top_right_widget.update_info()

        elif self.central_widget.mode == 'histo_time':
            self.central_widget.options_widget.start_acq_clicked.connect(self.action_histo_time)
            self.central_widget.options_widget.set_enabled_save(False)

        elif self.central_widget.mode == 'quant_samp':
            pass

        elif self.central_widget.mode == 'quantization':
            self.central_widget.options_widget.quantized.connect(self.action_quantize_image)

        elif self.central_widget.mode == 'sampling':
            self.central_widget.options_widget.resampled.connect(self.action_sampling_image)

        elif self.central_widget.mode == 'threshold':
            self.central_widget.options_widget.threshold_changed.connect(self.action_threshold)

        elif self.central_widget.mode == 'pre_proc':
            self.kernel_type = 'cross'

        elif self.central_widget.mode == 'bright_contrast':
            self.check_diff = False
            self.central_widget.options_widget.contrast_brithtness_changed.connect(self.action_contrast_brightness)
            self.action_contrast_brightness('contrast_brightness')

        elif self.central_widget.mode == 'enhance_contrast':
            self.check_diff = False
            self.central_widget.options_widget.options_clicked.connect(self.action_enhance_contrast)
            self.action_enhance_contrast('enhance_contrast')

        elif self.central_widget.mode == 'erosion_dilation':
            self.check_diff = False
            self.central_widget.options_widget.ero_dil_changed.connect(self.action_erosion_dilation)
        elif self.central_widget.mode == 'opening_closing':
            self.check_diff = False
            self.central_widget.options_widget.open_close_changed.connect(self.action_erosion_dilation)

        elif self.central_widget.mode == 'gradient':
            self.check_diff = False
            self.central_widget.options_widget.gradient_changed.connect(self.action_erosion_dilation)

        elif self.central_widget.mode == 'filter_smooth':
            self.check_diff = False
            self.central_widget.options_widget.options_changed.connect(self.action_filter_smooth)

    def thread_update_image(self, image_array):
        if image_array is not None:
            if self.image_bits_depth > 8:
                self.raw_image = image_array.view(np.uint16)
                self.image = self.raw_image >> (self.image_bits_depth-8)
                self.image = self.image.astype(np.uint8)
            else:
                self.raw_image = image_array.view(np.uint8)
                self.image = self.raw_image

        self.central_widget.top_left_widget.set_image_from_array(self.image)

        if self.central_widget.mode == 'images':
            if self.camera is not None:
                # Histogram of the global image.
                self.central_widget.top_right_widget.set_bit_depth(self.image_bits_depth)
                self.central_widget.top_right_widget.set_image(self.raw_image, fast_mode=self.fast_mode)
                self.central_widget.top_right_widget.update_info()

        elif self.central_widget.mode == 'aoi_select':
            self.action_aoi_selected('aoi_selected')
        elif self.central_widget.mode == 'histo':
            self.action_histo_space('live')
        elif self.central_widget.mode == 'histo_space':
            self.central_widget.update_image(aoi=True)
        elif self.central_widget.mode == 'histo_time':
            self.central_widget.update_image(aoi=True)
            if self.central_widget.options_widget.is_acquiring():
                self.central_widget.options_widget.increase_counter(self.raw_image)

        elif self.central_widget.mode == 'quant_samp':
            self.central_widget.update_image(aoi=True)
        elif self.central_widget.mode == 'quantization':
            self.central_widget.update_image(aoi=True)
            self.action_quantize_image('quantized')
        elif self.central_widget.mode == 'sampling':
            self.central_widget.update_image(aoi=True)
            self.action_sampling_image('resampled')
        elif self.central_widget.mode == 'pre_proc':
            self.central_widget.update_image(aoi=True)
        elif self.central_widget.mode == 'threshold':
            self.central_widget.update_image(aoi=True)
            self.action_threshold(None)

        elif self.central_widget.mode == 'enhance_contrast':
            self.central_widget.update_image(aoi=True)
            self.action_enhance_contrast('enhance_contrast')

        elif self.central_widget.mode == 'bright_contrast':
            self.central_widget.update_image(aoi=True)
            self.action_contrast_brightness('contrast_brightness')

        elif self.central_widget.mode == 'erosion_dilation':
            self.central_widget.update_image(aoi=True)
            self.action_erosion_dilation(None)
            if self.central_widget.submode == 'erorion':
                self.action_erosion_dilation('erosion')
            elif self.central_widget.mode == 'dilation':
                self.action_erosion_dilation('dilation')
        elif self.central_widget.mode == 'opening_closing':
            self.central_widget.update_image(aoi=True)
            self.action_erosion_dilation(None)
            if self.central_widget.submode == 'opening':
                self.action_erosion_dilation('opening')
            elif self.central_widget.mode == 'closing':
                self.action_erosion_dilation('closing')
        elif self.central_widget.mode == 'gradient':
            self.central_widget.update_image(aoi=True)
            self.action_erosion_dilation('gradient')
        elif self.central_widget.mode == 'filter_smooth':
            self.central_widget.update_image(aoi=True)
            self.action_filter_smooth(None)

    def action_image_from_file(self, event: np.ndarray):
        """
        Action performed when an image file is opened.
        :param event: Event that triggered the action - np.ndarray.
        """
        if self.camera is not None:
            self.camera_thread.stop()
            self.camera.stop_acquisition()
            self.camera.disconnect()
            self.camera = None
            self.camera_device = None
        self.raw_image = event.copy()
        if self.image_bits_depth > 8:
            image = self.raw_image.view(np.uint16)
        else:
            image = self.raw_image.view(np.uint8)
        self.raw_image = image.squeeze()
        self.image = self.raw_image
        self.aoi = None
        self.central_widget.top_left_widget.set_image_from_array(self.raw_image)
        self.central_widget.top_left_widget.repaint()
        self.central_widget.options_widget.button_open_image.setStyleSheet(unactived_button)
        self.central_widget.main_menu.set_enabled([3], True)
        menu2 = self.central_widget.get_list_menu('type2')
        self.central_widget.main_menu.set_enabled(menu2, False)

    def action_camera_selected(self, event):
        """
        Action performed when an industrial camera is selected.
        :param event: Event that triggered the action - np.ndarray.
        """
        self.central_widget.main_menu.set_enabled([3], True)
        menu2 = self.central_widget.get_list_menu('type2')
        self.central_widget.main_menu.set_enabled(menu2, False)
        self.brand_camera = event['brand']
        camera_list = cam_list_brands[self.brand_camera]()
        self.camera_device = camera_list.get_cam_device(int(event['cam_dev']))
        self.camera = cam_from_brands[self.brand_camera](self.camera_device)
        self.camera.init_camera()
        self.camera_thread.set_camera(self.camera)
        # Init default parameters
        self.central_widget.init_default_camera_params()
        # Update menu exposure time slider
        min_expo, max_expo = self.camera.get_exposure_range()
        if min_expo < 100:
            min_expo = 100
        if max_expo > 400000:
            max_expo = 400000
        self.central_widget.main_menu.expo_widget.set_min_max_values(min_expo/1000,
                                                                     max_expo/1000)
        # Start Thread
        self.image_bits_depth = get_bits_per_pixel(self.camera.get_color_mode())
        self.camera_thread.start()

    def action_aoi_selected(self, event):
        """Action performed when an event occurred in the aoi_select options widget."""
        if event == 'aoi_selected':
            x, y = self.central_widget.options_widget.get_position()
            w, h = self.central_widget.options_widget.get_size()
            self.aoi = (x, y, w, h)
            menu1 = self.central_widget.get_list_menu('type1')
            self.central_widget.main_menu.set_enabled(menu1, True)

            # Histogram of the global image.
            self.central_widget.top_right_widget.set_bit_depth(self.image_bits_depth)
            self.central_widget.top_right_widget.set_image(self.raw_image, fast_mode=self.fast_mode)
            self.central_widget.top_right_widget.update_info()
            # Histogram of the AOI.
            if self.aoi is not None:
                aoi_array = get_aoi_array(self.raw_image, self.aoi)
                if aoi_array.shape[0]*aoi_array.shape[1] < 1000:
                    fast = False
                else:
                    fast = True
                self.central_widget.bot_right_widget.set_bit_depth(self.image_bits_depth)
                self.central_widget.bot_right_widget.set_image(aoi_array, fast_mode=fast)
                self.central_widget.bot_right_widget.update_info()
            # Display the image with a rectangle for the AOI.
            self.central_widget.update_image(aoi_disp=True)

    def action_histo_space(self, event):
        """Action performed when an event occurred in the histo_space options widget."""
        image = get_aoi_array(self.raw_image, self.aoi)
        if event == 'snap':
            self.saved_image = self.raw_image
            self.central_widget.top_right_widget.set_image(image)
            self.central_widget.top_right_widget.update_info()
        elif event == 'live':
            self.central_widget.top_right_widget.set_image(image, self.fast_mode)
            self.central_widget.top_right_widget.update_info()
        elif event == 'save_png':
            if self.saved_image is not None:
                image = get_aoi_array(self.saved_image, self.aoi)
                bins = np.linspace(0, 2 ** self.image_bits_depth, 2 ** self.image_bits_depth+1)
                bins, hist_data = process_hist_from_array(image, bins)
                save_hist(image, hist_data, bins,
                               f'Image Histogram',
                               f'image_histo.png')
        # Display the AOI.
        self.central_widget.update_image(aoi=True)

    def action_histo_time(self, event):
        """Action performed when an event occurred in the histo_time options widget."""
        if event == 'start':
            self.central_widget.options_widget.start_acquisition()
            self.central_widget.options_widget.set_enabled_save(False)
        elif event == 'acq_end':
            pixels = self.central_widget.options_widget.get_pixels(0)
            self.central_widget.options_widget.set_enabled_save()
            self.central_widget.top_right_widget.set_bit_depth(self.image_bits_depth)
            self.central_widget.top_right_widget.set_image(pixels)
            self.central_widget.top_right_widget.update_info()
        elif event == 'pixel_changed':
            pixel_index = self.central_widget.options_widget.get_pixel_index()
            pixels = self.central_widget.options_widget.get_pixels(pixel_index)
            self.central_widget.top_right_widget.set_bit_depth(self.image_bits_depth)
            self.central_widget.top_right_widget.set_image(pixels)
            self.central_widget.top_right_widget.update_info()
        elif event == 'save_hist_time':
            pixel_index = self.central_widget.options_widget.get_pixel_index()
            pixels = self.central_widget.options_widget.get_pixels(pixel_index)
            bins = np.linspace(0, 2 ** self.image_bits_depth, 2 ** self.image_bits_depth+1)
            bins, hist_data = process_hist_from_array(pixels, bins)
            save_hist(pixels, hist_data, bins,
                      f'Time Histogram - Pixel {pixel_index+1}',
                      f'time_histo_pixel_{pixel_index+1}.png')

    def action_quantize_image(self, event):
        """Action performed when an event occurred in the quantization options widget."""
        aoi_array_raw = get_aoi_array(self.raw_image, self.aoi)
        aoi_array = get_aoi_array(self.image, self.aoi)
        if event == 'quantized':
            bit_depth = self.central_widget.options_widget.get_bits_depth()
            quantized_image = quantize_image(aoi_array, bit_depth)
            self.central_widget.top_right_widget.set_image_from_array(quantized_image << (8-bit_depth))
            self.central_widget.bot_right_widget.set_bit_depth(bit_depth, histo1=self.image_bits_depth)
            self.central_widget.bot_right_widget.set_images(aoi_array_raw, quantized_image)

    def action_sampling_image(self, event):
        """Action performed when an event occurred in the sampling options widget."""
        aoi_array = get_aoi_array(self.image, self.aoi)
        if event == 'resampled':
            sample_factor = self.central_widget.options_widget.get_sample_factor()
            small_image, downsampled_image = downsample_and_upscale(aoi_array, sample_factor)
            self.central_widget.top_right_widget.set_image_from_array(downsampled_image)
            self.central_widget.bot_right_widget.set_bit_depth(8)
            self.central_widget.bot_right_widget.set_images(aoi_array, small_image)

    def action_contrast_brightness(self, event):
        """Action performed when an event occurred in the erosion/dilation options widget."""
        if event == 'check_diff:0':
            self.check_diff = False
        elif event == 'check_diff:1':
            self.check_diff = True
        elif event == 'contrast_brightness':
            self.central_widget.submode = 'contrast_brightness'

        aoi_array = get_aoi_array(self.image, self.aoi)
        if self.central_widget.submode == 'contrast_brightness':
            contrast_value = self.central_widget.options_widget.get_contrast()
            brightness_value = self.central_widget.options_widget.get_brightness()
            eroded = contrast_brightness_image(aoi_array, contrast_value, brightness_value)
        else:
            eroded = aoi_array
        self.central_widget.bot_right_widget.set_bit_depth(8)
        self.central_widget.bot_right_widget.set_images(aoi_array, eroded)
        if self.check_diff:
            eroded = aoi_array - eroded
        self.central_widget.top_right_widget.set_image_from_array(eroded)

    def action_enhance_contrast(self, event):
        """Action performed when an event occurred in the erosion/dilation options widget."""
        aoi_array = get_aoi_array(self.image, self.aoi)
        print(f'Shape = {self.image.shape}')
        delta_image_depth = (self.image_bits_depth - 8)  # Power of 2 for depth conversion
        min_value = int(self.central_widget.options_widget.get_min() // 2**delta_image_depth)
        max_value = int(self.central_widget.options_widget.get_max() // 2**delta_image_depth)
        max_range = 255
        gain = max_range/(max_value-min_value)
        output_image = ((self.image.astype(np.int16)-min_value+1) * gain).astype(np.int16)
        output_image[output_image > max_range] = 255
        output_image[output_image <= 1] = 0
        output_image = output_image.astype(np.uint8)

        self.central_widget.bot_right_widget.set_bit_depth(8)
        self.central_widget.bot_right_widget.set_images(aoi_array, output_image)
        if self.check_diff:
            output_image = aoi_array - output_image
        self.central_widget.top_right_widget.set_image_from_array(output_image)

    def action_threshold(self, event):
        """Action performed when an event occurred in the threshold options widget."""
        if event == 'threshold_type':
            threshold_index = self.central_widget.options_widget.get_threshold_type_index()
            self.central_widget.submode = threshold_index
        aoi_array_raw = get_aoi_array(self.raw_image, self.aoi)

        threshold_value = int(self.central_widget.options_widget.get_threshold_value())
        threshold_value_hat = int(self.central_widget.options_widget.get_threshold_hat_value())

        if self.central_widget.submode == 1: # Normal threshold
            ret, output_image = cv2.threshold(aoi_array_raw, threshold_value, 255, cv2.THRESH_BINARY)
        elif self.central_widget.submode == 2: # Inverted threshold
            ret, output_image = cv2.threshold(aoi_array_raw, threshold_value,
                                              255, cv2.THRESH_BINARY_INV)
        elif self.central_widget.submode == 3: # Hat threshold
            output_image = cv2.inRange(aoi_array_raw, threshold_value, threshold_value_hat)
        else:
            delta_depth = self.image_bits_depth - 8
            output_image = (aoi_array_raw >> delta_depth).astype(np.uint8)

        self.central_widget.bot_right_widget.set_bit_depth(self.image_bits_depth)
        self.central_widget.bot_right_widget.set_image(aoi_array_raw, fast_mode=True)
        self.central_widget.top_right_widget.set_image_from_array(output_image)

    def action_erosion_dilation(self, event):
        """Action performed when an event occurred in the erosion/dilation options widget."""
        if event == 'check_diff:0':
            self.check_diff = False
        elif event == 'check_diff:1':
            self.check_diff = True
        elif event == 'erosion':
            self.central_widget.submode = 'erosion'
        elif event == 'dilation':
            self.central_widget.submode = 'dilation'
        elif event == 'opening':
            self.central_widget.submode = 'opening'
        elif event == 'closing':
            self.central_widget.submode = 'closing'

        if event == 'resize':
            self.central_widget.options_widget.resize_kernel()

        if event == 'pixel':
            self.kernel_type = None
        elif event == 'cross':
            self.kernel_type = 'cross'
        elif event == 'rect':
            self.kernel_type = 'rect'
        elif event == 'ellip':
            self.kernel_type = 'ellip'

        kernel = self.central_widget.options_widget.get_kernel().T
        if self.kernel_type == 'cross':
            kernel = get_cross_kernel(kernel.shape[0])
            self.central_widget.options_widget.set_kernel(kernel)
        elif self.kernel_type == 'rect':
            kernel = get_rect_kernel(kernel.shape[0])
            self.central_widget.options_widget.set_kernel(kernel)
        elif self.kernel_type == 'ellip':
            kernel = get_ellip_kernel(kernel.shape[0])
            self.central_widget.options_widget.set_kernel(kernel)
        else:
            self.central_widget.options_widget.inactivate_kernel()
            self.central_widget.options_widget.set_kernel(kernel.T)
        self.central_widget.options_widget.repaint()

        aoi_array = get_aoi_array(self.image, self.aoi)
        if self.central_widget.submode == 'erosion':
            eroded = erode_image(aoi_array, kernel)
        elif self.central_widget.submode == 'dilation':
            eroded = dilate_image(aoi_array, kernel)
        elif self.central_widget.submode == 'opening':
            eroded = opening_image(aoi_array, kernel)
        elif self.central_widget.submode == 'closing':
            eroded = closing_image(aoi_array, kernel)
        elif self.central_widget.submode == 'gradient':
            eroded = gradient_image(aoi_array, kernel)
        else:
            eroded = aoi_array
        self.central_widget.bot_right_widget.set_bit_depth(8)
        self.central_widget.bot_right_widget.set_images(aoi_array, eroded)
        if self.check_diff:
            eroded = aoi_array - eroded
        self.central_widget.top_right_widget.set_image_from_array(eroded)

    def action_filter_smooth(self, event):
        """Action performed when an event occurred in the erosion/dilation options widget."""
        if event == 'check_diff:0':
            self.check_diff = False
        elif event == 'check_diff:1':
            self.check_diff = True

        aoi_array = get_aoi_array(self.image, self.aoi)
        eroded = aoi_array #self.central_widget.options_widget.get_selection(aoi_array)
        '''
        self.central_widget.bot_right_widget.set_bit_depth(8)
        self.central_widget.bot_right_widget.set_images(aoi_array, eroded)
        '''
        if self.check_diff:
            eroded = aoi_array - eroded
        self.central_widget.top_right_widget.set_image_from_array(eroded)


    def resizeEvent(self, event):
        """
        Action performed when the main window is resized.
        :param event: Object that triggered the event.
        """
        self.central_widget.update_size()

    def closeEvent(self, event):
        """
        closeEvent redefinition. Use when the user clicks
        on the red cross to close the window
        """
        reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            print('Closing App')
            if self.camera is not None:
                print('With camera')
                if self.brand_camera == 'IDS':
                    self.camera_thread.stop(timeout=False)
                else:
                    self.camera_thread.stop()
                self.camera.disconnect()
            event.accept()
        else:
            event.ignore()



app = QApplication(sys.argv)
app.setStyleSheet(StyleSheet)
window = MainWindow()
window.showMaximized()
sys.exit(app.exec())