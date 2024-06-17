# -*- coding: utf-8 -*-
"""*x_y_chart_widget.py* file.

*x_y_chart_widget* file that contains :class::XYChartWidget

XYChartWidget for displaying data on a 2D chart.

---------------------------------------
(c) 2024 - LEnsE - Institut d'Optique
---------------------------------------

Modifications
-------------
    Creation on 2023/07/02
    Modification on 2024/06/11

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>
"""

import numpy as np
import sys

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from pyqtgraph import PlotWidget, mkPen

from lensepy.css import *

styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"


# -----------------------------------------------------------------------------------------------

class XYChartWidget(QWidget):
    """
    Widget used to display data in a 2D chart - X and Y axis.
    Children of QWidget - QWidget can be put in another widget and / or window
    ---

    Attributes
    ----------
    title : str
        title of the chart
    plot_chart_widget : PlotWidget
        pyQtGraph Widget to display chart
    plot_chart : PlotWidget.plot
        plot object of the pyQtGraph widget
    plot_x_data : Numpy array
        value to display on X axis
    plot_y_data : Numpy array
        value to display on Y axis
    line_color : CSS color
        color of the line in the graph - default #0A3250
    line_width : float
        width of the line in the graph - default 1

    Methods
    -------
    set_data(x_axis, y_axis):
        Set the X and Y axis data to display on the chart.
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
        Initialisation of the time-dependent chart.

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

        self.plot_chart_widget = PlotWidget()  # pyQtGraph widget
        # Create Numpy array for X and Y data
        self.plot_x_data = np.array([])
        self.plot_y_data = np.array([])

        # No data at initialization
        self.plot_chart = self.plot_chart_widget.plot([0])
        self.set_axis_and_ticks_color()
        self.master_widget.setLayout(self.layout)

        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

        # Width and color of line in the graph
        self.line_color = ORANGE_IOGS
        self.line_width = 1

        # Enable chart to add widgets to the layout
        self.enable_chart()

    def set_data(self, x_axis, y_axis):
        """
        Set the X and Y axis data to display on the chart.

        Parameters
        ----------
        x_axis : Numpy array
            X-axis value to display.
        y_axis : Numpy array
            Y-axis value to display.

        Returns
        -------
        None.

        """
        self.plot_x_data = x_axis
        self.plot_y_data = y_axis

    def set_x_label(self, label, color=BLUE_IOGS):
        """
        Set the label of the X axis.

        Parameters
        ----------
        label : str
            Label for the X axis.

        Returns
        -------
        None.
        """
        self.plot_chart_widget.setLabel('bottom', label, color=color)

    def set_y_label(self, label, color=BLUE_IOGS):
        """
        Set the label of the Y axis.

        Parameters
        ----------
        label : str
            Label for the Y axis.

        Returns
        -------
        None.
        """
        self.plot_chart_widget.setLabel('left', label, color=color)

    def set_axis_and_ticks_color(self, axis_color=BLUE_IOGS, ticks_color=BLUE_IOGS):
        """
        Set the color of the axes, their ticks, and labels.

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
        # Set the pen for the X and Y axes
        axis_pen = mkPen(color=axis_color, width=2)
        self.plot_chart_widget.getAxis('bottom').setPen(axis_pen)
        self.plot_chart_widget.getAxis('left').setPen(axis_pen)

        # Set the pen for the ticks
        ticks_pen = mkPen(color=ticks_color, width=1)
        self.plot_chart_widget.getAxis('bottom').setTickPen(ticks_pen)
        self.plot_chart_widget.getAxis('left').setTickPen(ticks_pen)

        # Set the color for the tick labels
        self.plot_chart_widget.getAxis('bottom').setTextPen(axis_pen)
        self.plot_chart_widget.getAxis('left').setTextPen(axis_pen)

    def refresh_chart(self):
        """
        Refresh the data of the chart.

        Returns
        -------
        None.

        """
        self.plot_chart_widget.removeItem(self.plot_chart)
        self.adjustSize()
        if isinstance(self.plot_y_data, list):
            for i, y_data in enumerate(self.plot_y_data):
                self.plot_chart = self.plot_chart_widget.plot(self.plot_x_data,
                                                              y_data,
                                                              pen=mkPen(self.line_color, width=self.line_width))
        else:
            self.plot_chart = self.plot_chart_widget.plot(self.plot_x_data,
                                                      self.plot_y_data,
                                                      pen=mkPen(self.line_color, width=self.line_width))


    def update_infos(self, val=True):
        """
        Update mean and standard deviation data and display.

        Parameters
        ----------
        val : bool
            True to display mean and standard deviation.
            False to display "acquisition in progress".

        Returns
        -------
        None

        """
        if val:
            mean_d = round(np.mean(self.plot_y_data), 2)
            stdev_d = round(np.std(self.plot_y_data), 2)
            self.set_information(f'Mean = {mean_d} / Standard Dev = {stdev_d}')
        else:
            self.set_information('Data Acquisition In Progress')

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

    def set_line_color_width(self, color, width):
        self.line_color = color
        self.line_width = width


# -----------------------------------------------------------------------------------------------
# Only for testing
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("XY Chart")
        self.setGeometry(100, 100, 800, 600)

        self.centralWid = QWidget()
        self.layout = QVBoxLayout()

        self.chart_widget = XYChartWidget()
        self.chart_widget.set_title('My Super Chart')
        self.chart_widget.set_information('This is a test')
        self.layout.addWidget(self.chart_widget)

        x = np.linspace(0, 100, 101)
        y = np.random.randint(0, 100, 101, dtype=np.int8)

        self.chart_widget.set_background('lightgray')

        self.chart_widget.set_data(x, y)
        self.chart_widget.set_x_label('X')
        self.chart_widget.set_y_label('Y')

        self.chart_widget.refresh_chart()

        self.centralWid.setLayout(self.layout)
        self.setCentralWidget(self.centralWid)


# Launching as main for tests
from PyQt6.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
