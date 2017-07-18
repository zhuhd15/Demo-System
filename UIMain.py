#five face to find the different area
from GUI.uiMainwindow import Ui_MainWindow
from GUI.uiwindow2 import Ui_Dialog
import caffe, sys,threading
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from database.Database import *
from imgproc.face_detection import *
from imgproc.liveness_detection import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys, os,time,cv2

class Camera(QMainWindow, Ui_MainWindow):
    def __init__(self, cameraNum,detectionModel,recognitionModel,svmModels,parent=None):
        super(Camera, self).__init__(parent)
        self.cameraNum = cameraNum
        self.device = cv2.VideoCapture(cameraNum)
        self.detectionModel = detectionModel
        self.recognitionModel = recognitionModel
        self.recog = False
        self.tempList = {'valid': False, 'data': []}
        self.svmModels = svmModels

        self.setupUi(self)
        self.timer = QTimer()                                                           #show on screen
        self.timerRec = QTimer()                                                        #show on label
        self.timerSet = QTimer()                                                         #input the data
        self.backColor = QPixmap(self.label.size()).fill(Qt.white)
        self.label.autoFillBackground()
        self.timer.setInterval(10)
        self.timerRec.setInterval(1000)
        self.timerSet.setInterval(15000)                                              #milisecond
        self.timer.timeout.connect(self.showCamera)
        self.timerRec.timeout.connect(self.preRecognize)
        self.timerSet.timeout.connect(self.dataAppend)
        self.pushButton.setCheckable(True)
        self.pushButton.clicked[bool].connect(self.startCamera)
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.clicked[bool].connect(self.startRecognize)
        self.pushButton_4.clicked.connect(QCoreApplication.instance().quit)

        self.Message = dialogWindow()
        self.pushButton_3.clicked.connect(self.Message.handle_click)
        self.Message.pushButton_2.clicked.connect(self.Confirm)

    #two clock initial
    def startRecognize(self,pressed):
        if pressed:
            self.timerRec.start()
            self.timerSet.start()
        else:
            self.timerRec.stop()
            self.timerSet.stop()
            self.dataAppend()

    def startCamera(self,pressed):
        if pressed:
            self.timer.start()
        else:
            self.timer.stop()
        pass

    def dataAppend(self):
        databaseAppend(self.tempList)
        self.tempList['valid'] = False
        self.tempList['data'] = []
        pass


    def showCamera(self):
        if self.device.isOpened():
            self.ret, self.img = self.device.read()
        else:
            self.ret = False
        height, width, bytesPerComponent = self.img.shape
        bytesPerLine = bytesPerComponent * width
        self.img2=self.img;
        cv2.cvtColor(self.img2, cv2.COLOR_BGR2RGB, self.img2)
        self.image = QImage(self.img2.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(self.image))

    def preRecognize(self):
        pic1 = self.img.copy()
        time.sleep(0.02)
        pic2 = self.img.copy()
        time.sleep(0.02)
        pic3 = self.img.copy()
        [bboxCam1, imgCam1] = FaceDetect(pic1, 50, self.detectionModel)
        [bboxCam2, imgCam2] = FaceDetect(pic2, 50, self.detectionModel)
        [bboxCam3, imgCam3] = FaceDetect(pic3, 50, self.detectionModel)
        leftup1 = max(bboxCam1[0],bboxCam2[0],bboxCam3[0])
        leftup2 = max(bboxCam1[1],bboxCam2[1],bboxCam3[1])
        rightdown1 = min(bboxCam1[0]+bboxCam1[2],bboxCam2[0]+bboxCam2[2],bboxCam3[0]+bboxCam3[2])
        rightdown2 = min(bboxCam1[1]+bboxCam1[3],bboxCam2[1]+bboxCam2[3],bboxCam3[1]+bboxCam3[3])
        if rightdown2 <= leftup2 or rightdown1 <= leftup1:
            return None
        self.recognize()
        pass

    def recognize(self):
        [self.bboxCam, self.imgCam] = FaceDetect(self.img, 50, self.detectionModel)
        if len(self.bboxCam) == 0:
            return None
        feature = feature_Extract(self.recognitionModel,self.bboxCam,self.imgCam,128,128)
        feature = numpy.divide(feature,numpy.sqrt(numpy.dot(feature,feature.T)))
        timelabel = time.strftime("%Y%m%d%H%M%S", time.localtime())
        timelabel = int(timelabel)
        information = databaseSearch(feature)
        if information=={}:
            return None
        if 'name' in information:
            self.name = information['name']
        if 'recentVisit' in information:
            self.recent = information['recentVisit']
        if 'firstVisit' in information:
            self.record = information['firstVisit']
        if 'pageAddress' in information:
            self.homePage = information['pageAddress']
        if 'famiPeople' in information:
            self.relationship = information['famiPeople']
        if 'photo' in information:
            self.photo = information['photo']
        self.label_2.setPixmap(QPixmap(self.photo))                #recover
        if self.tempList['valid']==False:
            self.tempList['valid']=True
        startVariable = max(0,len(self.tempList['data'])-100)
        for items in range(startVariable,len(self.tempList['data'])):   #further recover from the front
            info = self.tempList['data']
            if abs(feature*info['feature']-0.15<0.25):
                if abs(timelabel-info['time']<10):
                    return None
        pass
        #truthness = livenessDetectNoCaffe(self.imgCam,self.bboxCam,self.svmModels)
        #if ~truthness:
        #    return None
        feaMap = {'time':timelabel,'feature':feature}
        self.tempList['data'].append(feaMap)
        print(self.tempList['valid'],len(self.tempList['data']))
        pass

    def Confirm(self):
        self.text1 = self.Message.lineEdit.text()
        self.text2 = self.Message.lineEdit_6.text()
        self.text3 = self.Message.lineEdit_7.text()
        self.text4 = self.Message.lineEdit_8.text()
        self.text5 = self.Message.lineEdit_9.text()


class dialogWindow(Ui_Dialog,QDialog):
    def __init__(self,parent = None):
        super(dialogWindow, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.hide)
        self.pushButton_2.clicked.connect(self.hide)

    def handle_click(self):
        if not self.isVisible():
            self.show()


def main():
    rootFile = '/home/luka/Github/caffe models/'
    detectionPrototxt = rootFile + 'face detection/deploy_face_w.prototxt'
    detectionCaffeModel = rootFile + 'face detection/w_iter_100000.caffemodel'
    detectionModel = caffe.Net(detectionPrototxt, detectionCaffeModel, caffe.TEST)

    RecognitionPrototxt = rootFile + 'face recognition/newer/recognition.prototxt'
    RecognitionCaffeModel = rootFile + 'face recognition/newer/_iter_70000.caffemodel'
    recognitionModel = caffe.Net(RecognitionPrototxt, RecognitionCaffeModel, caffe.TEST)
    # GUI init

    svmAddress = 'home/luka/Github/Demo-System/database/svm.data'
    with open(svmAddress,'rb') as svmFile:
        svmModels = pickle.load(svmFile)
    app = QApplication(sys.argv)
    form = Camera(0,detectionModel,recognitionModel,svmModels)
    form.show()
    app.exec_()
    pass



if __name__ == '__main__':
    main()
