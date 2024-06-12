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
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QGuiApplication
import numpy as np
from lensepy import load_dictionary, translate
from lensepy.css import *
import cv2
from lensepy.images.conversion import array_to_qimage, resize_image_ratio

if __name__ == '__main__':
    from combobox_bloc import ComboBoxBloc
else:
    from widgets.combobox_bloc import ComboBoxBloc

styleCheckbox = f"font-size: 12px; padding: 7px; color: {BLUE_IOGS}; font-weight: normal;"
styleH3 = f"font-size:15px; padding:7px; color:{BLUE_IOGS};"

# %% Params
BUTTON_HEIGHT = 30  # px

# %% Widget


class MasksMenuWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)

        self.parent = parent

        if self.parent is None:
            self.mask = None
            self.list_masks = []
            self.list_original_masks = []
            self.mask_unactived = None
        else:
            self.mask = self.parent.mask
            self.list_masks = self.parent.list_masks
            self.list_original_masks = self.parent.list_original_masks
            self.mask_unactived = self.parent.mask_unactived
        self.index_mask_selected = -1

        self.setStyleSheet("background-color: white;")
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.master_widget = QWidget()
        self.master_layout = QVBoxLayout()

        self.label_title_masks_menu = QLabel(
            translate('label_title_masks_menu'))
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

        self.button_rectangle_mask = QPushButton(
            translate('button_rectangle_mask'))
        self.button_rectangle_mask.setStyleSheet(unactived_button)
        self.button_rectangle_mask.setFixedHeight(BUTTON_HEIGHT)
        self.button_rectangle_mask.clicked.connect(
            self.selection_mask_rectangle)

        self.button_polygon_mask = QPushButton(
            translate('button_polygon_mask'))
        self.button_polygon_mask.setStyleSheet(unactived_button)
        self.button_polygon_mask.setFixedHeight(BUTTON_HEIGHT)
        self.button_polygon_mask.clicked.connect(self.selection_mask_polygon)

        self.combobox_select_mask = ComboBoxBloc(
            translate('mask_selected'), map(str, list(range(1, len(self.list_masks)+1))))
        self.combobox_select_mask.currentIndexChanged.connect(
            self.combobox_mask_selected_changed)

        self.sublayout_left.addWidget(self.button_circle_mask)
        self.sublayout_left.addWidget(self.button_rectangle_mask)
        self.sublayout_left.addWidget(self.button_polygon_mask)
        self.sublayout_left.addWidget(self.combobox_select_mask)
        self.sublayout_left.addStretch()
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
        self.button_erase_mask.clicked.connect(
            self.button_erase_mask_isClicked)

        self.checkbox_apply_mask = QCheckBox(translate('checkbox_apply_mask'))
        self.checkbox_apply_mask.setStyleSheet(styleCheckbox)
        self.checkbox_apply_mask.setChecked(True)
        self.checkbox_apply_mask.stateChanged.connect(
            self.checkbox_apply_mask_changed)

        self.checkbox_inverse_mask = QCheckBox(
            translate('checkbox_inverse_mask'))
        self.checkbox_inverse_mask.setStyleSheet(styleCheckbox)
        self.checkbox_inverse_mask.stateChanged.connect(
            self.checkbox_inverse_mask_changed)

        self.sublayout_right.addWidget(self.button_move_mask)
        self.sublayout_right.addWidget(self.button_resize_mask)
        self.sublayout_right.addWidget(self.button_erase_mask)
        self.sublayout_right.addWidget(self.checkbox_apply_mask)
        self.sublayout_right.addWidget(self.checkbox_inverse_mask)
        self.sublayout_right.addStretch()
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
        print('checkbox_apply_mask_changed')
        if self.index_mask_selected == -1:
            msg_box = QMessageBox()
            msg_box.setStyleSheet(styleH3)
            msg_box.warning(self, translate('error'), translate(
                'message_no_mask_selected_error'))
            self.checkbox_apply_mask.setChecked(True)
            return None
        try:
            if self.index_mask_selected is not None:
                if state == 0:
                    self.list_masks[self.index_mask_selected] = self.mask_unactived
                else:
                    self.list_masks[self.index_mask_selected] = self.list_original_masks[self.index_mask_selected]

            print(f'Updated self.list_masks: {self.list_masks}')
        except Exception as e:
            print(f'Exception - checkbox_apply_mask_changed {e}')

        self.mask = np.logical_or.reduce(self.list_masks).astype(int)
        if np.all(self.mask == 0):
            self.mask = 1-self.mask

        import matplotlib.pyplot as plt

        plt.figure()
        plt.imshow(self.mask)
        plt.colorbar()
        plt.show()

    def checkbox_inverse_mask_changed(self, state):
        if self.index_mask_selected == -1:
            msg_box = QMessageBox()
            msg_box.setStyleSheet(styleH3)
            msg_box.warning(self, translate('error'), translate(
                'message_no_mask_selected_error'))
            self.checkbox_apply_mask.setChecked(False)
            return None
        self.mask_selected = 1-self.mask_selected
        self.list_masks[self.index_mask_selected] = self.mask_selected
        self.mask = np.logical_or.reduce(self.list_masks).astype(int)

        import matplotlib.pyplot as plt
        plt.figure()
        plt.imshow(self.mask)
        plt.colorbar()
        plt.show()

    def get_image(self) -> np.ndarray:
        self.parent.camera_thread.stop()
        self.parent.camera.init_camera()
        self.parent.camera.alloc_memory()
        self.parent.camera.start_acquisition()
        raw_array = self.parent.camera_widget.camera.get_image().copy()
        '''
        frame_width = self.parent.camera_widget.width()
        frame_height = self.parent.camera_widget.height()
        # Resize to the display size
        image_array_disp2 = resize_image_ratio(raw_array, frame_width, frame_height)
        # Convert the frame into an image
        image = array_to_qimage(image_array_disp2)
        # display it in the cameraDisplay
        self.camera_widget.camera_display.setPixmap(pmap)
        self.camera_widget.camera.stop_acquisition()
        self.camera_widget.camera.free_memory()
        '''
        print(f'Image Get_ MASKS {raw_array.shape}')
        self.parent.camera.stop_acquisition()
        self.parent.camera.free_memory()
        self.parent.camera_thread.start()

        return raw_array

    def selection_mask_circle(self):
        try:
            import matplotlib.pyplot as plt

            # Récupérer l'image à partir de la caméra ou d'une autre source
            # image = self.get_image()
            image = 255*np.ones((1000, 1000))
            plt.figure()
            plt.imshow(image)
            plt.show()

            n, m = image.shape

            # Récupérer les dimensions de l'écran
            screen = QGuiApplication.primaryScreen()
            screen_size = screen.size()
            screen_width = screen_size.width()
            screen_height = screen_size.height()

            # Calculer le facteur de redimensionnement si l'image est plus grande que l'écran
            resize_factor = min(screen_width / m, screen_height / n)
            print(resize_factor)

            # Redimensionner l'image si nécessaire
            if resize_factor < 1.0:
                image = cv2.resize(
                    image, (0, 0), fx=resize_factor, fy=resize_factor)

            plt.figure()
            plt.imshow(image)
            plt.show()

            # Ouvrir la fenêtre de sélection du masque
            selection_window = SelectionMaskWindow(image, 'Circle')
            selection_window.exec()
            mask = selection_window.mask

            # Redimensionner le masque aux dimensions originales de l'image
            mask = cv2.resize(mask, (m, n))

            # Ajouter le masque à la liste des masques
            self.list_masks.append(mask)
            self.list_original_masks.append(mask)

            # Mettre à jour la liste déroulante des masques
            self.combobox_select_mask.update_options(
                map(str, list(range(1, len(self.list_masks)+1))))
            self.mask = np.logical_or.reduce(self.list_masks).astype(int)

            # Si le masque non activé n'a pas été initialisé, le créer
            if self.mask_unactived is None:
                self.mask_unactived = np.zeros_like(self.mask)

            # Afficher le masque
            plt.figure()
            plt.imshow(self.mask)
            plt.show()

        except Exception as e:
            print(f'Exception - selection_mask_circle_isClicked {e}')

    # Repeat similar modifications for selection_mask_rectangle and selection_mask_polygon methods

    def selection_mask_rectangle(self):
        if self.parent is not None:
            try:
                image = self.get_image()
                selection_window = SelectionMaskWindow(image, 'Rectangle')
                selection_window.exec()
                mask = selection_window.mask
                self.list_masks.append(mask)
                self.list_original_masks.append(mask)

                self.combobox_select_mask.update_options(
                    map(str, list(range(1, len(self.list_masks)+1))))
                self.mask = np.logical_or.reduce(self.list_masks).astype(int)

                if self.mask_unactived is None:
                    print("Unactived mask SET")
                    self.mask_unactived = np.zeros_like(self.mask)

                import matplotlib.pyplot as plt
                plt.figure()
                plt.imshow(self.mask)
                plt.show()
            except Exception as e:
                print(f'Exception - selection_mask_rectangle_isClicked {e}')

    def selection_mask_polygon(self):
        if self.parent is not None:
            try:
                image = self.get_image()
                selection_window = SelectionMaskWindow(image, 'Polygon')
                selection_window.exec()
                mask = selection_window.mask
                self.list_masks.append(mask)
                self.list_original_masks.append(mask)

                self.combobox_select_mask.update_options(
                    map(str, list(range(1, len(self.list_masks)+1))))
                self.mask = np.logical_or.reduce(self.list_masks).astype(int)

                if self.mask_unactived is None:
                    print("Unactived mask SET")
                    self.mask_unactived = np.zeros_like(self.mask)

                import matplotlib.pyplot as plt
                plt.figure()
                plt.imshow(self.mask)
                plt.show()
            except Exception as e:
                print(f'Exception - selection_mask_polygon_isClicked {e}')

    def combobox_mask_selected_changed(self, index):
        self.index_mask_selected = index - 1
        if self.index_mask_selected >= 0 and self.index_mask_selected < len(self.list_masks):
            self.mask_selected = self.list_masks[self.index_mask_selected]
            print(f"self.index_mask_selected: {self.index_mask_selected}")

    def button_erase_mask_isClicked(self):
        if self.index_mask_selected == -1:
            msg_box = QMessageBox()
            msg_box.setStyleSheet(styleH3)
            msg_box.warning(self, translate('error'), translate(
                'message_no_mask_selected_error'))
            self.checkbox_apply_mask.setChecked(True)
            return None

        elif len(self.list_masks) > 0:
            reply = QMessageBox.question(self, translate('erase'), translate('confirmation_erase_mask_question'),
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                del self.list_masks[self.index_mask_selected]
                del self.list_original_masks[self.index_mask_selected]
                self.index_mask_selected -= 1

                self.combobox_select_mask.update_options(
                    map(str, list(range(1, len(self.list_masks)+1))))
                self.mask = np.logical_or.reduce(self.list_masks).astype(int)

                msg_box = QMessageBox()
                msg_box.setStyleSheet(styleH3)
                msg_box.information(self, translate('information'), translate(
                    'message_mask_erased_information'))


class SelectionMaskWindow(QDialog):
    def __init__(self, image, mask_type):
        super().__init__()

        self.layout = QVBoxLayout()

        self.image = image
        self.qimage = QImage(
            self.image.data, self.image.shape[1], self.image.shape[0], self.image.strides[0], QImage.Format.Format_Grayscale8)
        self.pixmap = QPixmap.fromImage(self.qimage)

        self.point_layer = QPixmap(self.pixmap.size())
        self.point_layer.fill(Qt.GlobalColor.transparent)

        self.label = QLabel()
        self.label.setPixmap(self.pixmap)

        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.points = []
        self.mask = np.zeros_like(self.image, dtype=np.uint8)

        if mask_type == 'Circle':
            print('Circle')
            self.label.mousePressEvent = self.get_points_circle
        elif mask_type == 'Rectangle':
            print('Rectangle')
            self.label.mousePressEvent = self.get_points_rectangle
        elif mask_type == 'Polygon':
            print('Polygon')
            self.label.mousePressEvent = self.get_points_polygon

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            self.close_window()

    def get_points_circle(self, event):
        self.can_draw = True
        if self.can_draw and len(self.points) < 3:
            pos = event.pos()
            self.points.append((pos.x(), pos.y()))
            self.draw_point(pos.x(), pos.y())
            if len(self.points) == 3:
                self.draw_circle()
                self.can_draw = False

    def get_points_rectangle(self, event):
        self.can_draw = True
        if self.can_draw and len(self.points) < 2:
            pos = event.pos()
            self.points.append((pos.x(), pos.y()))
            self.draw_point(pos.x(), pos.y())
            if len(self.points) == 2:
                self.draw_rectangle()
                self.can_draw = False

    def get_points_polygon(self, event):
        limit = 10  # px

        self.can_draw = True
        if self.can_draw:
            pos = event.pos()
            self.points.append((pos.x(), pos.y()))
            self.draw_point(pos.x(), pos.y())

            if len(self.points) > 1 and (self.points[-1][0] - self.points[0][0])**2+(self.points[-1][1] - self.points[0][1])**2 < limit**2:
                self.draw_polygon()
                self.can_draw = False

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
            X = (intercept_perp_02 - intercept_perp_01) / \
                (slope_perp_01 - slope_perp_02)
            Y = slope_perp_01 * X + intercept_perp_01

        return X, Y

    def draw_circle(self):
        try:
            x0, y0 = self.points[-3]
            x1, y1 = self.points[-2]
            x2, y2 = self.points[-1]

            x_center, y_center = self.find_circle_center(
                x0, y0, x1, y1, x2, y2)
            x_center = int(x_center)
            y_center = int(y_center)
            radius = int(np.sqrt((x_center-x0)**2+(y_center-y0)**2))

            print(f"x0={x0}, y0={y0}")
            print(f"x1={x1}, y1={y1}")
            print(f"x2={x2}, y2={y2}")
            print(f"centre: ({x_center},{y_center})")
            print(
                f"dist P1-centre: {np.sqrt((x_center-x0)**2+(y_center-y0)**2)}")
            print(
                f"dist P2-centre: {np.sqrt((x_center-x1)**2+(y_center-y1)**2)}")
            print(
                f"dist P3-centre: {np.sqrt((x_center-x2)**2+(y_center-y2)**2)}")
            print(f"rayon: {radius}")

            painter = QPainter(self.pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
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
        except Exception as e:
            print(f'Exception - circle_mask_draw {e}')

    def draw_rectangle(self):
        x1, y1 = self.points[-2]
        x2, y2 = self.points[-1]

        print(f"x1={x1}, y1={y1}")
        print(f"x2={x2}, y2={y2}")

        painter = QPainter(self.pixmap)
        pen = QPen(QColor(255, 0, 0), 2)
        painter.setPen(pen)
        painter.drawRect(x1, y1, (x2-x1), (y2-y1))
        painter.end()

        # Afficher le cercle
        combined_pixmap = self.pixmap.copy()
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.point_layer)
        painter.end()

        self.label.setPixmap(combined_pixmap)

        # Update mask
        self.mask = self.create_rectangular_mask(x1, y1, x2, y2)

    def draw_polygon(self):
        points = [QPoint(self.points[i][0], self.points[i][1])
                  for i in range(len(self.points))]

        painter = QPainter(self.pixmap)
        pen = QPen(QColor(255, 0, 0), 2)
        painter.setPen(pen)
        painter.drawPolygon(points)
        painter.end()

        # Afficher le cercle
        combined_pixmap = self.pixmap.copy()
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.point_layer)
        painter.end()

        self.label.setPixmap(combined_pixmap)

        # Update mask
        self.mask = self.create_polygonal_mask()

    def create_circular_mask(self, x_center, y_center, radius):
        mask = np.zeros_like(self.image, dtype=np.uint8)
        y, x = np.ogrid[:self.image.shape[0], :self.image.shape[1]]
        mask_area = (x - x_center) ** 2 + (y - y_center) ** 2 <= radius ** 2
        mask[mask_area] = 1
        return mask

    def create_rectangular_mask(self, x1, y1, x2, y2):
        mask = np.zeros_like(self.image, dtype=np.uint8)
        mask[y1:y2, x1:x2] = 1
        mask[y1:y2, x2:x1] = 1
        mask[y2:y1, x2:x1] = 1
        mask[y2:y1, x1:x2] = 1
        return mask

    def create_polygonal_mask(self):
        mask = np.zeros_like(self.image, dtype=np.uint8)
        cv2.fillPoly(mask, [np.array(self.points)], 1)
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
