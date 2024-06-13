from PyQt6.QtGui import QColor
import numpy as np
import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt
import pyqtgraph.opengl as gl

# Définition des styles CSS, à adapter selon vos besoins
styleH1 = "font-size:20px; padding:10px; color:white;"
styleH3 = "font-size:15px; padding:7px; color:blue;"

class XYZChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.title = ''  
        self.layout = QVBoxLayout()  

        self.master_layout = QVBoxLayout()
        self.master_widget = QWidget()

        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(styleH1)

        self.info_label = QLabel('')
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet(styleH3)

        self.plot_chart_widget = gl.GLViewWidget()  # Utilisation de GLViewWidget
        self.plot_x_data = np.array([])
        self.plot_y_data = np.array([])
        self.plot_z_data = np.array([])

        self.plot_chart = gl.GLSurfacePlotItem()  # Utilisation de GLSurfacePlotItem
        self.plot_chart_widget.addItem(self.plot_chart)

        # Ajout des axes
        self.axis = gl.GLAxisItem()
        self.plot_chart_widget.addItem(self.axis)

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

        self.surface_color = QColor("orange")
        self.enable_chart()

    def set_data(self, x_axis, y_axis, z_axis):
        self.plot_x_data = x_axis.astype(np.float32)
        self.plot_y_data = y_axis.astype(np.float32)
        self.plot_z_data = z_axis.astype(np.float32)

    def refresh_chart(self):
        self.plot_chart_widget.removeItem(self.plot_chart)
        
        rgba_color = (self.surface_color.redF(), self.surface_color.greenF(), 
                      self.surface_color.blueF(), self.surface_color.alphaF())
        
        self.plot_chart = gl.GLSurfacePlotItem(
            x=self.plot_x_data,
            y=self.plot_y_data,
            z=self.plot_z_data,
            color=rgba_color
        )
        self.plot_chart_widget.addItem(self.plot_chart)

        # Actualiser les axes avec les données actuelles
        self.axis.setSize(x=self.plot_x_data, y=self.plot_y_data, z=self.plot_z_data)

        self.adjustSize()

    def set_title(self, title):
        self.title = title
        self.title_label.setText(self.title)

    def set_information(self, infos):
        self.info_label.setText(infos)

    def set_background(self, css_color):
        self.plot_chart_widget.setBackgroundColor(css_color)
        self.setStyleSheet("background:" + css_color + ";")

    def clear_graph(self):
        self.plot_chart_widget.clear()

    def disable_chart(self):
        count = self.layout.count()
        for i in reversed(range(count)):
            item = self.layout.itemAt(i)
            widget = item.widget()
            widget.deleteLater()

    def enable_chart(self):
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.plot_chart_widget)
        self.layout.addWidget(self.info_label)

    def set_surface_color(self, color):
        self.surface_color = color

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("3D Surface Chart")
        self.setGeometry(100, 100, 800, 600)

        self.centralWid = QWidget()
        self.layout = QVBoxLayout()

        self.chart_widget = XYZChartWidget()
        self.chart_widget.set_title('My 3D Surface Chart')
        self.chart_widget.set_information('This is a test')
        self.layout.addWidget(self.chart_widget)

        x = np.linspace(-5, 5, 50)
        y = np.linspace(-5, 5, 50)
        _x, _y = np.meshgrid(x, y)
        z = np.sin(np.sqrt(_x**2 + _y**2))

        self.chart_widget.set_background('lightgray')

        self.chart_widget.set_data(x, y, z)
        self.chart_widget.refresh_chart()

        self.centralWid.setLayout(self.layout)
        self.setCentralWidget(self.centralWid)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
