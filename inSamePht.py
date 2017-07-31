#! /usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Lin Po-Yu'

import caffe
from imgproc.face_detection_for_spider import *
import re
import urllib
import urllib.request
import urllib.parse
import urllib.error
import datetime
import time
import os
import copy
from collections import deque
from PIL import Image
import numpy
import cv2
import shutil
import io


def currentTime():
    a = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return a

def get_Html(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    return html

def get_info(url, info):
    html = get_Html(url).decode('utf-8', 'ignore')
    # print(html)
    html = html.replace('&nbsp;', '')
    html = html.replace('&ldquo;', '"')
    html = html.replace('&rdquo;', '"')
    html = html.replace('&ndash;', '-')
    html = html.replace('&ndash;', '-')
    html = html.replace('&bull;', '')
    html = html.replace('&quot;', '')
    html = html.replace('<p><br/></p>', '')
    html = html.replace('<p></p>', '')
    # print(html)
    form_name = re.compile('con开始处-->\s?.+?\s?.+?\s?\s?<p>(.+?)<')
    name = form_name.findall(html)
    name = str(name).replace('姓名：', '')
    name = str(name).replace(',', ' ')
    name = str(name).replace('，', ' ')
    # print(name)
    form_addr = re.compile('\s?<.{1,3}>\s?([^<>;]+?清华.+?100084\)?)\s?<')
    addr = form_addr.findall(html)
    # print(addr)
    # form_tel = re.compile('[1084]?\s?</p>\s?<p>\s?(电话.+?)\s?<')
    form_tel = re.compile('(电话[^/<>。]+?[0-9].+?)\s?[<，]')
    tel = form_tel.findall(html)
    tel = str(tel).replace(' ', '')
    # print(tel)
    form_fax = re.compile('(传真[^至]+?)\s?<')
    fax = form_fax.findall(html)
    fax = str(fax).replace(' ', '')
    # print(fax)
    form_email = re.compile('(电?子?邮[^<>]+?tsinghua.+?)\s?</')
    email = form_email.findall(html)
    # print(email)
    if 'href' in str(email):
        form_email2 = re.compile('"mailto:(.+?@.+?)"')
        email2 = form_email2.findall(str(email))
        email[0] = '电子邮箱：' + email2[0]  # 超鏈接email....
    email = str(email).replace('AT', '@')
    email = str(email).replace('(at)', '@')
    email = str(email).replace('[at]', '@')
    email = str(email).replace(' ', '')
    # print(email)
    form_page = re.compile('主页.+?\s?.+?\s?.+?href="(.+?)"')
    page = form_page.findall(html)
    # print(page)
    # form_academic1 = re.compile('学术成果.+?(\[1][^<>[]+)',re.DOTALL)
    form_academic1 = re.compile('学术成果.+?(\[?1[\.\]、][^<>[]+)', re.DOTALL)
    academic1 = form_academic1.findall(html)
    # print(academic1)
    form_academic2 = re.compile('学术成果.+?(\[?2[\.\]、][^<>[]+)', re.DOTALL)
    academic2 = form_academic2.findall(html)
    # print(academic2)
    form_academic3 = re.compile('学术成果.+?(\[?3[\.\]、][^<>[]+)', re.DOTALL)
    academic3 = form_academic3.findall(html)
    # print(academic3)
    academic = academic1 + academic2 + academic3
    # print(academic)
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
    info.update(name=name, address=addr, tel=tel, fax=fax, email=email, page=page, academic=academic)

    # if info['name']!='[]':
    #    print(info)
    return info

def find_imglist(url):
    html = get_Html(url)
    reg = r'src="(.+?\.[jJpP][pPnN][gG])"'
    imgre = re.compile(reg)
    html = html.decode('utf-8', 'ignore')  # python3
    img_list = imgre.findall(html)
    return img_list

def store_pic(img_url, infos):
    # create new folder
    new_path = "/home/luka/PycharmProjects/Github/Spider/Spider/From_website/"
    if not os.path.isdir(new_path):
        os.makedirs(new_path)
    name = 'p' + img_url.split('/')[-1]
    pic_path = os.path.join(new_path, name) + '.jpg'
    #urllib.request.urlretrieve(img_url, pic_path) #store in the new folder
    infos.update(img_path=pic_path)

def get_Img(start_url, url,caffemodel):
    detectionModel = caffemodel[0]
    recognitionModel = caffemodel[1]
    img_list = find_imglist(url)
    info = {'valid':False}

    for img_url in img_list:
        info = {}
        # time.sleep(1)
        if 'http' not in img_url:
            img_url = start_url + img_url
        # print('saved  ' + str(sum) + ' pictures   capturing <---  ' + img_url)

        #info = get_info(url, info)
        #info.update(img_url=img_url, url=url)
        #if info['name'] != '[]':
        #    store_pic(img_url, info)            #save the picture to local

        try:
            img = Image.open(io.BytesIO(urllib.request.urlopen(img_url, timeout=2).read()))
        except:
            continue
        imag = numpy.array(img)
        if len(imag[0])<2:
            aaa=1
            aaa=2

        infos = {}
        store_pic(url,infos)
        #print(url)
        try:
            imag = imag[:, :, ::-1].copy()
        except:
            continue
        W, H, D = imag.shape
        if D>3:
            continue
            #imag = Image.new("RGB", img.size, (255, 255, 255))
            #imag = numpy.array(imag)
            #imag = cv2.cvtColor(imag,cv2.COLOR_RGB2BGR)
            # Convert RGB to BGR
        img = imag
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
            if H > 2000 or W > 2000:
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
        if len(bboxset) <2:
            continue
        featurebox = []
        for bbox in bboxset:
            feature = feature_Extract_spider(recognitionModel, bbox, extend, 128, 128)
            featurebox.append(numpy.divide(feature, numpy.sqrt(numpy.dot(feature, feature.T))))
        #for items in featurebox:
        info['valid']=True
        info['data'] = [featurebox]
        if not os.path.exists(infos['img_path']):
            cv2.imwrite(infos['img_path'], img)
        # [bbox, extend] = FaceDetect(image2, 50, self.detectionModel)
        # if len(self.bboxCam) == 0:
        #    return None
        # feature = feature_Extract(self.recognitionModel, bbox, extend, 128, 128)
        # feature = numpy.divide(feature, numpy.sqrt(numpy.dot(feature, feature.T)))
        # info['feature'] = feature
        # print(info)
        # infos.append(info)
        yield info  # except for 姚铮 having no personal picture, choose the first picture in the other pages on which plural pictures are
        # return info


def spiderFull(caffemodel):
    '''
    Fetch the information of the  photo that may have relationship with the image input
     need to use the face detection system
    :param img: input image of a specific person
    :return:(dict){'personal information':,'similar images':}
    '''
    # codes here
    initial_url = 'http://www.ee.tsinghua.edu.cn'  # ee page

    queue = deque()
    visited = set()
    queue.append(initial_url)
    # new_infos = infos
    while queue:
        url = queue.popleft()  # 队首元素出队
        visited |= {url}  # 标记为已访问
        # print('have been ' + str(cnt) + ' pages    traversing <---  ' + url)
        try:
            urlop = urllib.request.urlopen(url, timeout=2)
            data = urlop.read().decode('utf-8')
            # html = get_Html(url).decode('utf-8', 'ignore')
        except:
            continue

        linkre = re.compile('href="(.+?\.html)"')
        for x in linkre.findall(data):
            if 'http' not in x:
                x = initial_url + x
            if 'eeen' not in x and 'tsinghua' in x and x not in visited and x not in queue:  # block english vision of the ee page and non-tsinghua websites
                queue.append(x)
                # print('sum=' + str(len(queue) + len(visited)) + ', ' + str(len(queue)) + 'to go    add to queue --->  ' + x)

        # new_info = get_Img(initial_url, url)
        for j in get_Img(initial_url, url,caffemodel):
            yield j
            # yield new_info

if __name__ == '__main__':
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
    print('start:', time.time())
    #for i in spiderFull(caffemodel):
    #    print(i)
    print('finish:', time.time())