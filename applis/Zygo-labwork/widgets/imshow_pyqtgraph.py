# -*- coding: utf-8 -*-
"""ImageWidget for displaying 2D images with a specified colormap in a pyQtGraph widget.

---------------------------------------
(c) 2024 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2024/06/13

Authors
-------
    Dorian MENDES (Promo 2026)
"""

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
import numpy as np
import sys
import pyqtgraph as pg
import matplotlib.cm as cm

from lensepy.css import *

styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

class ImageWidget(QWidget):
    """
    Widget used to display 2D images with a specified colormap.
    Inherits from QWidget - can be placed in another widget and/or window
    ---

    Attributes
    ----------
    title : str
        title of the chart
    plot_widget : GraphicsLayoutWidget
        pyQtGraph Widget to display the image
    image_item : ImageItem
        pyQtGraph ImageItem to display the image data

    Methods
    -------
    set_image_data(image_data):
        Set the image data to display.
    set_title(title):
        Set the title of the chart.
    set_information(infos):
        Set informations in the informations label of the chart.
    set_background(css_color):
        Modify the background color of the widget.
    """

    def __init__(self):
        """
        Initialize the image display widget.

        """
        super().__init__()
        self.title = ''  # Title of the chart
        self.layout = QVBoxLayout()  # Main layout of the QWidget

        self.master_layout = QVBoxLayout()
        self.master_widget = QWidget()

        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(styleH1)

        # Option label
        self.info_label = QLabel('')
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet(styleH3)

        self.plot_widget = pg.GraphicsLayoutWidget()  # pyQtGraph GraphicsLayoutWidget

        # Increase the height of the plot widget
        self.plot_widget.setMinimumWidth(400)
        self.plot_widget.setMinimumHeight(400)

        self.image_item = pg.ImageItem()
        self.view_box = self.plot_widget.addViewBox()  # Add a ViewBox to the layout
        self.view_box.addItem(self.image_item)
        self.view_box.setAspectLocked(True)  # Lock the aspect ratio to ensure orthonormal graph

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

        # Enable chart to add widgets to the layout
        self.enable_chart()

    def set_image_data(self, image_data):
        """
        Set the image data to display.

        Parameters
        ----------
        image_data : 2D Numpy array
            Image data to display.

        Returns
        -------
        None.

        """
        # Apply colormap
        colormap = cm.get_cmap('magma')  # Get the 'Magma' colormap from matplotlib
        colored_image = colormap(image_data)  # Apply colormap to the image data

        # Set the colored image to the ImageItem
        self.image_item.setImage(colored_image)

        # Adjust view range to fit the image
        self.view_box.autoRange()

    def set_title(self, title):
        """
        Set the title of the chart.

        Parameters
        ----------
        title : str
            Title of the chart.

        Returns
        -------
        None.

        """
        self.title = title
        self.title_label.setText(self.title)

    def set_information(self, infos):
        """
        Set informations in the informations label of the chart.
        (bottom)

        Parameters
        ----------
        infos : str
            Informations to display.

        Returns
        -------
        None.

        """
        self.info_label.setText(infos)

    def set_background(self, css_color):
        """
        Modify the background color of the widget.

        Parameters
        ----------
        css_color : str
            Color in CSS style.

        Returns
        -------
        None.

        """
        self.plot_widget.setBackground(css_color)
        self.setStyleSheet("background:" + css_color + ";")

    def clear_graph(self):
        """
        Clear the main chart of the widget.

        Returns
        -------
        None

        """
        self.image_item.clear()

    def disable_chart(self):
        """
        Erase all the widget of the layout.

        Returns
        -------
        None

        """
        count = self.layout.count()
        for i in reversed(range(count)):
            item = self.layout.itemAt(i)
            widget = item.widget()
            widget.deleteLater()

    def enable_chart(self):
        """
        Display all the widget of the layout.

        Returns
        -------
        None

        """
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.plot_widget)
        self.layout.addWidget(self.info_label)


# -----------------------------------------------------------------------------------------------
# Only for testing
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("2D Image Display with Colormap")
        self.setGeometry(100, 100, 800, 600)

        self.centralWid = QWidget()
        self.layout = QVBoxLayout()

        self.image_widget = ImageWidget()
        self.image_widget.set_title('Image Display with Colormap')
        self.image_widget.set_information('Displaying a 2D image with colormap "Magma"')
        self.layout.addWidget(self.image_widget)

        # Example image data
        x = np.linspace(-10, 10, 100)
        y = np.linspace(-10, 10, 100)
        x, y = np.meshgrid(x, y)
        z = np.sin(np.sqrt(x**2 + y**2))

        self.image_widget.set_background('lightgray')
        self.image_widget.set_image_data(z)

        self.centralWid.setLayout(self.layout)
        self.setCentralWidget(self.centralWid)


# Launching as main for tests

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
