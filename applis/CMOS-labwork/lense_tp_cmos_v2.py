# -*- coding: utf-8 -*-
"""GUI for CMOS Sensor Labwork @ LEnsE.

/!\ Only for IDS USB 2.0 CMOS camera
Based on pyueye library

---------------------------------------
(c) 2023 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2023/07/02


Authors
-------
    Julien VILLEMEJANE

TO DO
-----
- Add warning popup when reset !!
- Add Snap possibilities to analyze only one frame

"""

''' SEE : 
https://www.pythonguis.com/tutorials/plotting-pyqtgraph/

'''

import sys
import os
import cv2
import datetime

# Standard Libraries
import numpy as np
from PyQt6.QtCore import QTimer
# Third pary imports
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtWidgets import QLabel, QFileDialog

import SupOpNumTools.camera.cameraIDSdisplayQt6 as camDisp
import SupOpNumTools.camera.cameraIDS as camIDS
from CMOSMenu import CMOSMenu, progress_bar_style
from SupOpNumTools.pyqt6.HistWidget import HistWidget
from SupOpNumTools.pyqt6.TimeChartWidget import TimeChartWidget


# Local libraries


class MainWindow(QMainWindow):
    """
    MainWindow of the application.
    Children of QMainWindow 
    ---
    GUI for CMOS Sensor caracterization - PyQt5
    - 3 columns : parameters, camera display, pixels caracterization graphs
    - IDS camera v2 (USB2 only)

    Attributes
    ----------
    camera: camera
        Camera uses in the application - IDS CMOS Sensor only (for the moment).
    
    Methods
    -------
    connectCam():
        Initializes the USB connexion to the camera.
    closeEvent(event):
        Closes the application properly.
    """

    def __init__(self):
        super().__init__(parent=None)
        self.run_live_started = False
        self.acquisition_started = False

        ''' Main Window parameters '''
        self.setWindowTitle("CMOS Sensor - Labwork / LEnsE 2024")
        # self.setGeometry(100, 100, 1000, 600)
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        ''' Layout Manager '''
        self.main_layout = QGridLayout()
        self.main_widget.setLayout(self.main_layout)

        ''' Graphical Elements '''
        # Main Menu
        self.menu = CMOSMenu()
        self.main_layout.addWidget(self.menu, 1, 0)
        self.menu_progress_value = 0
        # Main Title of the window
        self.label_lense = QLabel('LEnsE - CMOS Sensor')
        style = "font-size:18px; font-weight:bold; padding:10px; color:Navy;"
        self.label_lense.setStyleSheet(style)
        self.main_layout.addWidget(self.label_lense, 0, 0, 1, 3)
        self.stop_value = 0  # stop value of the progress bar

        # IDS Camera
        self.nb_bits_per_pixel = 0
        self.camera = None
        self.raw_data = np.array([])
        self.display_cam = camDisp.CameraIDSDisplay(self.camera)
        self.display_cam.connected_signal.connect(self.connect_cam)
        self.main_layout.addWidget(self.display_cam, 1, 1)
        self.camera_params = camDisp.cameraIDSmainParams()
        self.camera_params.setEnabled(False)
        self.main_layout.addWidget(self.camera_params, 2, 0)
        self.data_ready = False
        self.snap_ready = False
        self.aoi_mode = False  # False if all frame mode, True if aoi mode
        self.x_aoi = 0
        self.y_aoi = 0
        self.w_aoi = 0
        self.h_aoi = 0

        # Time-dependent Chart
        self.chart_widget = TimeChartWidget()
        self.chart_widget.set_title('Time-Dependent pixel value')
        self.chart_widget.set_information('')
        self.chart_widget.set_background('white')
        self.chart_widget.disable_chart()
        self.main_layout.addWidget(self.chart_widget, 1, 2)
        self.time_data = np.array([])
        self.time_axis = np.array([])

        # Frame Histogram
        self.frame_hist_widget = HistWidget()
        self.frame_hist_widget.set_title('Frame Histogram')
        self.frame_hist_widget.set_information('')
        self.frame_hist_widget.set_background('white')
        self.main_layout.addWidget(self.frame_hist_widget, 2, 1)
        self.bins = np.array([])
        self.mean_frame_acq = []
        self.stdev_frame_acq = []

        # Pixel Histogram
        self.pixel_hist_widget = HistWidget()
        self.pixel_hist_widget.set_title('Central Pixel Histogram')
        self.pixel_hist_widget.set_information('')
        self.pixel_hist_widget.set_background('white')
        self.main_layout.addWidget(self.pixel_hist_widget, 2, 2)

        # # Column Size
        self.main_layout.setColumnStretch(0, 1)  # Camera Parameters
        self.main_layout.setColumnStretch(1, 2)  # Camera Display and Frame Hist
        self.main_layout.setColumnStretch(2, 2)  # Pixel Hist and Time Chart

        ''' Events '''
        self.timer_time = int(1000.0)
        self.timer_update = QTimer()
        self.timer_update.stop()
        self.timer_update.timeout.connect(self.refresh_app)
        self.menu.menu_signal.connect(self.menu_action)
        self.camera_params.fps_signal.connect(self.update_params)
        self.camera_params.expo_signal.connect(self.update_params)
        self.camera_params.blacklevel_signal.connect(self.update_params)
        self.showMaximized()
        print('Init Win OK')

    def refresh_pixels(self):
        """
        Refresh data of the chart in RunLive or Acquisition mode

        Returns
        -------
        None

        """
        if self.acquisition_started or self.run_live_started:
            # Central Pixel
            size_raw = len(self.raw_data)
            if size_raw != 0:
                # Adding a new point in time_data and time_axis lists
                self.time_data = np.append(self.time_data, self.raw_data[(size_raw // 2)])
                self.time_axis = np.append(self.time_axis, len(self.time_data) - 1)

                # Depending on Run Live or Acquisition mode, refresh graph at each loop or only 1 times on 10
                refresh_graphs = False
                if self.acquisition_started:
                    if self.menu_progress_value % 10 == 9:
                        refresh_graphs = True
                else:
                    refresh_graphs = True

                # Refresh histograms
                # Zoom on the histograms / Zoom around mean
                if refresh_graphs:
                    # Time Chart
                    nb_of_value = len(self.time_data)
                    if nb_of_value < 100:
                        self.chart_widget.set_data(self.time_axis, self.time_data)
                    else:
                        self.chart_widget.set_data(self.time_axis[nb_of_value - 100:nb_of_value],
                                                   self.time_data[nb_of_value - 100:nb_of_value])
                    self.chart_widget.refresh_chart()
                    # Histogram
                    if nb_of_value == 1:
                        mean_pix = self.time_data[0]
                        stdev_pix = 10
                    else:
                        mean_pix = np.mean(self.time_data)
                        stdev_pix = np.std(self.time_data)
                    bins_pixel = np.arange(mean_pix-3*stdev_pix, mean_pix+3*stdev_pix)
                    self.pixel_hist_widget.set_data(self.time_data, bins_pixel)
                    self.pixel_hist_widget.refresh_chart()
                ''' NO ZOOM
                bins_pixel = np.linspace(0, 2**self.nb_bits_per_pixel-1, 2**self.nb_bits_per_pixel)
                self.pixel_hist_widget.set_data(self.time_data, bins_pixel)
                self.pixel_hist_widget.refresh_chart()
                '''

    def refresh_frame(self):
        """
        Update histogram data from raw_data.

        Returns
        -------
        None

        """
        # Frame Histogram
        self.frame_hist_widget.set_data(self.raw_data, self.bins)
        self.frame_hist_widget.refresh_chart()

    def refresh_app(self):
        """
        Update camera display (depending on the mode of acquisition : Run Live or Acquisition) and all charts

        Returns
        -------
        None

        """
        if self.run_live_started:   # refresh the image in the interface
            self.raw_data = self.display_cam.refresh()
        elif self.acquisition_started:  # no refresh
            self.raw_data = self.display_cam.get_raw_data()
        # Refresh all the charts
        if self.acquisition_started or self.run_live_started:
            self.refresh_pixels()
            self.refresh_frame()
        if self.acquisition_started:
            self.menu_progress_value = len(self.time_data)
            self.menu.update_progress_bar(self.menu_progress_value)

            # Mean and stdev stored in 2 lists
            mean_ = round(np.mean(self.raw_data), 2)
            stdev_ = round(np.std(self.raw_data), 2)
            self.mean_frame_acq.append(mean_)
            self.stdev_frame_acq.append(stdev_)

            # At the end of acquisition
            if self.menu_progress_value == self.stop_value:
                self.data_ready = True
                self.menu.stop_live_action()
                self.frame_hist_widget.update_infos()
                self.pixel_hist_widget.update_infos()
                self.chart_widget.update_infos()

                # Zoom on the histograms
                mean_pix = np.mean(self.time_data)
                stdev_pix = np.std(self.time_data)
                bins_pixel = np.arange(mean_pix-3*stdev_pix, mean_pix+3*stdev_pix)
                self.pixel_hist_widget.set_data(self.time_data, bins_pixel)
                self.pixel_hist_widget.refresh_chart()
                
                print('END OF ACQ')
        elif self.run_live_started:
            self.frame_hist_widget.update_infos()
            self.chart_widget.update_infos()
            self.pixel_hist_widget.update_infos()

    def update_params(self, event=''):
        """
        Event function when camera parameters are updated.

        Returns
        -------
        None

        """
        if event == 'fps':
            fps = self.camera_params.get_FPS()
            self.display_cam.set_frame_rate(fps)
            expo_min, expo_max = self.display_cam.get_exposure_range()
            self.camera_params.set_exposure_time_range(expo_min + 1, expo_max)
            self.camera_params.set_exposure_time(self.display_cam.get_exposure_time())
        elif event == 'expo':
            expo = self.camera_params.get_exposure_time()
            self.display_cam.set_exposure_time(expo)
        elif event == 'blacklevel':
            blacklevel = self.camera_params.get_blacklevel()
            self.display_cam.set_blacklevel(blacklevel)

    def menu_action(self, event):
        """
        Event function when buttons of the menu are pressed.

        Returns
        -------
        None

        """
        if event == 'start':    # Start acquisition (Run Live Mode)
            self.run_live_started = True
            self.acquisition_started = False
            self.display_cam.stop_cam()
            # Select best color mode for camera (12 bits if possible)
            if self.display_cam.set_color_mode("MONO12") is False:
                if self.display_cam.set_color_mode("MONO10") is False:
                    self.display_cam.set_color_mode("MONO8")
            # Start camera and display image on the interface
            self.display_cam.start_cam()
            self.display_cam.refresh()
            self.timer_update.start()
        elif event == 'stop':   # Stop acquisition
            self.run_live_started = False
            self.acquisition_started = False
            self.timer_update.stop()
        elif event == 'reset':  # Reset data
            self.time_axis = np.array([])
            self.time_data = np.array([])
            self.raw_data = np.array([])
            self.data_ready = False
            self.run_live_started = False
            self.acquisition_started = False
            self.chart_widget.clear_graph()
            self.frame_hist_widget.clear_graph()
            self.pixel_hist_widget.clear_graph()
            self.menu_progress_value = 0
            self.menu.update_progress_bar(self.menu_progress_value)
            self.pixel_hist_widget.update_infos(False)
            self.chart_widget.update_infos(False)
            self.frame_hist_widget.update_infos(False)
        elif event == 'acquisition':    # Start acquisition of N points
            self.time_axis = np.array([])
            self.time_data = np.array([])
            # Test if progression bar is full or not
            if self.menu.set_max_progress_bar():
                # Update data
                self.stop_value = self.menu.get_max_progress_bar_value()
                self.chart_widget.update_infos(False)
                self.frame_hist_widget.update_infos(False)
                self.pixel_hist_widget.update_infos(False)
                self.acquisition_started = True
                self.display_cam.start_cam()
                self.timer_update.start()
            else:
                self.acquisition_started = False
        elif event == 'aoi':    # Update the area of interest at x,y position
            self.timer_update.stop()
            x_aoi, y_aoi, w_aoi, h_aoi = self.menu.get_aoi_size()
            max_w = self.display_cam.get_camera_width()
            max_h = self.display_cam.get_camera_height()
            # Set new values of AOI
            self.display_cam.set_aoi(self.x_aoi, self.y_aoi, self.w_aoi, self.h_aoi)
        elif event == 'all_frame':  # Update the area of interest to all frame
            self.timer_update.stop()
            max_width = self.display_cam.get_camera_width()
            max_height = self.display_cam.get_camera_height()
            self.display_cam.set_aoi(0, 0, max_width, max_height)
        elif event == 'center':     # Update the area of interest in the center of the camera
            self.timer_update.stop()
            self.x_aoi, self.y_aoi, self.w_aoi, self.h_aoi = self.menu.get_aoi_size()
            # Centering AOI and size of 100 x 100
            max_width = self.display_cam.get_camera_width()
            max_height = self.display_cam.get_camera_height()
            self.aoi_mode = self.menu.get_aoi_mode()
            x0 = max_width // 2 - self.w_aoi // 2
            y0 = max_height // 2  - self.h_aoi // 2
            self.display_cam.set_aoi(x0, y0, self.w_aoi, self.h_aoi)
        elif event == 'save_data':  # Save data to CSV files
            if self.data_ready:
                # Open a dialog File Window
                dialog = QFileDialog()
                dialog.setFileMode(QFileDialog.FileMode.Directory)
                dialSuccess = dialog.exec()
                # Select dir and name of first CSV
                if dialSuccess:
                    dirName = dialog.selectedFiles()[0]
                    # Save 2 CSV files : pixel time chart and frame mean and stdev values
                    print(dirName)
                    file_name = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S_")
                    # Create filename _pixel_time.csv and _frame_mean.csv
                    file_name1 = dirName + '/' + file_name + '_pixel_time.csv'
                    file_name2 = dirName + '/' + file_name + '_frame_mean.csv'
                    # Pixel vs time data
                    data_to_save = np.zeros((len(self.time_data), 2))
                    data_to_save[:, 0] = self.time_axis
                    data_to_save[:, 1] = self.time_data
                    np.savetxt(file_name1, data_to_save, delimiter=";", fmt='%f')
                    # Pixel vs time data
                    data_to_save = np.zeros((len(self.time_data), 3))
                    data_to_save[:, 0] = np.arange(1, len(self.time_data)+1)
                    data_to_save[:, 1] = self.mean_frame_acq
                    data_to_save[:, 2] = self.stdev_frame_acq
                    np.savetxt(file_name2, data_to_save, delimiter=";", fmt='%f')
                    print('Data Saved')
                    # self.data_ready = False

                else:
                    print('Error in destination / No File Saved')
            else:
                print('No Data To Save')

        elif event == 'save_snap':      # Save image in a RAW format or PNG
            print('TO TEST')
            if self.snap_ready:
                default_dir = os.path.expanduser('~')
                default_filename = os.path.join(default_dir, 'data_file')
                file_name, _ = QFileDialog.getSaveFileName(
                    self, "Save Image", default_filename, "Image File (*.png)"
                )
                if file_name:
                    print(file_name)
                    image = self.display_cam.get_image_raw()
                    cv2.imwrite(file_name, image)
                    print('Image Save')
                else:
                    print('File Error')
            else:
                print('No Image to Save')
        elif event == 'snap':       # Take an image and update the interface (camera display and charts)
            print('TO DO')
            '''
            if self.display_cam.set_color_mode("MONO12") is False:
                if self.display_cam.set_color_mode("MONO10") is False:
                    self.display_cam.set_color_mode("MONO8")
            self.display_cam.start_cam()
            '''
            '''
            self.display_cam.refresh()
            self.display_cam.stop_cam()
            self.snap_ready = True
            self.time_axis = np.array([])
            self.time_data = np.array([])
            self.raw_data = np.array([])
            self.data_ready = False
            self.run_live_started = False
            self.acquisition_started = False
            self.chart_widget.clear_graph()
            self.frame_hist_widget.clear_graph()
            self.pixel_hist_widget.clear_graph()
            self.pixel_hist_widget.update_infos(False)
            self.chart_widget.update_infos(False)
            self.refresh_app()
            self.refresh_frame()
            self.frame_hist_widget.update_infos()
            '''
            pass
        else:
            print('No Event')

    def set_enable_graph(self):
        """
        Enable all the chart and histograms widgets.

        Returns
        -------
        None

        """
        self.chart_widget.enable_chart()
        self.pixel_hist_widget.enable_chart()
        self.frame_hist_widget.enable_chart()

    def connect_cam(self):
        """
        Initializes the USB connexion to the camera.
        All the main parameters of the camera are already set in the cameraDisplayQt6 module

        Returns
        -------
        None.

        """
        if self.display_cam.is_camera_connected():
            print('Camera Connected')
            self.menu.set_enable()
            self.camera = self.display_cam.get_camera()
            self.nb_bits_per_pixel = self.display_cam.get_nb_bits_per_pixel()
            self.bins = np.linspace(0, 2 ** self.nb_bits_per_pixel, (2 ** self.nb_bits_per_pixel) + 1)
            self.timer_time = int(1000.0 / self.display_cam.get_frame_rate()) + 100
            fps_min, fps_max = self.display_cam.get_frame_rate_range()
            expo_min, expo_max = self.display_cam.get_exposure_range()
            self.camera_params.set_FPS_range(fps_min, fps_max)
            self.camera_params.set_FPS(self.display_cam.get_frame_rate())
            self.camera_params.set_exposure_time_range(expo_min + 1, expo_max)
            expo = int((expo_max-expo_min)/2 + expo_min)
            self.camera_params.set_exposure_time(expo)
            self.camera_params.set_blacklevel(self.display_cam.get_blacklevel())
            self.camera_params.set_pixel_clock(self.display_cam.get_pixel_clock())
            self.camera_params.setEnabled(True)
            self.set_enable_graph()
            self.w_aoi = self.display_cam.get_camera_width()
            self.h_aoi = self.display_cam.get_camera_height()
            self.menu.set_width_height_camera(self.w_aoi, self.h_aoi)
            self.acquisition_started = False
            self.run_live_started = False
            self.menu.set_aoi_mode(False)
            self.timer_update.setInterval(self.timer_time)
            self.timer_update.stop()
            self.display_cam.start_cam()
            self.display_cam.refresh()
            self.display_cam.stop_cam()

    def closeEvent(self, event):
        """
        Closes the application properly.

        Parameters
        ----------
        event : event
            Event that triggers the action.

        Returns
        -------
        None.

        """
        self.menu_action(event='stop')
        if self.camera is not None:
            self.display_cam.disconnect()
        QApplication.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(progress_bar_style)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
