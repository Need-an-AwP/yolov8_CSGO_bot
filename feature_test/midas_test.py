import cv2
import numpy as np
import torch
import urllib.request
import matplotlib.pyplot as plt
import win32gui
import time
from PIL import ImageGrab


def csgo_screenshot():
    csgo_handle = win32gui.FindWindow(None, 'Counter-Strike: Global Offensive - Direct3D 9')
    left, top, right, bottom = win32gui.GetWindowRect(csgo_handle)
    img = ImageGrab.grab(bbox=(left, top, right, bottom))
    return img, left, top, right, bottom


# 加载模型
model_type = "DPT_Large"
midas = torch.hub.load("intel-isl/MiDaS", model_type)
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
midas.to(device)
midas.eval()
# 加载变换
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
if model_type == "DPT_Large" or model_type == "DPT_Hybrid":
    transform = midas_transforms.dpt_transform
else:
    transform = midas_transforms.small_transform

while 1:
    # 读取图像
    img, left, top, right, bottom = csgo_screenshot()
    img = np.array(img)
    input_batch = transform(img).to(device)
    # 预测并调整大小至原始分辨率
    with torch.no_grad():
        prediction = midas(input_batch)

        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()

    output = prediction.cpu().numpy()
    nearest = np.max(output[output > 0])
    depth_threshold = 5
    # output[(output < depth_threshold)] = nearest

    # 假设 output 是 MiDaS 模型的输出
    output = prediction.cpu().numpy()
    # 计算横向和纵向梯度
    grad_x = cv2.Sobel(output, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(output, cv2.CV_64F, 0, 1, ksize=3)
    # 计算梯度幅值
    grad_mag = np.sqrt(grad_x ** 2 + grad_y ** 2)
    # 设置梯度阈值
    grad_threshold = 5  # 根据实际情况调整
    # 二值化梯度图
    binary_grad = np.where(grad_mag > grad_threshold, 255, 0).astype(np.uint8)
    # 寻找连续区域
    contours, _ = cv2.findContours(binary_grad, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 绘制结果
    plt.figure(figsize=(15, 5))
    plt.subplot(131)
    plt.imshow(output, cmap='gray')
    plt.title('Depth Map')
    plt.subplot(132)
    plt.imshow(binary_grad, cmap='gray')
    plt.title('Binary Gradient')
    plt.subplot(133)
    contour_img = cv2.cvtColor(binary_grad, cv2.COLOR_GRAY2BGR)
    contour_img = cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 2)
    plt.imshow(cv2.cvtColor(contour_img, cv2.COLOR_BGR2RGB))
    plt.title('Contours')

    plt.imshow(output)
    plt.show()
    time.sleep(0.5)

print()
