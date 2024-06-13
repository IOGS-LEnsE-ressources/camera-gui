# -*- coding: utf-8 -*-
"""ContourWidget for displaying contour lines of a surface in 2D.

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
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
import pyqtgraph as pg

from lensepy.css import *

styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"


class ContourWidget(QWidget):
    """
    Widget used to display contour lines of a surface chart.
    Children of QWidget - QWidget can be put in another widget and/or window
    ---

    Attributes
    ----------
    title : str
        title of the chart
    plot_chart_widget : PlotWidget
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
        Initialisation of the 2D contour chart.

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

        self.plot_chart_widget = pg.PlotWidget()  # pyQtGraph 2D widget

        # Increase the height of the plot chart widget
        self.plot_chart_widget.setMinimumWidth(400)
        self.plot_chart_widget.setMinimumHeight(400)

        # Create Numpy array for X, Y, and Z data
        self.plot_x_data = np.array([])
        self.plot_y_data = np.array([])
        self.plot_z_data = np.array([])

        # No data at initialization
        self.contour_plot = None

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

    def refresh_chart(self):
        """
        Refresh the data of the chart.

        Returns
        -------
        None.
        """
        if self.contour_plot:
            self.plot_chart_widget.clear()

        x = self.plot_x_data
        y = self.plot_y_data
        z = self.plot_z_data

        # Create a contour plot using matplotlib
        fig, ax = plt.subplots()
        CS = ax.contour(x, y, z, levels=10)
        
        for collection in CS.collections:
            path = collection.get_paths()
            for p in path:
                vertices = p.vertices
                self.plot_chart_widget.plot(vertices[:, 0], vertices[:, 1], pen=BLUE_IOGS)

        plt.close(fig)

        self.plot_chart_widget.setXRange(x.min(), x.max())
        self.plot_chart_widget.setYRange(y.min(), y.max())
        self.plot_chart_widget.setAspectLocked(True)  # Lock the aspect ratio to ensure orthonormal graph
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
        self.plot_chart_widget.setBackground(css_color)
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
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.plot_chart_widget)
        self.layout.addWidget(self.info_label)


# -----------------------------------------------------------------------------------------------
# Only for testing
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("2D Contour Chart")
        self.setGeometry(100, 100, 800, 600)

        self.centralWid = QWidget()
        self.layout = QVBoxLayout()

        self.chart_widget = ContourWidget()
        self.chart_widget.set_title('Contour Plot')
        self.chart_widget.set_information('Contour plot of a 2D function')
        self.layout.addWidget(self.chart_widget)

        x = np.linspace(-10, 10, 100)
        y = np.linspace(-10, 10, 100)
        x, y = np.meshgrid(x, y)
        z = np.sin(np.sqrt(x**2+y**2))

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
