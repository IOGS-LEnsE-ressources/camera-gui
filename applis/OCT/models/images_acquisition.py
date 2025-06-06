
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from PyQt6.QtCore import QObject, QThread, pyqtSignal
import numpy as np
import time

#from models.motor_control import *

class ImageAcquisition(QObject):
    images_ready = pyqtSignal(np.ndarray, np.ndarray, np.ndarray)
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self._running = True

    def run(self):
        while self._running:
            # Get first image
            image1 = np.random.normal(loc=128, scale=40, size=(100, 100)).clip(0, 255).astype(np.uint8)
            image2 = np.random.normal(loc=128, scale=40, size=(100, 100)).clip(0, 255).astype(np.uint8)
            image_oct = np.sqrt((image1 - image2)**2)

            # Get second image

            self.images_ready.emit(image1, image2, image_oct)
            time.sleep(0.2)
        self.finished.emit()

    def stop(self):
        self._running = False