# -*- coding: utf-8 -*-
"""*masks_widget.py* file.

...

This file is attached to a 1st year of engineer training labwork in photonics.
Subject : http://lense.institutoptique.fr/ressources/Annee1/TP_Photonique/S5-2324-PolyCI.pdf

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/contents/appli_CMOS_labwork.html

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Dorian MENDES (Promo 2026) <dorian.mendes@institutoptique.fr>

"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QDialog,
    QLabel, QComboBox, QPushButton, QCheckBox, 
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt, QPoint
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor
import numpy as np
from lensepy import load_dictionary, translate
from lensepy.css import *

styleCheckbox = f"font-size: 12px; padding: 7px; color: {BLUE_IOGS}; font-weight: normal;"

# %% Params
BUTTON_HEIGHT = 30 #px

# %% Widget
class MasksMenuWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)

        self.parent = parent

        self.setStyleSheet("background-color: white;")
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()
        
        self.label_title_masks_menu = QLabel(translate('label_title_masks_menu'))
        self.label_title_masks_menu.setStyleSheet(styleH1)
        
        self.subwidget_masks = QWidget()
        self.sublayout_masks = QHBoxLayout()

        # First col
        # ---------
        self.subwidget_left = QWidget()
        self.sublayout_left = QVBoxLayout()
        
        self.button_circle_mask = QPushButton(translate('button_circle_mask'))
        self.button_circle_mask.setStyleSheet(unactived_button)
        self.button_circle_mask.setFixedHeight(BUTTON_HEIGHT)
        self.button_circle_mask.clicked.connect(self.selection_mask_circle)
        
        self.button_rectangle_mask = QPushButton(translate('button_rectangle_mask'))
        self.button_rectangle_mask.setStyleSheet(unactived_button)
        self.button_rectangle_mask.setFixedHeight(BUTTON_HEIGHT)
        
        self.button_polygon_mask = QPushButton(translate('button_polygon_mask'))
        self.button_polygon_mask.setStyleSheet(unactived_button)
        self.button_polygon_mask.setFixedHeight(BUTTON_HEIGHT)
        
        self.checkbox_apply_mask = QCheckBox(translate('checkbox_apply_mask'))
        self.checkbox_apply_mask.setStyleSheet(styleCheckbox)
        self.checkbox_apply_mask.setChecked(True)
        self.checkbox_apply_mask.stateChanged.connect(self.checkbox_apply_mask_changed)
        
        self.sublayout_left.addWidget(self.button_circle_mask)
        self.sublayout_left.addWidget(self.button_rectangle_mask)
        self.sublayout_left.addWidget(self.button_polygon_mask)
        self.sublayout_left.addWidget(self.checkbox_apply_mask)
        self.sublayout_left.setContentsMargins(0, 0, 0, 0)
        self.subwidget_left.setLayout(self.sublayout_left)
        
        # Second col
        # ----------
        self.subwidget_right = QWidget()
        self.sublayout_right = QVBoxLayout()
        
        self.button_move_mask = QPushButton(translate('button_move_mask'))
        self.button_move_mask.setStyleSheet(unactived_button)
        self.button_move_mask.setFixedHeight(BUTTON_HEIGHT)
        
        self.button_resize_mask = QPushButton(translate('button_resize_mask'))
        self.button_resize_mask.setStyleSheet(unactived_button)
        self.button_resize_mask.setFixedHeight(BUTTON_HEIGHT)
        
        self.button_erase_mask = QPushButton(translate('button_erase_mask'))
        self.button_erase_mask.setStyleSheet(unactived_button)
        self.button_erase_mask.setFixedHeight(BUTTON_HEIGHT)
        
        self.checkbox_inverse_mask = QCheckBox(translate('checkbox_inverse_mask'))
        self.checkbox_inverse_mask.setStyleSheet(styleCheckbox)
        self.checkbox_inverse_mask.stateChanged.connect(self.checkbox_inverse_mask_changed)
        
        self.sublayout_right.addWidget(self.button_move_mask)
        self.sublayout_right.addWidget(self.button_resize_mask)
        self.sublayout_right.addWidget(self.button_erase_mask)
        self.sublayout_right.addWidget(self.checkbox_inverse_mask)
        self.sublayout_right.setContentsMargins(0, 0, 0, 0)
        self.subwidget_right.setLayout(self.sublayout_right)
        
        # Combined
        # --------
        self.sublayout_masks.addWidget(self.subwidget_left)
        self.sublayout_masks.addWidget(self.subwidget_right)
        self.sublayout_masks.setContentsMargins(0, 0, 0, 0)
        self.subwidget_masks.setLayout(self.sublayout_masks)
        
        self.layout.addWidget(self.label_title_masks_menu)
        self.layout.addWidget(self.subwidget_masks)

        self.master_widget.setLayout(self.layout)
        self.master_layout.addWidget(self.master_widget)
        self.setLayout(self.master_layout)

    def checkbox_apply_mask_changed(self, state):
        try:
            if state == 2:
                self.mask_unactived, self.mask = self.mask, self.mask_unactived
            else:
                self.mask, self.mask_unactived = self.mask_unactived, self.mask
        except:
            pass
        import matplotlib.pyplot as plt
        plt.figure()
        plt.imshow(self.mask)
        plt.colorbar()
        plt.show()

    def checkbox_inverse_mask_changed(self, state):
        try:
            if state == 2:
                self.mask_inversed, self.mask = self.mask, self.mask_inversed
            else:
                self.mask, self.mask_inversed = self.mask_inversed, self.mask
        except:
            pass
        import matplotlib.pyplot as plt
        plt.figure()
        plt.imshow(self.mask)
        plt.colorbar()
        plt.show()

    def selection_mask_circle(self):
        if self.parent is not None:
            try:
                image = self.parent.camera_widget.get_image()
                selection_window = SelectionMaskWindow(image, 'Circle')
                selection_window.exec()
                self.mask = selection_window.mask
                self.mask_unactived = np.ones_like(self.mask)
                self.mask_inversed = 1-self.mask

                import matplotlib.pyplot as plt
                plt.figure()
                plt.imshow(self.mask)
                plt.show()
            except Exception as e:
                print(f'Exception - selection_mask_circle_isClicked {e}')

class SelectionMaskWindow(QDialog):
    def __init__(self, image, mask_type):
        super().__init__()

        self.layout = QVBoxLayout()

        self.image = image
        self.qimage = QImage(self.image.data, self.image.shape[1], self.image.shape[0], self.image.strides[0], QImage.Format.Format_Grayscale8)
        self.pixmap = QPixmap.fromImage(self.qimage)

        # Couche pour dessiner les points
        self.point_layer = QPixmap(self.pixmap.size())
        self.point_layer.fill(Qt.GlobalColor.transparent)

        self.label = QLabel()
        self.label.setPixmap(self.pixmap)

        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.points = []
        self.mask = np.zeros_like(self.image, dtype=np.uint8)
        self.can_draw = True  # Variable pour indiquer si le dessin est autorisé

        if mask_type == 'Circle':
            self.label.mousePressEvent = self.get_points_circle

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            self.close_window()

    def get_points_circle(self, event):
        if self.can_draw and len(self.points) < 3:  # Vérifier si le dessin est autorisé
            pos = event.pos()
            self.points.append((pos.x(), pos.y()))
            self.draw_point(pos.x(), pos.y())
            if len(self.points) == 3:
                self.draw_circle()
                self.can_draw = False  # Désactiver le dessin une fois que les trois points ont été sélectionnés

    def draw_point(self, x, y):
        painter = QPainter(self.point_layer)
        point_size = 10
        pen = QPen(Qt.GlobalColor.red, point_size)
        painter.setPen(pen)
        painter.drawPoint(QPoint(x, y))
        painter.end()

        # Afficher la couche des points
        combined_pixmap = self.pixmap.copy()
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.point_layer)
        painter.end()

        self.label.setPixmap(combined_pixmap)

    def find_circle_center(self, x0, y0, x1, y1, x2, y2):
        mid_x_01 = (x0 + x1) / 2
        mid_y_01 = (y0 + y1) / 2
        mid_x_02 = (x0 + x2) / 2
        mid_y_02 = (y0 + y2) / 2
        
        if x0 == x1:
            slope_perp_01 = None
            intercept_perp_01 = mid_x_01
        else:
            slope_perp_01 = -1 / ((y1 - y0) / (x1 - x0))
            intercept_perp_01 = mid_y_01 - slope_perp_01 * mid_x_01
            
        if x0 == x2:
            slope_perp_02 = None
            intercept_perp_02 = mid_x_02
        else:
            slope_perp_02 = -1 / ((y2 - y0) / (x2 - x0))
            intercept_perp_02 = mid_y_02 - slope_perp_02 * mid_x_02
        
        if slope_perp_01 is None or slope_perp_02 is None:
            if slope_perp_01 is None:
                X = mid_x_01
                Y = slope_perp_02 * X + intercept_perp_02
            else:
                X = mid_x_02
                Y = slope_perp_01 * X + intercept_perp_01
        else:
            X = (intercept_perp_02 - intercept_perp_01) / (slope_perp_01 - slope_perp_02)
            Y = slope_perp_01 * X + intercept_perp_01
        
        return X, Y

    def draw_circle(self):
        x0, y0 = self.points[0]
        x1, y1 = self.points[1]
        x2, y2 = self.points[2]

        x_center, y_center = self.find_circle_center(x0, y0, x1, y1, x2, y2)
        x_center = int(x_center)
        y_center = int(y_center)
        radius = np.sqrt((x_center-x0)**2+(y_center-y0)**2)

        print(f"x0={x0}, y0={y0}")
        print(f"x1={x1}, y1={y1}")
        print(f"x2={x2}, y2={y2}")
        print(f"centre: ({x_center},{y_center})")
        print(f"dist P1-centre: {np.sqrt((x_center-x0)**2+(y_center-y0)**2)}")
        print(f"dist P2-centre: {np.sqrt((x_center-x1)**2+(y_center-y1)**2)}")
        print(f"dist P3-centre: {np.sqrt((x_center-x2)**2+(y_center-y2)**2)}")
        print(f"rayon: {radius}")

        painter = QPainter(self.pixmap)
        pen = QPen(QColor(255, 0, 0), 2)
        painter.setPen(pen)
        painter.drawEllipse(QPoint(x_center, y_center), radius, radius)
        painter.end()

        # Afficher le cercle
        combined_pixmap = self.pixmap.copy()
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.point_layer)
        painter.end()

        self.label.setPixmap(combined_pixmap)

        # Update mask
        self.mask = self.create_circular_mask(x_center, y_center, radius)

    def create_circular_mask(self, x_center, y_center, radius):
        mask = np.zeros_like(self.image, dtype=np.uint8)
        y, x = np.ogrid[:self.image.shape[0], :self.image.shape[1]]
        mask_area = (x - x_center) ** 2 + (y - y_center) ** 2 <= radius ** 2
        mask[mask_area] = 1
        return mask
    
    def close_window(self):
        self.accept()

# %% Example
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Translation
            dictionary = {}

            self.setWindowTitle(translate("window_title_masks_widget"))
            self.setGeometry(300, 300, 600, 600)

            self.central_widget = MasksMenuWidget()
            self.setCentralWidget(self.central_widget)


    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec())
