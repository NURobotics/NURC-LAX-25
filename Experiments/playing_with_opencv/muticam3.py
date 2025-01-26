import cv2
import numpy as np
import sys
import threading


NUM_CAMS = 3

"""

IDEAS: do hough transform only on contours rather than the weird variance thing I was trying


DSHOW (and MSMF) are windows only.

on linux, use V4L, FFMPEG or GSTREAMER

also, please check the return val of capture.set(), not all properties/values will be supported on any given machine





"""

class camThread(threading.Thread):
    def __init__(self, previewName, camID):
        threading.Thread.__init__(self)
        self.previewName = previewName
        self.camID = camID
    
    def run(self):
        print("Starting " + self.previewName)
        camPreview(self.previewName, self.camID)


def camPreview(previewName, camID):
    # cv2.namedWindow(previewName + "-detected circles")
    cam = cv2.VideoCapture(camID, cv2.CAP_DSHOW)

    cam.set(cv2.CAP_PROP_BUFFERSIZE, 2)
    # cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    # cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cam.set(cv2.CAP_PROP_FPS, 60)

    # set camera to 90hz 
    # try:
    #     cam.set(cv2.CAP_PROP_FPS, 90)
    #     cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    #     cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # except:
    #     print('cannot set to 90fps')
    
    
    if cam.isOpened():  # try to get the first frame
        rval, frame = cam.read()
        print('cam', camID, 'has started')
    else:
        rval = False

    prefframe = frame

    while rval:


        # print('cam', camID, 'is running')

        # cv2.imshow(previewName, frame)
        frame = np.zeros((2,2))
        rval, frame = cam.read()

        

        # BLUR = 33
        # frame = cv2.blur(frame, (BLUR, BLUR))

        BLUR2 = 23
        frame = cv2.GaussianBlur(frame, (BLUR2, BLUR2), 10)

        # tempframe = frame.copy()
        # frame = frame - prefframe
        # prefframe = tempframe

        frame2 = frame.copy()
        # frame3 = frame.copy()


        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


        # better ranges? https://stackoverflow.com/questions/10948589/choosing-the-correct-upper-and-lower-hsv-boundaries-for-color-detection-withcv
        # orange_mask = cv2.inRange(hsv, (  0,  90, 80), ( 25, 255, 255))
        # orange_mask = cv2.inRange(hsv, (  0,  100, 100), ( 25, 255, 255))
        # (hMin = 0 , sMin = 165, vMin = 91), (hMax = 65 , sMax = 255, vMax = 255)
        orange_mask = cv2.inRange(hsv, (0, 165, 91), (65, 255, 255))
        # frame[orange_mask >= 150] = (255, 255, 255)
        # frame[orange_mask < 150] = (0, 0, 0)

        contours, hierarchy = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # print(contours)

        hull_list = []
        for i in range(len(contours)):
            hull = cv2.convexHull(contours[i])
            hull_list.append(hull)
        


        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # cv2.imshow(previewName, frame)
        cv2.drawContours(frame2, contours, -1, (0, 255, 0), 3)
        cv2.imshow(previewName + 'contours', frame2)

        drawing = np.zeros((orange_mask.shape[0], orange_mask.shape[1], 3), dtype=np.uint8)
        cv2.drawContours(drawing, hull_list, -1, (0, 0, 255))
        # for i in range(len(contours)):
            # color = (0, 0, 255)
            # # cv2.drawContours(drawing, contours, i, color)
            # cv2.drawContours(drawing, hull_list, i, color)
        # Show in a window

        idx, mse = find_most_circular_contour(hull_list)
        cv2.drawContours(drawing, hull_list, idx, (0, 255, 0), 4)
        # idx, mse = find_most_circular_contour(contours)
        # cv2.drawContours(drawing, contours, idx, (255, 255, 255))


        cv2.imshow(previewName + 'Hulls', drawing)


       


        


        cv2.imshow(previewName, frame)

        key = cv2.waitKey(int(1000 * 1/90))
        if key in [27, ord('q')]:  # exit on ESC or q
            break


    print('Camera feed ended')
    cv2.destroyWindow(previewName)


def find_most_circular_contour(contours : np.array):
    """
    
    Returns most "circular" contour in the contours list
    
    """


    """
    each countour is a nested list of points
    so you would need to do like
    contours[i][j, 0] to get a pair of points
    
    """

    POINT_THRESHOLD = 4
    # AREA_THRESHOLD = 100

    small_variance = float('inf')
    contour_idx = -1

    for i in range(len(contours)):


        # fetch the centroid
        moments = cv2.moments(contours[i])

        try:
            cx = int(moments['m10']/moments['m00'])
            cy = int(moments['m01']/moments['m00'])
        except:
            continue


        # find average distance from the center
        # distance array should only be 1d
        points = contours[i][:, 0]
        distance = (points[:, 0] - cx) ** 2 + (points[:, 1] - cy) ** 2
        distance = distance ** 0.5

        # points will be an array where every row has an entry for a point
        # so I want the average to only do by columns
        # so averages is [x_Average, y_average]
        # averages = np.average(distance)
        # std_dev = np.std(distance)

        # calculate variance / MSE I guess
        average = np.average(distance)
        variance = np.square(distance - average).mean()

        # area = cv2.contourArea(contours[i])

        # filter out the small things
        
        if len(distance) > POINT_THRESHOLD and  variance < small_variance: #and area >= AREA_THRESHOLD 
            small_variance = variance
            contour_idx = i
        


    return contour_idx, small_variance



# launch all the cameras
threads = []
for i in range(NUM_CAMS):
    threads.append(  camThread(f"camera{i}", i) )
    threads[i].start()
    