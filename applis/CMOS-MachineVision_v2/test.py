import sys
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QImage, QPainter, QColor, QFont, QPixmap

class ImageWithText(QWidget):
    def __init__(self):
        super().__init__()

        # Créer une image vide (par exemple, 400x400 pixels)
        self.image = QImage(400, 400, QImage.Format.Format_ARGB32)
        self.image.fill(QColor(0, 0, 0, 255))  # Remplir avec du noir

        # Ajouter du texte à l'image
        self.add_text_to_image("Bonjour, PyQt6!", 50, 200)

        # Configurer l'interface utilisateur
        self.label = QLabel()
        self.pmap = QPixmap(self.image)
        self.label.setPixmap(self.pmap)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setWindowTitle("Image avec texte")
        self.resize(400, 400)

    def add_text_to_image(self, text, x, y):
        painter = QPainter(self.image)
        painter.setPen(QColor(255, 255, 255))  # Couleur blanche pour le texte
        painter.setFont(QFont("Arial", 20))  # Police et taille
        painter.drawText(x, y, text)
        painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageWithText()
    window.show()
    sys.exit(app.exec())