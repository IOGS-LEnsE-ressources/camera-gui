import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import QTranslator, QLocale
import numpy as np

# Declare the global dictionary variable
dictionary = {}


def load_dictionary(language: str) -> None:
    """
    Load a dictionary from a CSV file based on the specified language.

    Parameters
    ----------
    language : str
        The language code to specify which CSV file to load.
        The file should be located in the 'lang/' directory and named 'dico_<language>.csv'.

    Returns
    -------
    None

    Notes
    -----
    This function reads a CSV file that contains key-value pairs separated by semicolons (';')
    and stores them in a global dictionary variable. The CSV file may contain comments
    prefixed by '//', which will be ignored.

    The file should have the following format:
        // comment
        // comment
        key_1 ; language_word_1
        key_2 ; language_word_2

    The function will strip any leading or trailing whitespace from the keys and values.

    See Also
    --------
    numpy.genfromtxt : Load data from a text file, with missing values handled as specified.
    """
    global dictionary
    dictionary = {}

    # Read the CSV file, ignoring lines starting with '//'
    data = np.genfromtxt(
        f"lang/dict_{language}.csv", delimiter=';', dtype=str, comments='//')

    # Populate the dictionary with key-value pairs from the CSV file
    for key, value in data:
        dictionary[key.strip()] = value.strip()


def translate(key: str) -> str:
    """
    Translate a given key to its corresponding value.

    Parameters
    ----------
    key : str
        The key to translate.

    Returns
    -------
    str
        The translated value corresponding to the key. If the key does not exist, it returns the key itself.

    """
    if key not in dictionary:
        dictionary[key] = key
    return dictionary[key]


class LanguageIterator:
    def __init__(self):
        self.languages = ['EN', 'FR']
        self.current_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        lang = self.languages[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.languages)
        return lang


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language_iterator = LanguageIterator()
        load_dictionary('EN')

        self.setWindowTitle("Translector")

        layout = QVBoxLayout()

        self.label = QLabel("Hello, World!")
        layout.addWidget(self.label)

        self.button = QPushButton("Click me!")
        self.button.clicked.connect(self.button_clicked)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def button_clicked(self):
        lang = next(self.language_iterator)
        load_dictionary(lang)
        self.update_labels()

    def update_labels(self):
        self.setWindowTitle(translate('window_title'))
        self.label.setText(translate('label'))
        self.button.setText(translate('button'))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
