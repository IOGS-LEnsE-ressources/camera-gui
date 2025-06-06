
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from PyQt6.QtCore import QObject, QThread, pyqtSignal
import numpy as np
import time

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from oct_lab_app import MainWindow


class ImageAcquisition(QObject):
    images_ready = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, main_app: "MainWindow"):
        super().__init__()
        self.main_app = main_app
        self._running = True

    def run(self):
        while self._running:
            # Get images
            piezo = self.main_app.piezo
            camera = self.main_app.camera
            if piezo is not None and self.main_app.camera_connected:
                if not self.main_app.camera_acquiring:
                    print("Start ACQUISITION")
                    camera.alloc_memory()
                    camera.start_acquisition()
                    self.main_app.camera_acquiring = True
            else:
                print('No Piezo or camera connected')
            time.sleep(0.1)
            self.images_ready.emit()
        self.finished.emit()

    def stop(self):
        self._running = False