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

def find_department(initial_url,major):
    #queue = deque()
    urlop = urllib.request.urlopen(initial_url, timeout=2)
    data = urlop.read().decode('utf-8')
    linkre = re.compile('href="(.+?\.edu\.cn)')
    for x in linkre.findall(data):
        if 'http' in x:
            if '.'+major+'.' in x or '/'+major+'.' in x:
                return x
    return 'error major!!'

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
    if '姓' in html and '名' in html:
        form_name = re.compile('>姓\s*?名\s?(.+?)<')
    else:
        form_name = re.compile('con开始处-->\s?.+?\s?.+?\s?\s?<p>(.+?)<')
    name = form_name.findall(html)
    name = str(name).replace('：', '')
    name = str(name).replace(',', ' ')
    name = str(name).replace('，', ' ')
    name = str(name).replace('[', '')
    name = str(name).replace(']', '')
    name = str(name).replace('\'', '')
    info.update(name=name)
    #print(name)
    if name == '':
        return info
    elif len(name)>4:
        name0 = name.split()
        name = name0[0]
        title = ''
        for i in range(1,len(name0)):
            title = title + name0[i] + ' '
            #print(title)
    else:
        form_title = re.compile('职称：?(.+?)\s?<')
        title = form_title.findall(html)
        title = str(title).replace('[', '')
        title = str(title).replace(']', '')
        title = str(title).replace('\'', '')
        title = str(title).replace(' ', '')
    info.update(name=name, title=title)
    #print(title)
    #form_addr = re.compile('\s?<.{1,3}>\s?([^<>;]+?清华.+?100084\)?)\s?<')
    #addr = form_addr.findall(html)
    #addr = str(addr).replace('[', '')
    #addr = str(addr).replace(']', '')
    #addr = str(addr).replace('\'', '')
    #addr = str(addr).replace('</p><p>', ' ')
    #info.update(address=addr)
    #print(addr)
    # form_tel = re.compile('[1084]?\s?</p>\s?<p>\s?(电话.+?)\s?<')
    form_tel = re.compile('(电话[^/<>。]+?[0-9].+?)\s?[<，]')
    tel = form_tel.findall(html)
    tel = str(tel).replace(' ', '')
    tel = str(tel).replace('[', '')
    tel = str(tel).replace(']', '')
    tel = str(tel).replace('\'', '')
    info.update(tel=tel)
    #print(tel)
    form_fax = re.compile('(传真[^至]+?)\s?<')
    fax = form_fax.findall(html)
    fax = str(fax).replace(' ', '')
    fax = str(fax).replace('[', '')
    fax = str(fax).replace(']', '')
    fax = str(fax).replace('\'', '')
    info.update(fax=fax)
    #print(fax)
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
    form_page = re.compile('主页.+?\s?.+?\s?.+?href="([^\(\)]+?)"')
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
    except:
        academic =''
    info.update(academic=academic)
    #print(academic)
    return info

def find_imglist(url):
    html = get_Html(url)
    reg = r'src="(.+?\.[jJpP][pPnN][gG])"'
    imgre = re.compile(reg)
    html = html.decode('utf-8', 'ignore')  # python3
    img_list = imgre.findall(html)
    return img_list

def store_pic(img_url, info, url):
    # create new folder
    path = 'd:\Demo-System\Spider'              #store in this folder
    if not os.path.isdir(path):
        os.makedirs(path)                       #create the folder if it doesn't exist
    #title = time.strftime("%Y_%m_%d", time.localtime())
    #new_path = os.path.join(path, info['name'])

    #if info['name']!='':
    #    name = info['name']
    #else:
    #    name = url.split('/')[-1]
    name = 'p' + img_url.split('/')[-1]
    pic_path = os.path.join(path, name)         #names include the type of pictures

    #if 'png' in img_url or 'PNG' in img_url:
    #    pic_path = os.path.join(path, name + '.png')
    #elif 'jpg' in img_url or 'JPG' in img_url:
    #    pic_path = os.path.join(path, name + '.jpg')
    #elif 'bmp' in img_url or 'BMP' in img_url:
    #    pic_path = os.path.join(path, name + '.bmp')  # dicide the name of the picture and the type

    if not os.path.exists(pic_path):                        #if the picture already exists, don't save again
        try:
            urllib.request.urlretrieve(img_url, pic_path)  #store in the new folder
        except:
            pass            #404 Not Found

    info.update(img_path=pic_path)

def get_img_by_info(start_url, url, name, title):
    img_list = find_imglist(url)

    for img_url in img_list:
        info = {}
        # time.sleep(1)
        if 'http' not in img_url:
            #img_url = start_url + img_url
            img_url = start_url + img_url
        #print('saved  ' + str(sum) + ' pictures   capturing <---  ' + img_url)

        info = get_info(url, info)
        #print(info)
        if name in info['name']:    #match
            info.update(img_url=img_url, url=url)  # adding url
            store_pic(img_url, info, url)  # save the picture to local
            try:
                img = Image.open(io.BytesIO(urllib.request.urlopen(img_url, timeout=2).read()))
                # print(img0)
                # img0.show()
                # show pictures of everyone
                # image1 = img.resize((W, H))
                # image1.show()
                image2 = numpy.asarray(img)
            except:
                print('ya')
                continue

            # compare the image with our feature
            # [bbox, extend] = FaceDetect(image2, 50, self.detectionModel)
            # if len(self.bboxCam) == 0:
            #    return None
            # feature = feature_Extract(self.recognitionModel, bbox, extend, 128, 128)
            # feature = numpy.divide(feature, numpy.sqrt(numpy.dot(feature, feature.T)))
            min_size = 50
            feature = []
            # dealing with score larger than a threshold

            #info['image'] = image2
            # info['feature'] = feature

            #print(info)
            yield info
            #return info
    #yield info
    #return info

def SpiderRenewerByInfo(name, school, major, title):
    '''
    Spider's daily work in renewing the existing database
    :param information(dict): personal information of the existing person
    :param image(list):       existing image in the database (changed to saving in infomation(dict))
    :param caffemodel:        caffemodel to compare the similarity between two pictures
    :return:(dict){'name':,'address':,'tel':,'fax':.'email':,'academic':,'image_url':,'profile_url':,'image'(list)}
    '''
    if school=='tsinghua university':
        initial_url = 'http://www.tsinghua.edu.cn/publish/newthu/newthu_cnt/faculties/index.html'  # 科系列表
        school_name = 'tsinghua'
    elif school=='peking university':
        initial_url = 'http://www.pku.edu.cn/academics/index.htm'  # 科系列表
        school_name = 'pku'
    else:
        return 'error input(school)!!!'

    start_url = find_department(initial_url,major)
    print(start_url)

    if start_url == "error major!!":
        return "error input(major)!!"
    #start_url = 'http://www.cs.tsinghua.edu.cn/publish/cs/4797/index.html'
    queue = deque()
    visited = set()
    queue.append(start_url)

    while queue:
        url = queue.popleft()  # 队首元素出队
        visited |= {url}  # 标记为已访问
        #print('have been ' + str('cnt') + ' pages    traversing <---  ' + url)
        try:
            html = get_Html(url).decode('utf-8', 'ignore')
            if name=='':
                for j in get_img_by_info(start_url, url, name, title):
                    #print(j)
                    if j != {} and name in j['name']:
                        yield j
                    #print('no name:',time.time())
            else:
                if name in html:
                #if name in html or title in html:
                    print('there is a name:', time.time())
                    for j in get_img_by_info(start_url, url, name, title):
                        if j != {} and name in j['name']:
                            yield j

                else:
                    #print('not yet',name)
                    pass

            urlop = urllib.request.urlopen(url, timeout=2)
            data = urlop.read().decode('utf-8')
        except :
            continue

        #get new link
        linkre = re.compile('href="(.+?\.html)"')
        for x in linkre.findall(data):
            if 'http' not in x:
                x = start_url + x
                #x = start_url + x
            if major+'en' not in x and school_name in x and x not in visited and x not in queue:  # block english vision of the ee page and non-tsinghua websites
                queue.append(x)
                #print('sum=' + str(len(queue) + len(visited)) + ', ' + str(len(queue)) + 'to go    add to queue --->  ' + x)
        #print(info)


    # clean the saved pictures
    #path = new_info['img_path']
    #remove_num = path.rfind('/')  # for linux
    # remove_num = path.rfind('\\')  #for windows
    #remove_path = path[0:remove_num]
    #shutil.rmtree(remove_path)

    return 'can\'t find :('

if __name__ == '__main__':
    print('start:', time.time())
    #information = SpiderRenewerByInfo('黄翊东','tsinghua university','ee','')
    #information = SpiderRenewerByInfo('陈健生', 'tsinghua university', 'ee', '')
    #information = SpiderRenewerByInfo('', 'tsinghua university', 'cs', '')
    for x in SpiderRenewerByInfo('陈健生', 'tsinghua university', 'ee', ''):
    #for x in SpiderRenewerByInfo('', 'tsinghua university', 'thss', ''):
    #for x in SpiderRenewerByInfo('建华', 'tsinghua university', 'cs', ''):
        print(x)
    #print(information)
    print('finish:',time.time())

