from numpy import *
from numpy import linalg as la
import cv2
import os
import math


# 为了让LBP具有旋转不变性，将二进制串进行旋转。
# 假设一开始得到的LBP特征为10010000，那么将这个二进制特征，
# 按照顺时针方向旋转，可以转化为00001001的形式，这样得到的LBP值是最小的。
# 无论图像怎么旋转，对点提取的二进制特征的最小值是不变的，
# 用最小值作为提取的LBP特征，这样LBP就是旋转不变的了。
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

        # 加载图像


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


# 算法主过程
def LBP(FaceMat, R=2, P=8):
    Region8_x = [-1, 0, 1, 1, 1, 0, -1, -1]
    Region8_y = [-1, -1, -1, 0, 1, 1, 1, 0]
    pi = math.pi
    LBPoperator = mat(zeros(shape(FaceMat)))
    for i in range(shape(FaceMat)[1]):
        # 对每一个图像进行处理
        face = FaceMat[:, i].reshape(116, 98)
        W, H = shape(face)
        tempface = mat(zeros((W, H)))
        for x in range(R, W - R):
            for y in range(R, H - R):
                repixel = ''
                pixel = int(face[x, y])
                # 　圆形LBP算子
                for p in [2, 1, 0, 7, 6, 5, 4, 3]:
                    p = float(p)
                    xp = x + R * cos(2 * pi * (p / P))
                    yp = y - R * sin(2 * pi * (p / P))
                    if face[xp, yp] > pixel:
                        repixel += '1'
                    else:
                        repixel += '0'
                        # minBinary保持LBP算子旋转不变
                tempface[x, y] = int(minBinary(repixel), base=2)
        LBPoperator[:, i] = tempface.flatten().T
        # cv2.imwrite(str(i)+'hh.jpg',array(tempface,uint8))
    return LBPoperator

    # judgeImg:未知判断图像
    # LBPoperator:实验图像的LBP算子
    # exHistograms:实验图像的直方图分布

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



'''def judgeFace(judgeImg, LBPoperator, exHistograms):
    judgeImg = judgeImg.T
    ImgLBPope = LBP(judgeImg)
    #  把图片分为7*4份 , calHistogram返回的直方图矩阵有28个小矩阵内的直方图
    judgeHistogram = calHistogram(ImgLBPope)
    minIndex = 0
    minVals = inf

    for i in range(shape(LBPoperator)[1]):
        exHistogram = exHistograms[:, i]
        diff = (array(exHistogram - judgeHistogram) ** 2).sum()
        if diff < minVals:
            minIndex = i
            minVals = diff
    return minIndex


# 统计直方图
def calHistogram(ImgLBPope):
    Img = ImgLBPope.reshape(116, 98)
    W, H = shape(Img)
    # 把图片分为7*4份
    Histogram = mat(zeros((256, 7 * 4)))
    maskx, masky = W / 4, H / 7
    for i in range(4):
        for j in range(7):
            # 使用掩膜opencv来获得子矩阵直方图
            mask = zeros(shape(Img), uint8)
            mask[i * maskx: (i + 1) * maskx, j * masky:(j + 1) * masky] = 255
            hist = cv2.calcHist([array(Img, uint8)], [0], mask, [256], [0, 256])
            Histogram[:, (i + 1) * (j + 1) - 1] = mat(hist).flatten().T
    return Histogram.flatten().T


def runLBP():
    # 加载图像
    FaceMat = loadImageSet('D:\python/face recongnition\YALE\YALE\unpadded/').T

    LBPoperator = LBP(FaceMat)  # 获得实验图像LBP算子

    # 获得实验图像的直方图分布，这里计算是为了可以多次使用
    exHistograms = mat(zeros((256 * 4 * 7, shape(LBPoperator)[1])))
    for i in range(shape(LBPoperator)[1]):
        exHistogram = calHistogram(LBPoperator[:, i])
        exHistograms[:, i] = exHistogram

        # 　下面的代码都是根据我的这个数据库来的，就是为了验证算法准确性，如果大家改了实例，请更改下面的代码
    nameList = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15']
    characteristic = ['centerlight', 'glasses', 'happy', 'normal', 'leftlight', 'noglasses', 'rightlight', 'sad',
                      'sleepy', 'surprised', 'wink']
    for c in characteristic:
        count = 0
        for i in range(len(nameList)):
            # 这里的loadname就是我们要识别的未知人脸图，我们通过15张未知人脸找出的对应训练人脸进行对比来求出正确率
            loadname = 'D:\python/face recongnition\YALE\YALE\unpadded\subject' + nameList[i] + '.' + c + '.pgm'
            judgeImg = cv2.imread(loadname, 0)
            if judgeFace(mat(judgeImg).flatten(), LBPoperator, exHistograms) + 1 == int(nameList[i]):
                count += 1
        print
        'accuracy of %s is %f' % (c, float(count) / len(nameList))  # 求出正确率


if __name__ == '__main__':
    # 测试这个算法的运行时间
    from timeit import Timer

    t1 = Timer("runLBP()", "from __main__ import runLBP")
    print(t1.timeit(1))'''
