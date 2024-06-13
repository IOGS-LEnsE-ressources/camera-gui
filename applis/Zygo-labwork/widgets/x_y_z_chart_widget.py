# -*- coding: utf-8 -*-
"""Surface3DWidget for displaying data on a 3D surface.

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

from PyQt6.QtWidgets import QApplication
import numpy as np
import sys
from matplotlib import cm

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
import pyqtgraph.opengl as gl

from lensepy.css import *

styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"


class Surface3DWidget(QWidget):
    """
    Widget used to display data in a 3D surface chart.
    Children of QWidget - QWidget can be put in another widget and / or window
    ---

    Attributes
    ----------
    title : str
        title of the chart
    plot_chart_widget : GLViewWidget
        pyQtGraph Widget to display chart
    plot_x_data : Numpy array
        value to display on X axis
    plot_y_data : Numpy array
        value to display on Y axis
    plot_z_data : Numpy array
        value to display on Z axis

    Methods
    -------
    set_data(x_axis, y_axis, z_axis):
        Set the X, Y and Z axis data to display on the chart.
    refresh_chart():
        Refresh the data of the chart.
    set_title(title):
        Set the title of the chart.
    set_information(infos):
        Set informations in the informations label of the chart.
    set_background(css_color):
        Modify the background color of the widget.
    """

    def __init__(self):
        """
        Initialisation of the 3D surface chart.

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

        self.plot_chart_widget = gl.GLViewWidget()  # pyQtGraph 3D widget

        # Increase the height of the plot chart widget
        self.plot_chart_widget.setMinimumWidth(400)
        self.plot_chart_widget.setMinimumHeight(400)

        # Create Numpy array for X, Y, and Z data
        self.plot_x_data = np.array([])
        self.plot_y_data = np.array([])
        self.plot_z_data = np.array([])

        # No data at initialization
        self.surface_plot = None
        self.set_axis_and_ticks_color()
        self.master_widget.setLayout(self.layout)

        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

        # Enable chart to add widgets to the layout
        self.enable_chart()

    def set_data(self, x_axis, y_axis, z_axis):
        """
        Set the X, Y, and Z axis data to display on the chart.

        Parameters
        ----------
        x_axis : Numpy array
            X-axis values to display.
        y_axis : Numpy array
            Y-axis values to display.
        z_axis : Numpy array
            Z-axis values to display.

        Returns
        -------
        None.

        """
        self.plot_x_data = x_axis
        self.plot_y_data = y_axis
        self.plot_z_data = z_axis

    def set_axis_and_ticks_color(self, axis_color=BLUE_IOGS, ticks_color=BLUE_IOGS):
        """
        Set the color of the axes and their ticks.

        Parameters
        ----------
        axis_color : str
            Color for the axes in CSS color format (e.g., '#0000FF').
        ticks_color : str
            Color for the ticks in CSS color format (e.g., '#FF0000').

        Returns
        -------
        None.
        """
        # GLViewWidget doesn't have a straightforward way to set axis and tick colors
        pass

    def apply_colormap(self, z_values):
        """
        Apply a colormap to the Z values.

        Parameters
        ----------
        z_values : Numpy array
            Z values of the surface.

        Returns
        -------
        colors : Numpy array
            Colors corresponding to the Z values.
        """
        norm = (z_values - z_values.min()) / (z_values.max() - z_values.min())
        colormap = cm.get_cmap('magma')
        colors = colormap(norm)
        return colors

    def adjust_camera_position(self):
        """
        Adjust camera position to fit the data nicely.
        """
        x_min, x_max = self.plot_x_data.min(), self.plot_x_data.max()
        y_min, y_max = self.plot_y_data.min(), self.plot_y_data.max()
        z_min, z_max = self.plot_z_data.min(), self.plot_z_data.max()

        # Calculate center of the plot
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2
        center_z = (z_min + z_max) / 2

        # Calculate distance for camera position
        distance = max(x_max - x_min, y_max - y_min, z_max - z_min) * 2

        # Set camera position
        self.plot_chart_widget.setCameraPosition(
            distance=distance,
            azimuth=0,  # Adjust azimuth as needed
            elevation=90,  # Adjust elevation as needed
            center=(center_x, center_y, center_z),
            up=(0, 0, 1)  # Adjust up vector as needed
        )

    def adjust_camera_position(self):
        """
        Adjust camera position to fit the data nicely.
        """
        x_min, x_max = self.plot_x_data.min(), self.plot_x_data.max()
        y_min, y_max = self.plot_y_data.min(), self.plot_y_data.max()
        z_min, z_max = self.plot_z_data.min(), self.plot_z_data.max()

        # Calculate center of the plot
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2
        center_z = (z_min + z_max) / 2

        # Calculate distance for camera position
        distance = max(x_max - x_min, y_max - y_min, z_max - z_min) * 2

        # Set camera position
        self.plot_chart_widget.setCameraPosition(
            distance=distance,
            azimuth=0,  # Adjust azimuth as needed
            elevation=15  # Adjust elevation as needed
        )

    def refresh_chart(self):
        """
        Refresh the data of the chart.

        Returns
        -------
        None.
        """
        if self.surface_plot:
            self.plot_chart_widget.removeItem(self.surface_plot)

        x = self.plot_x_data
        y = self.plot_y_data
        z = self.plot_z_data

        vertices = np.vstack([x.ravel(), y.ravel(), z.ravel()]).T
        faces = []
        face_colors = []
        rows, cols = x.shape

        z_colors = self.apply_colormap(z)  # Get the colors for the z values

        for i in range(rows - 1):
            for j in range(cols - 1):
                faces.append([i * cols + j, i * cols +
                             j + 1, (i + 1) * cols + j])
                faces.append([(i + 1) * cols + j, i * cols +
                             j + 1, (i + 1) * cols + j + 1])

                face_colors.append(z_colors[i, j, :])
                face_colors.append(z_colors[i, j, :])

        faces = np.array(faces)
        face_colors = np.array(face_colors)

        self.surface_plot = gl.GLMeshItem(
            vertexes=vertices, faces=faces, faceColors=face_colors, smooth=False, drawEdges=False)
        self.plot_chart_widget.addItem(self.surface_plot)
        self.adjust_camera_position()  # Adjust camera position after adding item
        self.adjustSize()

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
        self.plot_chart_widget.setBackgroundColor(css_color)
        self.setStyleSheet("background:" + css_color + ";")

    def clear_graph(self):
        """
        Clear the main chart of the widget.

        Returns
        -------
        None

        """
        self.plot_chart_widget.clear()

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
        # self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.plot_chart_widget)
        # self.layout.addWidget(self.info_label)


# -----------------------------------------------------------------------------------------------
# Only for testing
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("3D Surface Chart")
        self.setGeometry(100, 100, 800, 600)

        self.centralWid = QWidget()
        self.layout = QVBoxLayout()

        self.chart_widget = Surface3DWidget()
        self.chart_widget.set_title('')
        self.chart_widget.set_information('')
        self.layout.addWidget(self.chart_widget)

        x = np.linspace(-10, 10, 100)
        y = np.linspace(-10, 10, 100)
        x, y = np.meshgrid(x, y)
        z = 10*np.exp(-(x**2+y**2)/50)
        z -= z.max()/4

        self.chart_widget.set_background('lightgray')

        self.chart_widget.set_data(x, y, z)
        self.chart_widget.refresh_chart()

        self.centralWid.setLayout(self.layout)
        self.setCentralWidget(self.centralWid)


# Launching as main for tests

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
