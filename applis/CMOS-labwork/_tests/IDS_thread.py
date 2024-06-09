import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QThread, pyqtSignal
import numpy as np
from ids_peak import ids_peak
from lensecam.ids.camera_ids import CameraIds

class CameraThread(QThread):
    image_acquired = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.running = True
        self.camera = None
        self.init_camera()

    def init_camera(self):
        # Initialisez la caméra IDS ici (utilisez l'API ids_peak)
        ids_peak.Library.Initialize()
        # Create a camera manager
        self.device_manager = ids_peak.DeviceManager.Instance()
        self.device_manager.Update()
        self.device = self.device_manager.Devices()[0].OpenDevice(ids_peak.DeviceAccessType_Exclusive)
        self.camera = CameraIds(self.device)
        self.camera.start_acquisition()

    def run(self):
        while self.running:
            # Acquisition de l'image de la caméra
            buffer = self.camera.datastream.waitForNextBuffer(1000)
            if buffer:
                image_array = buffer.getImage()
                self.image_acquired.emit(image_array)
                buffer.queueBuffer()

    def stop(self):
        self.running = False
        self.camera.stop_acquisition()
        self.wait()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.camera_thread = CameraThread()
        self.camera_thread.image_acquired.connect(self.update_image)
        self.camera_thread.start()

    def initUI(self):
        self.setWindowTitle("IDS Camera Display")
        self.setGeometry(100, 100, 800, 600)

        self.label = QLabel(self)
        self.label.resize(800, 600)

        layout = QVBoxLayout()
        layout.addWidget(self.label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_image(self, image_array):
        height, width, channel = image_array.shape
        bytes_per_line = 3 * width
        q_image = QImage(image_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.camera_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())