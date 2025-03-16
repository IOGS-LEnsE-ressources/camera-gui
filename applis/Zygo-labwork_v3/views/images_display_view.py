# -*- coding: utf-8 -*-
"""*main_menu.py* file.

./views/main_menu.py contains MainMenu class to display the main menu.

--------------------------------------
| Menu |  TOPLEFT     |  TOPRIGHT    |
|      |              |              |
|      |--------------|--------------|
|      |SUB |OPTS|OPTS|  BOTRIGHT    |
|      |MENU| 1  | 2  |              |
--------------------------------------

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QLabel,
    QVBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QResizeEvent, QPixmap, QPainter, QColor, QFont
from lensepy.images.conversion import resize_image_ratio, resize_image, array_to_qimage



class ImagesDisplayView(QWidget):
    """
    Widget to display an image.
    """

    def __init__(self):
        """
        Default Constructor.
        :param parent: Parent widget of this widget.
        """
        super().__init__()
        self.width = 0
        self.height = 0
        # GUI Structure
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        # Objects
        self.image = None
        self.text = ''
        # GUI Elements
        self.image_display = QLabel('No Image to display')
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display.setScaledContents(False)
        self.layout.addWidget(self.image_display)

    def set_image_from_array(self, pixels: np.ndarray, text: str = '') -> None:
        """
        Display a new image from an array (Numpy)
        :param pixels: Array of pixels to display.
        :param text: Text to display in the top of the image.
        """
        self.text = text
        self.image = np.array(pixels, dtype='uint8')
        image_to_display = self.image.copy()
        image_to_display = np.squeeze(image_to_display)
        self.resizeEvent(None)
        if self.image.shape[1] > self.width or self.image.shape[0] > self.height:
            image_to_display = resize_image_ratio(self.image, self.height-50, self.width-50)
        qimage = array_to_qimage(image_to_display)

        if self.text != '':
            painter = QPainter(qimage)
            painter.setPen(QColor(0, 255, 255))   # Text color, white
            painter.setFont(QFont("Arial", 20))     # Size and police
            painter.drawText(20, 20, self.text)
            painter.end()
        pmap = QPixmap.fromImage(qimage)
        self.image_display.setPixmap(pmap)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        """
        Update view display when resizing the window.
        :param a0: Event.
        """
        new_size = self.size()
        self.width = new_size.width()
        self.height = new_size.height()

        if self.image is not None:
            image_to_display = self.image
            if self.image.shape[1] > self.width or self.image.shape[0] > self.height:
                image_to_display = resize_image_ratio(self.image, self.height-50, self.width-20)
            qimage = array_to_qimage(image_to_display)
            if self.text != '':
                painter = QPainter(qimage)
                painter.setPen(QColor(0, 255, 255))  # Text color, white
                painter.setFont(QFont("Arial", 20))  # Size and police
                painter.drawText(20, 20, self.text)
                painter.end()
            pmap = QPixmap.fromImage(qimage)
            self.image_display.setPixmap(pmap)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    main_widget = ImagesDisplayView()
    main_widget.setGeometry(100, 100, 100, 100)
    main_widget.show()

    # Random Image
    width, height = 256, 256
    random_pixels = np.random.randint(0, 256, (height, width), dtype=np.uint8)

    main_widget.set_image_from_array(random_pixels, 'Test')

    sys.exit(app.exec())