import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
import time
import numpy as np
import threading

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from oct_lab_app import MainWindow

class ModesController:
    """
    Modes manager.
    """

    def __init__(self, main_app: "MainWindow"):
        """
        Default constructor.
        :param manager: Main manager of the application (ModesManager).
        """
        self.main_app: "MainWindow" = main_app
        self.mode = 'live'

        thread = threading.Thread(target=self.main_thread)
        thread.start()


    def main_thread(self):
        """

        :return:
        """
        if self.mode == 'live':
            print('LIVE')
            # Get images
            self.live_sequence()
            # Display images
            self.display_live_images()

        time.sleep(0.2) # TO TEST
        if self.mode != 'stop':
            thread = threading.Thread(target=self.main_thread)
            thread.start()
        else:
            print('End Thread')

    def display_live_images(self):
        """
        Display images for live mode in the main_view
        """
        image_view = self.main_app.central_widget
        print(image_view.image1_widget.size())
        piezo = self.main_app.piezo
        if piezo is not None and self.main_app.camera_connected:
            image_view.image1_widget.set_image_from_array(self.main_app.image1) #, 'Image 1')
            image_view.image2_widget.set_image_from_array(self.main_app.image2) #, 'Image 2')
            image_view.image_oct_graph.set_image_from_array(self.main_app.image_oct) # 'OCT')
        else:
            black = np.random.normal(size=(100, 100))
            image_view.image1_widget.set_image_from_array(black, "No Piezo or camera")
            image_view.image2_widget.set_image_from_array(black, "No Piezo or camera")
            image_view.image_oct_graph.set_image_from_array(black, "No Piezo or camera")
            print('No piezo or camera')


    def live_sequence(self, step_size=0.6, V0=0):
        piezo = self.main_app.piezo
        camera = self.main_app.camera
        if piezo is not None and self.main_app.camera_connected:
            piezo.set_voltage_piezo(V0)
            self.main_app.image1 = camera.get_image()
            print(f'Im1 ? {self.main_app.image1.shape} / Type ? {self.main_app.image1.dtype}')
            piezo.set_voltage_piezo(step_size + V0)
            self.main_app.image2 = camera.get_image()
            self.main_app.image_oct = np.sqrt((self.main_app.image1 - self.main_app.image2) ** 2)
        else:
            print('No Piezo or camera connected')

