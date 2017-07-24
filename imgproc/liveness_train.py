import cv2
import os,pickle,caffe
import caffe
import os
import pickle

import cv2

import LBP_pattern
from LBP_pattern import *
from face_detection import FaceDetect
from svm_train import *


def livenessTrain(filepaths,labels,caffemodel):
    slackVariables = 0.1
    collection0 = livenessLabel(caffemodel,filepaths[0],labels[0])
    collection1 = livenessLabel(caffemodel,filepaths[1],labels[1])
    collection2 = livenessLabel(caffemodel,filepaths[2],labels[2])
    collection3 = livenessLabel(caffemodel,filepaths[3],labels[3])
    svmModel00 = trainSVM([collection0[1],collection1[1]],collection0[0]+collection1[0],slackVariables,0.001,40000,'linear')
    svmModel01 = trainSVM([collection0[1],collection2[1]],collection0[0]+collection2[0],slackVariables,0.001,40000,'linear')
    svmModel02 = trainSVM([collection0[1],collection3[1]],collection0[0]+collection3[0],slackVariables,0.001,40000,'linear')
    svmModel03 = trainSVM([collection0[1],collection1[1],collection2[1],collection3[1]],collection0[0]+collection1[0]+collection2[0]+collection3[0],slackVariables,0.001,40000,'linear')

    svmModel10 = trainSVM([collection0[2], collection1[2]], collection0[0] + collection1[0], slackVariables, 0.001,
                          40000, 'linear')
    svmModel11 = trainSVM([collection0[2], collection1[2]], collection0[0] + collection2[0], slackVariables, 0.001,
                          40000, 'linear')
    svmModel12 = trainSVM([collection0[2], collection1[2]], collection0[0] + collection3[0], slackVariables, 0.001,
                          40000, 'linear')
    svmModel13 = trainSVM([collection0[2], collection1[2], collection2[2], collection3[2]],
                          collection0[0] + collection1[0] + collection2[0] + collection3[0], slackVariables, 0.001,
                          40000, 'linear')

    svmModel20 = trainSVM([collection0[3], collection1[3]], collection0[0] + collection1[0], slackVariables, 0.001,
                          40000, 'linear')
    svmModel21 = trainSVM([collection0[3], collection1[3]], collection0[0] + collection2[0], slackVariables, 0.001,
                          40000, 'linear')
    svmModel22 = trainSVM([collection0[3], collection1[3]], collection0[0] + collection3[0], slackVariables, 0.001,
                          40000, 'linear')
    svmModel23 = trainSVM([collection0[3], collection1[3], collection2[3], collection3[3]],
                          collection0[0] + collection1[0] + collection2[0] + collection3[0], slackVariables, 0.001,
                          40000, 'linear')
    svmModels=[svmModel00,svmModel01,svmModel02,svmModel03,svmModel10,svmModel11,svmModel12,svmModel13,svmModel20,svmModel21,svmModel22,svmModel23]
    svmAddress = 'svm.data'
    with open(svmAddress,'wb') as svmFile:
        pickle.dump(svmModels,svmFile)
    pass


def livenessLabel(caffemodel,filePath,label):
    pathDir = os.listdir(filePath)
    groupLBP = []
    groupCM = []
    groupFeatures = []
    i = int(0)
    for fileName in pathDir:
        i += 1
        allFiles = os.path.join('%s%s' % (filePath, fileName))
        picture = cv2.imread(allFiles,cv2.IMREAD_COLOR)
        feature = featureGenerate(caffemodel,picture)
        lbpPattern = feature[0]
        colourMoment = feature[1]
        groupLBP = [groupLBP,lbpPattern]
        groupCM = [groupCM,colourMoment]
        groupFeatures = [groupFeatures,lbpPattern+colourMoment]
    labels = label * i
    return [labels,groupLBP,groupCM,groupFeatures]

def featureGen(Ip,bbox):
    a = int(bbox[0])
    b = int(bbox[1])
    c = int(bbox[2])
    d = int(bbox[3])
    if bbox[2] < 100 or bbox[3] < 100:
        return []
    faceImg = Ip[b:(b + d), a: (a + c)]
    faceImg = cv2.resize(faceImg, (144, 120), interpolation=cv2.INTER_CUBIC)[:, :, 0]
    facePattern = LBP(faceImg)
    lbp = []
    for x in range(0, 113, 16):
        for y in range(0, 97, 16):
            pix = facePattern[x:min(x + 31, 142), y:min(y + 31, 118)]
            lbpValue = faceLBP(pix)
            lbp = lbp + lbpValue
    colour_moment = colorMoment(faceImg)
    return [lbpValue, colour_moment]
    pass

def featureGenerate(caffemodel,picture):
    picture = cv2.cvtColor(picture,cv2.COLOR_BGR2RGB)
    min_size = 50
    [bbox, Ip] = FaceDetect(picture, min_size, caffemodel)
    S = max(bbox[2], bbox[3]) * 1.3
    bbox[0] = bbox[0] + (bbox[2] - S) / 2
    bbox[1] = bbox[1] + (bbox[3] - S) / 2
    bbox[3] = bbox[2] = S
    a = int(bbox[0])
    b = int(bbox[1])
    c = int(bbox[2])
    d = int(bbox[3])
    if bbox[2] < 100 or bbox[3] < 100:
        return []
    faceImg = Ip[b:(b + d), a: (a + c)]
    cv2.imshow('tst',faceImg)
    cv2.waitKey(0)
    faceImg = cv2.resize(faceImg,(144,120),interpolation=cv2.INTER_CUBIC)[:,:,0]
    facePattern = LBP(faceImg)
    lbp = []
    for x in range(0,113,16):
        for y in range(0,97,16):
            pix = facePattern[x:min(x+31,142),y:min(y+31,118)]
            lbpValue = faceLBP(pix)
            lbp=lbp+lbpValue
    colour_moment = colorMoment(faceImg)
    return [lbpValue,colour_moment]
    pass


if __name__ == '__main__':
    caffe.set_mode_gpu()
    picRoot = '/home/luka/PycharmProjects/cvlab/svmTrain/'
    path1 = picRoot + 'true_origin/'
    path2 = picRoot + 'false1_origin/'
    path3 = picRoot + 'false2_origin/'
    path4 = picRoot + 'false3_origin/'
    paths = [path1,path2,path3,path4]
    labels = [-1,1,1,1]
    root = "/home/luka/PycharmProjects/cvlab/"
    deploy = root + "protobuf/deploy_face_w.prototxt"
    caffe_model = root + "protobuf/w_iter_100000.caffemodel"
    caffemodel = caffe.Net(deploy,caffe_model,caffe.TEST)
    livenessTrain(paths,labels,caffemodel)
    pass