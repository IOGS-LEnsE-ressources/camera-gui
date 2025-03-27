

class AberrationsChoiceWidget(QWidget):
    """Aberrations Choice for selecting aberrations to compensate."""

    aberrations_choice_changed = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        """Default constructor of the class.
        """
        super().__init__(parent=None)
        self.parent = parent
        # Data
        self.check_boxes = []
        self.signal_list = []
        self.aberrations_list = []
        # Graphical objects
        self.max_cols = 6
        self.max_rows = 6
        self.layout = QGridLayout()
        for k in range(self.max_cols):
            self.layout.setColumnStretch(k, 1)
        for k in range(self.max_rows):
            self.layout.setRowStretch(k, 1)
        self.setLayout(self.layout)
        self.load_file('./config/aberrations_choice.txt')

    def load_file(self, file_path: str):
        """
        Load choice from a txt file.
        Each line of the file contains :
        Name; Row; Col; List_of_orders; Global; type;
        Commentary lines start with #
        """
        if os.path.exists(file_path):
            # Read the CSV file, ignoring lines starting with '//'
            data = np.genfromtxt(file_path, delimiter=';', dtype=str, comments='#', encoding='UTF-8')
            # Populate the dictionary with key-value pairs from the CSV file
            for ab_name, ab_row, ab_col, ab_orders, ab_global, ab_type, _ in data:
                if ab_global == 'Y':
                    check = QCheckBox(translate(ab_name))
                    check.stateChanged.connect(self.action_checked)
                    self.check_boxes.append(check)
                    self.signal_list.append(str(ab_type))
                    self.layout.addWidget(check, int(ab_row), int(ab_col), 2, 1)
                else:
                    label = QLabel(translate(ab_name))
                    self.layout.addWidget(label, int(ab_row), int(ab_col), 2, 1)
                    orders = ab_orders.split(',')
                    col_counter = 2
                    for order in orders:
                        if order != '':
                            check_signal = ab_type + order
                            check = QCheckBox(order)
                            check.stateChanged.connect(self.action_checked)
                            self.check_boxes.append(check)
                            self.signal_list.append(check_signal)
                            self.layout.addWidget(check, int(ab_row), col_counter)
                        col_counter += 1
        else:
            print('CHOICE File error')

    def action_checked(self):
        self.aberrations_list = []
        for i, check in enumerate(self.check_boxes):
            if check.isChecked():
                self.aberrations_list.append(self.signal_list[i])
        self.aberrations_choice_changed.emit('choice_changed')
