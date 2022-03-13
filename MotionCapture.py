"""
Motion Module for Tennis Training System
By: Matheus Abrao
"""


import cv2
from PoseModule import PoseDetector
import numpy as np


class MotionCapture():
    def __init__(self):
        #test video object:
        self.cap = cv2.VideoCapture('./Videos/federer_serve_side_cut.mp4')
        #creating the pose detector object:
        self.detector = PoseDetector()
        #List with landmarks that will be drawn according with mediapipe pose landmark model
        self.lmDraw = [lm for lm in range(11,29)] #create a list from 11 to 28
        #Set window dimensions:
        self.height, self.width = 720, 1280
        #initialize empty list to store strings with landmarks 'x,y,z'
        self.posList = []
    

    def createRacketBox(self, image):
        success, img = self.cap.read() #getting the image

        #find pose landmarks and do not draw them
        img = self.detector.findPose(img, draw=False) 

        # #resize image
        # img = cv2.resize(img, (self.width,self.height))
        width, height = img.shape[0], img.shape[1]

        #get all landmark data and do not draw bounding box
        lmList, bboxInfo = self.detector.findPosition(img, draw = False) #set a bigger bounding box (with hands)
        
        # print(f'{bboxInfo}')
        self.cx, self.cy = bboxInfo['center'][0], bboxInfo['center'][1]
        x1, y1 = self.cx - width//4, self.cy + height//7
        x2, y2 = self.cx + width//2, self.cy + height//7
        x3, y3 = self.cx + width//2, 0 #set the box until the top of the image
        x4, y4 = self.cx - width//4, 0 #set the box until the top of the image

        #debugging and visualization of personalized bounding box:

        # print(f'cx = {cx} cy = {cy} width = {width} height = {height}') 
        # print(f'x1 = {x1} y1 = {y1}')

        cutImg = img[y3:y1, x1:x2]
        #cv2.imshow('Cut image', cutImg)
        
        return cutImg

        
        
    
    def detectAndDrawRacket(self, image):
        params = cv2.SimpleBlobDetector_Params()

        params.filterByArea = True
        params.minArea = 100 #what is this measurement

        # params.filterByCircularity = True
        # params.minCircularity = 0.9

        # params.filterByConvexity = True
        # params.minConvexity = 0.2

        # params.filterByInertia = True
        # params.minInertiaRatio = 0.01

        #create a detector with the parameters
        detector = cv2.SimpleBlobDetector_create(params)

        #detect blobs
        keypoints = detector.detect(image)

        # Draw blobs on our image as red circles
        blank = np.zeros((1, 1))
        blobs = cv2.drawKeypoints(image, keypoints, blank, (0, 0, 255),
                                cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        
        number_of_blobs = len(keypoints)
        text = "Number of Circular Blobs: " + str(len(keypoints))
        cv2.putText(blobs, text, (20, 550),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 255), 2)

        
        # Show blobs
        cv2.imshow("Filtering Circular Blobs Only", blobs)
    

    def main(self):
        while True:
            success, img = self.cap.read() #getting the image

            #find pose landmarks and do not draw them
            img = self.detector.findPose(img, draw=False) 

            #resize image
            img = cv2.resize(img, (self.width,self.height))

            #get all landmark data and do not draw bounding box
            lmList, bboxInfo = self.detector.findPosition(img, draw = False) 

            self.detector.drawCustomizedFigure(img, self.lmDraw, drawRacket=False)

            cutImg = self.createRacketBox(img)
            self.detectAndDrawRacket(cutImg)

            cv2.imshow('Image', img)

            if bboxInfo:
                lmString = ''
                for lm in lmList:
                    lmString += f'{lm[1]},{lm[2]},{lm[3]},' #landmark string is x,y,z
                
                self.posList.append(lmString)

            key = cv2.waitKey(1)
            if key == 27: #esc is pressed
                cv2.destroyAllWindows()
                self.cap.release()
                break

            #write landmarks to a text file if the s key is pressed
            elif key == ord('s'): 
                with open('ServeLandmark.txt', 'w') as f:
                    f.writelines(['%s\n' % item for item in self.posList]) #loop through all items and put then on the text file line

            #draw customized stick figure in blank image:
            elif key == ord('q'):
                #create a blank image and place stick figure in it:
                blankImg = np.zeros((self.height, self.width,3), np.uint8)
                self.detector.drawCustomizedFigure(img, self.lmDraw, drawExtra=True, blankImg=blankImg, drawPointsBlank=True)
                cv2.imshow('Stick Figure', blankImg)


#In case you want to run this file
if __name__ == '__main__':
    mc = MotionCapture()
    mc.main()