import sys
import asyncio
import qasync

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QColorDialog
from PyQt5.QtCore import Qt
from bluetooth_device import BluetoothDevice


class BluetoothControl(QWidget):
    def __init__(self, bluetooth_device):
        super().__init__()
        self.bluetooth_device = bluetooth_device
        self.device_on = False
        self.bluetooth_device.connection_changed.connect(self.update_ui)
        self.init_ui()

    def init_ui(self):
        self.status_label = QLabel('Не подключено', self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet('color: red')

        self.buttonChangeColor = QPushButton('Изменить цвет', self)
        self.buttonChangeColor.setEnabled(False)
        self.buttonChangeColor.clicked.connect(self.change_color_dialog)

        self.buttonToggle = QPushButton('Включить/Выключить', self)
        self.buttonToggle.setEnabled(False)
        self.buttonToggle.clicked.connect(self.async_toggle_device)

        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.buttonChangeColor)
        layout.addWidget(self.buttonToggle)

        self.setLayout(layout)
        self.setWindowTitle('Bluetooth Control')
        self.setGeometry(300, 300, 300, 100)

        self.update_ui(self.bluetooth_device.connected)

    def update_ui(self, connected):
        if connected:
            self.status_label.setText('Подключено')
            self.status_label.setStyleSheet('color: green')
            self.buttonChangeColor.setEnabled(True)
            self.buttonToggle.setEnabled(True)
        else:
            self.status_label.setText('Не подключено')
            self.status_label.setStyleSheet('color: red')
            self.buttonChangeColor.setEnabled(False)
            self.buttonToggle.setEnabled(False)

    def async_toggle_device(self):
        self.device_on = not self.device_on
        asyncio.create_task(self.bluetooth_device.toggle_device(self.device_on))

    def change_color_dialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            r, g, b = color.red(), color.green(), color.blue()
            asyncio.create_task(self.bluetooth_device.set_led_color(r, g, b))

    def run(self):
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        with loop:
            loop.create_task(self.bluetooth_device.connect())
            sys.exit(loop.run_forever())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    device = BluetoothDevice()
    ex = BluetoothControl(device)
    ex.show()
    ex.run()
