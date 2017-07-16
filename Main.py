import caffe
from database.Database import *
from imgproc.face_detection import *
from GUI.UIMain import *

#Interface main
def main():
    '''
    main function
    :return: None
    '''
    rootFile = '/home/luka/Github/caffe models/'
    detectionPrototxt = rootFile + 'face detection/deploy_face_w.prototxt'
    detectionCaffeModel = rootFile + 'face detection/w_iter_100000.caffemodel'
    detectionModel = caffe.Net(detectionPrototxt, detectionCaffeModel, caffe.TEST)

    RecognitionPrototxt = rootFile + 'face recognition/newer/recognition.prototxt'
    RecognitionCaffeModel = rootFile + 'face recognition/newer/_iter_70000.caffemodel'
    recognitionModel = caffe.Net(RecognitionPrototxt, RecognitionCaffeModel, caffe.TEST)

    pass


if __name__=="__main__":
    main()