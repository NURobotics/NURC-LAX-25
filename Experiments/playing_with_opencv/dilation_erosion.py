
import math
import cv2
import numpy as np
import imutils

import cProfile
from pstats import SortKey, Stats

"""
following this tutorial
https://pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/

"""


"""
possible thresholds

(hMin = 0 , sMin = 161, vMin = 71), (hMax = 13 , sMax = 255, vMax = 255)
(hMin = 0 , sMin = 139, vMin = 106), (hMax = 10 , sMax = 255, vMax = 255)
(hMin = 0 , sMin = 98, vMin = 116), (hMax = 11 , sMax = 255, vMax = 255)
notes: do not have to wait key since we will do this in rasp Pi
so that just wastes precious time


current profiler dump
   Ordered by: internal time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
      500   16.723    0.033   16.723    0.033 {method 'read' of 'cv2.VideoCapture' objects}
      500    0.371    0.001    0.371    0.001 {cvtColor}
      500    0.309    0.001    0.309    0.001 {GaussianBlur}
      500    0.280    0.001    0.280    0.001 {inRange}
      500    0.274    0.001    0.274    0.001 {minEnclosingCircle}
      500    0.158    0.000    0.158    0.000 {findContours}
      500    0.067    0.000    0.067    0.000 {erode}
      500    0.041    0.000    0.041    0.000 {dilate}
     1000    0.040    0.000    0.040    0.000 {circle}
      500    0.011    0.000    0.011    0.000 {built-in method builtins.max}
      500    0.010    0.000    0.010    0.000 {method 'copy' of 'numpy.ndarray' objects}
      500    0.010    0.000    0.010    0.000 {moments}
        1    0.002    0.002    0.002    0.002 {built-in method builtins.print}
      500    0.002    0.000    0.003    0.000 convenience.py:154(grab_contours)
     1001    0.001    0.000    0.001    0.000 {built-in method builtins.len}
      500    0.000    0.000    0.000    0.000 {method 'append' of 'list' objects}
        1    0.000    0.000    0.000    0.000 pstats.py:117(init)
        1    0.000    0.000    0.000    0.000 {built-in method builtins.isinstance}
        1    0.000    0.000    0.000    0.000 pstats.py:136(load_stats)
        1    0.000    0.000    0.000    0.000 pstats.py:107(__init__)
        1    0.000    0.000    0.000    0.000 cProfile.py:50(create_stats)
        1    0.000    0.000    0.000    0.000 {built-in method builtins.hasattr}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}


"""



cv2.namedWindow('normal')
# cv2.namedWindow('detected balls')

# vc = cv2.VideoCapture(1, cv2.CAP_DSHOW)
vc = cv2.VideoCapture(0, cv2.CAP_DSHOW)



# camera settings?
# vc.set(cv2.CAP_PROP_FPS, 90)
vc.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
vc.set(cv2.CAP_PROP_FRAME_WIDTH, 720)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False




def process_frame(frame):
    frame = cv2.GaussianBlur(frame, (11, 11), 0.2)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    """increase saturation"""
    # (h, s, v) = cv2.split(hsv)
    # s = s*1.5
    # s = np.clip(s,0,255)
    # hsv = cv2.merge([h,s,v])


    mask = cv2.inRange(hsv, (0 , 139,  106), ( 10 ,  255, 255))

    # eroding then dialating seems to be a weird way of denoising the image
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)


    # find contours in the mask and initialize the current
	# (x, y) center of the ball
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    center = None

    # frame2 = frame.copy()
    # cv2.drawContours(frame2, contours, -1, (0, 255, 0), 3)
    # cv2.imshow('contours', frame2)

    
	# only proceed if at least one contour was found
    if len(contours) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        # only proceed if the radius meets a minimum size
        if radius > 10:
        	# draw the circle and centroid on the frame,
        	# then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
        		(0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

    return frame


# with cProfile.Profile() as prof:

#     center_tracking = []

#     for i in range(500):
#         # cv2.imshow("normal", frame)
#         rval, frame = vc.read()

#         if not rval:
#             break


#         frame = cv2.GaussianBlur(frame, (11, 11), 0.2)

#         hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#         mask = cv2.inRange(hsv, (0 , 139,  106), ( 10 ,  255, 255))

#         # eroding then dialating seems to be a weird way of denoising the image
#         mask = cv2.erode(mask, None, iterations=2)
#         mask = cv2.dilate(mask, None, iterations=2)


#         # find contours in the mask and initialize the current
#         # (x, y) center of the ball
#         contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
#             cv2.CHAIN_APPROX_SIMPLE)
#         contours = imutils.grab_contours(contours)
#         center = None

#         # frame2 = frame.copy()
#         # cv2.drawContours(frame2, contours, -1, (0, 255, 0), 3)
#         # cv2.imshow('contours', frame2)

        
#         # only proceed if at least one contour was found
#         if len(contours) > 0:
#             # find the largest contour in the mask, then use
#             # it to compute the minimum enclosing circle and
#             # centroid
#             c = max(contours, key=cv2.contourArea)
#             ((x, y), radius) = cv2.minEnclosingCircle(c)
#             M = cv2.moments(c)
#             center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

#             center_tracking.append(center)
#             # only proceed if the radius meets a minimum size
#             if radius > 10:
#                 # draw the circle and centroid on the frame,
#                 # then update the list of tracked points
#                 cv2.circle(frame, (int(x), int(y)), int(radius),
#                     (0, 255, 255), 2)
#                 cv2.circle(frame, center, 5, (0, 0, 255), -1)

#         # key = cv2.waitKey(1)
#         # if key == ord('q'): # exit on q
#         #     break


#     print(center_tracking)

#     (
#         Stats(prof)
#         .strip_dirs()
#         .sort_stats(SortKey.TIME)
#         .print_stats()
#     )

while rval:
    cv2.imshow("normal", frame)
    rval, frame = vc.read()

    
    frame = process_frame(frame)
        



    key = cv2.waitKey(1)
    if key == ord('q'): # exit on q
        break