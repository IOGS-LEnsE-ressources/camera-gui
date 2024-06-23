import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QImage, QPixmap

class ImageViewer(QMainWindow):
    def __init__(self, image_array):
        super().__init__()
        self.setWindowTitle('Image Viewer')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Convert ndarray to QImage
        height, width, channel = image_array.shape
        bytes_per_line = 3 * width
        qimage = QImage(image_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

        # Display QImage using QLabel
        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap.fromImage(qimage))

        # Set up layout
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.image_label)

        self.setGeometry(100, 100, width, height)

if __name__ == '__main__':
    # Example ndarray (replace this with your own ndarray loading logic)
    image_array = np.random.randint(0, 256, size=(300, 400, 3), dtype=np.uint8)

    app = QApplication(sys.argv)
    viewer = ImageViewer(image_array)
    viewer.show()
    sys.exit(app.exec())
