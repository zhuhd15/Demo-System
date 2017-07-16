from .uiMainwindow import Ui_MainWindow
from .uiwindow2 import Ui_Dialog
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import sys, os,time,cv2

class Camera(QMainWindow, Ui_MainWindow):
    def __init__(self, cameraNum,parent=None):
        super(Camera, self).__init__(parent)
        self.cameraNum = cameraNum
        self.device = cv2.VideoCapture(cameraNum)
        self.setupUi(self)
        self.timer = QTimer()
        self.backColor = QPixmap(self.label.size()).fill(Qt.white)
        self.label.autoFillBackground()
        self.timer.setInterval(0.04)
        self.timer.timeout.connect(self.showCamera)
        self.pushButton.setCheckable(True)
        self.pushButton.clicked[bool].connect(self.startCamera)
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.clicked[bool].connect(self.recognize)
        self.pushButton_4.clicked.connect(QCoreApplication.instance().quit)

        self.Message = dialogWindow()
        self.pushButton_3.clicked.connect(self.Message.handle_click)
        self.Message.pushButton_2.clicked.connect(self.Confirm)

    def startCamera(self,pressed):
        if pressed:
            self.timer.start()
        else:
            self.timer.stop()
#            self.label.setPixmap(self.backColor)
        pass

    def showCamera(self):
        if self.device.isOpened():
            self.ret, self.img = self.device.read()
        else:
            self.ret = False
        height, width, bytesPerComponent = self.img.shape
        bytesPerLine = bytesPerComponent * width
        cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB, self.img)
        self.image = QImage(self.img.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(self.image))

    def recognize(self):
        self.label_2.setPixmap(QPixmap('1.jpg'))
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





if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Camera(0)
    form.show()
    app.exec_()