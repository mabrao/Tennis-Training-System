import cv2
from PoseModule import PoseDetector

#just a test video, change it later to a video filmed from the side
cap = cv2.VideoCapture('./Videos/serve_slow_motion_cut.mp4') 


#create pose detector object
detector = PoseDetector()

#This will append the landmark string 'x,y,z'
posList = []

#List with landmarks that will be drawn
#according with mediapipe pose landmark model
lmDraw = [lm for lm in range(11,33)] #create a list from 11 to 32

while True:
    success, img = cap.read() #getting the image

    #find pose landmarks and do not draw them
    img = detector.findPose(img, draw=False) 

    #resize image
    img = cv2.resize(img, (1280,720))

    #get all landmark data and do not draw bounding box
    lmList, bboxInfo = detector.findPosition(img, draw = False) 

    detector.drawCustomizedFigure(img, lmDraw)

    cv2.imshow('Image', img)

    if bboxInfo:
        lmString = ''
        for lm in lmList:
            lmString += f'{lm[1]},{lm[2]},{lm[3]},' #landmark string is x,y,z
        
        posList.append(lmString)

    key = cv2.waitKey(1)
    if key == 27: #esc is pressed
        cv2.destroyAllWindows()
        cap.release()
        break

    #write landmarks to a text file if the s key is pressed
    elif key == ord('s'): 
        with open('ServeLandmark.txt', 'w') as f:
            f.writelines(['%s\n' % item for item in posList]) #loop through all items and put then on the text file line



        