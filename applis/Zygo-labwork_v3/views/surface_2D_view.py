# -*- coding: utf-8 -*-
"""*surface_2D_view.py* file.

./views/surface_2D_view.py contains Surface2DView class to display a 2D surface.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
Creation : march/2025
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
import numpy as np

import sys
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene,
    QHBoxLayout,
)
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
from pyqtgraph import ColorMap

pg.setConfigOptions(imageAxisOrder='row-major')

class Surface2DView(QWidget):
    """
    Class Surface 2D allowing to display a 2D array in a widget.
    """

    def __init__(self):
        """
        Default constructor.
        """
        super().__init__()
        # Data
        self.array_2D = np.random.rand(20, 20)
        # Graphic area for image
        self.imv = pg.ImageItem(image=self.array_2D)
        # Création du layout principal
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.plot = pg.PlotWidget()
        self.plot.setBackground('lightgray')
        layout.addWidget(self.plot)

    def set_array(self, array: np.ndarray):
        """
        Set an array to the surface viewer.
        :param array: Array to display.
        """
        self.array_2D = array

        # Create an ImageItem for the new image
        self.imv = pg.ImageItem(image=self.array_2D)

        # Add the image to the plot
        self.plot.addItem(self.imv)
        self.plot.setAspectLocked(True)
        pen = QPen(QColor('black'))
        color_bar = self.plot.addColorBar(self.imv, colorMap='plasma', interactive=False, pen=pen)

        self.plot.setMouseEnabled(x=False, y=False)
        self.plot.hideButtons()
        # p1.setRange(xRange=(0, 20), yRange=(0, 20), padding=0)
        self.plot.showAxes(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Surface2DView()
    array_2D = np.random.rand(50, 50)
    window.set_array(array_2D)
    window.show()
    sys.exit(app.exec())
