import cv2,sys
import numpy,pickle,caffe,sklearn,time
sys.path.append('/home/luka/PycharmProjects/Github/Demo-System/imgproc')
from .LBP_pattern import featureGenerate,featureGen
from .featureCal import *
import warnings
warnings.filterwarnings("ignore")

def liveness_detection(image,caffemodel,svmModels):
    picFeatures = featureGenerate(caffemodel,image)
    if picFeatures == None or picFeatures == []:
        return []

    lbpFeature = picFeatures[0]
    colorFeature = picFeatures[1]


    totalFeature = numpy.zeros(3313)
    totalFeature[0:9] = colorFeature[:]
    totalFeature[9:3313] = lbpFeature[:]
    label00 = svmModels[0].predict(lbpFeature)
    label01 = svmModels[1].predict(lbpFeature)
    label02 = svmModels[2].predict(lbpFeature)
    #label03 = svmModels[3],lbpFeature)

    label10 = svmModels[3].predict(colorFeature)
    label11 = svmModels[4].predict(colorFeature)
    label12 = svmModels[5].predict(colorFeature)
    #label13 = resultSVM(svmModels[7], colorFeature)

    label20 = svmModels[6].predict(totalFeature)
    label21 = svmModels[7].predict(totalFeature)
    label22 = svmModels[8].predict(totalFeature)
    #label23 = resultSVM(svmModels[11], totalFeature)
    #further feature calculation here
    #label = numpy.mean([label00,label01,label02,label03,label10,label11,label12,label13,label20,label21,label22,label23])
    print([label00,label01,label02,label10,label11,label12,label20,label21,label22])
    label = numpy.mean([label00, label01, label02, label10, label11, label12,label20, label21, label22])
    return label

def livenessDetectNoCaffe(image,bbox,svmModels):
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
    originFace = image[b:(b + d), a: (a + c)]
    picFeatures = featureGen(originFace)
    lbpFeature = picFeatures[0]
    colorFeature = picFeatures[1]

    totalFeature = numpy.zeros(3313)
    totalFeature[0:9] = colorFeature[:]
    totalFeature[9:3313] = lbpFeature[:]
    label00 = svmModels[0].predict(lbpFeature)
    label01 = svmModels[1].predict(lbpFeature)
    label02 = svmModels[2].predict(lbpFeature)
    # label03 = svmModels[3],lbpFeature)

    label10 = svmModels[3].predict(colorFeature)
    label11 = svmModels[4].predict(colorFeature)
    label12 = svmModels[5].predict(colorFeature)
    # label13 = resultSVM(svmModels[7], colorFeature)

    label20 = svmModels[6].predict(totalFeature)
    label21 = svmModels[7].predict(totalFeature)
    label22 = svmModels[8].predict(totalFeature)
    # label23 = resultSVM(svmModels[11], totalFeature)

    # further feature calculation here
    # label = numpy.mean([label00,label01,label02,label03,label10,label11,label12,label13,label20,label21,label22,label23])
    print([label00, label01, label02, label10, label11, label12, label20, label21, label22])
    label = numpy.mean([label00, label01, label02, label10, label11, label12, label20, label21, label22])
    return label

if __name__=='__main__':
    caffe.set_mode_gpu()
    fileName = '/home/luka/PycharmProjects/cvlab/img/2.jpg'
    img = cv2.imread(fileName,cv2.IMREAD_COLOR)

    root = "/home/luka/PycharmProjects/cvlab/"
    deploy = root + "protobuf/deploy_face_w.prototxt"
    caffe_model = root + "protobuf/w_iter_100000.caffemodel"
    caffemodel = caffe.Net(deploy,caffe_model,caffe.TEST)

    svmAddress = 'svm.data'
    with open(svmAddress,'rb') as svmFile:
        svmModels = pickle.load(svmFile)
    cap = cv2.VideoCapture(0)
    while (True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        cv2.imshow('tst',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        label = liveness_detection(frame,caffemodel,svmModels)
        if label == []:
            continue
        print(label)

    cap.release()
    cv2.destroyAllWindows()

    pass