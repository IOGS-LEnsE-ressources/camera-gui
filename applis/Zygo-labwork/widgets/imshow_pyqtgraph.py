# -*- coding: utf-8 -*-
"""
ImageWidget for displaying 2D images with a specified colormap in a pyQtGraph widget.

---------------------------------------
(c) 2024 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2024/06/13

Authors
-------
    Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
import numpy as np
import sys
import pyqtgraph as pg
import matplotlib.cm as cm

from lensepy.css import *  # Import CSS styles if needed

# CSS style for the widget
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"


class ImageWidget(QWidget):
    """
    Widget used to display 2D images with a specified colormap.

    Attributes
    ----------
    title : str
        Title of the image display widget.
    plot_widget : pg.GraphicsLayoutWidget
        pyQtGraph widget to display the image
    image_item : pg.ImageItem
        pyQtGraph ImageItem to display the image data

    Methods
    -------
    set_image_data(image_data: np.ndarray) -> None
        Set the image data to display.
    set_title(title: str) -> None
        Set the title of the image display widget.
    set_information(infos: str) -> None
        Set information text displayed below the image.
    set_background(css_color: str) -> None
        Set the background color of the widget.
    clear_graph() -> None
        Clear the image display widget.
    disable_chart() -> None
        Erase all widgets from the layout.
    enable_chart() -> None
        Enable and display all widgets in the layout.
    """

    def __init__(self) -> None:
        """
        Initialize the image display widget.
        """
        super().__init__()
        self.title: str = ''  # Initialize title as an empty string
        self.layout: QVBoxLayout = QVBoxLayout()  # Create a vertical layout for the widget

        self.master_layout: QVBoxLayout = QVBoxLayout()  # Create a master layout for the widget
        self.master_widget: QWidget = QWidget()  # Create a master widget to hold the layout

        # Title label setup
        self.title_label: QLabel = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(styleH1)

        # Information label setup
        self.info_label: QLabel = QLabel('')
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet(styleH3)

        # pyQtGraph GraphicsLayoutWidget setup
        self.plot_widget: pg.GraphicsLayoutWidget = pg.GraphicsLayoutWidget()
        self.plot_widget.setMinimumWidth(400)
        self.plot_widget.setMinimumHeight(400)

        # ImageItem setup
        self.image_item: pg.ImageItem = pg.ImageItem()
        self.view_box: pg.ViewBox = self.plot_widget.addViewBox()  # Add a ViewBox to the GraphicsLayoutWidget
        self.view_box.addItem(self.image_item)  # Add the ImageItem to the ViewBox
        self.view_box.setAspectLocked(True)  # Lock the aspect ratio to ensure the image displays correctly

        # Set up the layout hierarchy
        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

        # Enable chart to add widgets to the layout
        self.enable_chart()

    def set_image_data(self, image_data: np.ndarray) -> None:
        """
        Set the image data to display.

        Parameters
        ----------
        image_data : np.ndarray
            2D array of image data.

        Returns
        -------
        None
            No return value.

        See Also
        --------
        matplotlib.cm.get_cmap : Function to retrieve a colormap.

        Notes
        -----
        This method applies the 'Magma' colormap from matplotlib to the input image data,
        enhancing visualization by mapping scalar values to colors.
        """
        # Apply colormap 'Magma' from matplotlib to the image data
        colormap = cm.get_cmap('magma')
        colored_image = colormap(image_data)

        # Set the colored image data to the ImageItem
        self.image_item.setImage(colored_image)

        # Adjust the view range to fit the image
        self.view_box.autoRange()

    def set_title(self, title: str) -> None:
        """
        Set the title of the image display widget.

        Parameters
        ----------
        title : str
            Title of the image display widget.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method updates the title displayed at the top of the widget.

        See Also
        --------
        QLabel.setText : Method to set text for QLabel.
        """
        self.title = title
        self.title_label.setText(self.title)

    def set_information(self, infos: str) -> None:
        """
        Set information text displayed below the image.

        Parameters
        ----------
        infos : str
            Information to display below the image.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method updates the information text displayed below the image.

        See Also
        --------
        QLabel.setText : Method to set text for QLabel.
        """
        self.info_label.setText(infos)

    def set_background(self, css_color: str) -> None:
        """
        Set the background color of the widget.

        Parameters
        ----------
        css_color : str
            Color in CSS style.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method updates the background color of the widget using CSS styles.

        See Also
        --------
        QWidget.setStyleSheet : Method to set stylesheet for QWidget.
        """
        self.plot_widget.setBackground(css_color)
        self.setStyleSheet("background:" + css_color + ";")

    def clear_graph(self) -> None:
        """
        Clear the image display widget.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method clears the displayed image and resets the widget.
        """
        self.image_item.clear()

    def disable_chart(self) -> None:
        """
        Erase all widgets from the layout.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method removes all widgets from the layout, effectively disabling the chart display.
        """
        count = self.layout.count()
        for i in reversed(range(count)):
            item = self.layout.itemAt(i)
            widget = item.widget()
            widget.deleteLater()

    def enable_chart(self) -> None:
        """
        Enable and display all widgets in the layout.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method ensures all necessary widgets are added and displayed in the layout.
        """
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.plot_widget)
        self.layout.addWidget(self.info_label)


# -----------------------------------------------------------------------------------------------
# Example usage of the ImageWidget class
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
