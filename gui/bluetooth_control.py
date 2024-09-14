import asyncio
import json
import os
import sys
import qasync

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout

from gui.color_wheel import ColorWheel
from gui.hex_input_dialog import HexInputDialog
from gui.styles import button_style


class BluetoothControl(QWidget):
    def __init__(self, bluetooth_device):
        super().__init__()
        self.bluetooth_device = bluetooth_device
        self.device_on = False
        self.favorite_colors = []
        self.max_favorites = 12

        # Определяем путь к файлу с избранными цветами в %appdata%
        self.appdata_dir = os.path.join(os.getenv('APPDATA'), 'BluetoothLedControl')
        self.favorite_colors_file = os.path.join(self.appdata_dir, "favourite_colors.json")

        # Создаем папку, если её нет
        if not os.path.exists(self.appdata_dir):
            os.makedirs(self.appdata_dir)

        self.bluetooth_device.connection_changed.connect(self.update_ui)
        self.load_favorite_colors()  # Загрузка избранных цветов при запуске
        self.init_ui()

    def init_ui(self):
        self.setFont(QFont("Arial", 12))

        # Статус подключения
        self.status_label = QLabel('Не подключено', self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet('color: red; font-size: 16px; font-weight: bold;')

        # Цветовой круг
        self.color_wheel = ColorWheel(self)
        self.color_wheel.setEnabled(False)  # Деактивируем по умолчанию

        # Кнопка для вызова ввода HEX цвета
        self.open_hex_input_button = QPushButton('Ввести Hex вручную', self)
        self.open_hex_input_button.setStyleSheet(button_style())
        self.open_hex_input_button.setEnabled(False)  # Деактивируем по умолчанию
        self.open_hex_input_button.clicked.connect(self.open_hex_input)

        # Избранные цвета
        self.favorite_colors_layout = QHBoxLayout()
        self.update_favorite_colors()

        # Кнопка для добавления в избранное
        self.add_to_favorites_button = QPushButton('Добавить в избранные', self)
        self.add_to_favorites_button.setEnabled(False)
        self.add_to_favorites_button.setStyleSheet(button_style())
        self.add_to_favorites_button.clicked.connect(self.add_color_to_favorites)

        # Кнопка "Включить/Выключить"
        self.buttonToggle = QPushButton('Включить/Выключить', self)
        self.buttonToggle.setEnabled(False)
        self.buttonToggle.setStyleSheet(button_style())
        self.buttonToggle.clicked.connect(self.async_toggle_device)

        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.color_wheel, alignment=Qt.AlignCenter)
        layout.addWidget(self.open_hex_input_button)
        layout.addLayout(self.favorite_colors_layout)
        layout.addWidget(self.add_to_favorites_button)
        layout.addWidget(self.buttonToggle)

        self.setLayout(layout)
        self.setWindowTitle('Bluetooth Led Control')
        self.setWindowIcon(QIcon(self.resource_path("static/icon.png")))
        self.setGeometry(300, 300, 400, 500)
        self.setStyleSheet("background-color: #1e1e1e; border-radius: 10px; color: white;")

        self.update_ui(self.bluetooth_device.connected)

    def open_hex_input(self):
        hex_dialog = HexInputDialog(self)
        hex_dialog.exec_()

    def color_changed(self, color):
        self.current_color = color.name()
        r, g, b = color.red(), color.green(), color.blue()
        asyncio.create_task(self.bluetooth_device.set_led_color(r, g, b))
        self.add_to_favorites_button.setEnabled(True)

    def update_favorite_colors(self):
        """Обновляем отображение избранных цветов."""
        for i in reversed(range(self.favorite_colors_layout.count())):
            self.favorite_colors_layout.itemAt(i).widget().deleteLater()

        for color_hex in self.favorite_colors:
            color_button = QPushButton(self)
            color_button.setStyleSheet(f"background-color: {color_hex}; border-radius: 5px;")
            color_button.setFixedSize(40, 40)
            color_button.clicked.connect(lambda _, col=color_hex: self.select_color(col))
            self.favorite_colors_layout.addWidget(color_button)

    def add_color_to_favorites(self):
        """Добавляем текущий цвет в избранные и сохраняем."""
        if len(self.favorite_colors) < self.max_favorites and self.current_color not in self.favorite_colors:
            self.favorite_colors.append(self.current_color)
            self.update_favorite_colors()
            self.save_favorite_colors()  # Сохраняем изменения

    def select_color(self, color_hex):
        """Выбираем цвет из избранных и перемещаем кружок на палитре."""
        color = QColor(color_hex)
        r, g, b = color.red(), color.green(), color.blue()

        # Перемещаем кружок на палитре в соответствии с выбранным цветом
        self.color_wheel.set_selected_color(color)

        asyncio.create_task(self.bluetooth_device.set_led_color(r, g, b))

    def update_ui(self, connected):
        if connected:
            self.status_label.setText('Подключено')
            self.status_label.setStyleSheet('color: #66ff66; font-size: 16px; font-weight: bold;')
            self.add_to_favorites_button.setEnabled(False)
            self.buttonToggle.setEnabled(True)
            self.color_wheel.setEnabled(True)  # Активируем палитру
            self.open_hex_input_button.setEnabled(True)  # Активируем кнопку Hex
        else:
            self.status_label.setText('Не подключено')
            self.status_label.setStyleSheet('color: #ff6666; font-size: 16px; font-weight: bold;')
            self.buttonToggle.setEnabled(False)
            self.add_to_favorites_button.setEnabled(False)
            self.color_wheel.setEnabled(False)  # Деактивируем палитру
            self.open_hex_input_button.setEnabled(False)  # Деактивируем кнопку Hex

    def async_toggle_device(self):
        self.device_on = not self.device_on
        asyncio.create_task(self.bluetooth_device.toggle_device(self.device_on))

    def save_favorite_colors(self):
        """Сохраняем избранные цвета в файл."""
        with open(self.favorite_colors_file, "w") as f:
            json.dump(self.favorite_colors, f)

    def load_favorite_colors(self):
        """Загружаем избранные цвета из файла."""
        if os.path.exists(self.favorite_colors_file):
            with open(self.favorite_colors_file, "r") as f:
                self.favorite_colors = json.load(f)

    def run(self, app):
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        with loop:
            loop.create_task(self.bluetooth_device.connect())
            sys.exit(loop.run_forever())

    @staticmethod
    def resource_path(relative_path):
        """ Получить абсолютный путь к ресурсу, работает для dev и для PyInstaller """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
