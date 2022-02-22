"""
Module modification done by:
Matheus Abrao

Pose Module
By: Computer Vision Zone
Website: https://www.computervision.zone/
"""
import cv2
import mediapipe as mp
import math


class PoseDetector:
    """
    Estimates Pose points of a human body using the mediapipe library.
    """

    def __init__(self, mode=False, smooth=True,
                 detectionCon=0.5, trackCon=0.5):
        """
        :param mode: In static mode, detection is done on each image: slower
        :param upBody: Upper boy only flag
        :param smooth: Smoothness Flag
        :param detectionCon: Minimum Detection Confidence Threshold
        :param trackCon: Minimum Tracking Confidence Threshold
        """

        self.mode = mode
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(static_image_mode=self.mode,
                                     smooth_landmarks=self.smooth,
                                     min_detection_confidence=self.detectionCon,
                                     min_tracking_confidence=self.trackCon)

    def findPose(self, img, draw=True):
        """
        Find the pose landmarks in an Image of BGR color space.
        :param img: Image to find the pose in.
        :param draw: Flag to draw the output on the image.
        :return: Image with or without drawings
        """
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks,
                                           self.mpPose.POSE_CONNECTIONS)
        return img

    def findPosition(self, img, draw=True, bboxWithHands=False):
        self.lmList = []
        self.bboxInfo = {}
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy, cz = int(lm.x * w), int(lm.y * h), int(lm.z * w)
                self.lmList.append([id, cx, cy, cz])

            # Bounding Box
            ad = abs(self.lmList[12][1] - self.lmList[11][1]) // 2
            if bboxWithHands:
                x1 = self.lmList[16][1] - ad
                x2 = self.lmList[15][1] + ad
            else:
                x1 = self.lmList[12][1] - ad
                x2 = self.lmList[11][1] + ad

            y2 = self.lmList[29][2] + ad
            y1 = self.lmList[1][2] - ad
            bbox = (x1, y1, x2 - x1, y2 - y1)
            cx, cy = bbox[0] + (bbox[2] // 2), \
                     bbox[1] + bbox[3] // 2

            self.bboxInfo = {"bbox": bbox, "center": (cx, cy)}

            if draw:
                cv2.rectangle(img, bbox, (255, 0, 255), 3)
                cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

        return self.lmList, self.bboxInfo

    def findAngle(self, img, p1, p2, p3, draw=True):
        """
        Finds angle between three points. Inputs index values of landmarks
        instead of the actual points.
        :param img: Image to draw output on.
        :param p1: Point1 - Index of Landmark 1.
        :param p2: Point2 - Index of Landmark 2.
        :param p3: Point3 - Index of Landmark 3.
        :param draw:  Flag to draw the output on the image.
        :return:
        """

        # Get the landmarks
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]

        # Calculate the Angle
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                             math.atan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360

        # Draw
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 15, (0, 0, 255), 2)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (0, 0, 255), 2)
            cv2.circle(img, (x3, y3), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 15, (0, 0, 255), 2)
            cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 50),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
        return angle

    def drawCustomizedFigure(self, img, pointsList, r=5, t=3, drawExtra=False, blankImg = None, drawPointsBlank = False, drawRacket = True, hand = 'right'):
        '''
        Receives the index the points that the user wants based on
        the mediapipe declaration of the points. Then draw those 
        points on the image.

        The good thing about creating this module is that it can be
        customized to draw the 'stick figure' the way I want.

        :param: pointsList - list with the index of the points
        :param: img - image in which you want to draw
        :param: r - radius of circle which will be drawn
        :param: t - thickness used to draw line
        :param: drawExtra - boolean that specifies if stick figure is to be drawn on blank img
        :param: blankImg - boolean that specifies if blank img is to be drawn
        :param: drawPointsBlank- boolean that specifies if circles are to be drawn on blank img
        :param: drawRacket - boolean that specifies if racket is to be drawn
        :param: hand - string that determines what hand the racket will be drawn on 
        :return: None
        '''
        #finding the location of the nose so a new 'head' can be created
        xNose, yNose = self.lmList[0][1:3] #nose is index 0 of the mediapipe model
        cv2.circle(img, (xNose, yNose), 15, (0, 0, 255), t)

        #list containing only the specified landmarks. i.e. [[x1,y2], [x2,y2]...]
        specificLms = []
        for i in range(len(pointsList)):
            x,y = self.lmList[pointsList[i]][1:3] #get x,y from list that contains [id,x,y,z]
            specificLms.append((x,y))

            if i not in range(4,12): #do not draw "hand points" (15-11,23-11)
                #draw a circle only in the points that the user chooses:
                cv2.circle(img, (x,y), r, (0, 0, 255), cv2.FILLED)
                if drawPointsBlank:
                    cv2.circle(blankImg, (x,y), r, (0, 0, 255), cv2.FILLED)


        if drawExtra == False:
            #connect points new_index = old_index - 11 #change this!
            #drawing stick figure - make this customizabe to make sure it works with the user selecting different points
            cv2.line(img, specificLms[1], specificLms[0], (255, 0, 255), t)
            cv2.line(img, specificLms[1], specificLms[3], (255, 0, 255), t)
            cv2.line(img, specificLms[1], specificLms[13], (255, 0, 255), t)
            cv2.line(img, specificLms[13], specificLms[12], (255, 0, 255), t)
            cv2.line(img, specificLms[13], specificLms[15], (255, 0, 255), t)
            cv2.line(img, specificLms[15], specificLms[17], (255, 0, 255), t)
            cv2.line(img, specificLms[0], specificLms[12], (255, 0, 255), t)
            cv2.line(img, specificLms[12], specificLms[14], (255, 0, 255), t)
            cv2.line(img, specificLms[14], specificLms[16], (255, 0, 255), t)
            cv2.line(img, specificLms[0], specificLms[2], (255, 0, 255), t)
            cv2.line(img, specificLms[3], specificLms[5], (255, 0, 255), t)
            cv2.line(img, specificLms[2], specificLms[4], (255, 0, 255), t)
        else:
            #connect points new_index = old_index - 11 #change this!
            #drawing stick figure - make this customizabe to make sure it works with the user selecting different points
            cv2.circle(blankImg, (xNose, yNose), 20, (0, 0, 255), t) #create head
            cv2.line(blankImg, specificLms[1], specificLms[0], (255, 0, 255), t)
            cv2.line(blankImg, specificLms[1], specificLms[3], (255, 0, 255), t)
            cv2.line(blankImg, specificLms[1], specificLms[13], (255, 0, 255), t)
            cv2.line(blankImg, specificLms[13], specificLms[12], (255, 0, 255), t)
            cv2.line(blankImg, specificLms[13], specificLms[15], (255, 0, 255), t)
            cv2.line(blankImg, specificLms[15], specificLms[17], (255, 0, 255), t)
            cv2.line(blankImg, specificLms[0], specificLms[12], (255, 0, 255), t)
            cv2.line(blankImg, specificLms[12], specificLms[14], (255, 0, 255), t)
            cv2.line(blankImg, specificLms[14], specificLms[16], (255, 0, 255), t)
            cv2.line(blankImg, specificLms[0], specificLms[2], (255, 0, 255), t)
            cv2.line(blankImg, specificLms[3], specificLms[5], (255, 0, 255), t)
            cv2.line(blankImg, specificLms[2], specificLms[4], (255, 0, 255), t)
        
        #draw racket on both the blank img and the regular img
        if drawRacket and (hand == 'right'):
            #calculate racket direction:
            #landmark20/2+landmark18/2
            #landmark9/2+landmark7/2 - (x1+x2/2),(y1+y2/2)
            racketDirection = ((specificLms[9][0]+specificLms[7][0])//2, (specificLms[9][1]+specificLms[7][1])//2)
            # print(f'{racketDirection = }')
            # print(f'{specificLms[8] = }')
            # cv2.line(img, specificLms[5], (specificLms[8][0] + 50, specificLms[8][1] + 50), (255, 0, 0), t)
            cv2.line(img, racketDirection, (racketDirection[0] + 50, racketDirection[1] + 50), (255, 0, 0), t)

            
            

            

    def findDistance(self, p1, p2, img, draw=True, r=15, t=3):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)

        return length, img, [x1, y1, x2, y2, cx, cy]

    def angleCheck(self, myAngle, targetAngle, addOn=20):
        return targetAngle - addOn < myAngle < targetAngle + addOn


def main():
    cap = cv2.VideoCapture(0)
    detector = PoseDetector()
    while True:
        success, img = cap.read()
        img = detector.findPose(img)
        lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False)
        if bboxInfo:
            center = bboxInfo["center"]
            cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)

        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()