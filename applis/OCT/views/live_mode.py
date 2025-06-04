from _tests.camera_test import *
import sys
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout,
    QLabel, QComboBox, QPushButton, QFrame,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout, QApplication, QSlider, QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap, QImage
from controllers import MotCam_control
from controllers.MotCam_control import cameraControl


class liveWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__()

        self.control = cameraControl()
        self.layout = QHBoxLayout()
        self.parent = parent

        self.label = QLabel("Initialisation")
        self.label.setMinimumSize(320, 240)
        self.layout.addWidget(self.label)

        self.timer = QTimer()
        self.timer.timeout.connect(self.generate_frame)
        self.timer.start(33)

        self.setLayout(self.layout)

        self.control.update_exposure(300)

        self.control.motor.move_motor(3.09)

    def generate_frame(self, step_size = 2, V0 = 0):
        try:
            image1, image2, image = self.control.live_sequence(step_size, V0)
            if image is None:
                return
                return

            print(image.dtype())
            h, w = image.shape
            qimage = QImage(image.data, w, h, w, QImage.Format.Format_Grayscale8)
            pixmap = QPixmap.fromImage(qimage)
            scaled_pixmap = pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio)
            self.label.setPixmap(scaled_pixmap)

        except Exception as e:
            print(f"Erreur lors de l'affichage de la caméra : {e}")
            self.timer.stop()
            self.label.setText("Erreur : impossible de lire la caméra.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = liveWidget()
    widget.show()
    sys.exit(app.exec())