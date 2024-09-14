from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QDialog

from gui.styles import button_style


class HexInputDialog(QDialog):
    def __init__(self, parent=None):
        super(HexInputDialog, self).__init__(parent)
        self.setWindowTitle('Ввод Hex цвета')
        self.setFixedSize(250, 100)

        # Поле для ввода HEX цвета
        self.hex_input = QLineEdit(self)
        self.hex_input.setPlaceholderText("Введите цвет в HEX формате (#RRGGBB)")
        self.hex_input.setMaxLength(7)
        self.hex_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: white;
                border: 2px solid #444444;
                border-radius: 5px;
                padding: 5px;
            }
        """)

        # Кнопка "Применить"
        self.apply_button = QPushButton('Применить', self)
        self.apply_button.setStyleSheet(button_style())
        self.apply_button.clicked.connect(self.apply_hex_color)

        layout = QVBoxLayout(self)
        layout.addWidget(self.hex_input)
        layout.addWidget(self.apply_button)
        self.setLayout(layout)

        # Стили окна диалога
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: white;
                border-radius: 10px;
            }
        """)

    def apply_hex_color(self):
        hex_color = self.hex_input.text()
        if QColor.isValidColor(hex_color):
            color = QColor(hex_color)
            self.parent().color_wheel.set_selected_color(color, from_manual=True)
            self.parent().color_changed(color)
            self.close()
