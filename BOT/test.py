from ultralytics import YOLO
import win32gui
from PyQt5.QtCore import Qt, QRect, QThread
from PyQt5.QtGui import QPixmap, QPen
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush
import sys
import tkinter as tk
import pygetwindow as gw
import pyautogui
import numpy as np
from PIL import Image, ImageTk, ImageGrab


def csgo_screenshot():
    csgo_handle = win32gui.FindWindow(None, 'Counter-Strike: Global Offensive - Direct3D 9')
    left, top, right, bottom = win32gui.GetWindowRect(csgo_handle)
    img = ImageGrab.grab(bbox=(left, top, right, bottom))
    return img, left, top, right, bottom


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
            rect = QRect(int(rect[0])-30, int(rect[1])-40, int(rect[2]), int(rect[3]))
            painter.drawRect(rect)


img, left, top, right, bottom = csgo_screenshot()
model = YOLO(r"D:\yolov8_CSGO_bot\BOT\yolov8n.pt")
results = model(img)  # predict on an image
for result in results:
    boxes = result.boxes  # Boxes object for bbox outputs
    masks = result.masks  # Masks object for segmentation masks outputs
    probs = result.probs  # Class probabilities for classification outputs
oh, ow = results[0].orig_shape
rectangles = results[0].boxes.xywh.data.tolist()  # xywh form data
# create qt window
app = QApplication(sys.argv)
overlay = CustomDrawingLabel()
overlay.setWindowTitle("OVERLAY")

overlay.setFixedSize(ow, oh)  # resize qt window
overlay.set_rectangles(rectangles)
overlay.move(left, top)
overlay.show()
app.exec_()
'''
res_plotted = results[0].plot(conf=1, line_width=1)
# cv2.imwrite("res_plotted.jpg", res_plotted)
cv2.imshow("result", res_plotted)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''
print()
