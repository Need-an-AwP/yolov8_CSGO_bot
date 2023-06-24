from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPixmap, QPen
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush
import sys


class CustomDrawingLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.rectangles = []
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.WindowTransparentForInput |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.WA_TranslucentBackground
        )

    def set_rectangles(self, rectangles):
        self.rectangles = rectangles
        self.update()  # 更新窗口，触发 paintEvent

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)
        painter.setCompositionMode(QPainter.CompositionMode_Clear)  # 设置画笔像素透明

        painter.fillRect(QRect(0, 0, self.width(), self.height()), Qt.SolidPattern)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)  # 设置画笔像素不透明

        # 绘制矩形列表中的所有矩形
        painter.setPen(QPen(QColor(255, 0, 0)))
        for rect in self.rectangles:
            rect = QRect(int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3]))
            painter.drawRect(rect)


app = QApplication(sys.argv)
overlay = CustomDrawingLabel()
overlay.setWindowTitle("OVERLAY")

pixmap = QPixmap(r"D:\yolov8_CSGO_bot\BOT\res_plotted.jpg")
overlay.setPixmap(pixmap)

# 调整叠加层大小以匹配图片大小
overlay.setFixedSize(pixmap.size())
overlay.setWindowOpacity(0.5)
# 绘制矩形xywh
rectangles = [[633.0019, 402.4796, 355.6460, 198.2291],
              [74.2733, 267.5339, 28.8841, 46.6956],
              [510.0379, 266.5685, 16.0046, 37.1533],
              [469.6616, 275.0048, 25.3898, 62.6942],
              [577.9515, 274.7719, 27.2012, 56.1240]]
overlay.set_rectangles(rectangles)

overlay.show()
app.exec_()
print()
