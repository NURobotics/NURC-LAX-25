import cv2
import numpy as np

# cv2.namedWindow("preview")
cv2.namedWindow('edgedetected')
cv2.namedWindow('detected circles')
# cv2.namedWindow('blurred')
# cv2.namedWindow('blurred+edgedetected')
vc = cv2.VideoCapture(0)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

while rval:
    # cv2.imshow("preview", frame)
    rval, frame = vc.read()

    # frame = cv2.GaussianBlur(frame, (31, 31), 0.2)
    frame = cv2.blur(frame, (3, 3))


    # just do some color filtering I guess?
    # for i in range(frame.shape[0]):
    #     for j in range(frame.shape[1]):
    #         if frame[i, j, 0] < 100:
    #             frame[i, j] = [0, 0, 0]

    # print(frame.shape)
    # frame = frame - 100#np.array([100, 100, 255])
    # print(frame.shape)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # orange_mask = cv2.inRange(hsv, (0, 99, 142), (22, 187, 255))
    # orange_mask = cv2.inRange(hsv, (0, 104, 101), (18, 173, 255))
    orange_mask = cv2.inRange(hsv, (  0,  73, 121), ( 23, 255, 255))

    # frame[orange_mask >= 150] = (255, 255, 255)
    # frame[orange_mask < 150] = (0, 0, 0)

    """
    maybe this example would work?
    """

    # satadj = 10
    # imghsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype("float32")

    # (h, s, v) = cv2.split(imghsv)
    # s = s*satadj
    # s = np.clip(s,0,255)
    # imghsv = cv2.merge([h,s,v])

    # imgrgb = cv2.cvtColor(imghsv.astype("uint8"), cv2.COLOR_HSV2BGR)

    # cv2.imshow("saturated", imgrgb)

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # gray_frame = cv2.cvtColor(imgrgb, cv2.COLOR_BGR2GRAY)



    


    hori = np.matrix([
            [1, 2, 1],
            [0, 0, 0],
            [-1, -2, -1]]
        )
    vert = np.matrix([
            [1, 0, -1],
            [2, 0, -2],
            [1, 0, -1]]
        )
    vertical = cv2.filter2D(gray_frame, ddepth=-1, kernel=vert)
    horizontal = cv2.filter2D(gray_frame, ddepth=-1, kernel=hori)
    edge_detected = vertical + horizontal
    cv2.imshow("edgedetected", edge_detected)

    # gray_frame = edge_detected
    # gray_frame = cv2.medianBlur(gray_frame, 5) # they say it is extremely susceptible to noise
    rows = gray_frame.shape[0]

    # cv2.imshow("gray on blur", gray_frame)

    circles = cv2.HoughCircles(gray_frame, cv2.HOUGH_GRADIENT, 1, minDist=100,
                               param1=50, param2=30,
                               minRadius=1, maxRadius=100)
    
    # print(circles)

    # print("Frame Shape", frame.shape)


    # a = 0

    # print(1 / a)
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            # circle center

            row, col = center
            print("Color", hsv[col - 1, row - 1])


            h, s, v = hsv[col - 1, row - 1]
            low  = (  0,  73, 121)
            high = ( 23, 255, 255)

            if not ( low[0] <= h <= high[0] and low[1] <= s <= high[1]  and low[2] <= v <= high[2]  ):
                continue

            cv2.circle(frame, center, 1, (0, 100, 100), 3)
            # circle outline
            radius = i[2]
            cv2.circle(frame, center, radius, (255, 0, 255), 3)

            
    
    
    cv2.imshow("detected circles", frame)
    


    key = cv2.waitKey(1)
    if key == ord('q'): # exit on q
        break



cv2.destroyWindow("preview")
vc.release()