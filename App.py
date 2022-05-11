#kivy imports:
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.filechooser import FileChooserIconView

#for drawing:
from kivy.graphics.vertex_instructions import Line
from kivy.graphics.context_instructions import Color
from kivy.properties import ListProperty


from PoseModule import PoseDetector
import os
import cv2
import numpy as np


#Global variables which will be accessed in different classes:

# Standard Video Dimensions Sizes
std_dimensions =  {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}

# Video Encoding, might require additional installs
# Types of Codes: http://www.fourcc.org/codecs.php
video_type = {
    'avi': cv2.VideoWriter_fourcc(*'XVID'),
    #'avi': cv2.VideoWriter_fourcc(*'MJPG'),
    #'mp4': cv2.VideoWriter_fourcc(*'H264'),
    'mp4': cv2.VideoWriter_fourcc(*'XVID'),
}


class MainPage(Screen):
    def __init__(self, **kwargs):
        super(MainPage, self).__init__(**kwargs)

        #create pose module object
        self.detector = PoseDetector()
        
        #create landmarks list to be fed
        self.lmDraw = [lm for lm in range(11,29)] #create a list from 11 to 28

        #create main layout components
        #size hint is (width%, height%)
        self.camImage = Image(size_hint=(1,.6), pos_hint={'x':0, 'top':1})
        self.cameraButton = ToggleButton(on_press=(self.recordVideo), text='record', background_normal='./styling/record.png', background_down='./styling/stop.png', border=(0,0,0,0), size_hint=(.15,.15), pos_hint={'x':0.2, 'top':0.35})
        self.poseCheck = CheckBox(active = False, size_hint=(.1,.1), pos_hint={'x':0.35, 'top':0.35})
        self.poseLabel = Label(text='Pose estimation off', size_hint=(.1,.1), pos_hint={'x':0.5, 'top':0.35})
        self.bgCheck = CheckBox(active = False, size_hint=(.1,.1), pos_hint={'x':0.35, 'top':0.3})
        self.bgCheckLabel = Label(text='Blank background off', size_hint=(.1,.1), pos_hint={'x':0.5, 'top':0.3})
        self.analysisButton = Button(text='  go to \nanalysis', on_press=(self.goToAnalysis), size_hint=(.1,.1), pos_hint={'x':0.7, 'top':0.325})
        

        self.poseCheck.bind(active = self.poseEstimationOn)
        self.bgCheck.bind(active = self.bgCheckOn)

        #add components to layout:
        self.add_widget(self.camImage)
        self.add_widget(self.cameraButton)
        self.add_widget(self.poseCheck)
        self.add_widget(self.poseLabel)
        self.add_widget(self.bgCheck)
        self.add_widget(self.bgCheckLabel)
        self.add_widget(self.analysisButton)

        #setup video capture device
        self.camera = cv2.VideoCapture(0)

        #setup for video recording
        self.filename = 'savedVideo.avi'
        self.frames_per_second = 33.0
        self.res = '720p'

        self.record = False #set recording to false
        self.pose = False #set pose estimation to false
        self.poseBackground = False #set blank background to false
        self.out = cv2.VideoWriter(self.filename, self.get_video_type(), self.frames_per_second, self.get_dims())

        #Run the method update 1 / fps.
        #Check if fps is actually 33!
        Clock.schedule_interval(self.update, 1.0/self.frames_per_second)

    
    def change_res(self, cap, width, height):
        '''
        Set resolution for the video capture
        Function adapted from https://kirr.co/0l6qmh
        '''
        cap.set(3, width)
        cap.set(4, height)


    def get_dims(self):
        '''
        Grab resolution dimensions and set video capture to it.
        '''
        width, height = std_dimensions["480p"]
        if self.res in std_dimensions:
            width,height = std_dimensions[self.res]
        ## change the current caputre device
        ## to the resulting resolution
        self.change_res(self.camera, width, height)
        return width, height


    def get_video_type(self):
        self.filename, ext = os.path.splitext(self.filename)
        if ext in video_type:
            return  video_type[ext]
        return video_type['avi']


    def recordVideo(self, *args):
        if self.record:
            self.record = False
            self.cameraButton.text = 'record'
        else:
            self.record = True
            self.cameraButton.text = 'stop'
    

    def bgCheckOn(self, checkboxInstance, isActive):
        if isActive:
            self.bgCheckLabel.text = "Blank background on"
            self.poseBackground = True
        else:
            self.bgCheckLabel.text = "Blank background off"
            self.poseBackground = False


    def poseEstimationOn(self, checkboxInstance, isActive):
        if isActive:
            self.poseLabel.text = "Pose estimation on"
            self.pose = True
        else:
            self.poseLabel.text = "Pose estimation off"
            self.pose = False


    def goToAnalysis(self, *args):
        self.manager.current = 'analysis'


    def update(self, *args):
        '''
        This runs continuously.
        '''

        #read frame from opencv
        _, self.frame = self.camera.read()

        if self.pose: #MAKE THIS A FUNCTION
            try:
                #find pose landmarks and do not draw them
                self.frame = self.detector.findPose(self.frame, draw=False)
                #get all landmark data and do not draw bounding box
                lmList, bboxInfo = self.detector.findPosition(self.frame, draw = False) 
                #create customized figure
                self.detector.drawCustomizedFigure(self.frame, self.lmDraw, drawRacket=False)
            except:
                pass
        
        if self.poseBackground:
            width, height = self.get_dims()
            self.blankImg = np.zeros((height, width, 3), np.uint8)
            if self.pose: #MAKE THIS A FUNCTION
                try:
                    #find pose landmarks and do not draw them
                    self.frame = self.detector.findPose(self.frame, draw=False)
                    #get all landmark data and do not draw bounding box
                    lmList, bboxInfo = self.detector.findPosition(self.frame, draw = False) 
                    #create customized figure
                    self.detector.drawCustomizedFigure(self.frame, self.lmDraw, drawRacket=False, blankImg = self.blankImg, drawExtra=True)
                except:
                    pass
            self.frame = self.blankImg


        if self.record:
            self.out.write(self.frame)
        


        # Flip horizontall and convert image to texture ##This can be made into a function
        buf = cv2.flip(self.frame, 0).tostring()
        imgTexture = Texture.create(size=(self.frame.shape[1], self.frame.shape[0]), colorfmt='bgr')
        imgTexture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.camImage.texture = imgTexture

class Painter(Widget):
    color = ListProperty([0,0,0,1])

    def on_touch_down(self, touch):
        with self.canvas:
            Color(rgba=self.color)
            touch.ud['line'] = Line(points=(touch.x, touch.y))
    
    def on_touch_move(self, touch):
        touch.ud['line'].points += [touch.x, touch.y]

    def clear_canvas(self, *args):
        self.canvas.clear()

    def change_color(self, instance):
            self.color = instance.background_color

class AnalysisPage(Screen):
    def __init__(self, **kwargs):
        super(AnalysisPage, self).__init__(**kwargs)
        

        self.videofile = './Videos/federer_serve_side_cut.mp4' #example video
        self.cap = cv2.VideoCapture(self.videofile)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0) #looping the video
        self.videoplayer = Image(size_hint=(1,.7), pos_hint={'x':0, 'top':1})
        self.pauseButton = Button(text = 'play/\npause' , on_press=self.pause, size_hint=(.075,.075), pos_hint={'x':0.35, 'top':0.25})
        self.backButton = Button(text='go back', on_press=(self.goBack), size_hint=(.15,.1), pos_hint={'x':0.35, 'top':0.15})
        self.filesButton = Button(text='choose files', on_press=(self.openFileManager), size_hint=(.15,.1), pos_hint={'x':0.5, 'top':0.15})
        self.poseCheck = CheckBox(active = False, size_hint=(.1,.1), pos_hint={'x':0.425, 'top':0.24})
        self.poseLabel = Label(text='Pose estimation off', size_hint=(.1,.1), pos_hint={'x':0.55, 'top':0.24})
        self.bgCheck = CheckBox(active = False, size_hint=(.1,.1), pos_hint={'x':0.425, 'top':0.285})
        self.bgCheckLabel = Label(text='Blank Background off', size_hint=(.1,.1), pos_hint={'x':0.55, 'top':0.285})

        #operations related to painter:
        self.painter = Painter()
        self.clearButton = Button(text='Clear', on_press=(self.painter.clear_canvas), size_hint=(.15,.1), pos_hint={'x':0.15, 'top':0.15})

        #creating buttons for color selection:
        self.green = Button(background_color = 'green', size_hint=(.05,.05), pos_hint={'x':0.15, 'top':0.25}, on_press=(self.painter.change_color))
        self.red = Button(background_color = 'red', size_hint=(.05,.05), pos_hint={'x':0.2, 'top':0.25}, on_press=(self.painter.change_color))
        self.blue = Button(background_color = 'blue', size_hint=(.05,.05), pos_hint={'x':0.25, 'top':0.25}, on_press=(self.painter.change_color))
        self.white = Button(background_color = 'white', size_hint=(.05,.05), pos_hint={'x':0.15, 'top':0.20}, on_press=(self.painter.change_color))
        self.yellow = Button(background_color = 'yellow', size_hint=(.05,.05), pos_hint={'x':0.2, 'top':0.20}, on_press=(self.painter.change_color))
        self.purple = Button(background_color = 'purple', size_hint=(.05,.05), pos_hint={'x':0.25, 'top':0.20}, on_press=(self.painter.change_color))
        

        #frame is empty until it gets selected:
        width, height = std_dimensions['480p'] #setting as 480p for now, make it selectable later
        self.blankImg = np.zeros((height, width, 3), np.uint8)
        self.res = '720p'

        #declaring button variables:
        self.pauseVideo = False

        #for pose estimation:
        self.detector = PoseDetector()
        self.pose = False #set pose estimation to false
        self.poseBackground = False #set blank background to false
        #create landmarks list to be fed
        self.lmDraw = [lm for lm in range(11,29)] #create a list from 11 to 28
        self.poseCheck.bind(active = self.poseEstimationOn)
        self.bgCheck.bind(active = self.bgCheckOn)

        #add widgets to page:
        self.add_widget(self.backButton)
        self.add_widget(self.filesButton)
        self.add_widget(self.videoplayer)
        self.add_widget(self.pauseButton)
        self.add_widget(self.poseCheck)
        self.add_widget(self.poseLabel)
        self.add_widget(self.bgCheck)
        self.add_widget(self.bgCheckLabel)
        self.add_widget(self.painter)
        self.add_widget(self.clearButton)
        self.add_widget(self.green)
        self.add_widget(self.red)
        self.add_widget(self.blue)
        self.add_widget(self.white)
        self.add_widget(self.yellow)
        self.add_widget(self.purple)

        #Run the method update 1 / fps.
        #Check if fps is actually 33!
        Clock.schedule_interval(self.update, 1.0/33.0)
    
        
    def goBack(self, *args):
        self.manager.current = 'main'
    
    def openFileManager(self, *args):
        self.manager.current = 'files'
    
    def changeVideoFile(self, video, *args):
        self.cap = cv2.VideoCapture(video)
    
    def pause(self, *args):
        if self.pauseVideo:
            self.pauseVideo = False
        else:
            self.pauseVideo = True
    
    def bgCheckOn(self, checkboxInstance, isActive): #REFACTOR:
        if isActive:
            self.bgCheckLabel.text = "Blank background on"
            self.poseBackground = True
        else:
            self.bgCheckLabel.text = "Blank background off"
            self.poseBackground = False
        
    def poseEstimationOn(self, checkboxInstance, isActive): #REFACTOR:
        if isActive:
            self.poseLabel.text = "Pose estimation on"
            self.pose = True
        else:
            self.poseLabel.text = "Pose estimation off"
            self.pose = False
    
    def change_res(self, cap, width, height): #REFACTOR
        '''
        Set resolution for the video capture
        Function adapted from https://kirr.co/0l6qmh
        '''
        cap.set(3, width)
        cap.set(4, height)

    def get_dims(self): #REFACTOR
        '''
        Grab resolution dimensions and set video capture to it.
        '''
        width, height = std_dimensions["480p"]
        if self.res in std_dimensions:
            width,height = std_dimensions[self.res]
        ## change the current caputre device
        ## to the resulting resolution
        self.change_res(self.cap, width, height)
        return width, height

    def update(self, *args):
        if self.pauseVideo == False:
            self.ret, self.frame = self.cap.read()
            #width, height = self.frame.shape[0], self.frame.shape[1]

            # if width != 720 or height != 1280:
            #     self.frame = cv2.resize(self.frame, (1080,720))

            if self.ret:
                if self.pose: #MAKE THIS A FUNCTION (CHANGE: THIS IS REPEATING ON THE MAIN PAGE)
                    try:
                        #find pose landmarks and do not draw them
                        self.frame = self.detector.findPose(self.frame, draw=False)
                        #get all landmark data and do not draw bounding box
                        lmList, bboxInfo = self.detector.findPosition(self.frame, draw = False) 
                        #create customized figure
                        self.detector.drawCustomizedFigure(self.frame, self.lmDraw, drawRacket=False)
                    except:
                        pass
                
                
                if self.poseBackground:
                    width, height = self.get_dims()
                    self.blankImg = np.zeros((height, width, 3), np.uint8)
                    if self.pose:
                        try:
                            #find pose landmarks and do not draw them
                            self.frame = self.detector.findPose(self.frame, draw=False)
                            #get all landmark data and do not draw bounding box
                            lmList, bboxInfo = self.detector.findPosition(self.frame, draw = False) 
                            #create customized figure
                            self.detector.drawCustomizedFigure(self.frame, self.lmDraw, drawRacket=False, blankImg = self.blankImg, drawExtra=True)
                        except:
                            pass
                    self.frame = self.blankImg
                
                # Flip horizontall and convert image to texture ##This can be made into a function
                buf = cv2.flip(self.frame, 0).tostring()
                imgTexture = Texture.create(size=(self.frame.shape[1], self.frame.shape[0]), colorfmt='bgr')
                imgTexture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.videoplayer.texture = imgTexture
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0) #looping the video

class FileChooserPage(Screen):
    def __init__(self, **kwargs):
        super(FileChooserPage, self).__init__(**kwargs)

        self.backButton = Button(text='go back', on_press=(self.goBack), size_hint=(.1,.1), pos_hint={'x':0.05, 'top':0.95})
        self.files = FileChooserIconView(size_hint_y=0.8)
        #self.files.dirselect = True #start returning directories instead of file names
        self.files.path = './' #start with the current directory
        self.files.bind(selection=self.selectFile)
        self.videoPath = None
        
        self.add_widget(self.files)
        self.add_widget(self.backButton)
    
    def goBack(self, *args): #This is repeating (can be made global)
        self.manager.current = 'analysis'

    def selectFile(self, *args):
        try:
            self.videoPath = str(self.files.selection[0]) #grab the filename and directory
            self.manager.current = 'analysis' #change page
            #print(self.manager.current_screen.videofile) #debug
            self.manager.current_screen.changeVideoFile(self.videoPath) #change video player's source to selected file

        except:
            pass
    
class WindowManager(ScreenManager):
    def __init__(self, **kwargs):
        super(WindowManager, self).__init__(**kwargs)

class TennisTrainingApp(App):
    def build(self):
        sm = WindowManager(transition=FadeTransition())
        sm.add_widget(MainPage(name='main'))
        sm.add_widget(AnalysisPage(name='analysis'))
        sm.add_widget(FileChooserPage(name='files'))
        return sm
    

   
if __name__ == '__main__':
    TennisTrainingApp().run()
