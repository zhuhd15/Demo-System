from numpy import *
import numpy,time
from .featureCal import *
from .face_detection_For_liveness import FaceDetect
import cv2
import os
import math

def minBinary(pixel):
    length = len(pixel)
    zero = ''
    for i in range(length)[::-1]:
        if pixel[i] == '0':
            pixel = pixel[:i]
            zero += '0'
        else:
            return zero + pixel
    if len(pixel) == 0:
        return '0'


def loadImageSet(add):
    FaceMat = mat(zeros((15, 130 * 146)))
    j = 0
    for i in os.listdir(add):
        if i.split('.')[1] == 'noglasses':
            try:
                img = cv2.imread(add + i, 0)
                # cv2.imwrite(str(i)+'.jpg',img)
            except:
                print
                'load %s failed' % i
            FaceMat[j, :] = mat(img).flatten()
            j += 1
    return FaceMat


def LBP(FaceMat, R=2, P=8):
    Region8_x = [-1, 0, 1, 1, 1, 0, -1, -1]
    Region8_y = [-1, -1, -1, 0, 1, 1, 1, 0]
    pi = math.pi
    LBPoperator = mat(zeros(shape(FaceMat)))
    #for i in range(shape(FaceMat)[1]):
    #face = FaceMat[:, i].reshape(144, 120)
    i = 0;
    face = FaceMat;
    W, H = shape(face)
    tempface = mat(zeros((W, H)))
    for x in range(R, W - R):
        for y in range(R, H - R):
            repixel = ''
            pixel = int(face[x, y])
            for p in [2, 1, 0, 7, 6, 5, 4, 3]:
                p = float(p)
                xp = x + R * cos(2 * pi * (p / P))
                yp = y - R * sin(2 * pi * (p / P))
                if face[xp, yp] > pixel:
                    repixel += '1'
                else:
                    repixel += '0'
            tempface[x, y] = int(minBinary(repixel), base=2)
    LBPoperator[:, i] = tempface.flatten().T
        # cv2.imwrite(str(i)+'hh.jpg',array(tempface,uint8))
    return LBPoperator


def faceLBP(face_mat,R=2,PP=8):
    '''
    R is the radius，PP is the number of points
    '''
    height,width=face_mat.shape
    pi=math.pi
    face_LBP=np.zeros([height,width],dtype=np.uint8)
    for x in range(height):
        for y in range(width):
            center=face_mat[x,y]
            er=list()
            for p in range(1,PP+1):
                p=float(p)
                xp= x+R*math.cos(2*pi*(p/PP))
                yp= y-R*R*math.sin(2*pi*(p/PP))
                xp_low=min(max(math.floor(xp),0),height-1)
                xp_upper=min(max(math.ceil(xp),0),height-1)
                yp_low=min(max(math.floor(yp),0),width-1)
                yp_upper=min(max(math.ceil(yp),0),width-1)
                dx=xp-xp_low
                dy=yp-yp_low
                f00=face_mat[xp_low,yp_low]
                f01=face_mat[xp_low,yp_upper]
                f11=face_mat[xp_upper,yp_upper]
                f10=face_mat[xp_upper,yp_low]
                pixel=f00*(1-dx)*(1-dy)+f01*(1-dx)*dy+f11*dx*dy+f10*dx*(1-dy)
                if pixel>=center:
                    er+=['1']
                else:
                    er+=['0']
                face_LBP[x,y]=min_value_of_binary2dec(er)
    return face_LBP

def min_value_of_binary2dec(binary):
    min_value = int(''.join(binary[0:7]),2)
    for i in range(1,7):
        tempValue = int(''.join(binary[i*8:i*8+7]),2)
        min_value = min(min_value, tempValue)
    return min_value
    pass


def colorMoment(img):
    img = cv2.cvtColor(img,cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(img)
    color_feature = []
    h_mean = mean(h)  # np.sum(h)/float(N)
    s_mean = mean(s)  # np.sum(s)/float(N)
    v_mean = mean(v)  # np.sum(v)/float(N)
    color_feature.extend([h_mean, s_mean, v_mean])
    # The second central moment - standard deviation
    h_std = std(h)  # np.sqrt(np.mean(abs(h - h.mean())**2))
    s_std = std(s)  # np.sqrt(np.mean(abs(s - s.mean())**2))
    v_std = std(v)  # np.sqrt(np.mean(abs(v - v.mean())**2))
    color_feature.extend([h_std, s_std, v_std])
    # The third central moment - the third root of the skewness
    h_skewness = mean(abs(h - h.mean()) ** 3)
    s_skewness = mean(abs(s - s.mean()) ** 3)
    v_skewness = mean(abs(v - v.mean()) ** 3)
    h_thirdMoment = h_skewness ** (1. / 3)
    s_thirdMoment = s_skewness ** (1. / 3)
    v_thirdMoment = v_skewness ** (1. / 3)
    color_feature.extend([h_thirdMoment, s_thirdMoment, v_thirdMoment])

    return color_feature

def featureGenerate(caffemodel,picture):

    picture = cv2.cvtColor(picture,cv2.COLOR_BGR2RGB)
    min_size = 50
    [bbox, Ip] = FaceDetect(picture, min_size, caffemodel)
    if bbox == [] :
        return None
    if bbox[2] < 100 or bbox[3] < 100:
        return []
    #S = max(bbox[2], bbox[3])
    start = time.clock()
    S = max(bbox[2], bbox[3]) * 1.3

    bbox[0] = bbox[0] + (bbox[2] - S) / 2
    bbox[1] = bbox[1] + (bbox[3] - S) / 2
    bbox[3] = bbox[2] = S
    a = int(bbox[0])
    b = int(bbox[1])
    c = int(bbox[2])
    d = int(bbox[3])
    originFace = Ip[b:(b + d), a: (a + c)]
    print(originFace.shape)
    if originFace.shape[0]<10 or originFace.shape[1]<10:
        return []
    faceImg = cv2.resize(originFace,(146,130),interpolation=cv2.INTER_CUBIC)[:,:,0]
    sp = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
    LBP_pic =LBP_Picture(faceImg,sp, 0, 1)
    mapEd = getmapping(8, 1)
    #facePattern = LBP(faceImg)
    lbp = numpy.zeros(3304)
    lbpIndex = 0
    print(time.clock() - start)
    for x in range(0,113,16):
        for y in range(0,97,16):
            pix = LBP_pic[y:min(y+32,128),x:min(x+32,144)]
            lbpValue = LBP_Column(pix,1,8,mapEd,0)
            #lbpIndex+=59
            for z in range(lbpIndex,lbpIndex+59):
                lbp[z]=lbpValue[z%59]
            lbpIndex+=59
    colour_moment = colorMoment(originFace)
    return [lbp,colour_moment]
    pass

def featureGen(originFace):
    '''picture = cv2.cvtColor(picture,cv2.COLOR_BGR2RGB)
    min_size = 50
    [bbox, Ip] = FaceDetect(picture, min_size, caffemodel)
    if bbox == []:
        return None
    S = max(bbox[2], bbox[3])
#    S = max(bbox[2], bbox[3]) * 1.3

    bbox[0] = bbox[0] + (bbox[2] - S) / 2
    bbox[1] = bbox[1] + (bbox[3] - S) / 2
    bbox[3] = bbox[2] = S
    a = int(bbox[0])
    b = int(bbox[1])
    c = int(bbox[2])
    d = int(bbox[3])
    if bbox[2] < 100 or bbox[3] < 100:
        return []
    originFace = Ip[b:(b + d), a: (a + c)]'''
    faceImg = cv2.resize(originFace, (146, 130), interpolation=cv2.INTER_CUBIC)[:, :, 0]
    sp = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
    LBP_pic = LBP_Picture(faceImg, sp, 0, 1)
    mapEd = getmapping(8, 1)
    # facePattern = LBP(faceImg)
    lbp = numpy.zeros(3304)
    lbpIndex = 0
    for x in range(0, 113, 16):
        for y in range(0, 97, 16):
            pix = LBP_pic[y:min(y + 32, 128), x:min(x + 32, 144)]
            lbpValue = LBP_Column(pix, 1, 8, mapEd, 0)
            # lbpIndex+=59
            for z in range(lbpIndex, lbpIndex + 59):
                lbp[z] = lbpValue[z % 59]
            lbpIndex += 59
    colour_moment = colorMoment(originFace)
    return [lbp, colour_moment]
    pass

if __name__=='__main__':
    pass