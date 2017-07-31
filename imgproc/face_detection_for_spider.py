import caffe,cv2
import numpy,math,time
from skimage import measure

def FaceDetect_spider(im,min_size,net):
    M_BGR=[104.,117.,123.]
    heigth,width,depth=im.shape
    pad_size = min(256,round(heigth*0.31))
    mean_value=numpy.mean(im)
    Ip= cv2.copyMakeBorder(im,pad_size,pad_size,pad_size,pad_size,cv2.BORDER_CONSTANT,value=[mean_value,mean_value,mean_value])
    #cv2.imshow('ttt',Ip)
    #cv2.waitKey(0)
    Hp,Wp,Dp=Ip.shape
    rsz = math.ceil(2*math.ceil(16*min(Hp,Wp)/min_size)/16)*16;
    if Wp >= Hp:
        Hi = rsz
        Wi = math.ceil(rsz / Hp * Wp / 16) * 16;
    else:
        Wi = rsz
        Hi = math.ceil(rsz / Wp * Hp / 16) * 16;
    im_data=cv2.resize(Ip,(Wi,Hi))
    im_data=numpy.array(im_data,dtype=numpy.single)
    heigth,width,Dp=im_data.shape
    im_data[:, :, 0] = im_data[:,:,0] - M_BGR[0]
    im_data[:, :, 1] = im_data[:,:,1] - M_BGR[1]
    im_data[:, :, 2] = im_data[:,:,2] - M_BGR[2]
    s=net.blobs['data'].shape
    net.blobs['data'].reshape(1,3,heigth,width)
    transformer = caffe.io.Transformer({'data':net.blobs['data'].data.shape})
    transformer.set_transpose('data', (2,0,1))
    net.blobs['data'].data[...] = transformer.preprocess('data',im_data)
    scores = net.forward()
    ScoreInit=numpy.array(1.0/(1.0+numpy.exp(-scores['label/conv2'])),dtype=float)
    Boundary=numpy.array(scores['bbox/conv2'])
    a,b,c,d=ScoreInit.shape
    scoresOut=numpy.resize(ScoreInit,[c,d])
    scoresOut=cv2.resize(numpy.array(scoresOut),(Wp,Hp),interpolation=cv2.INTER_CUBIC)
    scoresOut=1*(scoresOut>0.23)
    label_img = measure.label(scoresOut, connectivity = 2)
    bd=measure.regionprops(label_img)

    if bd==[]:
        return [[],Ip]

    mx_area=0
    tempDict = {}
    for x in bd:
        tempDict[x.area] = x.bbox
    ind = sorted(tempDict)
    indexSet = ind[max(0,len(ind)-5):len(ind)]
    bboxSet = []
    for index in indexSet:
        bboxSet.append(tempDict[index])

    '''for x in bd:
        if x.area>mx_area:
            mx_area=x.area
            mx_bbox=x.bbox'''
    bboxCol = []
    for mx_bbox in bboxSet:
        bbox=[0,0,0,0]
        bbox[0]=int(numpy.floor( mx_bbox[0] * c/Hp ))
        bbox[1]=int(numpy.floor( mx_bbox[1] * d/Wp ))
        bbox[2]=int(numpy.floor( mx_bbox[2] * c/Hp ))
        bbox[3]=int(numpy.floor( mx_bbox[3] * d/Wp ))

        b_new=numpy.array([0,0,0,0])
        IterSum=0
        for x0 in range(bbox[1],bbox[3]):           #width
            for y0 in range(bbox[0],bbox[2]):
                b=Boundary[0,:,y0,x0]
                b=numpy.array([(x0+b[0])*Wp/d,(y0+b[2])*Hp/c,(x0+b[1])*Wp/d,(y0+b[3])*Hp/c])
                b[2]=b[2]-b[0]
                b[3]=b[3]-b[1]
                b_new=b_new+b*ScoreInit[0,0,y0,x0]
                IterSum=IterSum+ScoreInit[0,0,y0,x0]
        if IterSum == 0:
            continue
        b_new=b_new/IterSum
        b_new[0] = b_new[0] + b_new[2] / 2
        b_new[1] = b_new[1] + b_new[3] / 2
        repmat = max(numpy.ceil(b_new[2]*2/16)*16,numpy.ceil(b_new[3]*2/16)*16)-2
        b_new[2]=repmat
        b_new[3]=repmat
        b_new[0]=max(0,numpy.round(b_new[0]-b_new[2]/2))
        b_new[1]=max(0,numpy.round(b_new[1]-b_new[3]/2))
        b_new[2] = min(Wp, b_new[2]);
        b_new[3] = min(Hp, b_new[3]);

        bbox = b_new
        Ic=Ip[int(bbox[1]):int(bbox[1]+bbox[3]),int(bbox[0]):int(bbox[0]+bbox[2])]
        Hc,Wc,Dc=Ic.shape
        im_data=cv2.resize(numpy.array(Ic),(160,160),interpolation=cv2.INTER_CUBIC)
        im_data=numpy.array(im_data,dtype=numpy.single)

        im_data[:, :, 0] = im_data[:,:,0] - M_BGR[0]
        im_data[:, :, 1] = im_data[:,:,1] - M_BGR[1]
        im_data[:, :, 2] = im_data[:,:,2] - M_BGR[2]

        net.blobs['data'].reshape(1,3,160,160)
        transformer = caffe.io.Transformer({'data':net.blobs['data'].data.shape})
        transformer.set_transpose('data', (2,0,1))
        net.blobs['data'].data[...] = transformer.preprocess('data',im_data)
        scores1 = net.forward()

        ScoreInit1=numpy.array(1.0/(1.0+numpy.exp(-scores1['label/conv2'])),dtype=float)
        Boundary1=numpy.array(scores1['bbox/conv2'])
        b_new=[0,0,0,0]
        Tsum=0
        for x0 in [3,4,5]:
            for y0 in [3,4,5]:
                b=Boundary1[0,:,y0,x0]
                b = numpy.array([(x0 + b[0]) * Wc / 10, (y0 + b[2]) * Hc / 10, (x0 + b[1]) * Wc / 10, (y0 + b[3]) * Hc / 10])
                b[2]=b[2]-b[0]
                b[3]=b[3]-b[1]
                b_new=b_new+b*ScoreInit1[0,0,y0,x0]
                Tsum=Tsum+ScoreInit1[0,0,y0,x0]
        b_new=b_new/Tsum
        b_new[0]=b_new[0]+bbox[0]
        b_new[1]=b_new[1]+bbox[1]
        if b_new[3]<min_size:
            continue
    #    if b_new in bboxCol:
            continue
        for boxitem in bboxCol:
            pass
        bboxCol.append(b_new)
    #check the validity of the box set

    return [bboxCol,Ip]

def feature_Extract_spider(caffemodel,bbox,image,W,H):
    S = max(bbox[2], bbox[3]) * 1.4
    bbox[0] = bbox[0] + (bbox[2] - S) / 2
    bbox[1] = bbox[1] + (bbox[3] - S) / 2
    bbox[3] = bbox[2] = S
    a = int(bbox[0])
    b = int(bbox[1])
    c = int(bbox[2])
    d = int(bbox[3])
    im_data = cv2.resize(cv2.cvtColor(image[b:(b + d), a: (a + c)], cv2.COLOR_BGR2GRAY), (W, H),
                          interpolation=cv2.INTER_CUBIC)
#    cv2.imshow('tst',im_data)
#    cv2.waitKey(0)
    im_data = numpy.array(im_data, dtype=numpy.single) / 255
    transformer = caffe.io.Transformer({'data': caffemodel.blobs['I'].data.shape})
    caffemodel.blobs['I'].data[...] = transformer.preprocess('data', im_data)
    feature = caffemodel.forward()
    return feature['fc5'][0]

def feature_Extract2_spider(caffemodel,bbox,image,W,H):
    S = max(bbox[2], bbox[3]) * 1.4
    bbox[0] = bbox[0] + (bbox[2] - S) / 2
    bbox[1] = bbox[1] + (bbox[3] - S) / 2
    bbox[3] = bbox[2] = S
    a = int(bbox[0])
    b = int(bbox[1])
    c = int(bbox[2])
    d = int(bbox[3])
    im_data = cv2.resize(cv2.cvtColor(image[b:(b + d), a: (a + c)], cv2.COLOR_BGR2GRAY), (W, H),
                          interpolation=cv2.INTER_CUBIC)
#    cv2.imshow('tst',im_data)
#    cv2.waitKey(0)
    im_data = numpy.array(im_data, dtype=numpy.single) / 255
    transformer = caffe.io.Transformer({'data': net.blobs['I'].data.shape})
    caffemodel.blobs['I'].data[...] = transformer.preprocess('data', im_data)
    feature = caffemodel.forward()
    return feature['fc5'][0]

def face_Extract2_spider(caffemodel,bbox1,bbox2,image1,image2):
    H=128
    W=128
    S = max(bbox1[2], bbox1[3]) * 1.3
    bbox1[0] = bbox1[0] + (bbox1[2] - S) / 2
    bbox1[1] = bbox1[1] + (bbox1[3] - S) / 2
    bbox1[3] = bbox1[2] = S
    a = int(bbox1[0])
    b = int(bbox1[1])
    c = int(bbox1[2])
    d = int(bbox1[3])
    im_data1 = cv2.resize(cv2.cvtColor(image1[b:(b + d), a: (a + c)], cv2.COLOR_BGR2GRAY), (W, H),
                          interpolation=cv2.INTER_CUBIC)
    S = max(bbox2[2], bbox2[3]) * 1.3
    bbox2[0] = bbox2[0] + (bbox2[2] - S) / 2
    bbox2[1] = bbox2[1] + (bbox2[3] - S) / 2
    bbox2[3] = bbox2[2] = S
    a = int(bbox2[0])
    b = int(bbox2[1])
    c = int(bbox2[2])
    d = int(bbox2[3])
    im_data2 = cv2.resize(cv2.cvtColor(image2[b:(b + d), a: (a + c)], cv2.COLOR_BGR2GRAY), (W, H),
                          interpolation=cv2.INTER_CUBIC)

    im_data1 = numpy.array(im_data1, dtype=numpy.single) / 255
    im_data2 = numpy.array(im_data2, dtype=numpy.single) / 255
    im_data = [im_data1,im_data2]
    transformer = caffe.io.Transformer({'data': net.blobs['I'].data.shape})
    caffemodel.blobs['I'].data[0][...] = transformer.preprocess('data', im_data1)
    caffemodel.blobs['I'].data[1][...] = transformer.preprocess('data', im_data2)
    feature = caffemodel.forward()
    feature1 = feature['fc5'][0]
    feature2 = feature['fc5'][1]
#    feature1=feature_Extract(caffemodel,bbox1,image1,W,H).copy()
#    feature2=feature_Extract(caffemodel,bbox2,image2,W,H)
#    score=numpy.dot(feature1,feature2.T)/numpy.sqrt(numpy.dot(feature1,feature1.T)*numpy.dot(feature2,feature2.T))-0.15
#    score=round(100*max(min(score*2,1),0))
    score = numpy.dot(feature1, feature2.T) / numpy.sqrt(numpy.dot(feature1, feature1.T) * numpy.dot(feature2, feature2.T)) - 0.15
    score = round(100 * max(min(score * 2, 1), 0))
    return score



def face_Extract_spider(caffemodel,bbox1,bbox2,image1,image2):
    H=128
    W=128
    feature1=feature_Extract_spider(caffemodel,bbox1,image1,W,H).copy()
    print(feature1/numpy.sqrt(numpy.dot(feature1,feature1.T)))
    feature2=feature_Extract_spider(caffemodel,bbox2,image2,W,H)
    print(feature2/numpy.sqrt(numpy.dot(feature2,feature2.T)))
    score=numpy.dot(feature1,feature2.T)/numpy.sqrt(numpy.dot(feature1,feature1.T)*numpy.dot(feature2,feature2.T))-0.15
    score=round(100*max(min(score*2,1),0))
    return score


if __name__=='__main__':
    caffe.set_mode_gpu()
    start = time.clock()
    root = "/home/luka/PycharmProjects/cvlab/"
    deploy = root + "protobuf/deploy_face_w.prototxt"
    caffe_model = root + "protobuf/w_iter_100000.caffemodel"
    net = caffe.Net(deploy,caffe_model,caffe.TEST)
    min_size = 50

    img1 = root + "img/tst.jpg"
    im1 = cv2.imread(img1, cv2.IMREAD_COLOR)
    [bbox1,Ip1]=FaceDetect_spider(im1, min_size, net)

    img2 = root + "img/left1.jpg"
    im2 = cv2.imread(img2, cv2.IMREAD_COLOR)
    [bbox2,Ip2]=FaceDetect_spider(im2, min_size, net)
    #a=int(bbox1[0])
    #b=int(bbox1[1])
    #c=int(bbox1[2]+bbox1[0])
    #d=int(bbox1[3]+bbox1[1])
    #Ip1 = numpy.array(Ip1, dtype=numpy.uint8)
    #cv2.rectangle(Ip1,(a,b),(c,d),(0,255,0),5)
    #cv2.imwrite('messigray.png',Ip1)


    deploy = root + "protobuf/deploy_p.prototxt"
    caffe_model = root + "protobuf/pm_iter_78000.caffemodel"
    net = caffe.Net(deploy,caffe_model,caffe.TEST)
    similarity=face_Extract_spider(net,bbox1,bbox2,Ip1,Ip2)
    '''
    deploy = root + "protobuf/train_test.prototxt"
    caffe_model = root + "protobuf/_iter_70000.caffemodel"
    #
    net = caffe.Net(deploy, caffe_model, caffe.TEST)
    similarity = face_Extract2(net, bbox1, bbox2, Ip1, Ip2)'''
    print(time.clock()-start)
    print(similarity)

