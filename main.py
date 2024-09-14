import sys

from PyQt5.QtWidgets import QApplication
from bluetooth_device import BluetoothDevice
from gui.bluetooth_control import BluetoothControl


if __name__ == '__main__':
    app = QApplication(sys.argv)
    device = BluetoothDevice()
    ex = BluetoothControl(device)
    ex.show()
    ex.run(app)
