from numpy import *
from numpy import linalg as la
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
    FaceMat = mat(zeros((15, 98 * 116)))
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
    for i in range(shape(FaceMat)[1]):
        face = FaceMat[:, i].reshape(116, 98)
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

if __name__=='__main__':
    pass