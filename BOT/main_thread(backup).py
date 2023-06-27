import time
import random
import queue
from collections import deque
import cv2
from ultralytics import YOLO
import win32gui
from PyQt5.QtCore import Qt, QRect, QThread, pyqtSlot, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QPen
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush
import sys
from PIL import Image, ImageGrab
from ctypes import CDLL

gm = CDLL(r'D:\yolov8_CSGO_bot\feature_test\QT\ghub_device.dll')


def on_click(x, y, button, pressed):
    global press
    if pressed and button == button.x1:  # autoshot hotkey
        press = not press
        print('button.x1 pressed' if press else 'button.x1 released')


def key_down(key=''):
    gm.key_down(key.encode('utf-8'))


def key_up(key=''):
    gm.key_up(key.encode('utf-8'))


def mouse_move(x, y, abs_move=False):
    gm.moveR(x, y, abs_move)  # int only


def mouse_click(key):
    gm.mouse_down(key)
    time.sleep(0.001)
    gm.mouse_up(key)


def csgo_screenshot():
    csgo_handle = win32gui.FindWindow(None, 'Counter-Strike: Global Offensive - Direct3D 9')
    left, top, right, bottom = win32gui.GetWindowRect(csgo_handle)
    img = ImageGrab.grab(bbox=(left, top, right, bottom))
    return img, left, top, right, bottom


class CSGODetectionThread(QThread):
    detection_data_updated = pyqtSignal(list, list)

    def __init__(self, path, speed, queue):
        super().__init__()
        self.model = YOLO(path)
        self.detect_speed = speed
        self.detection_queue = queue

    def run(self):
        while True:
            img, left, top, right, bottom = csgo_screenshot()
            results = self.model(img, conf=0.5, device=0)
            res_plotted = results[0].plot(conf=1, line_width=1)
            # cv2.imshow("result", res_plotted)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            for result in results:
                boxes = result.boxes
                masks = result.masks
                probs = result.probs
            rectangles = boxes.xywh.data.tolist()
            # print(rectangles if rectangles else None)
            cls = boxes.cls.data.tolist()
            self.detection_queue.append((rectangles, cls))
            # print(rectangles)
            # self.detection_data_updated.emit(rectangles, cls)
            time.sleep(self.detect_speed)


class CustomDrawingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.head_rect = []
        self.rectangles = []
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.WindowTransparentForInput |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.WA_TranslucentBackground
        )

    @pyqtSlot(list)
    def update_rectangles(self, signal):
        self.head_rect = signal[0]
        self.rectangles = signal[1]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)
        painter.setCompositionMode(QPainter.CompositionMode_Clear)  # 设置画笔像素透明
        painter.fillRect(QRect(0, 0, self.width(), self.height()), Qt.SolidPattern)

        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)  # 设置画笔像素不透明
        # 绘制矩形列表中的所有矩形
        painter.setPen(QPen(QColor(0, 255, 0)))
        for rect in self.rectangles:
            rect = QRect(rect[0]*0.95, 0, int(rect[2]), int(rect[3]))
            # rect = QRect(int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3]))
            painter.drawRect(rect)

        painter.setPen(QPen(QColor(255, 0, 0)))
        for rect in self.head_rect:
            rect = QRect(rect[0]*0.95, 0, int(rect[2]), int(rect[3]))
            # rect = QRect(int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3]))
            painter.drawRect(rect)


class CustomDrawingLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.head_rect = []
        self.rectangles = []
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.WindowTransparentForInput |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.WA_TranslucentBackground
        )

    @pyqtSlot(list)
    def update_rectangles(self, signal):
        self.head_rect = signal[0]
        self.rectangles = signal[1]
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)
        painter.setCompositionMode(QPainter.CompositionMode_Clear)  # 设置画笔像素透明
        painter.fillRect(QRect(0, 0, self.width(), self.height()), Qt.SolidPattern)

        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)  # 设置画笔像素不透明
        # 绘制矩形列表中的所有矩形
        painter.setPen(QPen(QColor(0, 255, 0)))
        for rect in self.rectangles:
            rect = QRect(rect[0] * 0.98, 0, int(rect[2]), int(rect[3]))
            # rect = QRect(int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3]))
            painter.drawRect(rect)

        painter.setPen(QPen(QColor(255, 0, 0)))
        for rect in self.head_rect:
            rect = QRect(rect[0] * 0.98, 0, int(rect[2]), int(rect[3]))
            # rect = QRect(int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3]))
            painter.drawRect(rect)


class OverlayThread(QThread):
    rectangles_updated = pyqtSignal(list)

    def __init__(self, speed, queue):
        super().__init__()
        self.rectangles = []
        self.refresh_speed = speed
        self.detection_deque = queue
        self.head_rect = []
        self.signal = []

    def update_boxes(self):
        self.head_rect = []
        self.rectangles = []
        self.signal = []
        if self.detection_deque:
            new_rectangles, cls = self.detection_deque[0]
            for a in range(len(cls)):
                if cls[a] == 0:
                    self.rectangles.append(new_rectangles[a])
                else:
                    self.head_rect.append(new_rectangles[a])
        self.signal.append(self.head_rect)
        self.signal.append(self.rectangles)

    def run(self):
        while 1:
            # print(self.rectangles if self.rectangles else None)
            self.update_boxes()
            self.rectangles_updated.emit(self.signal)

            time.sleep(self.refresh_speed)


def update_boxes_main():
    new_boxes = random_boxes()
    overlay_thread.update_boxes()


def random_boxes():
    return [[random.randint(0, 1920), random.randint(0, 1080), 100, 100] for _ in range(5)]


if __name__ == '__main__':
    ow = 1920
    oh = 1080
    detection_queue = deque(maxlen=1)  # detection buffer
    img, left, top, right, bottom = csgo_screenshot()

    app = QApplication(sys.argv)
    # overlay = CustomDrawingLabel()
    overlay = CustomDrawingWidget()
    overlay.setWindowTitle("OVERLAY")
    overlay.setFixedSize(int(ow), int(oh))
    overlay.move(0, 0)
    overlay.show()

    refresh_speed = 0.005  # seconds of gui refresh speed
    overlay_thread = OverlayThread(speed=refresh_speed, queue=detection_queue)
    overlay_thread.rectangles_updated.connect(overlay.update_rectangles)  # 连接信号和槽
    overlay_thread.start()
    '''
    timer = QTimer()
    timer.timeout.connect(update_boxes_main)
    timer.start(1000)  # send in data refresh speed
    '''

    model_path = r"D:\yolov8_CSGO_bot\BOT\train\runs\detect\train10\weights\best.pt"
    detect_thread = CSGODetectionThread(model_path, speed=0.002, queue=detection_queue)
    # detect_thread.detection_data_updated.connect(overlay.update_rectangles)
    detect_thread.start()
    app.exec_()
    detect_thread.wait()
