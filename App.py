#kivy imports:
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
# from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture


from MotionCapture import MotionCapture
import os
import cv2


class MainPage(App):

    def build(self):
        '''
        :return:
        '''
        #create motion capture object
        self.mc = MotionCapture()

        #create main layout components
        self.camImage = Image(size_hint=(1,.8))
        self.cameraButton = Button(text='Record', on_press=(self.recordVideo), size_hint=(1,.1))
        self.stopButton = Button(text='Stop', on_press=(self.stopRecording), size_hint=(1,.1))
        # self.poseCheck = CheckBox(text='Pose Estimation On', on_press=(self.poseEstimationOn), size_hint=(1,.1))

        #add components to layout:
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.camImage)
        layout.add_widget(self.cameraButton)
        layout.add_widget(self.stopButton)
        # layout.add_widget(self.poseCheck)

        #setup video capture device
        self.camera = cv2.VideoCapture(0)

        #setup for video recording
        self.filename = 'savedVideo.avi'
        self.frames_per_second = 33.0
        self.res = '720p'

        # Standard Video Dimensions Sizes
        self.std_dimensions =  {
            "480p": (640, 480),
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "4k": (3840, 2160),
        }

        # Video Encoding, might require additional installs
        # Types of Codes: http://www.fourcc.org/codecs.php
        self.video_type = {
            'avi': cv2.VideoWriter_fourcc(*'XVID'),
            #'mp4': cv2.VideoWriter_fourcc(*'H264'),
            'mp4': cv2.VideoWriter_fourcc(*'XVID'),
        }

        self.record = False #set recording to false
        self.out = cv2.VideoWriter(self.filename, self.get_video_type(), 25, self.get_dims())

        #Run the method update 1 / fps.
        #Check if fps is actually 33!
        Clock.schedule_interval(self.update, 1.0/33.0)

        return layout

    # Set resolution for the video capture
    # Function adapted from https://kirr.co/0l6qmh
    def change_res(self, cap, width, height):
        cap.set(3, width)
        cap.set(4, height)


    # grab resolution dimensions and set video capture to it.
    def get_dims(self):
        width, height = self.std_dimensions["480p"]
        if self.res in self.std_dimensions:
            width,height = self.std_dimensions[self.res]
        ## change the current caputre device
        ## to the resulting resolution
        self.change_res(self.camera, width, height)
        return width, height


    def get_video_type(self):
        self.filename, ext = os.path.splitext(self.filename)
        if ext in self.video_type:
            return  self.video_type[ext]
        return self.video_type['avi']

    def recordVideo(self, *args):
        self.record = True


    def stopRecording(self, *args):
        self.record= False
    
    def poseEstimationOn(self, *args):
        pass

    
    def update(self, *args):
        '''
        This runs continuously.
        '''

        #read frame from opencv
        _, self.frame = self.camera.read()

        if self.record:
            self.out.write(self.frame)

        # Flip horizontall and convert image to texture
        buf = cv2.flip(self.frame, 0).tostring()
        imgTexture = Texture.create(size=(self.frame.shape[1], self.frame.shape[0]), colorfmt='bgr')
        imgTexture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.camImage.texture = imgTexture



    


if __name__ == '__main__':
    MainPage().run()
