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
import shutil
from .face_detection import faceSimilarityCompare

def spider(img,caffemodel1,caffemodel2):
    '''
    Fetch the information of the  photo that may have relationship with the image input
    need to use the face detection system
    :param img: input image of a specific person
    :return:(dict){'personal information':,'similar images':}
    '''
    #codes here
    #the image you fetch from the website is img2
    min_size = 50
    img2 = []
    score = faceSimilarityCompare(caffemodel1,caffemodel2,img,img2,min_size)
    #return the relative information or image
    pass


def currentTime():
    a = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return a

def get_Html(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    return html

def get_info(url,info):
    html = get_Html(url).decode('utf-8', 'ignore')
    #print(html)
    html = html.replace('&nbsp;','')
    html = html.replace('&ldquo;', '"')
    html = html.replace('&rdquo;', '"')
    html = html.replace('&ndash;', '-')
    html = html.replace('&ndash;', '-')
    html = html.replace('&bull;', '')
    html = html.replace('&quot;', '')
    html = html.replace('<p><br/></p>', '')
    html = html.replace('<p></p>','')
    #print(html)
    form_name = re.compile('con开始处-->\s?.+?\s?.+?\s?\s?<p>(.+?)<')
    name = form_name.findall(html)
    name = str(name).replace('姓名：', '')
    name = str(name).replace('，', ' ')
    #print(name)
    form_addr = re.compile('\s?<.{1,3}>\s?([^<>;]+?清华.+?100084\)?)\s?<')
    addr = form_addr.findall(html)
    #print(addr)
    #form_tel = re.compile('[1084]?\s?</p>\s?<p>\s?(电话.+?)\s?<')
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
    info.update(name = name,address = addr,tel = tel,fax = fax,email = email,academic = academic)

    #if info['name']!='[]':
    #    print(info)
    return info

def get_Img(start_url, url, keywords, info, initial_info):
    html = get_Html(url)
    reg = r'src="(.+?\.[jJpP][pPnN][gG])"'
    imgre = re.compile(reg)
    html = html.decode('utf-8','ignore')  # python3
    img_list = imgre.findall(html)

    #create new folder
    path = "d:\THU\Demo-System\Spider"
    title = time.strftime("%Y_%m_%d", time.localtime())
    new_path = os.path.join(path, title)
    #print(new_path)
    if not os.path.isdir(new_path):
        os.makedirs(new_path)

    for img_url in img_list:
        # time.sleep(1)
        if 'http' not in img_url:
            img_url = start_url + img_url
        #print('saved  ' + str(sum) + ' pictures   capturing <---  ' + img_url)
        curTime=currentTime()
        pic_path=os.path.join(new_path, curTime+'.jpg')
        #print(pic_path)
        urllib.request.urlretrieve(img_url, pic_path) #store in the new folder

        info = get_info(url, info)
        info.update(img_url=img_url, url=url,img_path=pic_path)
        #print(info)
        #print(initial_info['name'])
        if keywords in info['name']:
            return info
            break



        #if keywords not in info['name']:

        #info[img_url]=img_url
        #faceSimilarityCompare=1         #match!!
        #if faceSimilarityCompare>0.5:
        #    info=get_info(url)
        #    pass
    return info

def search_for_new_info(start_url,keywords,info):
    queue = deque()
    visited = set()
    queue.append(start_url)
    cnt = 0
    initial_info = copy.deepcopy(info)
    info['name'] = '电子工程系'
    while queue:
        url = queue.popleft()  # 队首元素出队
        visited |= {url}  # 标记为已访问
        #print('have been ' + str(cnt) + ' pages    traversing <---  ' + url)
        cnt += 1
        # 避免程序异常中止, 用try..catch处理异常
        try:
            urlop = urllib.request.urlopen(url, timeout=2)
            #urlop = urllib.request.urlopen(url)
            data = urlop.read().decode('utf-8')
            html = get_Html(url).decode('utf-8', 'ignore')
            if keywords in html:
                #print(info)
                info= get_Img(start_url, url, keywords, info, initial_info)  # 原本為沒有返回值的函數，但為了sum值所以改了
                #print(info)
        except :
            continue

        #get new link
        linkre = re.compile('href="(.+?\.html)"')
        for x in linkre.findall(data):
            if 'http' not in x:
                x = start_url + x
            if 'eeen' not in x and'sina' not in x and'youku' not in x and x not in visited and x not in queue: #block english vision of the ee page and sina, youku
                queue.append(x)
                #print('sum=' + str(len(queue) + len(visited)) + ', ' + str(len(queue)) + 'to go    add to queue --->  ' + x)

        if keywords in info['name']:
            break
    return info

def SpiderRenewer(info,caffemodel1):
    '''
    Spider's daily work in renewing the existing database
    :param information(dict): personal information of the existing person
    :param image(list):       existing image in the database
    :param caffemodel:        caffemodel to compare the similarity between two pictures
    :return:(dict){'name':,'address':,'tel':,'fax':.'email':,'academic':,'image_url':,'profile_url':,'image'(ltst)}
    '''
    initial_url = 'http://www.ee.tsinghua.edu.cn'  # ee page
    if info['name']!='[]':
        keywords=info['name'].split()[0].replace('[','').replace('\']','').replace('\'','').replace('*','')
    #print(keywords)
    #print(info)
    new_info=search_for_new_info(initial_url,keywords,info)
    img=cv2.imread(new_info['img_path'])
    #img = cv2.imread('D:/THU/Demo-System/Spider/2017_07_19/20170719_173457_741862.jpg')
    #cv2.imshow("original", img)
    #cv2.waitKey(1000)
    H, W, D=img.shape
    #print(H, W, D)
    r=H/W
    if r>1:
        H=512
        W=512/r
        W=int(W)
    else:
        H=512*r
        H=int(H)
        W=512

    min_size = 50
    image2 = numpy.array(cv2.resize(img, (W, H)))

    #cv2.imshow('changed size',img)
    #cv2.waitKey(1000)
    #cv2.imshow('array', image2)
    #cv2.waitKey(2000)

    new_info['image']=image2
    feature = []
    #dealing with score larger than a threshold

    #clean the saved pictures
    path = new_info['img_path']
    #path = 'C:/Users/rexli/Desktop/New folder/New folder/2015011082201702.jpg'
    #print(path)
    remove_num = path.rfind('/')
    #remove_num = path.rfind('\\')
    remove_path = path[0:remove_num]
    shutil.rmtree(remove_path)
    return new_info
