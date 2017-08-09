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
    if '女' in name:
        search = name.find('女')
        name = name[:search]
    name = str(name).replace('\"', '')
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

    return info

def find_imglist(url):
    html = get_Html(url)
    reg = r'src="(.+?\.[jJpP][pPnN][gG])"'
    imgre = re.compile(reg)
    html = html.decode('utf-8','ignore')  # python3
    img_list = imgre.findall(html)
    return img_list

def store_pic(img_url, info):
    path = "/home/luka/PycharmProjects/Github/Spider/Spider/From_website/"
    if not os.path.isdir(path):
        os.makedirs(path)

    name = 'p' + img_url.split('/')[-1]
    pic_path = os.path.join(path,name)+'.jpg'

    info.update(img_path=pic_path)


def get_img(start_url, url,caffemodel,infos):
    detectionModel = caffemodel[0]
    recognitionModel = caffemodel[1]
    img_list = find_imglist(url)
    flag = 0
    for img_url in img_list:
        info = {}
        info = get_info(url, info)
        if 'http' not in img_url:
            img_url = start_url + img_url
        if info['name'] != '':
            try:
                img = Image.open(io.BytesIO(urllib.request.urlopen(img_url, timeout=2).read()))
                rgb_im = img.convert('RGB')
                # rgb_im.save('colors.jpg')
                img = numpy.array(rgb_im)
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
                info = get_info(url, info)  # there is picture, thus get the infomations
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
                info.update(img_url=img_url, url=url)  # adding url
                store_pic(img_url, info)  # save the picture to local
                info['feature'] = feature
                if not os.path.exists(info['img_path']):
                    cv2.imwrite(info['img_path'], img)
                if info['name'] != '' and info['feature'] != []:
                    infos.append(info)
            except:
                continue
    return infos

def search_for_new_info(start_url,caffemodel,infos):
    start_time = time.time()
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
        infos= get_img(start_url, url, caffemodel,infos)
        linkre = re.compile('href="(.+?\.html)"')
        for x in linkre.findall(data):
            if 'http' not in x:
                x = start_url + x
            if 'eeen' not in x and 'tsinghua' in x and x not in visited and x not in queue:  # block english vision of the ee page and non-tsinghua websites
                queue.append(x)

    return infos

def SpiderRenewer1(initial_url,caffemodel):
    infos = []
    new_info = search_for_new_info(initial_url,caffemodel,infos)
    return new_info

if __name__ == '__main__':
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
    caffemodel = [detectionModel, recognitionModel]
    initial_url = 'http://www.cs.tsinghua.edu.cn'
    information = SpiderRenewer1(initial_url,caffemodel)
    print(time.time())
    print(information)

