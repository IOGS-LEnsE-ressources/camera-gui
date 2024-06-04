import sys
from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView
from PyQt6.QtCore import Qt
import numpy as np
from lensepy import load_dictionary, translate
from lensepy.css import *

table_style = f"background-color: {BLACK}; color: {BLUE_IOGS}; font-size: 12px;"

class TableFromNumpy(QTableWidget):
    def __init__(self, arr):
        super().__init__()
        self.array = arr
        nb_lines, nb_cols = arr.shape

        self.layout = QVBoxLayout()

        # Create the table
        self.table_widget = QTableWidget()

        # Set the number of rows and columns
        self.table_widget.setRowCount(nb_lines)
        self.table_widget.setColumnCount(nb_cols)

        # Fill the table with items
        for i in range(nb_lines):
            for j in range(nb_cols):
                item = QTableWidgetItem(str(self.array[i, j]))
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.table_widget.setItem(i, j, item)

        # Disable scroll bars
        self.table_widget.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_widget.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Disable row and column headers
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.horizontalHeader().setVisible(False)

        # Set column and row resize mode to stretch
        self.table_widget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.table_widget.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)

        self.table_widget.setStyleSheet(table_style)

        self.layout.addWidget(self.table_widget)
        self.setLayout(self.layout)


if __name__ == '__main__':
    arr = np.array([['Type', 'A', 'B', 'C'], [
                   'PV', 1, 2, 3], ['RMS', 4, 5, 6]])

    app = QApplication(sys.argv)
    mainWidget = TableFromNumpy(arr=arr)
    mainWidget.show()
    sys.exit(app.exec())
