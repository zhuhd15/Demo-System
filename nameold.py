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
from PIL import Image
import numpy
import cv2
import shutil
import io
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
    html = html.replace('<p>&nbsp;</p>', '')
    html = html.replace('&nbsp;', ' ')
    html = html.replace('<p><br/></p>', '')
    html = html.replace('<p></p>', '')
    html = html.replace('&ldquo;', '"')
    html = html.replace('&rdquo;', '"')
    html = html.replace('&ndash;', '-')
    html = html.replace('&ndash;', '-')
    html = html.replace('&bull;', ' ')
    html = html.replace('&quot;', ' ')

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
    if len(name)>4:
        name0 = name.split()
        name = name0[0]
        title = ''
        for i in range(1,len(name0)):
            title = title + name0[i] + ' '
            #print(title)
    else:
        form_title = re.compile('职称：(.+?)\s?<')
        title = form_title.findall(html)
        title = str(title).replace('[', '')
        title = str(title).replace(']', '')
        title = str(title).replace('\'', '')
        title = str(title).replace(' ', '')
    info.update(name=name, title=title)
    #print(title)
    form_addr = re.compile('\s?<.{1,3}>\s?([^<>;]+?清华.+?100084\)?)\s?<')
    addr = form_addr.findall(html)
    addr = str(addr).replace('[', '')
    addr = str(addr).replace(']', '')
    addr = str(addr).replace('\'', '')
    addr = str(addr).replace('</p><p>', ' ')
    info.update(address=addr)
    # print(addr)
    # form_tel = re.compile('[1084]?\s?</p>\s?<p>\s?(电话.+?)\s?<')
    form_tel = re.compile('(电话[^/<>。]+?[0-9].+?)\s?[<，]')
    tel = form_tel.findall(html)
    tel = str(tel).replace(' ', '')
    tel = str(tel).replace('[', '')
    tel = str(tel).replace(']', '')
    tel = str(tel).replace('\'', '')
    info.update(tel=tel)
    # print(tel)
    form_fax = re.compile('(传真[^至]+?)\s?<')
    fax = form_fax.findall(html)
    fax = str(fax).replace(' ', '')
    fax = str(fax).replace('[', '')
    fax = str(fax).replace(']', '')
    fax = str(fax).replace('\'', '')
    info.update(fax=fax)
    # print(fax)
    form_email0 = re.compile('(电?子?邮[^/]+?tsinghua[^<>]+?)\s?</')
    form_email1 = re.compile('([eE]?-?mail.{2,50}tsinghua[^<>]+?)\s?</')
    email0 = form_email0.findall(html)
    email1 = form_email1.findall(html)
    email = email0 + email1
    #print(email)
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
            #print(email)
            #print(email3)
            email = email3
        email = str(email).replace('[', '')
        email = str(email).replace(']', '')
        email = str(email).replace('\'', '')
    info.update(email=email)
    #print(email)
    form_page = re.compile('主页.+?\s?.+?\s?.+?href="(.+?)"')
    page = form_page.findall(html)
    page = str(page).replace('[', '')
    page = str(page).replace(']', '')
    info.update(page=page)
    #print(page)
    # form_academic1 = re.compile('学术成果.+?(\[1][^<>[]+)',re.DOTALL)
    form_academic1 = re.compile('学术成果.+?([\[\(（]?1[\.\]、\)）][^<>[]+)', re.DOTALL)
    academic1 = form_academic1.findall(html)
    # print(academic1)
    form_academic2 = re.compile('学术成果.+?([\[\(（]?2[\.\]、\)）][^<>[]+)', re.DOTALL)
    academic2 = form_academic2.findall(html)
    # print(academic2)
    form_academic3 = re.compile('学术成果.+?([\[\(（]?3[\.\]、\)）][^<>[]+)', re.DOTALL)
    academic3 = form_academic3.findall(html)
    # print(academic3)
    try:
        academic = str(academic1[0]) +' \n'+ str(academic2[0]) +' \n'+ str(academic3[0])
        academic = academic.replace('"','\"')
        info.update(academic=academic)
    except:
        pass
    #print(academic)

    return info

def find_imglist(url):
    html = get_Html(url)
    reg = r'src="(.+?\.[jJpP][pPnN][gG])"'
    imgre = re.compile(reg)
    html = html.decode('utf-8', 'ignore')  # python3
    img_list = imgre.findall(html)
    return img_list

def store_pic( info,img_url):
    # create new folder
    path = "/home/luka/PycharmProjects/Github/Spider/Spider/From_website/"
    if not os.path.isdir(path):
        os.makedirs(path)
    name = 'p' + img_url.split('/')[-1]
    pic_path = os.path.join(path,name)+'.jpg'

    info.update(img_path=pic_path)

#def get_img(start_url, url, keywords, info, initial_info):
def get_img(start_url, url, keywords, info,caffemodel):
    img_list = find_imglist(url)
    detectionModel = caffemodel[0]
    recognitionModel = caffemodel[1]
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
        except:
            continue

        #compare the image with our feature

        min_size = 50
        feature = []
        # dealing with score larger than a threshold

        info = get_info(url, info)                            #there is picture, thus get the infomations
        #print(info)

        if keywords in info['name']:    #match
            # create new folder to save pictures
            info.update(img_url=img_url, url=url)  # adding url
            store_pic(info, url)  # save the picture to local
            info['image'] = image2
            # info['feature'] = feature
            [bbox, extend] = FaceDetect_spider(image2, 50, detectionModel)
            if len(bbox) == 0:
                return None
            if not os.path.exists(info['img_path']):
                cv2.imwrite(info['img_path'],img)
            bbox = bbox[0]
            feature = feature_Extract_spider(recognitionModel, bbox, extend, 128, 128)
            feature = numpy.divide(feature, numpy.sqrt(numpy.dot(feature, feature.T)))
            info['feature'] = feature
            #print(info)
            return info
    return info

def SpiderRenewerByName(info, caffemodel):
    '''
    Spider's daily work in renewing the existing database
    :param information(dict): personal information of the existing person
    :param image(list):       existing image in the database (changed to saving in infomation(dict))
    :param caffemodel:        caffemodel to compare the similarity between two pictures
    :return:(dict){'name':,'address':,'tel':,'fax':.'email':,'academic':,'image_url':,'profile_url':,'image'(list)}
    '''
    initial_url = 'http://www.ee.tsinghua.edu.cn'  # ee main page
    if info['name'] != '':
        keywords= info['name'].split()[0].replace('[', '').replace('\']', '').replace('\'', '').replace('*', '')
    else:
        return 'error!!!'
    print(keywords)
    queue = deque()
    visited = set()
    queue.append(initial_url)
    #initial_info = copy.deepcopy(info)
    info['name'] = '电子工程系'
    while queue:
        url = queue.popleft()  # 队首元素出队
        visited |= {url}  # 标记为已访问
        #print('have been ' + str('cnt') + ' pages    traversing <---  ' + url)
        try:
            urlop = urllib.request.urlopen(url, timeout=2)
            data = urlop.read().decode('utf-8')
            html = get_Html(url).decode('utf-8', 'ignore')

        except :
            continue
        if keywords in html:
            # info= get_img(start_url, url, keywords, info, initial_info)
            info = get_img(initial_url, url, keywords, info, caffemodel)
        #get new link
        linkre = re.compile('href="(.+?\.html)"')
        for x in linkre.findall(data):
            if 'http' not in x:
                x = initial_url + x
            if 'eeen' not in x and 'tsinghua' in x and x not in visited and x not in queue:  # block english vision of the ee page and non-tsinghua websites
                queue.append(x)
                #print('sum=' + str(len(queue) + len(visited)) + ', ' + str(len(queue)) + 'to go    add to queue --->  ' + x)

        if keywords in info['name']:
            return info

    # clean the saved pictures
    #path = new_info['img_path']
    #remove_num = path.rfind('/')  # for linux
    # remove_num = path.rfind('\\')  #for windows
    #remove_path = path[0:remove_num]
    #shutil.rmtree(remove_path)
    if info['name'] == '电子工程系':
        return None
    return info

if __name__ == '__main__':
    print('start:', time.time())
    information = {'email': 'jschen'}
    #information = {'name': "['陈健生']", 'address': ['罗姆楼*****'], 'email': "['电子邮箱：********@tsinghua.edu.cn']"}
    #information = {'name': "['马惠敏 教授']", 'address': ['罗姆楼*****'], 'email': "['电子邮箱：********@tsinghua.edu.cn']"}
    #information = {'name': '宋健', 'address': '罗姆楼******', 'email': '电子邮箱：********@tsinghua.edu.cn', 'academic': '[1]Dengke Zhang, Xue Feng, Kaiyu Cui, Fang Liu, and Yidong Huang, \"Identifying Orbital Angular Momentum of Vectorial Vortices with Pancharatnam Phase and Stokes Parameters\", Scientific Reports, 5, 11982, 2015.'}
    information = SpiderRenewerByName(information,0)
    #info={}
    #get_info("http://www.ee.tsinghua.edu.cn/publish/ee/4157/2010/20101215181053606383396/20101215181053606383396_.html",info)
    print(information)
    print('finish:',time.time())

