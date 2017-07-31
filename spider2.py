#! /usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Lin Po-Yu'

appendList = ['ee']

import re
import urllib
import urllib.request
import urllib.parse
import urllib.error
import datetime
import time
import os
import caffe
import copy
from collections import deque
from PIL import Image
import numpy
import cv2
import shutil
import io
from imgproc.face_detection_for_spider import *
import spider3

global bigFlag
bigFlag= False

def find_department(initial_url):
    #queue = deque()
    majorList = ['cs','ee']
    url_list = []
    urlop = urllib.request.urlopen(initial_url, timeout=2)
    data = urlop.read().decode('utf-8')
    linkre = re.compile('href="(.+?\.edu\.cn)')
    for major in majorList:
        for x in linkre.findall(data):
            if 'http' in x:
                if '.'+major+'.' in x or '/'+major+'.' in x:
                    url_list.append(x)
    return url_list


def currentTime():
    a = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return a

def get_Html(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    return html

def get_info(url,info):
    html = get_Html(url).decode('utf-8', 'ignore')
    html = html.replace('&nbsp;','')
    html = html.replace('&ldquo;', '"')
    html = html.replace('&rdquo;', '"')
    html = html.replace('&ndash;', '-')
    html = html.replace('&ndash;', '-')
    html = html.replace('&bull;', '')
    html = html.replace('&quot;', '')
    html = html.replace('<p><br/></p>', '')
    html = html.replace('<p></p>','')
    form_name = re.compile('con开始处-->\s?.+?\s?.+?\s?\s?<p>(.+?)<')
    name = form_name.findall(html)
    name = str(name).replace('姓名：', '')
    name = str(name).replace('，', ' ')
    form_addr = re.compile('\s?<.{1,3}>\s?([^<>;]+?清华.+?100084\)?)\s?<')
    addr = form_addr.findall(html)
    form_tel = re.compile('(电话.+?)\s?[<，]')
    tel = form_tel.findall(html)
    tel = str(tel).replace(' ', '')
    #print(tel)
    form_fax = re.compile('(传真.+?)\s?<')
    fax = form_fax.findall(html)
    fax = str(fax).replace(' ', '')
    #print(fax)
    form_email = re.compile('(电?子?邮.+?tsinghua.+?)\s?</')
    email = form_email.findall(html)
    #print(email)
    if 'href' in str(email):
        form_email2 = re.compile('"mailto:(.+?@.+?)"')
        email2 = form_email2.findall(str(email))
        email[0]= '电子邮箱：' + email2[0]          #超鏈接email....
    email = str(email).replace('AT', '@')
    email = str(email).replace('(at)', '@')
    email = str(email).replace('[at]', '@')
    email = str(email).replace(' ', '')
    #print(email)
    #form_academic1 = re.compile('学术成果.+?(\[1][^<>[]+)',re.DOTALL)
    form_academic1 = re.compile('学术成果.+?(\[?1[\.\]、][^<>[]+)', re.DOTALL)
    academic1 = form_academic1.findall(html)
    #print(academic1)
    form_academic2 = re.compile('学术成果.+?(\[?2[\.\]、][^<>[]+)', re.DOTALL)
    academic2 = form_academic2.findall(html)
    #print(academic2)
    form_academic3 = re.compile('学术成果.+?(\[?3[\.\]、][^<>[]+)', re.DOTALL)
    academic3 = form_academic3.findall(html)
    #print(academic3)
    academic = academic1+academic2+academic3
    #print(academic)

    name = str(name).replace('姓名：', '')
    name = str(name).replace(',', ' ')
    name = str(name).replace('，', ' ')
    name = str(name).replace('[', '')
    name = str(name).replace(']', '')
    name = str(name).replace('\'', '')
    if '现任' in name:
        search = name.find('现任')
        name = name[:search]
    addr = str(addr).replace('[', '')
    addr = str(addr).replace(']', '')
    addr = str(addr).replace('\'', '')
    tel = str(tel).replace(' ', '')
    tel = str(tel).replace('[', '')
    tel = str(tel).replace(']', '')
    tel = str(tel).replace('\'', '')
    fax = str(fax).replace(' ', '')
    fax = str(fax).replace('[', '')
    fax = str(fax).replace(']', '')
    fax = str(fax).replace('\'', '')
    email = str(email).replace('AT', '@')
    email = str(email).replace('(at)', '@')
    email = str(email).replace('[at]', '@')
    email = str(email).replace(' ', '')
    email = str(email).replace('[', '')
    email = str(email).replace(']', '')
    email = str(email).replace('\'', '')
    email = str(email).replace('</font>', '')
    email = str(email).replace('<fontsize="2">', '')
    if '<' in email:
        search = email.find('<')
        email = email[:search]
    info.update(name = name,address = addr,tel = tel,fax = fax,email = email,academic = academic)
    #if info['name']!='[]':
    #    print(info)
    return info

def find_imglist(url):
    html = get_Html(url)
    reg = r'src="(.+?\.[jJpP][pPnN][gG])"'
    imgre = re.compile(reg)
    html = html.decode('utf-8','ignore')  # python3
    img_list = imgre.findall(html)
    return img_list

def store_pic(img_url, info):
    # create new folder
    path = "/home/luka/PycharmProjects/Github/Spider/Spider/From_website/"
    if not os.path.isdir(path):
        os.makedirs(path)  # create the folder if it doesn't exist
        # title = time.strftime("%Y_%m_%d", time.localtime())
        # new_path = os.path.join(path, info['name'])

    name = 'p' + img_url.split('/')[-1]
    pic_path = os.path.join(path,name)+'.jpg'

    info.update(img_path=pic_path)


def get_img(start_url, url, key, info,caffemodel):
    detectionModel = caffemodel[0]
    recognitionModel = caffemodel[1]
    img_list = find_imglist(url)
    flag = 0
    for img_url in img_list:
        if 'http' not in img_url:
            img_url = start_url + img_url
        try:
            img = Image.open(io.BytesIO(urllib.request.urlopen(img_url, timeout=2).read()))
            img = numpy.array(img)
            # Convert RGB to BGR
            img = img[:, :, ::-1].copy()
            W, H, D = img.shape
            if H < 512 or W < 512:
                r = H / W
                if r <= 1:
                    H = 512
                    W = 512 / r
                    W = int(W)
                else:
                    H = 512 * r
                    H = int(H)
                    W = 512
                img = numpy.array(cv2.resize(img, (H, W)))
            else:
                if H > 2000 or W >2000:
                    r = H / W
                    if r > 1:
                        H = 2000
                        W = 2000 / r
                        W = int(W)
                    else:
                        H = 2000 * r
                        H = int(H)
                        W = 2000
                    img = numpy.array(cv2.resize(img, (H, W)))
                else:
                    img = numpy.array(img)
            image2 = numpy.array(img)
            [bboxset, extend] = FaceDetect_spider(image2, 50, detectionModel)
            if len(bboxset) == 0:
                continue
            if len(bboxset) > 1:
                continue
            #print(img_url)
            for bbox in bboxset:
                feature = feature_Extract_spider(recognitionModel, bbox, extend, 128, 128)
                feature = numpy.divide(feature, numpy.sqrt(numpy.dot(feature, feature.T)))
            #if W==key[0] and H==key[1]:
            td = numpy.array(info['feature']).T
            #time.sleep(0.1)
            #print(feature)
            #print(abs(numpy.dot(td, feature)))
            if abs(numpy.dot(td, feature) - 0.15 > 0.4):
                flag=1
                global bigFlag
                bigFlag = True
        except:
            continue

        #compare the image with our feature
        # [bbox, extend] = FaceDetect(image2, 50, self.detectionModel)
        # if len(self.bboxCam) == 0:
        #    return None
        # feature = feature_Extract(self.recognitionModel, bbox, extend, 128, 128)
        # feature = numpy.divide(feature, numpy.sqrt(numpy.dot(feature, feature.T)))
        min_size = 50
        #feature = []
        # dealing with score larger than a threshold
        info = get_info(url, info)
        #print(info)
        #print(url)
        if flag:    #match!!!
            info = get_info(url, info)  # there is picture, thus get the infomations
            info.update(img_url=img_url, url=url)  # adding url
            store_pic(url, info)  # save the picture to local
            info['feature'] = feature
            #cv2.imshow('name',img)
            #cv2.waitKey(0)
            if not os.path.exists(info['img_path']):
                cv2.imwrite(info['img_path'],img)
            # info['feature'] = feature
            #print(time.time())
    #print(info)
    return info,flag

def search_for_new_info(start_url,key,info,caffemodel):
    start_time = time.time()
    #print('start:', start_time)
    queue = deque()
    visited = set()
    queue.append(start_url)
    while queue:
        url = queue.popleft()  # 队首元素出队
        visited |= {url}  # 标记为已访问
        try:
            urlop = urllib.request.urlopen(url, timeout=2)
            data = urlop.read().decode('utf-8')

        except :
            continue
        info, flag = get_img(start_url, url, key, info, caffemodel)
        # print(info)
        if flag:
            return info


        #get new link
        linkre = re.compile('href="(.+?\.html)"')
        for x in linkre.findall(data):
            if 'http' not in x:
                x = start_url + x
            if 'eeen' not in x and 'tsinghua' in x and x not in visited and x not in queue:  # block english vision of the ee page and non-tsinghua websites
                queue.append(x)

    return info

def SpiderRenewer(info,caffemodel):
    initial_url = 'http://www.tsinghua.edu.cn/publish/newthu/newthu_cnt/faculties/index.html'
    url_list = find_department(initial_url)
    key = info['feature']
    department = 0
    global bigFlag
    bigFlag = False
    for url in url_list:
        new_info = search_for_new_info(url, key, info, caffemodel)
        if bigFlag:
            department = url
            #print('I"m here!')
            break
        #if new_info
    if department == 0 or department =='http://www.ee.tsinghua.edu.cn' :
        return [0,new_info]
    else:
        new_info = spider3.SpiderRenewer1(department,caffemodel)
        return [1,new_info]
    return new_info

def SpiderRenewer1(info,caffemodel):
    '''caffe.set_mode_gpu()
    rootFile = '/home/luka/PycharmProjects/cvlab/protobuf1/'
    detectionPrototxt = rootFile + 'deploy_face_w.prototxt'
    detectionCaffeModel = rootFile + 'w_iter_100000.caffemodel'
    detectionModel = caffe.Net(detectionPrototxt, detectionCaffeModel, caffe.TEST)

    RecognitionPrototxt = rootFile + 'recognition.prototxt'
    RecognitionCaffeModel = rootFile + '_iter_70000.caffemodel'
    recognitionModel = caffe.Net(RecognitionPrototxt, RecognitionCaffeModel, caffe.TEST)
    # caffemodel=[detectionModel,recognitionModel]
    # tst = Spider(caffemodel)
    caffemodel = [detectionModel, recognitionModel]'''

    initial_url = 'http://www.ee.tsinghua.edu.cn'  # ee main page
    key = info['feature']
    new_info = search_for_new_info(initial_url, key, info,caffemodel)
    return new_info

if __name__ == '__main__':
    '''information = {'name': "['张志军']", 'address': ['???'], 'email': "['电子邮箱：??']", 'feature':[  6.73086708e-03,  -2.94301827e-02,   1.45628629e-02,
         1.83323175e-02,   3.12993526e-02,   3.68274823e-02,
        -5.73405959e-02,  -5.09380102e-02,  -6.85696723e-03,
        -9.19026136e-03,   3.61816883e-02,   3.98671068e-03,
         1.93181429e-02,  -2.10391805e-02,   3.68980132e-02,
        -5.48064522e-03,  -1.05138496e-02,  -2.47119460e-02,
         1.73759516e-02,  -5.59557788e-02,   4.44681523e-03,
        -7.41454735e-02,  -2.63592824e-02,   6.80855736e-02,
        -8.32661390e-02,   7.39095658e-02,   1.16308155e-02,
         4.82669733e-02,   2.43654530e-02,   3.12886238e-02,
         6.24769479e-02,  -6.36307299e-02,   4.28298488e-02,
        -2.79480647e-02,  -6.89153820e-02,   3.87214050e-02,
         4.06248271e-02,   5.34901917e-02,   1.12777829e-01,
         4.76565445e-03,   1.20948674e-02,  -1.10205598e-02,
        -1.80388018e-02,   2.65284125e-02,  -3.13562602e-02,
         2.57509924e-03,   6.90454170e-02,   3.36628268e-03,
         4.61370423e-02,   2.59142332e-02,   3.29599865e-02,
        -4.05383073e-02,   1.35945082e-02,   2.32415553e-03,
        -5.09171747e-02,   1.33676315e-02,  -5.10375574e-03,
        -3.17887478e-02,  -3.08070630e-02,  -1.23769911e-02,
        -1.96930896e-02,   1.76682677e-02,   1.56885237e-02,
         4.43000682e-02,   4.84952778e-02,   1.83967985e-02,
         2.23374087e-02,   1.07381314e-01,   2.34353729e-03,
        -3.97765404e-03,  -3.58772799e-02,   4.52539092e-03,
         6.05667643e-02,   3.65946926e-02,  -4.14976142e-02,
         3.98748741e-02,  -9.65051576e-02,  -4.54890653e-02,
        -5.54353073e-02,   4.18050662e-02,   1.50044833e-03,
         2.48108059e-02,  -3.51064131e-02,   1.78025998e-02,
        -4.06294614e-02,   5.36608929e-03,  -1.24338202e-01,
         1.92881785e-02,  -6.42301217e-02,  -1.03756767e-02,
        -3.52392793e-02,  -4.83942032e-02,   3.46364602e-02,
        -2.51202751e-02,   1.67029053e-02,   1.94565356e-02,
        -4.24611010e-02,  -4.36482802e-02,   4.71577309e-02,
        -1.97684355e-02,   4.81892079e-02,   2.52425745e-02,
         1.93801913e-02,   5.00888377e-02,   4.96191867e-02,
        -1.14566796e-02,  -1.31107541e-02,  -4.36267070e-02,
        -3.62377241e-02,   8.15830231e-02,   2.26670001e-02,
        -1.27674658e-02,   7.33955726e-02,  -6.04191795e-03,
        -7.73720592e-02,  -6.21486194e-02,   3.99936028e-02,
         3.23405489e-02,  -2.81365365e-02,   1.79489180e-02,
         2.50870106e-03,  -1.15597798e-02,  -3.14883627e-02,
        -3.86883728e-02,   1.28462969e-03,  -5.50674386e-02,
         8.66154302e-03,   7.23376591e-03,   6.19910937e-03,
         2.04048939e-02,   2.46340688e-02,  -4.29610088e-02,
         6.89437687e-02,  -7.49863451e-03,   1.87198557e-02,
        -5.68335224e-03,   4.79151495e-02,   7.28356615e-02,
        -4.10671681e-02,  -3.71318720e-02,  -4.27427031e-02,
        -7.38984048e-02,   7.30128139e-02,  -3.80222052e-02,
        -2.94176247e-02,   1.71365943e-02,   1.01640485e-02,
         2.11970359e-02,  -4.76328749e-03,  -1.19259860e-02,
        -2.15869676e-02,  -5.80632761e-02,  -3.83093916e-02,
         2.00355370e-02,  -3.70897017e-02,  -3.86573859e-02,
        -1.87054779e-02,  -5.02685532e-02,   2.19346453e-02,
         2.26766206e-02,   7.04408213e-02,  -4.00829092e-02,
        -6.79347068e-02,  -1.08407266e-01,   1.11914771e-02,
         3.54182795e-02,  -4.66443552e-03,  -2.55451035e-02,
        -5.55332825e-02,  -5.74690141e-02,  -3.29162553e-03,
        -5.37678425e-04,  -4.43524569e-02,   8.60468077e-04,
         7.41606858e-03,  -4.47724350e-02,   3.59006077e-02,
         2.29794942e-02,   2.77149621e-02,   9.28640068e-02,
         3.17951888e-02,   3.78747210e-02,  -2.36180751e-03,
        -6.83198348e-02,   2.01514876e-03,   1.59106478e-02,
        -3.89336497e-02,  -8.50734860e-02,  -2.59205848e-02,
        -1.91784739e-01,  -1.47017715e-02,   3.82660404e-02,
        -1.00710839e-02,  -2.35921633e-03,  -2.27355002e-03,
         4.27107587e-02,   1.05156571e-01,  -5.15448377e-02,
         6.02331106e-03,   8.97434913e-03,   7.43116885e-02,
        -5.20565696e-02,  -1.81006524e-03,  -2.64808927e-02,
         4.02310528e-02,  -4.56563272e-02,  -3.63261765e-03,
         6.84758974e-03,   4.58915271e-02,  -3.45880073e-03,
        -1.37378173e-02,  -2.32979450e-02,   3.61537114e-02,
        -3.69074531e-02,  -2.05637179e-02,   5.73105551e-02,
        -3.20997313e-02,  -3.93821439e-03,  -4.75018546e-02,
         1.31095098e-02,  -6.90061301e-02,   2.18694955e-02,
        -1.41384508e-02,  -4.68547307e-02,   5.08792810e-02,
        -3.24053457e-03,  -1.52940778e-02,  -5.35534136e-02,
        -4.25966009e-02,   4.94808052e-03,  -1.86370704e-02,
        -7.67818242e-02,   4.51534092e-02,   7.14136288e-02,
         5.76046817e-02,  -2.83318739e-02,   6.71081468e-02,
        -8.49447846e-02,   6.07815720e-02,   5.40368184e-02,
         4.59306389e-02,  -2.02329792e-02,  -7.33955503e-02,
        -7.73938373e-02,   7.65464008e-02,   6.65198267e-02,
        -7.24360272e-02,  -2.72260774e-02,  -2.28394456e-02,
        -1.52881555e-02,   3.79300527e-02,  -2.52969190e-02,
        -4.50866893e-02,   2.59067235e-03,   1.69761628e-02,
        -7.16275647e-02,   2.85739098e-02,   5.29297367e-02,
         4.89551853e-03,  -4.40959781e-02,  -1.88653786e-02,
         5.01667857e-02,   1.17949292e-03,   4.87342365e-02,
        -3.84358577e-02,   2.72358526e-02,   4.09651510e-02,
         5.57704456e-02,  -2.82040183e-02,  -5.64720333e-02,
        -4.75442111e-02,  -6.26633391e-02,  -7.63500109e-02,
        -3.39279845e-02,  -6.98818639e-02,  -6.28806353e-02,
        -2.30420772e-02,   6.03814460e-02,   4.54551205e-02,
         2.02868190e-02,  -1.82840787e-02,  -2.59453338e-03,
        -8.70001987e-02,   5.05006220e-03,  -6.03069959e-04,
        -3.32380198e-02,   3.06874458e-02,   9.19784009e-02,
         1.18212979e-02,   7.75002129e-03,  -6.09237738e-02,
        -3.03128995e-02,  -4.90321685e-03,  -5.93016595e-02,
         3.95998545e-02,   1.54991383e-02,   9.64512210e-03,
         2.59207059e-02,  -2.25530472e-02,  -2.45276205e-02,
        -2.14263313e-02,   3.17289904e-02,  -8.65958109e-02,
         7.10390955e-02,   6.75831363e-02,  -4.06231843e-02,
         6.78821728e-02,   7.06873182e-03,   5.60809411e-02,
         1.51192723e-03,  -5.91973737e-02,   3.99504900e-02,
         1.71808545e-02,   5.20870537e-02,   5.97743951e-02,
         1.29669318e-02,   2.06763148e-02,   5.40933013e-02,
        -2.80925096e-03,  -5.45007922e-02,   1.28601879e-01,
        -6.25106767e-02,  -8.88793729e-03,   2.87321303e-02,
        -3.52688879e-02,   9.98077076e-03,   9.25896782e-03,
        -1.26403170e-02,   3.31691206e-02,   1.11367062e-01,
         5.28096966e-02,   4.13753018e-02,   6.87546656e-02,
         7.58808404e-02,   8.48198123e-03,   7.86152706e-02,
         1.24239887e-03,  -7.37212924e-03,   3.95744480e-02,
         3.28333117e-03,  -1.41533306e-02,   1.08314883e-02,
         7.01383352e-02,  -2.53236536e-02,   5.44047281e-02,
        -2.09017470e-02,  -1.07216641e-01,  -2.24451162e-02,
         3.91361816e-03,   4.91617471e-02,  -9.38450824e-03,
         7.68807307e-02,  -1.98643841e-02,   4.84972931e-02,
         6.02341816e-03,   2.46985927e-02,  -3.65012069e-03,
        -3.66932526e-02,  -2.89552696e-02,   3.91362868e-02,
         1.43644689e-02,   3.88031900e-02,  -2.25609131e-02,
         1.09167444e-02,   2.62328424e-02,  -7.63828978e-02,
         5.52295074e-02,   1.96868442e-02,  -1.05432430e-02,
         4.49799118e-05,  -2.13553719e-02,  -1.93250668e-03,
         1.49910329e-02,   1.09923678e-02,   4.45025116e-02,
        -5.92797995e-02,   4.67666751e-03,   3.61543382e-03,
         3.20543535e-02,  -3.05566173e-02,   3.40715088e-02,
         9.04456377e-02,  -4.61067678e-03,   1.47137756e-03,
         7.15495795e-02,  -1.63266659e-02,  -9.92763340e-02,
        -3.72165591e-02,  -3.78872547e-03,  -6.44522207e-03,
         6.12584427e-02,   1.39892800e-02,  -3.49581093e-02,
        -3.55244949e-02,   3.25619094e-02,  -6.60414947e-03,
         7.19019994e-02,  -2.96380371e-02,  -7.64355436e-03,
        -1.71777233e-02,  -2.05337852e-02,  -7.66668096e-02,
         6.46559671e-02,   1.13752969e-02,  -1.19766062e-02,
         1.31874047e-02,   2.64917873e-02,   1.85914040e-02,
        -7.00949167e-04,   4.76376899e-02,   1.94561891e-02,
         3.11776102e-02,   1.32506993e-02,   1.24940062e-02,
        -3.13807353e-02,   4.76723828e-04,  -7.54705770e-03,
        -8.40000249e-03,   4.89070313e-03,  -4.80160341e-02,
         4.21047769e-02,   5.11926413e-02,   1.54927922e-02,
         5.12672737e-02,   5.34350658e-03,   2.60794396e-03,
         5.61702205e-03,   3.99596207e-02,   5.23508936e-02,
        -5.22502325e-02,   5.03775179e-02,  -1.83829328e-03,
         5.65930679e-02,  -5.91964982e-02,   1.69529300e-02,
         2.12711357e-02,   2.62868553e-02,  -5.74460812e-02,
         4.75092717e-02,   3.91144082e-02,  -3.99841517e-02,
         4.10010526e-03,  -3.40937860e-02,   5.64233139e-02,
        -2.75911894e-02,  -9.44606960e-02,  -4.10288498e-02,
        -2.93575693e-02,  -1.99856237e-02,   7.39237294e-02,
        -5.87126352e-02,   4.88568060e-02,   8.12605023e-02,
        -8.92232805e-02,  -3.52021903e-02,  -4.78064120e-02,
        -5.95240518e-02,   8.00767764e-02,  -4.60182615e-02,
        -5.46263717e-03,  -6.12969045e-03,  -4.62199040e-02,
        -2.12397296e-02,   6.53318539e-02,   4.75921594e-02,
         4.89275716e-02,   3.78907546e-02,  -2.28312127e-02,
        -7.77202770e-02,  -7.22896867e-03,   1.89303905e-02,
        -6.76713437e-02,   4.22497001e-03,  -4.37928177e-02,
        -3.11760493e-02,   1.87209267e-02,  -1.54944323e-02,
         4.66332724e-03,   4.68296148e-02,  -6.22479990e-02,
        -3.02057359e-02,   4.52510081e-02,  -2.31964011e-02,
        -1.58325024e-02,   3.47425267e-02,   3.16667594e-02,
        -7.82963336e-02,  -9.66563914e-03,   1.16355363e-02,
        -7.26174936e-02,  -4.42587957e-02,  -6.44550398e-02,
         1.73911080e-02,   3.00390199e-02,   7.79711828e-02,
        -2.33790111e-02,   1.36430021e-02,  -8.42198431e-02,
         3.73488367e-02,  -3.02923080e-02,   4.16007601e-02,
         4.30523045e-02,  -3.54150757e-02,   1.84170040e-03,
         2.37869993e-02,  -3.47432904e-02,  -3.63558754e-02,
         4.52818256e-03,  -7.45410696e-02,  -2.78840936e-03,
        -9.60513651e-02,   6.60470724e-02]}'''
    stddd = '艾海舟'
    information = {'feature':[ -7.24562351e-03,  5.77171855e-02,  -4.59639579e-02,  -1.10542439e-02,
   2.92042103e-02,   9.82348900e-03,  -7.37018371e-03,   9.91441607e-02,
  -4.58546765e-02,  -2.84999739e-02,  -1.09796338e-02,  -1.13867242e-02,
   3.15831900e-02,  -3.50909084e-02,  -2.31404547e-02,  -2.06068363e-02,
  -4.33162749e-02,   2.25265082e-02,   3.67385782e-02,  -2.42700707e-02,
  -4.76904213e-03,  -8.28890130e-03,   4.28150482e-02,   2.87340712e-02,
   4.23089508e-03,   2.98066977e-02,   8.65421072e-02,   2.16763504e-02,
  -4.23288494e-02,   3.89166288e-02,  -2.73158662e-02,  -2.04755017e-03,
   1.34798409e-02,  -2.09136121e-03,  -6.93607554e-02,  -4.61875238e-02,
  -1.72673520e-02,   2.54679983e-03,  -9.85342730e-03,   1.85539834e-02,
   2.16196086e-02,  -1.85315334e-03,   2.90456284e-02,   2.60677952e-02,
   2.37744246e-02,   4.28169295e-02,  -8.54186155e-03,  -2.06319373e-02,
   6.40659779e-02,   1.90178007e-02,   7.67481551e-02,   4.33125459e-02,
  -3.73095982e-02,   1.26404008e-02,  -6.83536530e-02,  -1.78197827e-02,
   3.14029194e-02,   6.46244287e-02,  -4.81765792e-02,   5.54400980e-02,
   1.65402726e-03,  -5.08435890e-02,  -5.03422096e-02,  -6.56283274e-02,
   4.77053933e-02,   4.68155146e-02,   7.08388388e-02,  -7.42185442e-03,
  -4.48349454e-02,  -4.03353944e-02,   3.13594867e-03,  -2.83565409e-02,
   8.12967271e-02,  -6.95854565e-03,   5.46846315e-02,   4.38718423e-02,
  -9.38010067e-02,  -4.71828580e-02,   2.36835401e-03,  -1.81714986e-02,
   4.18336503e-02,  -9.22641009e-02,   1.24886660e-02,   4.30109017e-02,
   5.27758002e-02,   8.49212334e-03,  -5.63660450e-02,  -1.26437163e-02,
  -2.57059112e-02,   7.23220408e-02,  -6.10881560e-02,  -1.98265985e-02,
   2.51987986e-02,   4.26376872e-02,  -2.71618012e-02,  -5.72843514e-02,
   3.67491767e-02,   5.89686707e-02,  -3.55249643e-02,  -3.12983282e-02,
   2.81921811e-02,   1.98211875e-02,  -1.18519086e-02,   2.89840028e-02,
   2.28534397e-02,   1.36012109e-02,   5.88442897e-03,  -3.39156166e-02,
   1.53122761e-03,  -5.20219374e-03,   9.41726416e-02,  -3.42329475e-03,
  -6.66771038e-03,  -5.17330244e-02,   4.71847579e-02,  -2.67326962e-02,
  -5.30079119e-02,   1.99690852e-02,   4.42076251e-02,  -4.41307425e-02,
   2.69936454e-02,  -3.37334014e-02,   7.13623166e-02,   3.01722437e-02,
  -3.02137714e-02,  -2.52477396e-02,  -1.58870574e-02,  -3.20223756e-02,
  -5.65900607e-03,  -4.37582321e-02,  -2.89793145e-02,   8.42674542e-03,
   1.00864664e-01,   1.50472973e-03,   2.58731954e-02,   3.24917957e-02,
   1.78769995e-02,   2.55601499e-02,  -1.05469055e-01,  -1.80251617e-02,
   1.25506073e-01,  -8.00145864e-02,   1.15235947e-01,  -1.02439962e-01,
  -7.13123456e-02,  -9.25394613e-03,  -3.22130062e-02,   3.13612148e-02,
  -2.70720590e-02,   1.76457297e-02,   1.28834434e-02,   2.79533584e-02,
  -1.33056436e-02,   6.00398630e-02,  -2.33990140e-02,  -2.62294523e-02,
   5.19629195e-03,   2.90181255e-03,   6.81194440e-02,   2.60652788e-02,
  -3.34962010e-02,  -4.36396599e-02,   3.27722356e-02,  -1.05254479e-01,
   4.27921638e-02,   4.04570960e-02,   7.02881664e-02,   1.38375163e-02,
  -4.80065271e-02,  -4.53121886e-02,  -1.45248510e-02,   2.72935890e-02,
   3.64441201e-02,   6.90545794e-03,  -4.23105992e-02,   2.65714191e-02,
  -2.57028872e-03,   2.14466564e-02,   4.01529297e-02,  -1.84896570e-02,
   2.38155071e-02,   7.11473450e-02,  -1.71085149e-02,  -1.87586062e-02,
  -3.57434005e-02,  -8.08097236e-03,   1.34299863e-02,   1.08240908e-02,
  -5.40980771e-02,  -5.73113002e-02,   2.16050204e-02,   4.34942637e-03,
  -4.10879143e-02,  -1.29853535e-04,  -6.27667457e-03,   1.27064518e-03,
   1.89478565e-02,   1.54811190e-04,  -2.43938621e-02,  -1.15822563e-02,
   8.11440051e-02,  -5.72287366e-02,  -3.05050947e-02,  -1.10278567e-02,
  -1.97671428e-02,   6.03749370e-03,  -6.92016482e-02,   2.30859760e-02,
   2.74797548e-02,   3.89262997e-02,  -8.29105172e-03,   3.76933604e-03,
   1.89423002e-02,   6.62064627e-02,   2.54820045e-02,   7.62557685e-02,
  -3.86140822e-03,  -6.33383840e-02,   4.28173691e-02,   7.68513009e-02,
   4.50024121e-02,  -5.84495738e-02,  -5.94895110e-02,  -6.67080954e-02,
  -2.24230252e-02,   3.76373082e-02,   2.14567059e-03,  -4.09397073e-02,
   1.10886609e-02,   4.90039103e-02,  -4.67381105e-02,   1.89696532e-02,
  -7.24845082e-02,   6.97108656e-02,   2.85795005e-03,   1.86273381e-02,
   3.77215669e-02,   7.99288321e-03,   6.05955534e-02,  -4.01975997e-02,
   8.38272795e-02,   8.87224264e-03,  -1.10079255e-02,  -2.17470285e-02,
   7.95692652e-02,  -1.36228313e-03,  -9.51254088e-03,   2.19553001e-02,
   3.86103950e-02,   5.24595454e-02,  -3.96651998e-02,   4.35903249e-03,
  -2.15812232e-02,   5.94431944e-02,  -1.48333889e-02,   1.11389915e-02,
  -5.82103543e-02,  -9.04786661e-02,   1.68138500e-02,   2.71088481e-02,
  -1.20533649e-02,  -7.25070015e-03,  -1.73466895e-02,  -3.26695144e-02,
  -4.60552201e-02,  -2.74177711e-03,   5.01594804e-02,  -2.20068786e-02,
   2.52103191e-02,  -1.58761162e-02,   4.48159873e-02,  -5.76260649e-02,
  -5.13429418e-02,   6.39179125e-02,  -1.17642740e-02,  -2.59822495e-02,
  -5.80202006e-02,   1.72927312e-03,   1.23686977e-02,   2.34164279e-02,
   4.03564088e-02,   1.58684570e-02,  -9.77782384e-02,   4.58914740e-03,
   4.60502505e-03,   4.55641560e-02,  -4.67570452e-03,   8.44359174e-02,
   7.62108061e-03,   4.44376729e-02,   6.10588826e-02,   1.30626902e-01,
  -2.76238075e-03,   1.11875460e-02,   1.88571587e-02,   1.41989086e-02,
  -6.30857870e-02,  -1.91119332e-02,   2.23402306e-02,   1.25944596e-02,
   2.87777395e-03,   3.08190566e-02,   6.12749951e-03,   2.34974269e-02,
   3.76726277e-02,  -6.12911060e-02,   3.08664120e-03,  -1.31398076e-02,
   2.00771820e-03,  -3.23534906e-02,  -9.67034847e-02,  -1.55621367e-02,
  -3.85132246e-03,   7.70792961e-02,  -2.63168453e-03,  -7.27875084e-02,
   5.93893602e-02,   1.28602302e-02,  -6.64980710e-02,  -2.66986322e-02,
   1.00033030e-01,  -3.77021934e-04,   5.08182198e-02,   6.62093982e-02,
   9.35561303e-03,  -1.09069580e-02,  -2.10199468e-02,  -4.92259637e-02,
   2.63690203e-02,   1.72453676e-03,   6.64631976e-03,  -7.14918897e-02,
   6.37180954e-02,  -2.05059099e-04,   3.49699259e-02,   2.43856031e-02,
  -4.60711829e-02,  -5.34364209e-02,   3.34583819e-02,  -1.14136219e-01,
  -1.01457760e-01,   4.27839905e-02,  -3.17293480e-02,   8.38863328e-02,
   6.47396548e-03,  -5.24462685e-02,  -3.42009626e-02,  -2.81112525e-03,
   5.78162931e-02,   4.10074294e-02,  -9.00703222e-02,  -2.00719032e-02,
   4.48312052e-03,   7.59649426e-02,   4.54616509e-02,   8.41988027e-02,
  -8.61305892e-02,  -1.60891097e-02,  -2.13840157e-02,  -3.81074771e-02,
  -1.38797639e-02,   2.32421104e-02,   5.70338331e-02,  -1.61301869e-03,
   4.19018269e-02,  -1.32024614e-02,   4.99757892e-03,   3.81091721e-02,
  -9.14864358e-04,  -1.14548104e-02,   1.48970187e-02,  -1.52850281e-02,
   1.36164548e-02,   7.83587166e-04,   4.24464345e-02,  -8.44755967e-04,
   3.45203467e-02,   1.89468521e-03,  -6.73624512e-04,  -2.93546114e-02,
   7.60294730e-03,   5.10325134e-02,  -7.61421770e-02,   5.57180084e-02,
  -1.23076634e-02,   4.89975624e-02,  -7.56138861e-02,  -5.37946783e-02,
  -6.08445629e-02,   3.29265222e-02,  -1.84854623e-02,  -5.20182960e-03,
  -9.10847727e-03,   5.04562669e-02,   1.92529429e-02,  -8.62206146e-02,
   9.09656286e-02,   2.26695035e-02,   1.45608718e-02,  -2.38089962e-03,
  -5.38578108e-02,  -3.76248136e-02,  -1.13341575e-02,  -4.13187183e-02,
   3.43256742e-02,   7.28909904e-03,  -4.49220017e-02,   4.39987471e-03,
   4.64106724e-02,   5.87124377e-02,  -5.12681110e-03,  -6.23301975e-02,
   6.84169605e-02,   2.06161514e-02,  -6.46235272e-02,  -2.46882662e-02,
   2.78752781e-02,   4.74097282e-02,   3.40779461e-02,  -7.70491138e-02,
   8.37259144e-02,  -2.65600216e-02,   2.12744242e-04,   5.07443920e-02,
   1.39892846e-02,   9.16786119e-03,  -2.92934757e-02,   7.91713893e-02,
  -1.92833189e-02,  -8.78019705e-02,   1.09481765e-03,   9.90787987e-03,
  -2.92319972e-02,  -5.09530306e-02,  -1.10497661e-01,  -5.27368067e-03,
   8.80108215e-03,   4.06660978e-03,  -2.92252358e-02,   6.08752742e-02,
   1.08115617e-02,  -1.92556642e-02,  -1.71328988e-02,   7.76289105e-02,
   6.84615644e-03,  -3.13465931e-02,  -9.47581157e-02,   3.06346659e-02,
   6.24517798e-02,  -5.90635836e-02,  -1.91141572e-02,  -5.71881309e-02,
   1.21609360e-01,   1.58086710e-03,  -3.37868114e-03,   1.57625079e-02,
  -3.74561585e-02,   1.20395124e-01,   1.74007565e-02,   1.33582903e-02,
   3.95838395e-02,  -3.81045379e-02,   1.34536987e-02,   5.59822507e-02,
  -1.81841217e-02,  -5.54770641e-02,   7.73482174e-02,   7.31118908e-03,
  -2.77341530e-02,   7.39228725e-02,  -5.19664139e-02,  -1.15202076e-03,
   6.21511936e-02,  -1.22609519e-04,  -5.98978996e-03,   1.65425222e-02,
   2.39238725e-04,  -5.23382872e-02,  -1.67948604e-02,   2.99114664e-03,
   2.60601919e-02,   9.15409531e-03,   1.40326209e-02,  -3.11894319e-03,
   6.69917986e-02,   5.03701903e-02,   1.24080935e-02,  -1.00738697e-01,
   7.86735043e-02,  -3.21581624e-02,  -2.48401053e-02,  -5.29039018e-02,
   1.94670558e-02,  -2.40934938e-02,   5.50688691e-02,   2.09302977e-02,
  -5.33825196e-02,   6.76446455e-03,   1.96857117e-02,  -9.90674831e-03,
   3.70582612e-03,   1.04618400e-01,   8.79158918e-03,  -1.23098660e-02,
  -4.07210849e-02,  -4.82213609e-02,   7.34242052e-03,   2.92535778e-03,
  -4.08628732e-02,   8.45976993e-02,   3.12922299e-02,   5.63512743e-02]}

    caffe.set_mode_gpu()
    rootFile = '/home/luka/PycharmProjects/cvlab/protobuf1/'
    detectionPrototxt = rootFile + 'deploy_face_w.prototxt'
    detectionCaffeModel = rootFile + 'w_iter_100000.caffemodel'
    detectionModel = caffe.Net(detectionPrototxt, detectionCaffeModel, caffe.TEST)

    RecognitionPrototxt = rootFile + 'recognition.prototxt'
    RecognitionCaffeModel = rootFile + '_iter_70000.caffemodel'
    recognitionModel = caffe.Net(RecognitionPrototxt, RecognitionCaffeModel, caffe.TEST)
    # caffemodel=[detectionModel,recognitionModel]
    # tst = Spider(caffemodel)
    caffemodel = [detectionModel, recognitionModel]
    information = SpiderRenewer(information,caffemodel)
    print(time.time())
    print(information)

