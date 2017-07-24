#! /usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Lin Po-Yu'

import re,caffe
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
import io,multiprocessing
from imgproc.face_detection_for_spider import *


def currentTime():
    a = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return a


def get_Html(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    return html


def get_info(url, info):
    html = get_Html(url).decode('utf-8', 'ignore')
    #print(html)
    html = html.replace('&nbsp;', '')
    html = html.replace('&ldquo;', '"')
    html = html.replace('&rdquo;', '"')
    html = html.replace('&ndash;', '-')
    html = html.replace('&ndash;', '-')
    html = html.replace('&bull;', '')
    html = html.replace('&quot;', '')
    html = html.replace('<p><br/></p>', '')
    html = html.replace('<p></p>', '')
    #print(html)
    form_name = re.compile('con开始处-->\s?.+?\s?.+?\s?\s?<p>(.+?)<')
    name = form_name.findall(html)
    name = str(name).replace('姓名：', '')
    name = str(name).replace(',', ' ')
    name = str(name).replace('，', ' ')
    name = str(name).replace('[', '')
    name = str(name).replace(']', '')
    name = str(name).replace('\'', '')
    #print(name)
    form_addr = re.compile('\s?<.{1,3}>\s?([^<>;]+?清华.+?100084\)?)\s?<')
    addr = form_addr.findall(html)
    addr = str(addr).replace('[', '')
    addr = str(addr).replace(']', '')
    addr = str(addr).replace('\'', '')
    # print(addr)
    # form_tel = re.compile('[1084]?\s?</p>\s?<p>\s?(电话.+?)\s?<')
    form_tel = re.compile('(电话[^/<>。]+?[0-9].+?)\s?[<，]')
    tel = form_tel.findall(html)
    tel = str(tel).replace(' ', '')
    tel = str(tel).replace('[', '')
    tel = str(tel).replace(']', '')
    tel = str(tel).replace('\'', '')
    # print(tel)
    form_fax = re.compile('(传真[^至]+?)\s?<')
    fax = form_fax.findall(html)
    fax = str(fax).replace(' ', '')
    fax = str(fax).replace('[', '')
    fax = str(fax).replace(']', '')
    fax = str(fax).replace('\'', '')
    # print(fax)
    form_email = re.compile('(电?子?邮.+?tsinghua[^<>]+?)\s?</')
    email = form_email.findall(html)
    #print(email)
    if name=='':
        email = ''
    #print(email)
    try:
        email = email[email.index('href')]
    except:
        pass
    #print(email)
    if 'href' in str(email):
        form_email2 = re.compile('"mailto:(.+?@.+?)"')
        email2 = form_email2.findall(str(email))
        email = '电子邮箱：' + str(email2)  # 超鏈接email....
    email = str(email).replace('AT', '@')
    email = str(email).replace('(at)', '@')
    email = str(email).replace('[at]', '@')
    email = str(email).replace(' ', '')
    email = str(email).replace('[', '')
    email = str(email).replace(']', '')
    email = str(email).replace('\'', '')
    email = str(email).replace('</font>', '')
    email = str(email).replace('<fontsize="2">', '')
    #print(email)
    form_page = re.compile('主页.+?\s?.+?\s?.+?href="(.+?)"')
    page = form_page.findall(html)
    page = str(page).replace('[', '')
    page = str(page).replace(']', '')
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
    info.update(name=name, address=addr, tel=tel, fax=fax, email=email, page=page, academic=academic)

    return info



def get_Img(start_url, url, infos,detectionModel,recognitionModel):
    html = get_Html(url)
    reg = r'src="(.+?\.[jJpP][pPnN][gG])"'
    imgre = re.compile(reg)
    html = html.decode('utf-8', 'ignore')  # python3
    img_list = imgre.findall(html)

    for img_url in img_list:
        info = {}
        if 'http' not in img_url:
            img_url = start_url + img_url


        info = get_info(url, info)

        if info['name'] != '':
            # create new folder
            path = "/home/luka/PycharmProjects/Github/Spider/Spider/"
            title = time.strftime("%Y_%m_%d", time.localtime())
            new_path = os.path.join(path, title)
            if not os.path.isdir(new_path):
                os.makedirs(new_path)
            pic_path = os.path.join(new_path, currentTime() + '.jpg')
            #urllib.request.urlretrieve(img_url, pic_path)  # store in the new folder

            info.update(img_url=img_url, url=url, img_path=pic_path)
            img = Image.open(io.BytesIO(urllib.request.urlopen(img_url).read()))
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
                image2 = numpy.array(cv2.resize(img, (H, W)))
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
                    image2 = numpy.array(cv2.resize(img, (H, W)))
                else:
                    image2 = numpy.array(img)
            [bboxset, extend] = FaceDetect_spider(image2, 50, detectionModel)
            info['feature'] = []
            if len(bboxset) == 0:
                return None

            cv2.imwrite(pic_path,img)
            for bbox in bboxset:
                feature = feature_Extract_spider(recognitionModel, bbox, extend, 128, 128)
                feature = numpy.divide(feature, numpy.sqrt(numpy.dot(feature, feature.T)))
                info['feature'].append(feature)
            info['feature'] = info['feature'][0]
            if len(info['address']):
                info['address'] = info['address'][0]
            if (len(info['feature']) == 1 and (info['name'] != '[]' or info['academic'] != [])) or len(
                        info['feature']) > 1:
                infos.append(info)

#    print(len(infos))
    print("Spider is working...")
    time.sleep(0.1)
    return infos


def search_in_department(start_url, infos,detectionModel,recognitionModel):
    queue = deque()
    visited = set()
    queue.append(start_url)
    cnt = 0
    new_infos = infos
    while queue:
        url = queue.popleft()
        visited |= {url}
        cnt += 1
        try:
            urlop = urllib.request.urlopen(url, timeout=2)
            data = urlop.read().decode('utf-8')
            html = get_Html(url).decode('utf-8', 'ignore')
            new_infos = get_Img(start_url, url, infos,detectionModel,recognitionModel)
        except:
            continue

        linkre = re.compile('href="(.+?\.html)"')
        for x in linkre.findall(data):
            if 'http' not in x:
                x = start_url + x
            if 'eeen' not in x and 'sina' not in x and 'youku' not in x and x not in visited and x not in queue:
                queue.append(x)
    return new_infos


def Spider(caffemodel):
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
    detectionModel=caffemodel[0]
    recognitionModel=caffemodel[1]
    initial_url = 'http://www.ee.tsinghua.edu.cn'  # ee page
    info = {}
    infos = [info]
    new_infos = search_in_department(initial_url, infos,detectionModel,recognitionModel)
    return new_infos

def tss():
    caffe.set_mode_gpu()
    rootFile = '/home/luka/PycharmProjects/cvlab/protobuf/'
    detectionPrototxt = rootFile + 'deploy_face_w.prototxt'
    detectionCaffeModel = rootFile + 'w_iter_100000.caffemodel'
    detectionModel = caffe.Net(detectionPrototxt, detectionCaffeModel, caffe.TEST)

    RecognitionPrototxt = rootFile + 'recognition.prototxt'
    RecognitionCaffeModel = rootFile + '_iter_70000.caffemodel'
    recognitionModel = caffe.Net(RecognitionPrototxt, RecognitionCaffeModel, caffe.TEST)
    # caffemodel=[detectionModel,recognitionModel]
    # tst = Spider(caffemodel)
    caffemodel = [detectionModel, recognitionModel]
    while(1):
    #    print("success!")
        time.sleep(0.1)

if __name__ == '__main__':
    tp=multiprocessing.Process(target=tss)
    ts=multiprocessing.Process(target=Spider)
    tp.start()
    ts.start()
    while(1):
    #    print(1)
        time.sleep(0.1)
