import pymysql
import numpy
import random
import sys
import time
sys.path.append('/home/luka/PycharmProjects/Github/Demo-System')
import spider,caffe
import spider2,spider3
import inSamePht
import os
from UIMain import dealWithImg

global tmpTrans
tmpTrans = 0.55
global srchTrans
srchTrans = 0.45
global Combine
Combine = 0.40

global databaseRebuilding
databaseRebuilding = 0
#global transLim
#transLim = 0.4


def RebaseStatus():
    global databaseRebuilding
    return databaseRebuilding

def fillInfo(informationDict):
    if (not 'leftson' in informationDict.keys()):
        informationDict['leftson'] = 0
    if (not 'rightson' in informationDict.keys()):
        informationDict['rightson'] = 0
    if (not 'depth' in informationDict.keys()):
        informationDict['depth'] = 0
    if (not 'img_path' in informationDict.keys()):
        informationDict['img_path'] = ''
    if (not 'name' in informationDict.keys()):
        informationDict['name'] = ''
    if (not 'address' in informationDict.keys()):
        informationDict['address'] = ''
    if (not 'tel' in informationDict.keys()):
        informationDict['tel'] = ''
    if (not 'fax' in informationDict.keys()):
        informationDict['fax'] = ''
    if (not 'email' in informationDict.keys()):
        informationDict['email'] = ''
    if (not 'academic' in informationDict.keys()):
        informationDict['academic'] = ''
    if (not 'url' in informationDict.keys()):
        informationDict['url'] = ''
    if (not 'firstVisit' in informationDict.keys()):
        informationDict['firstVisit'] = 0
    for i in range(0,3):
        if (not ('visit' + str(i)) in informationDict.keys()):
            informationDict['visit' + str(i)] = 0
    for i in range(0,10):
        if (not ('famiPeople' + str(i)) in informationDict.keys()):
            informationDict['famiPeople' + str(i)] = 0
    for i in range(0,10):
        if (not ('famiPeopleCnt' + str(i)) in informationDict.keys()):
            informationDict['famiPeopleCnt' + str(i)] = 0
    for i in range(0,5):
        if (not ('tempFamiPeople' + str(i)) in informationDict.keys()):
            informationDict['tempFamiPeople' + str(i)] = 0
    for i in range(0,5):
        if (not ('tempFamiPeopleCnt' + str(i)) in informationDict.keys()):
            informationDict['tempFamiPeopleCnt' + str(i)] = 0
    return informationDict
    pass

def featureDist(feature0 ,feature1):
    feature1 = numpy.array(feature1)
    feature0 = numpy.array(feature0)
    dist = numpy.sqrt(numpy.sum(numpy.square(feature0-feature1)))
    #dist = 0
    #for i in range(0,512):
    #    dist += ((feature0[i] - feature1[i])** 2)
    #dist = dist ** 0.5
    return dist
    pass

def featureTransvection(feature0 ,feature1):
    trans = 0
    for i in range(0,512):
        trans += feature0[i] * feature1[i]
    return trans
    pass

def timeDist(time1, time2):
    if time1 > time2:
        return time1 - time2 - (((time1 // 100) - (time2 // 100))* 40)
    else:
        return time2 - time1 - (((time2 // 100) - (time1 // 100))* 40)
    pass

def unionInfo(info1, info2):
    info = dict()
    info['img_path'] = info1['img_path']
    if info['img_path'] == '':
        info['img_path'] = info2['img_path']
    info['name'] = info1['name']
    if info['name'] == '':
        info['name'] = info2['name']
    info['address'] = info1['address']
    if info['address'] == '':
        info['address'] = info2['address']
    info['tel'] = info1['tel']
    if info['tel'] == '':
        info['tel'] = info2['tel']
    info['fax'] = info1['fax']
    if info['fax'] == '':
        info['fax'] = info2['fax']
    info['email'] = info1['email']
    if info['email'] == '':
        info['email'] = info2['email']
    info['academic'] = info1['academic']
    if info['academic'] == '':
        info['academic'] = info2['academic']
    info['url'] = info1['url']
    if info['url'] == '':
        info['url'] = info2['url']
    info['firstVisit'] = info1['firstVisit']
    if (info2['firstVisit'] != 0)and(info2['firstVisit']<info['firstVisit']):
        info['firstVisit'] = info2['firstVisit']
    visitList = []
    for i in range(0,3):
        visitList.append(info1['visit' + str(i)])
        visitList.append(info2['visit' + str(i)])
    visitList.sort()
    for i in range(0,3):
        info['visit' + str(i)] = visitList[i]
    famiList = []
    for i in range(0,10):
        flag = 0
        for j in range(0,len(famiList)):
            if info1['famiPeople' + str(i)] == famiList[j][0]:
                famiList[j][1] += info1['famiPeopleCnt' + str(i)]
                flag = 1
                break
        if flag:
            continue
        #famiList.append(list(info1['famiPeople' + str(i)], info1['famiPeopleCnt' + str(i)]))
        famiList.append([info1['famiPeople' + str(i)], info1['famiPeopleCnt' + str(i)]])

    for i in range(0,10):
        flag = 0
        for j in range(0,len(famiList)):
            if info2['famiPeople' + str(i)] == famiList[j][0]:
                famiList[j][1] += info2['famiPeopleCnt' + str(i)]
                flag = 1
                break
        if flag:
            continue
        #famiList.append(list(info2['famiPeople' + str(i)], info2['famiPeopleCnt' + str(i)]))
        famiList.append([info1['famiPeople' + str(i)], info1['famiPeopleCnt' + str(i)]])
    for i in range(len(famiList)):
        for j in range(0,i):
            if famiList[i][1] > famiList[j][1]:
                famiList[i], famiList[j] = famiList[j], famiList[i]
    for i in range(0,min(10,len(famiList))):
        info['famiPeople' + str(i)] = famiList[i][0]
        info['famiPeopleCnt' + str(i)] = famiList[i][1]
    info['feature'] = info1['feature']
    return info
    pass



def databaseInit():
    conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    cur.execute("drop table if exists user;")
    cur.execute("""
    create table user
    (
        idNo smallint not null primary key auto_increment,
        leftson smallint,
        rightson smallint,
        depth smallint,
        img_path varchar(2000),
        name varchar(2000),
        address varchar(2000),
        tel varchar(2000),
        fax varchar(2000),
        email varchar(2000),
        academic varchar(2000),
        url varchar(2000),
        firstVisit bigint,
        visit0 bigint,
        visit1 bigint,
        visit2 bigint,
        famiPeople0 smallint,
        famiPeople1 smallint,
        famiPeople2 smallint,
        famiPeople3 smallint,
        famiPeople4 smallint,
        famiPeople5 smallint,
        famiPeople6 smallint,
        famiPeople7 smallint,
        famiPeople8 smallint,
        famiPeople9 smallint,
        famiPeopleCnt0 int,
        famiPeopleCnt1 int,
        famiPeopleCnt2 int,
        famiPeopleCnt3 int,
        famiPeopleCnt4 int,
        famiPeopleCnt5 int,
        famiPeopleCnt6 int,
        famiPeopleCnt7 int,
        famiPeopleCnt8 int,
        famiPeopleCnt9 int,
        tempFamiPeople0 int,
        tempFamiPeople1 int,
        tempFamiPeople2 int,
        tempFamiPeople3 int,
        tempFamiPeople4 int,
        tempFamiPeopleCnt0 int,
        tempFamiPeopleCnt1 int,
        tempFamiPeopleCnt2 int,
        tempFamiPeopleCnt3 int,
        tempFamiPeopleCnt4 int
    )auto_increment = 1 character set utf8;
    """)
    conn.commit()
    cur.close()
    conn.close()
    pass

def databaseInsert(informationDict):
    informationDict = fillInfo(informationDict)
    conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    infoCnt = cur.execute("select * from user")
    if infoCnt > 0:
        pt = 1
    else:
        pt = 0
    infoCnt = infoCnt + 1
    dimNo = 0
    tmpId = 0
    sonTag = -1
    dep = 0
    while (pt != 0):
        dep += 1
        cur.execute("select * from feature" + str(pt))
        tmpFeature = 0
        for i in (0,dimNo + 1):
            tmpFeature = cur.fetchone()
        cur.execute("select * from user where idNo = {}".format(pt))
        tmpInfo = cur.fetchone()
        tmpId = tmpInfo[0]
        if (informationDict['feature'][dimNo] < tmpFeature[1]):
            pt = tmpInfo[1]
            sonTag = 1
        else:
            pt = tmpInfo[2]
            sonTag = 2
        dimNo = dimNo + 1
        dimNo = dimNo % 512
    if (sonTag != -1):
        if (sonTag == 1):
            cur.execute("update user set leftson = {} where idNo = {}".format(infoCnt, tmpId))
        else:
            cur.execute("update user set rightson = {} where idNo = {}".format(infoCnt, tmpId))
    informationDict['depth'] = dep + 1
    cur.execute("set names utf8;")
    cur.execute("""
    insert into user(
        leftson,
        rightson,
        depth,
        img_path,
        name,
        address,
        tel,
        fax,
        email,
        url,
        firstVisit,
        visit0,
        visit1,
        visit2,
        famiPeople0,
        famiPeople1,
        famiPeople2,
        famiPeople3,
        famiPeople4,
        famiPeople5,
        famiPeople6,
        famiPeople7,
        famiPeople8,
        famiPeople9,
        famiPeopleCnt0,
        famiPeopleCnt1,
        famiPeopleCnt2,
        famiPeopleCnt3,
        famiPeopleCnt4,
        famiPeopleCnt5,
        famiPeopleCnt6,
        famiPeopleCnt7,
        famiPeopleCnt8,
        famiPeopleCnt9,
        tempFamiPeople0,
        tempFamiPeople1,
        tempFamiPeople2,
        tempFamiPeople3,
        tempFamiPeople4,
        tempFamiPeopleCnt0,
        tempFamiPeopleCnt1,
        tempFamiPeopleCnt2,
        tempFamiPeopleCnt3,
        tempFamiPeopleCnt4)
        values({}, {}, {}, "{}", "{}", "{}", "{}", "{}", "{}", "{}", {}, {} ,{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {});
    """.format(informationDict['leftson'],#1
               informationDict['rightson'],#2
               informationDict['depth'],#3
               informationDict['img_path'],#4
               informationDict['name'],#5
               informationDict['address'],#6
               informationDict['tel'],#7
               informationDict['fax'],#8
               informationDict['email'],#9
               #informationDict['academic'],#10
               informationDict['url'],#11
               informationDict['firstVisit'],#12
               informationDict['visit0'],#13
               informationDict['visit1'],#14
               informationDict['visit2'],#15
               informationDict['famiPeople0'],#16
               informationDict['famiPeople1'],#17
               informationDict['famiPeople2'],#18
               informationDict['famiPeople3'],#19
               informationDict['famiPeople4'],#20
               informationDict['famiPeople5'],#21
               informationDict['famiPeople6'],#22
               informationDict['famiPeople7'],#23
               informationDict['famiPeople8'],#24
               informationDict['famiPeople9'],#25
               informationDict['famiPeopleCnt0'],#26
               informationDict['famiPeopleCnt1'],#27
               informationDict['famiPeopleCnt2'],#28
               informationDict['famiPeopleCnt3'],#29
               informationDict['famiPeopleCnt4'],#30
               informationDict['famiPeopleCnt5'],#31
               informationDict['famiPeopleCnt6'],#32
               informationDict['famiPeopleCnt7'],#33
               informationDict['famiPeopleCnt8'],#34
               informationDict['famiPeopleCnt9'],#35
               informationDict['tempFamiPeople0'],#36
               informationDict['tempFamiPeople1'],#37
               informationDict['tempFamiPeople2'],#38
               informationDict['tempFamiPeople3'],#39
               informationDict['tempFamiPeople4'],#40
               informationDict['tempFamiPeopleCnt0'],#41
               informationDict['tempFamiPeopleCnt1'],#42
               informationDict['tempFamiPeopleCnt2'],#43
               informationDict['tempFamiPeopleCnt3'],#44
               informationDict['tempFamiPeopleCnt4']))#45
    cur.execute("create table if not exists feature" + str(infoCnt) +
    """(
        dim int not null primary key auto_increment,
        value float not null
    )auto_increment = 0;
    """)
    for i in range(0,512):
        cur.execute("insert into feature" + str(infoCnt) + "(value)values({});".format(informationDict['feature'][i]))
    conn.commit()
    cur.close()
    conn.close()
    return infoCnt
    pass

def databaseFind(feature):
    conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    infoCnt = cur.execute("select * from user")
    if infoCnt > 0:
        pt = 1
    else:
        pt = 0
    dimNo = 0
    tmpId = 0
    que = []
    while (pt != 0):
        que.append(pt)
        cur.execute("select * from feature" + str(pt))
        tmpFeature = 0
        for i in (0,dimNo + 1):
            tmpFeature = cur.fetchone()
        cur.execute("select * from user where idNo = {}".format(pt))
        tmpInfo = cur.fetchone()
        tmpId = tmpInfo[0]
        if (feature[dimNo] < tmpFeature[1]):
            pt = tmpInfo[1]
        else:
            pt = tmpInfo[2]
        dimNo = dimNo + 1
        dimNo = dimNo % 512
    que = que[::-1]
    ans = []
    dist = []
    for i in que:
        cur.execute("select * from user where idNo = {}".format(i))
        tmpInfo = cur.fetchone()
        tmpDimFeature = 0
        cur.execute("select * from feature" + str(i))
        tmpFeature = []
        for j in range(0,512):
            tmp = cur.fetchone()
            tmpFeature.append(tmp[1])
        tmpFeature = numpy.array(tmpFeature)
        tmpDimFeature = tmpFeature[tmpInfo[3]]
        tmpDist = featureDist(tmpFeature, feature)
        global tmpTrans
        Tdist = numpy.sqrt(2-2*tmpTrans)
        if (tmpDist < Tdist):
            if (len(ans) < 5):
                ans.append(i)
                dist.append(tmpDist)
                for j in range(0,len(ans) - 1):
                    for k in range(j+1,len(ans)):
                        if dist[j] > dist[k]:
                            ans[j], ans[k] = ans[k], ans[j]
                            dist[j], dist[k] = dist[k], dist[j]
            else:
                for j in range(0,5):
                    if (tmpDist < dist[j]) and (tmpDist < Tdist):
                        for k in range(-3,-j+1):
                            ans[-k+1] = ans[-k]
                            dist[-k+1] = dist[-k]
                        ans[j] = i
                        dist[j] = tmpDist
                        break
        if (tmpInfo[1] != 0 and not(tmpInfo[1] in que)):
            cur.execute("select * from feature" + str(tmpInfo[1]))
            tmpFeature = []
            for j in range(0,512):
                tmp = cur.fetchone()
                tmpFeature.append(tmp[1])
            tmpFeature = numpy.array(tmpFeature)
            if (len(dist) != 0) and (featureDist(feature, tmpFeature) < dist[len(dist) - 1]):
                que.append(tmpInfo[1])
        if (tmpInfo[2] != 0 and not(tmpInfo[2] in que)):
            cur.execute("select * from feature" + str(tmpInfo[2]))
            tmpFeature = []
            for j in range(0,512):
                tmp = cur.fetchone()
                tmpFeature.append(tmp[1])
            tmpFeature = numpy.array(tmpFeature)
            if (len(dist) != 0) and (featureDist(feature, tmpFeature) < dist[len(dist) - 1]):
                que.append(tmpInfo[2])
    conn.commit()
    cur.close()
    conn.close()
    print(len(que))
    return ans
    pass

'''def databaseReappend(tempList):
    for i in tempList:
        if ('academic' in i.keys()) and (type(i['academic']) is list):
            tmpStr = ''
            for j in i['academic']:
                tmpStr += j + '$'
            i['academic'] = tmpStr
        if 'feature' in i.keys():
            databaseRenew(i)
    conn.commit()
    return None
    #conn.commit()'''

def databaseRenew(informationDict):
    conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    informationDict = fillInfo(informationDict)
    commonList = databaseFind(informationDict['feature'])
    if len(commonList) == 0:
        if informationDict['firstVisit'] == 0:
            informationDict['firstVisit'] = informationDict['visit0']
        conn.commit()
        cur.close()
        conn.close()
        return databaseInsert(informationDict)
    tmpId = 0
    #tmpTrans = 0.55
    #this should be bew
    #global tmpTrans
    #tempTrans = tmpTrans
    global Combine
    tempTrans = Combine
    for i in commonList:
        cur.execute("select * from feature" + str(i))
        tmpFeature = []
        for j in range(0,512):
            tmp = cur.fetchone()
            tmpFeature.append(tmp[1])
        tmpFeature = numpy.array(tmpFeature)
        trans = featureTransvection(informationDict['feature'], tmpFeature)
        if trans > tempTrans:
            tempTrans = trans
            tmpId = i
    if tmpId == 0:
        return 0
    if informationDict['img_path'] != '':
        cur.execute("update user set img_path = '{}' where idNo = {}".format(informationDict['img_path'], tmpId))
    if informationDict['name'] != '':
        cur.execute("update user set name = '{}' where idNo = {}".format(informationDict['name'], tmpId))
    if informationDict['address'] != '':
        cur.execute("update user set address = '{}' where idNo = {}".format(informationDict['address'], tmpId))
    if informationDict['tel'] != '':
        cur.execute("update user set tel = '{}' where idNo = {}".format(informationDict['tel'], tmpId))
    if informationDict['fax'] != '':
        cur.execute("update user set fax = '{}' where idNo = {}".format(informationDict['fax'], tmpId))
    if informationDict['email'] != '':
        cur.execute("update user set email = '{}' where idNo = {}".format(informationDict['email'], tmpId))
    #if informationDict['academic'] != '':
    #    cur.execute("update user set academic = '{}' where idNo = {}".format(informationDict['academic'], tmpId))
    if informationDict['url'] != '':
        cur.execute("update user set url = '{}' where idNo = {}".format(informationDict['url'], tmpId))
    if informationDict['visit0'] != 0:
        cur.execute("select * from user where idNo = {}".format(tmpId))
        tmpInfo = cur.fetchone()
        cur.execute("update user set visit2 = {} where idNo = {}".format(tmpInfo[14], tmpId))
        cur.execute("update user set visit1 = {} where idNo = {}".format(tmpInfo[13], tmpId))
        cur.execute("update user set visit0 = {} where idNo = {}".format(informationDict['visit0'], tmpId))
        if tmpInfo[12] == 0:
            cur.execute("update user set firstVisit = {} where idNo = {}".format(informationDict['visit0'], tmpId))
    conn.commit()
    cur.close()
    conn.close()
    return tmpId
    pass

def databaseUpdateFami(idNo):
    conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    cur.execute("select * from user where idNo = {}".format(idNo))
    conn.commit()
    tmpInfo = cur.fetchone()
    tmpInfo = list(tmpInfo)
    cur.close()
    conn.close()
    for i in range(0,5):
        for j in range(0,10):
            if (tmpInfo[36 + i] == tmpInfo[16 + j])and(tmpInfo[36 + i] != 0):
                conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
                cur = conn.cursor()
                cur.execute("update user set famiPeopleCnt" + str(j) + " = {} where idNo = {}".format(tmpInfo[41 + i] + tmpInfo[26 + j], idNo))
                tmpInfo[26 + j] += tmpInfo[41 + i]
                cur.execute("update user set tempFamiPeople" + str(i) + " = {} where idNo = {}".format(0, idNo))
                tmpInfo[36 + i] = 0
                cur.execute("update user set tempFamiPeopleCnt" + str(i) + " = {} where idNo = {}".format(0, idNo))
                tmpInfo[41 + i] = 0
                conn.commit()
                cur.close()
                conn.close()
                break
    conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    cur.execute("select * from user where idNo = {}".format(idNo))
    conn.commit()
    tmpInfo = cur.fetchone()
    tmpInfo = list(tmpInfo)
    cur.close()
    conn.close()
    for i in range(0,5):
        for j in range(0,10):
            if(tmpInfo[41 + i] >= tmpInfo[26 + j])and(tmpInfo[41 + i] != 0):
                conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
                cur = conn.cursor()
                for k in range(-8,1-j):
                    cur.execute("update user set famiPeople" + str(1-k) + " = {} where idNo = {}".format(tmpInfo[16 - k], idNo))
                    tmpInfo[17 - k] = tmpInfo[16 - k]
                    cur.execute("update user set famiPeopleCnt" + str(1-k) + " = {} where idNo = {}".format(tmpInfo[26 - k], idNo))
                    tmpInfo[27 - k] = tmpInfo[26 - k]
                cur.execute("update user set famiPeople" + str(j) + " = {} where idNo = {}".format(tmpInfo[36 + i], idNo))
                tmpInfo[16 + j] = tmpInfo[36 + i]
                cur.execute("update user set famiPeopleCnt" + str(j) + " = {} where idNo = {}".format(tmpInfo[41 + i], idNo))
                tmpInfo[26 + j] = tmpInfo[41 + i]
                cur.execute("update user set tempFamiPeople" + str(i) + " = {} where idNo = {}".format(0, idNo))
                tmpInfo[36 + i] = 0
                cur.execute("update user set tempFamiPeopleCnt" + str(i) + " = {} where idNo = {}".format(0, idNo))
                tmpInfo[41 + i] = 0
                conn.commit()
                cur.close()
                conn.close()
                break
    conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    cur.execute("select * from user where idNo = {}".format(idNo))
    tmpInfo = cur.fetchone()
    tmpInfo = list(tmpInfo)
    for i in range(0,10):
        for j in range(0,i):
            if tmpInfo[26 + j] < tmpInfo[26 + i]:
                tmpInfo[16 + i], tmpInfo[16 + j] = tmpInfo[16 + j], tmpInfo[16 + i]
                tmpInfo[26 + i], tmpInfo[26 + j] = tmpInfo[26 + j], tmpInfo[26 + i]
    for i in range(0,10):
        cur.execute("update user set famiPeople" + str(i) + " = {} where idNo = {}".format(tmpInfo[16 + i], idNo))
        cur.execute("update user set famiPeopleCnt" + str(i) + " = {} where idNo = {}".format(tmpInfo[26 + i], idNo))
    conn.commit()
    cur.close()
    conn.close()
    pass

def databaseAppPhoto(tempList):
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='666666', db='DemoSystemDatabase',
                           charset='utf8')
    cur = conn.cursor()
    idNo = []
    infoIn = False
    if tempList['valid']:
        for i in tempList['data']:
            for dt in i:
                informationDict = dict()
                informationDict = fillInfo(informationDict)
                informationDict['feature'] = dt
                infoFetch = databaseSearch(dt)
                if 'name' in infoFetch:
                    if infoFetch['name'] != 0 and infoFetch['name'] != '':
                        infoIn = True
                        break
                        #idNo.append(databaseRenew(informationDict))
        if infoIn == False:
            return None
        else:
            for i in tempList['data']:
                for dt in i:
                    informationDict = dict()
                    informationDict = fillInfo(informationDict)
                    informationDict['feature'] = dt
                    idNo.append(databaseRenew(informationDict))
            length = len(idNo)
            if length < 2:
                return None
            for i in range(0, length):
                pt = 0
                cur.execute("select * from user where idNo = {}".format(idNo[i]))
                tmpInfo = cur.fetchone()
                for j in range(-4, 1):
                    if tmpInfo[36 - j] != 0:
                        pt = 1 - j
                        break
                for j in range(1 - i, 1):
                    if idNo[-j] == idNo[i]:
                        continue
                    flag = 1
                    cur.execute("select * from user where idNo = {}".format(idNo[i]))
                    tmpInfo = cur.fetchone()
                    for k in range(0, pt):
                        if tmpInfo[36 + k] == idNo[-j]:
                            cur.execute("update user set tempFamiPeopleCnt" + str(k) + " = {} where idNo = {}".format(
                                tmpInfo[41 + k] + 1, idNo[i]))
                            flag = 0
                            break
                    if flag and pt < 5:
                        cur.execute(
                            "update user set tempFamiPeople" + str(pt) + " = {} where idNo = {}".format(idNo[-j], idNo[i]))
                        cur.execute(
                            "update user set tempFamiPeopleCnt" + str(pt) + " = {} where idNo = {}".format(1, idNo[i]))
                        pt += 1
                for j in range(i + 1, length):
                    if idNo[j] == idNo[i]:
                        continue
                    flag = 1
                    cur.execute("select * from user where idNo = {}".format(idNo[i]))
                    tmpInfo = cur.fetchone()
                    for k in range(0, pt):
                        if tmpInfo[36 + k] == idNo[j]:
                            cur.execute("update user set tempFamiPeopleCnt" + str(k) + " = {} where idNo = {}".format(
                                tmpInfo[41 + k] + 1, idNo[i]))
                            flag = 0
                            break
                    if flag and pt < 5:
                        cur.execute(
                            "update user set tempFamiPeople" + str(pt) + " = {} where idNo = {}".format(idNo[j], idNo[i]))
                        cur.execute(
                            "update user set tempFamiPeopleCnt" + str(pt) + " = {} where idNo = {}".format(1, idNo[i]))
                        pt += 1
            conn.commit()
        conn.commit()
    conn.commit()
    cur.close()
    conn.close()
    for i in idNo:
        databaseUpdateFami(i)
    pass

def databaseAppend(tempList):
    deltaTime = 10
    conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    idNo = []
    if tempList['valid']:
        for i in tempList['data']:
            #######
            ftTemp = databaseSearch(i['feature'])
            if 'feature' in ftTemp:
                if 'img_path' in ftTemp and ftTemp['img_path'] != '':
                    if os.path.isfile(ftTemp['img_path']) and ftTemp['img_path']!=i['img_path'] and ftTemp['feature']!=i['feature']:
                        dealWithImg(ftTemp)
            if 'feature' in ftTemp:
                if numpy.max(ftTemp['feature'])>0.0001 or numpy.min(ftTemp['feature'])<-0.001:
                    i['feature'] = i['feature']*0.2+ftTemp['feature']*0.8
                    i['feature'] = numpy.divide(i['feature'], numpy.sqrt(numpy.dot(i['feature'], i['feature'].T)))
            informationDict = dict()
            informationDict = fillInfo(informationDict)
            informationDict['feature'] = i['feature']
            if 'name' in i.keys() and i['name'] is not '':
                informationDict['name'] = i['name']
            if 'time' in i.keys():
                informationDict['visit0'] = i['time']
            if 'tel' in i.keys():
                informationDict['tel'] = i['tel']
            if 'address' in i.keys():
                informationDict['address'] = i['address']
            if 'email' in i.keys():
                informationDict['email'] = i['email']
            if 'fax' in i.keys():
                informationDict['fax'] = i['fax']
            if 'url' in i.keys():
                informationDict['url'] = i['url']
            if 'img_path' in i.keys():
                informationDict['img_path'] = i['img_path']
            idNo.append(databaseRenew(informationDict))
    length = len(idNo)
    for i in range(0,length):
        pt = 0
        cur.execute("select * from user where idNo = {}".format(idNo[i]))
        tmpInfo = cur.fetchone()
        for j in range(-4,1):
            if tmpInfo[36 - j] != 0:
                pt = 1 - j
                break
        for j in range(1-i,1):
            if idNo[-j] == idNo[i]:
                continue
            if timeDist(tempList['data'][i]['time'],tempList['data'][-j]['time']) <= deltaTime:
                flag = 1
                cur.execute("select * from user where idNo = {}".format(idNo[i]))
                tmpInfo = cur.fetchone()
                for k in range(0,pt):
                    if tmpInfo[36 + k] == idNo[-j]:
                        cur.execute("update user set tempFamiPeopleCnt" + str(k) + " = {} where idNo = {}".format(tmpInfo[41 + k] + 1, idNo[i]))
                        flag = 0
                        break
                if flag and pt < 5:
                    cur.execute("update user set tempFamiPeople" + str(pt) + " = {} where idNo = {}".format(idNo[-j], idNo[i]))
                    cur.execute("update user set tempFamiPeopleCnt" + str(pt) + " = {} where idNo = {}".format(1, idNo[i]))
                    pt += 1
            else:
                break
        for j in range(i+1,length):
            if idNo[j] == idNo[i]:
                continue
            if timeDist(tempList['data'][i]['time'],tempList['data'][j]['time']) <= deltaTime:
                flag = 1
                cur.execute("select * from user where idNo = {}".format(idNo[i]))
                tmpInfo = cur.fetchone()
                for k in range(0,pt):
                    if tmpInfo[36 + k] == idNo[j]:
                        cur.execute("update user set tempFamiPeopleCnt" + str(k) + " = {} where idNo = {}".format(tmpInfo[41 + k] + 1, idNo[i]))
                        flag = 0
                        break
                if flag and pt < 5:
                    cur.execute("update user set tempFamiPeople" + str(pt) + " = {} where idNo = {}".format(idNo[j], idNo[i]))
                    cur.execute("update user set tempFamiPeopleCnt" + str(pt) + " = {} where idNo = {}".format(1, idNo[i]))
                    pt += 1
            else:
                break
    conn.commit()
    cur.close()
    conn.close()
    for i in idNo:
        databaseUpdateFami(i)
    pass

def databaseQuery(idNo):
    conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    informationDict = dict()
    if idNo == 0:
        return informationDict
    informationDict = fillInfo(informationDict)
    cur.execute("select * from user where idNo = {}".format(idNo))
    tmpInfo = cur.fetchone()
    informationDict['img_path'] = tmpInfo[4]
    informationDict['name'] = tmpInfo[5]
    informationDict['address'] = tmpInfo[6]
    informationDict['tel'] = tmpInfo[7]
    informationDict['fax'] = tmpInfo[8]
    informationDict['email'] = tmpInfo[9]
    #informationDict['academic'] = tmpInfo[10]
    informationDict['url'] = tmpInfo[11]
    #informationDict['firstVisit'] = tmpInfo[12]
    #informationDict['visit0'] = tmpInfo[13]
    #informationDict['visit1'] = tmpInfo[14]
    #informationDict['visit2'] = tmpInfo[15]
    conn.commit()
    cur.close()
    conn.close()
    return informationDict
    pass

def databaseQueryFeature(idNo):
    conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    informationDict = dict()
    if idNo == 0:
        return informationDict
    informationDict = fillInfo(informationDict)
    cur.execute("select * from user where idNo = {}".format(idNo))
    tmpInfo = cur.fetchone()
    informationDict['img_path'] = tmpInfo[4]
    informationDict['name'] = tmpInfo[5]
    informationDict['address'] = tmpInfo[6]
    informationDict['tel'] = tmpInfo[7]
    informationDict['fax'] = tmpInfo[8]
    informationDict['email'] = tmpInfo[9]
    #informationDict['academic'] = tmpInfo[10]
    informationDict['url'] = tmpInfo[11]
    tmpFeature = []
    cur.execute("select * from feature" + str(idNo))
    for i in range(0,512):
        tmpInfo = cur.fetchone()
        tmpFeature.append(tmpInfo[1])
    informationDict['feature'] = tmpFeature
    conn.commit()
    cur.close()
    conn.close()
    return informationDict
    pass

def databaseSearch(feature):
    conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    informationDict = dict()
    informationDict = fillInfo(informationDict)
    commonList = databaseFind(feature)
    tmpId = 0
    global srchTrans
    tempTrans = srchTrans
    for i in commonList:
        cur.execute("select * from feature" + str(i))
        tmpFeature = []
        for j in range(0,512):
            tmp = cur.fetchone()
            tmpFeature.append(tmp[1])
        tmpFeature = numpy.array(tmpFeature)
        trans = featureTransvection(feature, tmpFeature)
        if trans > tempTrans:
            tempTrans = trans
            tmpId = i
    if tmpId == 0:
        return informationDict
    cur.execute("select * from user where idNo = {}".format(tmpId))
    tmpInfo = cur.fetchone()
    informationDict['img_path'] = tmpInfo[4]
    informationDict['name'] = tmpInfo[5]
    informationDict['address'] = tmpInfo[6]
    informationDict['tel'] = tmpInfo[7]
    informationDict['fax'] = tmpInfo[8]
    informationDict['email'] = tmpInfo[9]
    #informationDict['academic'] = tmpInfo[10]
    informationDict['url'] = tmpInfo[11]
    informationDict['firstVisit'] = tmpInfo[12]
    informationDict['visit0'] = tmpInfo[13]
    informationDict['visit1'] = tmpInfo[14]
    informationDict['visit2'] = tmpInfo[15]
    informationDict['famiPeople0'] = databaseQuery(tmpInfo[16])
    informationDict['famiPeople1'] = databaseQuery(tmpInfo[17])
    informationDict['famiPeople2'] = databaseQuery(tmpInfo[18])
    informationDict['famiPeople3'] = databaseQuery(tmpInfo[19])
    informationDict['famiPeople4'] = databaseQuery(tmpInfo[20])
    informationDict['famiPeople5'] = databaseQuery(tmpInfo[21])
    informationDict['famiPeople6'] = databaseQuery(tmpInfo[22])
    informationDict['famiPeople7'] = databaseQuery(tmpInfo[23])
    informationDict['famiPeople8'] = databaseQuery(tmpInfo[24])
    informationDict['famiPeople9'] = databaseQuery(tmpInfo[25])
    conn.commit()
    cur.close()
    conn.close()
    return informationDict
    pass

def databaseRebuild():
    global databaseRebuilding
    databaseRebuilding = 1
    conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    infoDictList = []
    visitList = []
    flagList = []
    cnt = cur.execute("select * from user")
    for i in range(0,cnt):
        cur.execute("select * from user where idNo = {}".format(i+1))
        tmpInfo = cur.fetchone()
        informationDict = dict()
        informationDict = fillInfo(informationDict)
        informationDict['img_path'] = tmpInfo[4]
        informationDict['name'] = tmpInfo[5]
        informationDict['address'] = tmpInfo[6]
        informationDict['tel'] = tmpInfo[7]
        informationDict['fax'] = tmpInfo[8]
        informationDict['email'] = tmpInfo[9]
        informationDict['academic'] = tmpInfo[10]
        informationDict['url'] = tmpInfo[11]
        informationDict['firstVisit'] = tmpInfo[12]
        informationDict['visit0'] = tmpInfo[13]
        informationDict['visit1'] = tmpInfo[14]
        informationDict['visit2'] = tmpInfo[15]
        informationDict['famiPeople0'] = tmpInfo[16]
        informationDict['famiPeople1'] = tmpInfo[17]
        informationDict['famiPeople2'] = tmpInfo[18]
        informationDict['famiPeople3'] = tmpInfo[19]
        informationDict['famiPeople4'] = tmpInfo[20]
        informationDict['famiPeople5'] = tmpInfo[21]
        informationDict['famiPeople6'] = tmpInfo[22]
        informationDict['famiPeople7'] = tmpInfo[23]
        informationDict['famiPeople8'] = tmpInfo[24]
        informationDict['famiPeople9'] = tmpInfo[25]
        informationDict['famiPeopleCnt0'] = tmpInfo[26]
        informationDict['famiPeopleCnt1'] = tmpInfo[27]
        informationDict['famiPeopleCnt2'] = tmpInfo[28]
        informationDict['famiPeopleCnt3'] = tmpInfo[29]
        informationDict['famiPeopleCnt4'] = tmpInfo[30]
        informationDict['famiPeopleCnt5'] = tmpInfo[31]
        informationDict['famiPeopleCnt6'] = tmpInfo[32]
        informationDict['famiPeopleCnt7'] = tmpInfo[33]
        informationDict['famiPeopleCnt8'] = tmpInfo[34]
        informationDict['famiPeopleCnt9'] = tmpInfo[35]
        informationDict['tempFamiPeople0'] = tmpInfo[36]
        informationDict['tempFamiPeople1'] = tmpInfo[37]
        informationDict['tempFamiPeople2'] = tmpInfo[38]
        informationDict['tempFamiPeople3'] = tmpInfo[39]
        informationDict['tempFamiPeople4'] = tmpInfo[40]
        informationDict['tempFamiPeopleCnt0'] = tmpInfo[41]
        informationDict['tempFamiPeopleCnt1'] = tmpInfo[42]
        informationDict['tempFamiPeopleCnt2'] = tmpInfo[43]
        informationDict['tempFamiPeopleCnt3'] = tmpInfo[44]
        informationDict['tempFamiPeopleCnt4'] = tmpInfo[45]
        tmpFeature = []
        cur.execute("select * from feature" + str(tmpInfo[0]))
        for j in range(0,512):
            tmpFeaInfo = cur.fetchone()
            tmpFeature.append(tmpFeaInfo[1])
        informationDict['feature'] = tmpFeature
        infoDictList.append(informationDict)
        visitList.append(tmpInfo[13])
        flagList.append(1)
        global tmpTrans
        transLim = tmpTrans
        for j in range(0,i):
            if (flagList[j] == 1)and(featureTransvection(infoDictList[i]['feature'],infoDictList[j]['feature']) > transLim):
                flagList[i] = 0
                infoDictList[j] = unionInfo(infoDictList[i],infoDictList[j])
        cur.execute("drop table feature" + str(tmpInfo[0]))
        conn.commit()
    conn.commit()
    cur.close()
    conn.close()
    for i in range(0,cnt):
        if flagList[i] * visitList[i] == 0:
            visitList[i] = 99999999999999
    for i in range(0,cnt):
        for j in range(0,i):
            if visitList[i] < visitList[j]:
                visitList[i], visitList[j] = visitList[j], visitList[i]
    timeLim = visitList[int(cnt * 0.5)]
    #timeLim = visitList[num]
    databaseInit()
    for i in range(0,min(int(cnt),400)):                         #here to judge the number in the database
        if infoDictList[i]['visit0'] <= timeLim:
            databaseInsert(infoDictList[i])
    global databaseRebuilding
    databaseRebuilding = 0
    pass


def databaseTest():
    tempList = dict()
    tempList['valid'] = 1
    tempList['data'] = []
    time = 20170726091500
    for i in range(0,50):
        if (i > 0) and (random.randint(0,1) == 0):
            tmpIdNo = random.randint(0,i-1)
            info = dict()
            info['feature'] = tempList['data'][tmpIdNo]['feature']
            time += random.randint(1,10)
            if time % 100 >= 60:
                time += 40
            info['time'] = time
            tempList['data'].append(info)
            continue
        a = []
        s = 0
        for j in range(0,512):
            a.append(random.uniform(-1,1))
            s += a[j] * a[j]
        s = s ** 0.5
        for j in range(0,512):
            a[j] /= s
        info = dict()
        info['feature'] = numpy.array(a)
        time += random.randint(1,10)
        if time % 100 >= 60:
            time += 40
        info['time'] = time
        tempList['data'].append(info)
    databaseAppend(tempList)
    pass

def DatabaseBase():
    global databaseRebuilding
    databaseRebuilding = 0
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
    #tmpList = spider.Spider(caffemodel)
    #tmpList = []
    #
    #initial_url = 'http://www.cs.tsinghua.edu.cn'
    #tmpList = spider3.SpiderRenewer1(initial_url,caffemodel)
    global tmpTrans
    tmpTrans = 0.55
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='666666', db='DemoSystemDatabase', charset='utf8')
    cur = conn.cursor()
    cur.execute('show tables')
    tablerows=cur.fetchall()
    conn.commit()
    if ('user',) not in tablerows:
        databaseInit()
        tmpList = spider.Spider(caffemodel)
        for i in tmpList:
            if ('academic' in i.keys()) and (type(i['academic']) is list):
                tmpStr = ''
                for j in i['academic']:
                    tmpStr += j + '$'
                i['academic'] = tmpStr
            if 'feature' in i.keys():
                databaseRenew(i)
        conn.commit()
        #for ispace in inSamePht.spiderFull(caffemodel):
        #    databaseAppPhoto(ispace)
    conn.commit()
    #

    #for ispace in inSamePht.spiderFull(caffemodel):
    #    databaseAppPhoto(ispace)
    while True:
        keyTime = int(time.strftime("%Y%m%d%H%M%S", time.localtime())) % 1000000
        if keyTime < 10000 and keyTime>3000:
            databaseRebuild()
            cnt = cur.execute("select * from user")
            conn.commit()
            #if cnt >= 50:
            #    conn.commit()
            #    databaseRebuild(cnt)
            #    continue
            #    pass

            if cnt == 0 or cnt == 1:
                time.sleep(2)
            for i in range(0,cnt):
                tmpInfo = cur.fetchone()
                informationDict = databaseQueryFeature(tmpInfo[0])
                flag = 0
                numa = 0
                if informationDict['name'] == '':
                    [numa,informationDict] = spider2.SpiderRenewer(informationDict, caffemodel)
                    flag = 1
                else:
                    '''if informationDict['address'] == '':
                        informationDict = spider2.SpiderRenewer1(informationDict, caffemodel)
                        flag = 1
                    if informationDict['tel'] == '':
                        informationDict = spider2.SpiderRenewer1(informationDict, caffemodel)
                        flag = 1
                    if informationDict['fax'] == '':
                        informationDict = spider2.SpiderRenewer1(informationDict, caffemodel)
                        flag = 1
                    if informationDict['email'] == '':
                        informationDict = spider2.SpiderRenewer1(informationDict, caffemodel)
                        flag = 1
                    if informationDict['academic'] == '':
                        informationDict = spider2.SpiderRenewer1(informationDict, caffemodel)
                        flag = 1
                    if informationDict['url'] == '':
                        informationDict = spider2.SpiderRenewer1(informationDict, caffemodel)
                        flag = 1'''
                    pass
                if flag == 1:
                    if numa == 0:
                        databaseRenew(informationDict)
                    else:
                        for i in informationDict:
                            if ('academic' in i.keys()) and (type(i['academic']) is list):
                                tmpStr = ''
                                for j in i['academic']:
                                    tmpStr += j + '$'
                                i['academic'] = tmpStr
                            if 'feature' in i.keys():
                                databaseRenew(i)
                    conn.commit()
                conn.commit()
                flag = 0
        time.sleep(1800)
        pass
    conn.commit()
    cur.close()
    conn.close()

if __name__=="__main__":
    DatabaseBase()