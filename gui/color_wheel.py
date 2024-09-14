import math

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QConicalGradient, QPen, QBrush
from PyQt5.QtWidgets import QWidget


class ColorWheel(QWidget):
    def __init__(self, parent=None):
        super(ColorWheel, self).__init__(parent)
        self.setMinimumSize(300, 300)
        self.selected_color = QColor(255, 255, 255)  # По умолчанию белый
        self.selected_point = None  # Точка для отображения выбранного цвета

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(10, 10, -10, -10)
        radius = min(rect.width(), rect.height()) // 2

        # Создаем плавный градиент для цветового круга
        gradient = QConicalGradient(QPoint(self.width() // 2, self.height() // 2), 0)
        for angle in range(0, 360, 1):
            color = QColor.fromHsv(angle, 255, 255)  # Максимальная насыщенность и яркость
            gradient.setColorAt(angle / 360.0, color)

        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(QPoint(self.width() // 2, self.height() // 2), radius, radius)

        # Отображаем выбранный цвет в виде кружка
        if self.selected_point:
            painter.setPen(QPen(Qt.black, 2))  # Черная рамка для выделения
            painter.setBrush(QBrush(self.selected_color))
            painter.drawEllipse(self.selected_point, 10, 10)  # Отрисовываем кружочек для выбранного цвета

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.isEnabled():
            self.select_color(event.pos())

    def select_color(self, pos):
        cx, cy = self.width() // 2, self.height() // 2
        dx, dy = pos.x() - cx, pos.y() - cy
        distance = math.sqrt(dx ** 2 + dy ** 2)
        radius = min(self.width(), self.height()) // 2 - 10

        if distance <= radius:  # Если клик был в пределах круга
            angle = (math.degrees(math.atan2(dy, dx)) + 360) % 360
            corrected_angle = (360 - angle) % 360
            self.selected_color = QColor.fromHsv(int(corrected_angle), 255, 255)
            self.selected_point = QPoint(pos.x(), pos.y())  # Сохраняем точку для отображения
            self.update()
            self.parent().color_changed(self.selected_color)

    def set_selected_color(self, color: QColor, from_manual=False):
        """Установка цвета и перемещение кружка на палитре."""
        self.selected_color = color
        s = color.saturation()
        v = color.value()

        # Для низкой насыщенности (например, белый) помещаем кружок в центр
        if s < 50 or v == 255:
            self.selected_point = QPoint(self.width() // 2, self.height() // 2)
        else:
            # Рассчитываем координаты для насыщенных оттенков
            h = color.hue()
            if h >= 0:
                angle_rad = math.radians(360 - h)
                cx, cy = self.width() // 2, self.height() // 2
                radius = min(self.width(), self.height()) // 2 - 10
                # Коррекция для более точного размещения кружка
                x = cx + math.cos(angle_rad) * (radius * (s / 255))  # Учитываем насыщенность
                y = cy - math.sin(angle_rad) * (radius * (s / 255))  # Учитываем насыщенность
                self.selected_point = QPoint(int(x), int(y))

        self.update()
