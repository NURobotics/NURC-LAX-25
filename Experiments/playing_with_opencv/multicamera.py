import cv2
import numpy as np

# cv2.namedWindow("preview")
vc = cv2.VideoCapture(1)

NUM_CAMS = 3
cameras = [
    cv2.VideoCapture(0),
    cv2.VideoCapture(1),
    cv2.VideoCapture(3),
]
previews = [
    "web cam",
    "external cam 1",
    "external cam 2"
]

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

while rval:

    for i in range(NUM_CAMS):
        rval, frame = cameras[i].read()
        cv2.imshow(previews[i], frame)

    key = cv2.waitKey(1)
    if key == ord('q'): # exit on q
        break




cv2.destroyAllWindows()
vc.release()