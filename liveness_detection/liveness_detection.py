import cv2
import numpy,pickle
from svm_train import resultSVM
from liveness_train import featureGenerate,caffe

def liveness_detection(image,caffemodel,svmModels):
    picFeatures = featureGenerate(caffemodel,image)
    lbpFeature = picFeatures[0]
    colorFeature = picFeatures[1]
    totalFeature = picFeatures[0]+picFeatures[1]
    label00 = resultSVM(svmModels[0],lbpFeature)
    label01 = resultSVM(svmModels[1],lbpFeature)
    label02 = resultSVM(svmModels[2],lbpFeature)
    label03 = resultSVM(svmModels[3],lbpFeature)

    label10 = resultSVM(svmModels[4], colorFeature)
    label11 = resultSVM(svmModels[5], colorFeature)
    label12 = resultSVM(svmModels[6], colorFeature)
    label13 = resultSVM(svmModels[7], colorFeature)

    label20 = resultSVM(svmModels[8], totalFeature)
    label21 = resultSVM(svmModels[9], totalFeature)
    label22 = resultSVM(svmModels[10], totalFeature)
    label23 = resultSVM(svmModels[11], totalFeature)

    #further feature calculation here
    label = numpy.mean([label00,label01,label02,label03,label10,label11,label12,label13,label20,label21,label22,label23])
    return label

    pass

if __name__=='__main__':
    fileName = 'img/1.jpg'
    img = cv2.imread(fileName,cv2.IMREAD_COLOR)

    root = "/home/luka/PycharmProjects/cvlab/"
    deploy = root + "protobuf/deploy_face_w.prototxt"
    caffe_model = root + "protobuf/w_iter_100000.caffemodel"
    caffemodel = caffe.Net(deploy,caffe_model,caffe.TEST)

    svmAddress = 'svm.data'
    with open(svmAddress,'rb') as svmFile:
        svmModels = pickle.load(svmFile)

    label = liveness_detection(img,caffemodel,svmModels)
    print(label)
    pass