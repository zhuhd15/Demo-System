#five face to find the different area
from GUI.uiMainwindow import Ui_MainWindow
from GUI.uiwindow2 import Ui_Dialog
import caffe, sys,multiprocessing
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebKitWidgets import *
from selenium import webdriver

from database.Database import *
from imgproc.face_detection import *
#from imgproc.liveness_detection import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys, os,time,cv2,pickle,numpy
import spider

'''
This pattern in for further test
'''


'''
test end
'''
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
        self.webimage = Screenshot()
        self.homePage = ''

        self.setupUi(self)
        self.timer = QTimer()                                                           #show on screen
        self.timerRec = QTimer()                                                        #show on label
        self.timerSet = QTimer()                                                         #input the data
        self.backColor = QPixmap(self.Qtvideo.size()).fill(Qt.white)
        self.Qtvideo.autoFillBackground()
        self.timer.setInterval(10)
        self.timerRec.setInterval(1000)
        self.timerSet.setInterval(7000)                                              #milisecond
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
        #caffemodel = [[detectionModel, recognitionModel]]
        #self.Spider=multiprocessing.Process(target=spider.Spider)
        #self.Spider.start()

    #two clock initial
    def startRecognize(self,pressed):
        if pressed:
            self.timerRec.start()
            self.timerSet.start()
        #    self.Spider.start()
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
        tempImg = QPixmap.fromImage(self.image).scaled(self.Qtvideo.size())
        self.Qtvideo.setPixmap(tempImg)

    def preRecognize(self):
        pic1 = self.img.copy()
        time.sleep(0.02)
        pic2 = self.img.copy()
        time.sleep(0.02)
        pic3 = self.img.copy()
        [bboxCam1, imgCam1] = FaceDetect(pic1, 50, self.detectionModel)
        [bboxCam2, imgCam2] = FaceDetect(pic2, 50, self.detectionModel)
        [bboxCam3, imgCam3] = FaceDetect(pic3, 50, self.detectionModel)
        if len(bboxCam1)*len(bboxCam2)*len(bboxCam3) == 0:
            return None
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
        feaMap = {'time': timelabel, 'feature': feature}
        if self.tempList['valid']==False:
            self.tempList['valid']=True
        startVariable = max(0,len(self.tempList['data'])-100)
        for items in range(startVariable,len(self.tempList['data'])):   #further recover from the front
            info = self.tempList['data'][items]
            #temp_value = numpy.dot(feature,info['feature'].T)
            if abs(numpy.dot(feature,info['feature'].T)-0.0>0.4):
                if abs(timelabel-info['time']<1000):
                    self.tempList['data'][items] = feaMap
                    return None
        self.tempList['data'].append(feaMap)
        #information={'name':'Zhu Haidong','recentVisit':[1,2,3],'firstVisit':5,'pageAddress':"http://mails.tsinghua.edu.cn/"}
        #information['photo']="/home/luka/PycharmProjects/cvlab/img/2.jpg"
        start = time.clock()
        information = databaseSearch(feature)
        print(time.clock()-start)
        if information=={}:
            self.QtuserName.setText('')
            self.QtVisit1.setText('')
            self.QtVisit2.setText('')
            self.QtVisit3.setText('')
            self.QtFirstVisit.setText('')
            return None
        print(time.clock()-start)
        if 'name' in information:
            self.name = information['name']
            self.QtuserName.setText(self.name)
        print(time.clock()-start)
        if 'visit0' in information:
            if information['visit0']!=0:
                self.QtVisit1.setText(str(information['visit0']))
            else:
                self.QtVisit1.setText('')
        if 'visit1' in information:
            if information['visit1']!=0:
                self.QtVisit2.setText(str(information['visit1']))
            else:
                self.QtVisit2.setText('')
        if 'visit2' in information:
            if information['visit2']!=0:
                self.QtVisit3.setText(str(information['visit2']))
            else:
                self.QtVisit3.setText('')

        #if 'recentVisit' in information:
        #    self.recent = information['recentVisit']
        #    self.QtVisit1.setText(str(self.recent[0]))
        #    self.QtVisit2.setText(str(self.recent[1]))
        #    self.QtVisit3.setText(str(self.recent[2]))
        print(time.clock()-start)
        if 'firstVisit' in information:
            self.QtFirstVisit.setText(str(information['firstVisit']))
        else:
            self.QtFirstVisit.setText('')
        print(time.clock()-start)
        if 'url' in information:
            if 1 or self.homePage != information['url']:
                self.homePage = information['url']
                if self.homePage!= '':
                    self.webimage.capture(self.homePage)
                    tempImg = QPixmap.fromImage(self.webimage.webimg).scaled(self.QtHomepage.size())
                    self.QtHomepage.setPixmap(tempImg)
            #self.QtHomepage.setPixmap(QPixmap('shot.png'))
        print(time.clock()-start)
        if 'famiPeople' in information:
            self.relationship = information['famiPeople']
            self.QtName1.setText(self.relationship[0]['name'])
            self.QtName2.setText(self.relationship[1]['name'])
            self.QtPhoto1.setPixmap(QPixmap(self.relationship[0]['photoAdd']))
            self.QtPhoto2.setPixmap(QPixmap(self.relationship[1]['photoAdd']))
        print(time.clock()-start)
        if 'img_path' in information:
            self.photo = information['img_path']                #recover
            tempPix = QPixmap(self.photo).scaled(self.QtPhoto.size())
            self.QtPhoto.setPixmap(tempPix)
        print(time.clock()-start)
        
        pass


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



def screenShot(url):
    browser = webdriver.PhantomJS()
    browser.set_window_size(900, 900)
    browser.get(url)
    std = browser.get_screenshot_as_png()
    browser.save_screenshot("shot.png")
    browser.quit()

class Screenshot(QWebView):
    def __init__(self):
        self.app = QApplication(sys.argv)
        QWebView.__init__(self)
        self._loaded = False
        self.loadFinished.connect(self._loadFinished)

    def capture(self, url):
        self.load(QUrl(url))
        self.wait_load()
        frame = self.page().mainFrame()
        self.page().setViewportSize(QSize(900, 900))
        self.webimg = QImage(self.page().viewportSize(), QImage.Format_ARGB32)
        painter = QPainter(self.webimg)
        frame.render(painter)
        painter.end()

    def wait_load(self, delay=0):
        while not self._loaded:
            self.app.processEvents()
            time.sleep(delay)
        self._loaded = False

    def _loadFinished(self, result):
        self._loaded = True


def main():
    caffe.set_mode_gpu()
    rootFile = '/home/luka/PycharmProjects/cvlab/protobuf/'
    detectionPrototxt = rootFile + 'deploy_face_w.prototxt'
    detectionCaffeModel = rootFile + 'w_iter_100000.caffemodel'
    detectionModel = caffe.Net(detectionPrototxt, detectionCaffeModel, caffe.TEST)



    RecognitionPrototxt = rootFile + 'recognition.prototxt'
    RecognitionCaffeModel = rootFile + '_iter_70000.caffemodel'
    recognitionModel = caffe.Net(RecognitionPrototxt, RecognitionCaffeModel, caffe.TEST)


    rootFile1 = '/home/luka/PycharmProjects/cvlab/protobuf1/'
    detectionPrototxt1 = rootFile1 + 'deploy_face_w.prototxt'
    detectionCaffeModel1 = rootFile1 + 'w_iter_100000.caffemodel'
    detectionModel1 = caffe.Net(detectionPrototxt1, detectionCaffeModel1, caffe.TEST)

    RecognitionPrototxt1 = rootFile1 + 'recognition.prototxt'
    RecognitionCaffeModel1 = rootFile1 + '_iter_70000.caffemodel'
    recognitionModel1 = caffe.Net(RecognitionPrototxt1, RecognitionCaffeModel1, caffe.TEST)
    # GUI init

    svmAddress = '/home/luka/PycharmProjects/Github/Demo-System/database/svm.data'
    #with open(svmAddress,'rb') as svmFile:
    #    svmModels = pickle.load(svmFile)
    #caffemodel = [[detectionModel1, recognitionModel1]]

#    t1=threading.Thread(target=spider.Spider,args=caffemodel)
 #   t1.start()


    svmModels = []
    app = QApplication(sys.argv)
    form = Camera(0,detectionModel,recognitionModel,svmModels)
    #ts = multiprocessing.Process(target=spider.Spider)
    #ts.start()
    form.show()
    app.exec_()
    pass

if __name__ == '__main__':
    #thread1=multiprocessing.Process(target=main)
    thread2=multiprocessing.Process(target=DatabaseBase)
    #thread1.start()
    thread2.start()
    main()
