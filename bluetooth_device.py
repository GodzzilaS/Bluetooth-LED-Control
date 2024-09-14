import asyncio
import colorsys
import configparser
import traceback

from bleak import BleakClient, BleakError
from PyQt5.QtCore import QObject, pyqtSignal

# Считывание настроек из файла
config = configparser.ConfigParser()
config.read("D:\dev\Bluetooth-LED-Control\settings.ini")
ADDRESS = config["Settings"]["address"]
CHARACTERISTIC_UUID = config["Settings"]["characteristic_uuid"]
TURN_ON = bytes((0x00, 0x04, 0x80, 0x00, 0x00, 0x0d, 0x0e, 0x0b, 0x3b, 0x23, 0x00,
                 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x32, 0x00, 0x00, 0x90))
TURN_OFF = bytes((0x00, 0x5b, 0x80, 0x00, 0x00, 0x0d, 0x0e, 0x0b, 0x3b, 0x24, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x32, 0x00, 0x00, 0x91))


class BluetoothDevice(QObject):
    connection_changed = pyqtSignal(bool)
    HSV_PACKET = bytearray.fromhex('00 05 80 00 00 0d 0e 0b 3b a1 00 64 64 00 00 00 00 00 00 00 00')

    def __init__(self):
        super().__init__()  # Инициализация базового класса QObject
        self.client = BleakClient(ADDRESS)
        self.connected = False

    async def connect(self):
        while not self.client.is_connected:
            try:
                await self.client.connect(timeout=10)
                self.connected = True
                self.connection_changed.emit(True)
                break
            except (BleakError, asyncio.TimeoutError) as e:
                self.connection_changed.emit(False)
                await asyncio.sleep(5)

    async def toggle_device(self, on):
        if self.client.is_connected:
            command = TURN_ON if on else TURN_OFF
            await self.client.write_gatt_char(CHARACTERISTIC_UUID, command)

    @staticmethod
    def rgb_to_hsv(r, g, b):
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        h, s, v = int(h * 360), int(s * 100), int(v * 100)
        h = int(h / 2)  # Поделить на 2, чтобы получить правильный диапазон для устройства
        return [h, s, v]

    async def set_led_color(self, r, g, b):
        hsv = self.rgb_to_hsv(r, g, b)
        hsv_packet = self.HSV_PACKET.copy()
        hsv_packet[0] = 0xFF00 & 0
        hsv_packet[1] = 0x00FF & 0
        hsv_packet[10], hsv_packet[11], hsv_packet[12] = hsv
        await self.client.write_gatt_char(CHARACTERISTIC_UUID, hsv_packet)
