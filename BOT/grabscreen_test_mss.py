import cv2
import numpy
import win32gui
from mss import mss

csgohandle = win32gui.FindWindow(None, 'Counter-Strike: Global Offensive - Direct3D 9')

while True:
    left, top, right, bottom = win32gui.GetWindowRect(csgohandle)
    grabrange = {'left': left, 'top': top, 'width': right - left, 'height': bottom - top}
    mssimage = mss().grab(grabrange)
    image = numpy.array(mssimage)
    a = 25
    cv2.namedWindow('image window', 0)
    cv2.resizeWindow('image window', 16*a, 9*a)
    cv2.imshow('image window', image)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
cv2.destroyAllWindows()

