#! /usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Lin Po-Yu'

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
import numpy
import cv2
import shutil,caffe
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
    addr = str(addr).replace('</p><p>', ' ')
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
    form_email0 = re.compile('(电?子?邮[^/]+?tsinghua[^<>]+?)\s?</')          #中文
    form_email1 = re.compile('([eE]?-?mail.{2,50}tsinghua[^<>]+?)\s?</')        #english version
    email0 = form_email0.findall(html)
    email1 = form_email1.findall(html)
    email = email0 + email1
    if name=='':
        email = ''
    else:
        if len(email)>1:
            for x in range(0,len(email)-1):
                if 'mailto' in str(email[x]):
                    email = email[x]
        email = str(email).replace(' AT ', '@')
        email = str(email).replace('(at)', '@')
        email = str(email).replace('[at]', '@')
        email = str(email).replace('[dot]', '.')
        email = str(email).replace(' ', '')
        if 'mailto' in str(email):
            form_email2 = re.compile('mailto:(.+?@.+?)"')
            email2 = form_email2.findall(str(email))
            email = email2[0]  # 超鏈接email
        else:
            form_email3 = re.compile('([a-zA-Z0-9\-_*]+?@.+)\']')
            email3 = form_email3.findall(str(email))
            email = email3
        email = str(email).replace('[', '')
        email = str(email).replace(']', '')
        email = str(email).replace('\'', '')
    #print(email)
    form_page = re.compile('主页.+?\s?.+?\s?.+?href="(.+?)"')
    page = form_page.findall(html)
    page = str(page).replace('[', '')
    page = str(page).replace(']', '')
    # print(page)
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

def find_imglist(url):
    html = get_Html(url)
    reg = r'src="(.+?\.[jJpP][pPnN][gG])"'
    imgre = re.compile(reg)
    html = html.decode('utf-8', 'ignore')  # python3
    img_list = imgre.findall(html)
    return img_list

def store_pic(img_url, info):
    # create new folder
    path = "d:\Demo-System\Spider"
    title = time.strftime("%Y_%m_%d", time.localtime())
    new_path = os.path.join(path, title)
    if not os.path.isdir(new_path):
        os.makedirs(new_path)
    if 'png' in img_url or 'PNG' in img_url:
        pic_path = os.path.join(new_path, currentTime() + '.png')
    elif 'jpg' in img_url or 'JPG' in img_url:
        pic_path = os.path.join(new_path, currentTime() + '.jpg')
    elif 'bmp' in img_url or 'BMP' in img_url:
        pic_path = os.path.join(new_path, currentTime() + '.bmp')
    try:
        urllib.request.urlretrieve(img_url, pic_path)  #store in the new folder
    except:
        pass            #404 Not Found
    info.update(img_path=pic_path)

def get_img_name(start_url, url, keywords, info):
    img_list = find_imglist(url)

    for img_url in img_list:
        # time.sleep(1)
        if 'http' not in img_url:
            img_url = start_url + img_url
        #print('saved  ' + str(sum) + ' pictures   capturing <---  ' + img_url)

        info = get_info(url, info)                            #there is picture, thus get the infomations
        

        if keywords in info['name']:    #match
            info.update(img_url=img_url, url=url)                  #adding url
            store_pic(img_url, info)                # save the picture to local
            return info
            break

    return info

def search_for_new_info_by_name(start_url,keywords,info):
    queue = deque()
    visited = set()
    queue.append(start_url)
    info['name'] = '电子工程系'
    while queue:
        url = queue.popleft()  # 队首元素出队
        visited |= {url}  # 标记为已访问
        #print('have been ' + str(cnt) + ' pages    traversing <---  ' + url)
        cnt += 1
        # 避免程序异常中止, 用try..catch处理异常
        try:
            urlop = urllib.request.urlopen(url, timeout=2)
            data = urlop.read().decode('utf-8')
            html = get_Html(url).decode('utf-8', 'ignore')
            if keywords in html:
                info= get_img_by_name(start_url, url, keywords, info)  
        except :
            continue

        #get new link
        linkre = re.compile('href="(.+?\.html)"')
        for x in linkre.findall(data):
            if 'http' not in x:
                x = start_url + x
            if 'eeen' not in x and 'tsinghua' in x and x not in visited and x not in queue:  # block english vision of the ee page and non-tsinghua websites
                queue.append(x)
                #print('sum=' + str(len(queue) + len(visited)) + ', ' + str(len(queue)) + 'to go    add to queue --->  ' + x)

        if keywords in info['name']:
            break
    return info


def SpiderRenewer(info, caffemodel):
    '''
    Spider's daily work in renewing the existing database
    :param information(dict): personal information of the existing person
    :param image(list):       existing image in the database (changed to saving in infomation(dict))
    :param caffemodel:        caffemodel to compare the similarity between two pictures
    :return:(dict){'name':,'address':,'tel':,'fax':.'email':,'academic':,'image_url':,'profile_url':,'image'(list)}
    '''
    initial_url = 'http://www.ee.tsinghua.edu.cn'  # ee main page
    detectionModel = caffemodel[0]
    recognitionModel = caffemodel[1]
    if info['name'] != '[]':
        keywords = info['name'].split()[0].replace('[', '').replace('\']', '').replace('\'', '').replace('*', '')
    new_info = search_for_new_info_by_name(initial_url, keywords, info)
    img = cv2.imread(new_info['img_path'])  # get image form disk
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
            image2 = numpy.array(cv2.resize(img, (H, W)))
        else:
            image2 = numpy.array(img)
    [bboxset, extend] = FaceDetect_spider(image2, 50, detectionModel)
    info['feature'] = []
    if len(bboxset) == 0:
        return None
    for bbox in bboxset:
        feature = feature_Extract_spider(recognitionModel, bbox, extend, 128, 128)
        feature = numpy.divide(feature, numpy.sqrt(numpy.dot(feature, feature.T)))
        info['feature'].append(feature)

    # show pictures of everyone
    # cv2.imshow('arrayimg', image2)
    # cv2.waitKey(500)

    #new_info['image'] = image2
    feature = []
    # dealing with score larger than a threshold

    # clean the saved pictures
    path = new_info['img_path']
    # remove_num = path.rfind('/')  # for linux
    # remove_num = path.rfind('\\')  #for windows
    # remove_path = path[0:remove_num]
    # shutil.rmtree(remove_path)            #delete the whole folder
    os.remove(path)                         #delete the saved picture(just keep the feature)
    return new_info

if __name__ == '__main__':
    information = {'name': "['张志军']", 'address': ['???'], 'email': "['电子邮箱：??']"}
    caffe.set_mode_gpu()
    rootFile = '/home/luka/PycharmProjects/cvlab/protobuf/'
    detectionPrototxt = rootFile + 'deploy_face_w.prototxt'
    detectionCaffeModel = rootFile + 'w_iter_100000.caffemodel'
    detectionModel = caffe.Net(detectionPrototxt, detectionCaffeModel, caffe.TEST)

    RecognitionPrototxt = rootFile + 'recognition.prototxt'
    RecognitionCaffeModel = rootFile + '_iter_70000.caffemodel'
    recognitionModel = caffe.Net(RecognitionPrototxt, RecognitionCaffeModel, caffe.TEST)

    caffemodel = [detectionModel, recognitionModel]
    information = SpiderRenewer(information,caffemodel)
    print(information)

