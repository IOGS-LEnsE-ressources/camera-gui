# -*- coding: utf-8 -*-
"""
Surface3DWidget for displaying data on a 3D surface.

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
from matplotlib import cm

import pyqtgraph.opengl as gl  # Import pyqtgraph for 3D OpenGL integration

from lensepy.css import *  # Import CSS styles if needed

styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"


class Surface3DWidget(QWidget):
    """
    Widget used to display data in a 3D surface chart.

    Attributes
    ----------
    title : str
        Title of the surface plot widget.
    plot_chart_widget : gl.GLViewWidget
        pyqtgraph OpenGL widget to display the surface plot.
    plot_x_data : np.ndarray
        X-axis values to display.
    plot_y_data : np.ndarray
        Y-axis values to display.
    plot_z_data : np.ndarray
        Z-axis values to display.
    surface_plot : gl.GLMeshItem or None
        Surface plot object.

    Methods
    -------
    set_data(x_axis: np.ndarray, y_axis: np.ndarray, z_axis: np.ndarray) -> None
        Set the X, Y, and Z axis data to display on the surface plot.
    set_axis_and_ticks_color(axis_color: str = BLUE_IOGS, ticks_color: str = BLUE_IOGS) -> None
        Set the color of the axes and their ticks.
    apply_colormap(z_values: np.ndarray) -> np.ndarray
        Apply a colormap to the Z values.
    adjust_camera_position() -> None
        Adjust camera position to fit the data nicely.
    refresh_chart() -> None
        Refresh the data and display the surface plot.
    set_title(title: str) -> None
        Set the title of the surface plot.
    set_information(infos: str) -> None
        Set information text displayed below the surface plot.
    set_background(css_color: str) -> None
        Set the background color of the widget.
    clear_graph() -> None
        Clear the surface plot.
    disable_chart() -> None
        Remove all widgets from the layout.
    enable_chart() -> None
        Add and display all widgets in the layout.
    """

    def __init__(self) -> None:
        """
        Initialization of the 3D surface chart widget.
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

        # pyqtgraph OpenGL GLViewWidget setup
        self.plot_chart_widget: gl.GLViewWidget = gl.GLViewWidget()
        self.plot_chart_widget.setMinimumWidth(400)
        self.plot_chart_widget.setMinimumHeight(400)

        # Initialize Numpy arrays for X, Y, and Z data
        self.plot_x_data: np.ndarray = np.array([])
        self.plot_y_data: np.ndarray = np.array([])
        self.plot_z_data: np.ndarray = np.array([])

        # Initialize surface plot object to None
        self.surface_plot: gl.GLMeshItem or None = None

        # Set up the layout hierarchy
        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

        # Enable chart to add widgets to the layout
        self.enable_chart()

    def set_data(self, x_axis: np.ndarray, y_axis: np.ndarray, z_axis: np.ndarray) -> None:
        """
        Set the X, Y, and Z axis data to display on the surface plot.

        Parameters
        ----------
        x_axis : np.ndarray
            X-axis values to display.
        y_axis : np.ndarray
            Y-axis values to display.
        z_axis : np.ndarray
            Z-axis values to display.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method sets the data for the X, Y, and Z axes that will be used to generate the surface plot.
        """
        self.plot_x_data = x_axis
        self.plot_y_data = y_axis
        self.plot_z_data = z_axis

    def set_axis_and_ticks_color(self, axis_color: str = BLUE_IOGS, ticks_color: str = BLUE_IOGS) -> None:
        """
        Set the color of the axes and their ticks.

        Parameters
        ----------
        axis_color : str, optional
            Color for the axes in CSS color format (default is BLUE_IOGS).
        ticks_color : str, optional
            Color for the ticks in CSS color format (default is BLUE_IOGS).

        Returns
        -------
        None
            No return value.

        Notes
        -----
        GLViewWidget doesn't have a straightforward way to set axis and tick colors.
        """
        pass

    def apply_colormap(self, z_values: np.ndarray) -> np.ndarray:
        """
        Apply a colormap to the Z values.

        Parameters
        ----------
        z_values : np.ndarray
            Z values of the surface.

        Returns
        -------
        colors : np.ndarray
            Colors corresponding to the Z values.
        """
        norm = (z_values - z_values.min()) / (z_values.max() - z_values.min())
        colormap = cm.get_cmap('magma')
        colors = colormap(norm)
        return colors

    def adjust_camera_position(self) -> None:
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

    def refresh_chart(self) -> None:
        """
        Refresh the data and display the surface plot.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method refreshes the surface plot using the current X, Y, and Z data.
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

    def set_title(self, title: str) -> None:
        """
        Set the title of the surface plot.

        Parameters
        ----------
        title : str
            Title of the surface plot.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method updates the title displayed at the top of the surface plot widget.
        """
        self.title = title
        self.title_label.setText(self.title)

    def set_information(self, infos: str) -> None:
        """
        Set information text displayed below the surface plot.

        Parameters
        ----------
        infos : str
            Information to display below the surface plot.

        Returns
        -------
            -------
    None
        No return value.

    Notes
    -----
    This method updates the information text displayed below the surface plot widget.
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
        This method sets the background color of the entire widget.
        """
        self.plot_chart_widget.setBackgroundColor(css_color)
        self.setStyleSheet("background:" + css_color + ";")

    def clear_graph(self) -> None:
        """
        Clear the surface plot from the widget.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method clears the main surface plot from the widget.
        """
        self.plot_chart_widget.clear()

    def disable_chart(self) -> None:
        """
        Remove all widgets from the layout.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method removes all child widgets from the layout.
        """
        count = self.layout.count()
        for i in reversed(range(count)):
            item = self.layout.itemAt(i)
            widget = item.widget()
            widget.deleteLater()

    def enable_chart(self) -> None:
        """
        Add and display all widgets in the layout.

        Returns
        -------
        None
            No return value.

        Notes
        -----
        This method adds all child widgets to the layout for display.
        """
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.plot_chart_widget)
        self.layout.addWidget(self.info_label)


# -----------------------------------------------------------------------------------------------
# Only for testing
class MyWindow(QMainWindow):
    """
    Main application window for testing the Surface3DWidget.
    """

    def __init__(self) -> None:
        """
        Initialization of the main application window.
        """
        super().__init__()

        self.setWindowTitle("3D Surface Chart")
        self.setGeometry(100, 100, 800, 600)

        self.centralWid: QWidget = QWidget()
        self.layout: QVBoxLayout = QVBoxLayout()

        self.chart_widget: Surface3DWidget = Surface3DWidget()
        self.chart_widget.set_title('')
        self.chart_widget.set_information('')
        self.layout.addWidget(self.chart_widget)

        x: np.ndarray = np.linspace(-10, 10, 100)
        y: np.ndarray = np.linspace(-10, 10, 100)
        x, y = np.meshgrid(x, y)
        z: np.ndarray = np.sin(np.sqrt(x**2 + y**2))

        z *= (x.max() - x.min()) * .75 / (z.max() - z.min())

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

