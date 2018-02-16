import numpy
import os,pickle,caffe
import caffe
import os
import pickle
from imgproc.LivenessFuncs.featureCal import *
import cv2
from sklearn import svm

from imgproc.LivenessFuncs.LBP_pattern import *

def livenessTrain(filepaths,labels,caffemodel):
    slackVariables = 0.1
    collection0 = livenessLabel(caffemodel,filepaths[0],labels[0])
    collection1 = livenessLabel(caffemodel,filepaths[1],labels[1])
    collection2 = livenessLabel(caffemodel,filepaths[2],labels[2])
    #collection3 = livenessLabel(caffemodel,filepaths[3],labels[3])
    svmModel00 = svm.LinearSVC()
    svmModel01 = svm.LinearSVC()
    svmModel02 = svm.LinearSVC()

    svmModel10 = svm.LinearSVC()
    svmModel11 = svm.LinearSVC()
    svmModel12 = svm.LinearSVC()

    svmModel20 = svm.LinearSVC()
    svmModel21 = svm.LinearSVC()
    svmModel22 = svm.LinearSVC()

    svmModel00.fit(collection0[1]+collection2[1],collection0[0]+collection2[0])
    svmModel01.fit(collection0[1]+collection1[1],collection0[0]+collection1[0])
    svmModel02.fit(collection0[1]+collection2[1]+collection1[1],collection0[0]+collection2[0]+collection1[0])

    svmModel10.fit(collection0[2]+collection2[2],collection0[0]+collection2[0])
    svmModel11.fit(collection0[2]+collection1[2],collection0[0]+collection1[0])
    svmModel12.fit(collection0[2]+collection2[2]+collection1[2],collection0[0]+collection2[0]+collection1[0])

    svmModel20.fit(collection0[3]+collection2[3],collection0[0]+collection2[0])
    svmModel21.fit(collection0[3]+collection1[3],collection0[0]+collection1[0])
    svmModel22.fit(collection0[3]+collection2[3]+collection1[3],collection0[0]+collection2[0]+collection1[0])

    tho = svmModel00.predict([collection2[1][0]])

    print(tho)
    tho = svmModel01.predict([collection2[1][0]])

    print(tho)
    tho = svmModel02.predict([collection2[1][0]])

    print(tho)
    aa=1
    #svmModel00 = trainSVM([collection0[1],collection1[1]],collection0[0]+collection1[0],slackVariables,0.001,40000,('linear',1.0))
    #svmModel01 = trainSVM([collection0[1],collection2[1]],collection0[0]+collection2[0],slackVariables,0.001,40000,('linear',1.0))
    #svmModel02 = trainSVM([collection0[1],collection3[1]],collection0[0]+collection3[0],slackVariables,0.001,40000,('linear',1.0))
    #svmModel03 = trainSVM([collection0[1],collection1[1],collection2[1],collection3[1]],collection0[0]+collection1[0]+collection2[0]+collection3[0],slackVariables,0.001,40000,'linear')
#
    #svmModel10 = trainSVM([collection0[2], collection1[2]], collection0[0] + collection1[0], slackVariables, 0.001,
    #                      40000, 'linear')
    #svmModel11 = trainSVM([collection0[2], collection1[2]], collection0[0] + collection2[0], slackVariables, 0.001,
    #                      40000, 'linear')
    #svmModel12 = trainSVM([collection0[2], collection1[2]], collection0[0] + collection3[0], slackVariables, 0.001,
    #                      40000, 'linear')
    #svmModel13 = trainSVM([collection0[2], collection1[2], collection2[2], collection3[2]],
    #                      collection0[0] + collection1[0] + collection2[0] + collection3[0], slackVariables, 0.001,
    #                      40000, 'linear')
#
    #svmModel20 = trainSVM([collection0[3], collection1[3]], collection0[0] + collection1[0], slackVariables, 0.001,
    #                      40000, 'linear')
    #svmModel21 = trainSVM([collection0[3], collection1[3]], collection0[0] + collection2[0], slackVariables, 0.001,
    #                      40000, 'linear')
    #svmModel22 = trainSVM([collection0[3], collection1[3]], collection0[0] + collection3[0], slackVariables, 0.001,
    #                      40000, 'linear')
    #svmModel23 = trainSVM([collection0[3], collection1[3], collection2[3], collection3[3]],
    #                      collection0[0] + collection1[0] + collection2[0] + collection3[0], slackVariables, 0.001,
    #                      40000, 'linear')
    #svmModels=[svmModel00,svmModel01,svmModel02,svmModel03,svmModel10,svmModel11,svmModel12,svmModel13,svmModel20,svmModel21,svmModel22,svmModel23]
    svmModels = [svmModel00, svmModel01, svmModel02, svmModel10, svmModel11, svmModel12,
                 svmModel20, svmModel21, svmModel22]

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
        allFiles = os.path.join('%s%s' % (filePath, fileName))
        picture = cv2.imread(allFiles,cv2.IMREAD_COLOR)
        feature = featureGenerate(caffemodel,picture)
        if feature == None:
            continue
        if feature == []:
            continue
        lbpPattern = feature[0]
        colourMoment = feature[1]
        groupLBP.append(lbpPattern)

        groupCM.append(colourMoment)
        GPFeature = numpy.zeros(3313)
        GPFeature[0:9]=colourMoment[:]
        GPFeature[9:3313]=lbpPattern[:]
        groupFeatures.append(GPFeature)
        #groupFeatures=0
        i += 1
    print(i)
    labels = [label] * i
    return [labels,groupLBP,groupCM,groupFeatures]

'''def featureGen(Ip,bbox):
    a = int(bbox[0])
    b = int(bbox[1])
    c = int(bbox[2])
    d = int(bbox[3])
    if bbox[2] < 100 or bbox[3] < 100:
        return []
    faceImg = Ip[b:(b + d), a: (a + c)]
    faceImg = cv2.resize(faceImg, (144, 120), interpolation=cv2.INTER_CUBIC)[:, :, 0]
    sp=[[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]]
    facePattern = LBP(faceImg)
    lbp = []
    for x in range(0, 113, 16):
        for y in range(0, 97, 16):
            pix = facePattern[x:min(x + 31, 142), y:min(y + 31, 118)]
            lbpValue = faceLBP(pix)
            lbp = lbp + lbpValue
    colour_moment = colorMoment(faceImg)
    return [lbpValue, colour_moment]
    pass'''










if __name__ == '__main__':
    caffe.set_mode_gpu()
    picRoot = '/home/luka/PycharmProjects/cvlab/imgcollection/'
    path1 = picRoot + 'true/'
    path2 = picRoot + 'phone/'
    path3 = picRoot + 'screen/'
    #path4 = picRoot + 'false3_origin/'
    paths = [path1,path2,path3]
    labels = [-1,1,1]
    root = "/home/luka/PycharmProjects/cvlab/"
    deploy = root + "protobuf/deploy_face_w.prototxt"
    caffe_model = root + "protobuf/w_iter_100000.caffemodel"
    caffemodel = caffe.Net(deploy,caffe_model,caffe.TEST)
    livenessTrain(paths,labels,caffemodel)
    pass