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


mc = MotionCapture()
mc.main()