from threading import Thread
import cv2, time
 
class VideoStreamWidget(object):
    def __init__(self, src=0):
        self.capture = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)


        # FPS = 1/X
        # X = desired FPS
        self.FPS = 1/90
        self.FPS_MS = int(self.FPS * 1000)


        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        # Read the next frame from the stream in a different thread
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()
            time.sleep(self.FPS_MS)
    
    def show_frame(self):
        # Display frames in main program
        cv2.imshow('frame', self.frame)
        key = cv2.waitKey(self.FPS_MS)
        if key == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            exit(1)

if __name__ == '__main__':

    NUM_CAMS = 3
    cams : list[VideoStreamWidget] = []

    for i in range(NUM_CAMS):
        cams.append(VideoStreamWidget(src=i))


    time.sleep(5)

    while True:
        try:
            for i in cams:
                i.show_frame()
        except Exception as ex:
            print(ex)
            break
