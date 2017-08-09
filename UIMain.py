#five face to find the different area
from GUI.uiMainwindow import Ui_MainWindow
from GUI.uiwindow2 import Ui_Dialog
import caffe
import multiprocessing
from PyQt5.QtWebKitWidgets import *
from gtts import gTTS
from pygame import mixer
import tempfile
from database.Database import *
from imgproc.face_detection import *
from imgproc.liveness_detection import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import os
import time
import cv2
import pickle
import numpy
from nameold import SpiderRenewerByName

global scoreT
scoreT = 0.55


class Camera(QMainWindow, Ui_MainWindow):
    def __init__(self, cameraNum,detectionModel,recognitionModel,svmModels,child_conn,parent=None):
        super(Camera, self).__init__(parent)
        self.cameraNum = cameraNum
        self.device = cv2.VideoCapture(cameraNum)
        self.detectionModel = detectionModel
        self.recognitionModel = recognitionModel
        self.recog = False
        self.tempList = {'valid': False, 'data': []}
        self.tempListCache = []
        self.svmModels = svmModels
        self.webimage = Screenshot()
        self.homePage = ''
        self.Child = child_conn
        self.setupUi(self)
        self.timer = QTimer()                                                           #show on screen
        self.timerRec = QTimer()                                                        #show on label
        self.timerSet = QTimer()                                                         #input the data
        self.backColor = QPixmap(self.Qtvideo.size()).fill(Qt.white)
        self.Qtvideo.autoFillBackground()
        self.timer.setInterval(10)
        self.timerRec.setInterval(1000)
        self.timerSet.setInterval(20000)                                              #milisecond
        self.timer.timeout.connect(self.showCamera)
        self.timerRec.timeout.connect(self.preRecognize)
        self.timerSet.timeout.connect(self.dataAppendPre)
        self.pushButton.setCheckable(True)
        self.pushButton.clicked[bool].connect(self.startCamera)
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.clicked[bool].connect(self.startRecognize)
        #self.pushButton_2.clicked.connect(self.startRecognize)
        self.pushButton_4.clicked.connect(QCoreApplication.instance().quit)
        self.chars = [0]*32
        self.stus = False

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
            appendData = self.tempList.copy()
            threadAppend = multiprocessing.Process(target=self.dataAppend,args=(appendData,))
            threadAppend.start()
            print('start data appending...')
            self.tempList['valid'] = False
            self.tempList['data'] = []

    def startCamera(self,pressed):
        if pressed:
            self.timer.start()
        else:
            self.timer.stop()
        pass

    def dataAppendPre(self):
        appendData = self.tempList.copy()
        threadAppend = multiprocessing.Process(target=self.dataAppend, args=(appendData,))
        threadAppend.start()
        print('start data appending...')
        self.tempList['valid'] = False
        self.tempList['data'] = []

    def dataAppend(self,appendData):
        status = RebaseStatus()
        if status == 0:
            ###########
            #we need to append sth here
            appendData = TempListArrange(appendData)
            ###########
            print(len(appendData))
            databaseAppend(appendData)
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
        ######kill the procedure
        if int(time.strftime("%Y%m%d%H%M%S", time.localtime()))%1000000<180000:
            #self.pushButton_2.clicked = False
            pass


    def preRecognize(self):
        pic1 = self.img.copy()
        pic2 = self.img.copy()
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
        grayMax = 2.9
        bbox = [bboxCam1,bboxCam2,bboxCam3]
        img =  [imgCam1,imgCam2,imgCam3]
        for num in range(len(bbox)):
            a = int(bbox[num][0])
            b = int(bbox[num][1])
            c = int(bbox[num][2] + bbox[num][0])
            d = int(bbox[num][3] + bbox[num][1])
            Ip1 = numpy.array(img[num], dtype=numpy.uint8)

            gray = cv2.cvtColor(Ip1, cv2.COLOR_BGR2GRAY)
            diffx = gray[b + 1:d + 1, a:c] - gray[b:d, a:c]
            diffy = gray[b:d, a + 1:c + 1] - gray[b:d, a:c]
            diffs = numpy.sqrt(numpy.square(diffx) + numpy.square(diffy))
            gray = numpy.mean(diffs)
            if gray>grayMax:
                grayMax = gray
                bestImg = img[num]
                bestBox = bbox[num]
        print(grayMax)
        if grayMax < 3:
            return None

        self.bboxCam = bestBox
        self.imgCam = bestImg
        if len(self.bboxCam) == 0:
            return None
        truthness1 = livenessDetectNoCaffe(imgCam1, bboxCam1, self.svmModels)
        #truthness2 = livenessDetectNoCaffe(imgCam2, bboxCam2, self.svmModels)
        #truthness3 = livenessDetectNoCaffe(imgCam3, bboxCam3, self.svmModels)
        if truthness1< 0:
            self.recognize(True)
            print([True]*10)
        else:
            self.recognize(True)
            #self.recognize(False)
            print([False]*10)

        pass

    def recognize(self,judge):
        feature = feature_Extract(self.recognitionModel,self.bboxCam,self.imgCam,128,128)
        feature = numpy.divide(feature,numpy.sqrt(numpy.dot(feature,feature.T)))
        timelabel = time.strftime("%Y%m%d%H%M%S", time.localtime())
        timelabel = int(timelabel)
        feaMap = {'time': timelabel, 'feature': feature}
        if self.tempList['valid']==False:
            self.tempList['valid']=True
        startVariable = max(0,len(self.tempList['data'])-2)
        hehe = False
        '''for items in range(startVariable,len(self.tempList['data'])):   #further recover from the front
            info = self.tempList['data'][items]
            if abs(numpy.dot(feature,info['feature'].T)-0.0>0.45):
                if abs(timelabel-info['time']<1000):
                    if judge:
                        self.tempList['data'][items]['time'] = feaMap['time']
                        self.tempList['data'][items]['feature'] = feaMap['feature']
                    return None'''
        start = time.clock()
        #information = {'name':'Unknown','visit0':0}
        dtime = int(time.strftime("%Y%m%d%H%M%S", time.localtime())) % 1000000
        if dtime<2000:
            self.timerRec.stop()
            self.timerSet.stop()
            appendData = self.tempList.copy()
            threadAppend = multiprocessing.Process(target=self.dataAppend, args=(appendData,))
            threadAppend.start()
            print('start data appending...')
            self.tempList['valid'] = False
            self.tempList['data'] = []
            time.sleep(3600*6)
            self.timerRec.start()
            self.timerSet.start()
            return None


        information = databaseSearch(feature)
        print(time.clock()-start)
        S = max(self.bboxCam[2], self.bboxCam[3]) * 1.4
        self.bboxCam[0] = self.bboxCam[0] + (self.bboxCam[2] - S) / 2
        self.bboxCam[1] = self.bboxCam[1] + (self.bboxCam[3] - S) / 2
        self.bboxCam[3] = self.bboxCam[2] = S
        a = int(self.bboxCam[0])
        b = int(self.bboxCam[1])
        c = int(self.bboxCam[2])
        d = int(self.bboxCam[3])
        self.photoImage = self.imgCam[b:(b + d), a: (a + c)]
        if information=={}:
            self.QtuserName.setText(' ')
            self.QtVisit1.setText(' ')
            self.QtVisit2.setText(' ')
            self.QtVisit3.setText(' ')
            self.QtFirstVisit.setText(' ')
            self.QtName1.setText(' ')
            self.QtName2.setText(' ')
            self.QtPhoto1.setText(' ')
            self.QtPhoto2.setText(' ')
            self.QtFirstVisit.setText(' ')
            self.QtHomepage.setText(' ')
            self.QtPhoto.setText(' ')
            return None
        print(time.clock()-start)
        if 'name' in information:
            if information['name']!=0 and information['name']!='':
                words = information['name'].replace(' ',',')
                presentTime =  int(time.strftime("%Y%m%d%H%M%S", time.localtime()))
                self.chars[presentTime%30] = words
                if 'visit0' in information and 'visit1' in information and 'visit0' in information:
                    recentTime = max(int(information['visit0']),int(information['visit1']),int(information['visit2']))
                else:
                    recentTime = 0
                thread3 = multiprocessing.Process(target=speech,args=(self.chars[presentTime%30],presentTime,recentTime,judge))
                thread3.start()
            else:
                for items in range(startVariable, len(self.tempList['data'])):  # further recover from the front
                    info = self.tempList['data'][items]
                    if abs(numpy.dot(feature, info['feature'].T) - 0.0 < 0.45 or abs(timelabel - info['time'] > 10)):
                        words = ''
                        presentTime = int(time.strftime("%Y%m%d%H%M%S", time.localtime()))
                        self.chars[presentTime % 30] = words
                        if 'visit0' in information and 'visit1' in information and 'visit0' in information:
                            recentTime = max(int(information['visit0']), int(information['visit1']), int(information['visit2']))
                        else:
                            recentTime = 0
                        thread3 = multiprocessing.Process(target=speech,
                                                          args=(self.chars[presentTime % 30], presentTime, recentTime, judge))
                        thread3.start()
            self.name = information['name']
            self.QtuserName.setText(self.name)
            self.QtuserName.setWordWrap(True)

        print(time.clock()-start)
        if 'visit0' in information:
            if information['visit0']!=0:
                visit0 = str(information['visit0'])
                self.QtVisit1.setText(visit0[0:4]+'年'+visit0[4:6]+'月'+visit0[6:8]+'日')
            else:
                self.QtVisit1.setText(' ')
        if 'visit1' in information:
            if information['visit1']!=0:

                visit1 = str(information['visit0'])
                self.QtVisit2.setText(visit1[0:4]+'年'+visit1[4:6]+'月'+visit1[6:8]+'日')
            else:
                self.QtVisit2.setText(' ')
        if 'visit2' in information:
            if information['visit2']!=0:
                visit2 = str(information['visit0'])
                self.QtVisit3.setText(visit2[0:4]+'年'+visit2[4:6]+'月'+visit2[6:8]+'日')
            else:
                self.QtVisit3.setText(' ')

        #if 'recentVisit' in information:
        #    self.recent = information['recentVisit']
        #    self.QtVisit1.setText(str(self.recent[0]))
        #    self.QtVisit2.setText(str(self.recent[1]))
        #    self.QtVisit3.setText(str(self.recent[2]))
        print(time.clock()-start)
        if 'firstVisit' in information:
            fv = str(information['firstVisit'])
            self.QtFirstVisit.setText(fv[0:4]+'年'+fv[4:6]+'月'+fv[6:8]+'日')
        else:
            self.QtFirstVisit.setText(' ')
        print(time.clock()-start)
        if 'url' in information:
            if 1 or self.homePage != information['url']:
                self.homePage = information['url']
                if self.homePage!= '' and self.homePage != 0:
                    self.webimage.capture(self.homePage)
                    tempImg = QPixmap.fromImage(self.webimage.webimg).scaled(self.QtHomepage.size())
                    self.QtHomepage.setPixmap(tempImg)
                else:
                    self.QtHomepage.setText(' ')
        print(time.clock()-start)
        if 'famiPeople0' in information:
            if information['famiPeople0'] != 0 and information['famiPeople0'] != {}:
                tempImg = QPixmap(information['famiPeople0']['img_path']).scaled(self.QtPhoto1.size())
                self.QtPhoto1.setPixmap(tempImg)
                self.QtName1.setText(information['famiPeople0']['name'])
                self.QtName1.setWordWrap(True)
                #self.QtName1.setAlignment()
            else:
                self.QtPhoto1.setText(' ')
                self.QtName1.setText(' ')
        if 'famiPeople1' in information:
            if information['famiPeople1'] != 0 and information['famiPeople1'] != {}:
                tempImg = QPixmap(information['famiPeople1']['img_path']).scaled(self.QtPhoto2.size())
                self.QtPhoto2.setPixmap(tempImg)
                self.QtName2.setText(information['famiPeople1']['name'])
                self.QtName2.setWordWrap(True)
            else:
                self.QtPhoto2.setText(' ')
                self.QtName2.setText(' ')

        if 'img_path' in information:
            if information['img_path'] == '' and judge == True and hehe == False:
                path = '/home/luka/PycharmProjects/Github/Spider/Spider/From_camera/'
                if not os.path.isdir(path):
                    os.makedirs(path)
                path = path + str(timelabel) + '.jpg'
                cv2.imwrite(path, cv2.cvtColor(self.photoImage,cv2.COLOR_BGR2RGB))
                feaMap['img_path'] = path
                self.QtPhoto.setText(' ')
            else:
                ################################################
                ##should delete all these considering Hardward##
                ################################################
                path = '/home/luka/PycharmProjects/Github/Spider/Spider/From_camera/'
                if not os.path.isdir(path):
                    os.makedirs(path)
                path = path + str(timelabel) + '.jpg'
                cv2.imwrite(path, cv2.cvtColor(self.photoImage, cv2.COLOR_BGR2RGB))
                feaMap['img_path'] = path
                ################################################
                ##should delete all these considering Hardward##
                ################################################
                self.photo = information['img_path']                #recover
                tempPix = QPixmap(self.photo).scaled(self.QtPhoto.size())
                self.QtPhoto.setPixmap(tempPix)
                ###find logical problems here
                #if os.path.isdir(information['img_path']):
                #    dealWithImg(information)

        if hehe == False and judge == True:
            self.tempList['data'].append(feaMap)
        print(time.clock()-start)
        print(self.tempList['valid'],len(self.tempList['data']))
        pass

    def Confirm(self):
        self.text1 = self.Message.lineEdit.text()
        self.text2 = self.Message.lineEdit_6.text()
        self.text3 = self.Message.lineEdit_7.text()
        self.text4 = self.Message.lineEdit_8.text()
        self.text5 = self.Message.lineEdit_9.text()
        self.Child.send(['name',self.text1])

#a new thread
#append the data every single day
'''
Need to debug
'''
def TempListArrange(tempList):
    '''
    method:
    to renew the database every single day
    '''
    global scoreT
    score = scoreT
    if tempList['valid'] == False:
        return tempList
    info = tempList['data'].copy()
    label = 0
    features = []
    for items in info:
        if 'label' in items:
            for sim in info:
                feature1 = sim['feature']
                if 'label' not in sim and numpy.sqrt(numpy.dot(feature0, feature1.T)) > score:
                    features[label].append(feature1)
                    sim['label'] = items['label']
        else:
            items['label'] = label
            feature0 = items['feature']
            features.append([])
            features[label].append(feature0)
            for sim in info:
                feature1 = sim['feature']
                if 'label' not in sim and numpy.sqrt(numpy.dot(feature0,feature1.T))>score:
                    features[label].append(feature1)
                    sim['label'] = label
            label += 1
    for items in info:
        for tems in info:
            feature0 = items['feature']
            feature1 = tems['feature']
            if items['label']!=tems['label'] and numpy.sqrt(numpy.dot(feature0,feature1.T))>score:
                for t in info:
                    if t['label'] == tems['label']:
                        t['label'] = items['label']


    #We need to decide whether to use 'average fake feature' or just the nearest real one
    finalFeature = []
    for i in range(label):
        if len(features[i] )>0:

            cent = numpy.mean(features[i],axis=0)
            nearest = None
            distNearest = -numpy.Inf
            iCount = 0
            for j in info:
                if j['label'] != i:
                    continue
                iCount += 1
                if numpy.dot(cent,j['feature']) > distNearest:
                    dealWithImg(nearest)
                    distNearest = numpy.dot(cent,j['feature']).copy()
                    nearest = j
                else:
                    dealWithImg(j)
            nearest_temp = nearest.copy()
            del(nearest_temp['label'])
            #tempFull = [nearest_temp]*iCount
            #tempFullList = tempFull.copy()
            tempFullList = []
            TCount = 0
            for k in info:
                if k['label'] == i:
                    nt = nearest_temp.copy()
                    nt['time'] = k['time']
                    tempFullList.append(nt)        #We need to apppend time here
                    #TCount += 1
                if TCount >= iCount:
                    break
            finalFeature=finalFeature+tempFullList
        else:
            finalFeature = finalFeature+features[i][0]

    finalList = {'data':finalFeature,'valid':True}
    return finalList

    pass

def dealWithImg(infoDict):
    if infoDict == None:
        return
    if 'img_path' in infoDict:
        os.remove(infoDict['img_path'])
    pass


'''
Need to debug
'''


def DirectAppend(parent_conn):
    rootFile = '/home/luka/PycharmProjects/cvlab/protobuf2/'
    detectionPrototxt = rootFile + 'deploy_face_w.prototxt'
    detectionCaffeModel = rootFile + 'w_iter_100000.caffemodel'
    detectionModel = caffe.Net(detectionPrototxt, detectionCaffeModel, caffe.TEST)

    RecognitionPrototxt = rootFile + 'recognition.prototxt'
    RecognitionCaffeModel = rootFile + '_iter_70000.caffemodel'
    recognitionModel = caffe.Net(RecognitionPrototxt, RecognitionCaffeModel, caffe.TEST)
    while True:
        inform = {}
        type,informs = parent_conn.recv()
        if type == 'name':
            inform['name'] = informs
        caffemodel = [detectionModel,recognitionModel]
        dict={'valid':False,'data':[]}
        value = SpiderRenewerByName(inform,caffemodel)
        if value['name'] is not '':
            dict['valid'] = True
            dict['data'].append(value)
            databaseAppend(dict)

class dialogWindow(Ui_Dialog,QDialog):
    def __init__(self,parent = None):
        super(dialogWindow, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.hide)
        self.pushButton_2.clicked.connect(self.hide)

    def handle_click(self):
        if not self.isVisible():
            self.show()

def speech(userinfo,presentTime,recentTime,truthness):
    #userinfo.replace(' ','。')
    str = '您好！'
    if truthness == False:
        if userinfo != '':
            str = userinfo + '到访实验室的信息如下'
        else:
            str = '您到访实验室的信息如下'
    else:
        if userinfo == '':
            userinfo = '您'
        if recentTime == 0:
            str = '欢迎'+userinfo+'来到实验室！'
        elif presentTime-recentTime > 10:
            if presentTime%2 == 1 and userinfo != '您':
                str = '好久不见！'+userinfo
            elif userinfo != '您':
                str = userinfo + '，咱们又见面了！'
            else:
                str = '欢迎回来！'
        else:
            if userinfo == '您':
                userinfo = ''
            str = '欢迎回来！'+userinfo
    print(str)
    with tempfile.NamedTemporaryFile(delete=True)as fp:
        tts = gTTS(text=str, lang='zh')
        tts.save('{}.mp3'.format(fp.name))
        mixer.init()
        mixer.music.load('{}.mp3'.format(fp.name))
        mixer.music.play()
        time.sleep(30)

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


def main(child_conn):
    caffe.set_mode_gpu()
    rootFile = '/home/luka/PycharmProjects/cvlab/protobuf/'
    detectionPrototxt = rootFile + 'deploy_face_w.prototxt'
    detectionCaffeModel = rootFile + 'w_iter_100000.caffemodel'
    detectionModel = caffe.Net(detectionPrototxt, detectionCaffeModel, caffe.TEST)

    RecognitionPrototxt = rootFile + 'recognition.prototxt'
    RecognitionCaffeModel = rootFile + '_iter_70000.caffemodel'
    recognitionModel = caffe.Net(RecognitionPrototxt, RecognitionCaffeModel, caffe.TEST)


    svmAddress = '/home/luka/PycharmProjects/Github/Demo-System/imgproc/svm.data'
    with open(svmAddress,'rb') as svmFile:
        svmModels = pickle.load(svmFile)

    app = QApplication(sys.argv)
    form = Camera(0,detectionModel,recognitionModel,svmModels,child_conn)
    form.show()
    app.exec_()
    pass


if __name__ == '__main__':
    parent_conn, child_conn = multiprocessing.Pipe()
    thread3 = multiprocessing.Process(target=DirectAppend,args=(parent_conn,))
    thread3.start()
    thread2 = multiprocessing.Process(target=DatabaseBase)
    Timetype = False
    thread2.start()
    main(child_conn)

