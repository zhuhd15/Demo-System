import MySQLdb
import numpy
import random
root = 0

def fillInfo(informationDict):
    if (not 'leftson' in informationDict.keys()):
        informationDict['leftson'] = 0
    if (not 'rightson' in informationDict.keys()):
        informationDict['rightson'] = 0
    if (not 'depth' in informationDict.keys()):
        informationDict['depth'] = 0
    if (not 'photoAdd' in informationDict.keys()):
        informationDict['photoAdd'] = ''
    if (not 'name' in informationDict.keys()):
        informationDict['name'] = ''
    if (not 'pageAdd' in informationDict.keys()):
        informationDict['pageAdd'] = ''
    if (not 'firstVisit' in informationDict.keys()):
        informationDict['firstVisit'] = 0
    for i in range(0,3):
        if (not ('visit' + str(i)) in informationDict.keys()):
            informationDict['visit' + str(i)] = 0
    for i in range(0,10):
        if (not ('famiPeople' + str(i)) in informationDict.keys()):
            informationDict['famiPeople' + str(i)] = 0
    for i in range(0,5):
        if (not ('tempFamiPeople' + str(i)) in informationDict.keys()):
            informationDict['tempFamiPeople' + str(i)] = 0
    return informationDict
    pass

def featureDist(feature0 ,feature1):
    dist = 0
    for i in range(0,512):
        dist += ((feature0[i] - feature1[i])** 2)
    dist = dist ** 0.5
    return dist
    pass

def featureTransvection(feature0 ,feature1):
    trans = 0
    for i in range(0,512):
        trans += feature0[i] * feature1[i]
    return trans
    pass

def databaseInit():
    #database init
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'Demo-SystemAdmin', passwd = '666666', db = 'Demo-SystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    cur.execute("""
    create table if not exists user
    (
        idNo smallint not null primary key auto_increment,
        leftson smallint,
        rightson smallint,
        depth smallint,
        photoAdd varchar(200) not null,
        name varchar(20),
        pageAdd varchar(200),
        firstVisit bigint not null,
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
        tempFamiPeople0 smallint,
        tempFamiPeople1 smallint,
        tempFamiPeople2 smallint,
        tempFamiPeople3 smallint,
        tempFamiPeople4 smallint
    )auto_increment = 1;
    """)
    conn.commit()
    cur.close()
    conn.close()
    pass

def databaseInsert(informationDict):
    '''
    insert a point into the K-dimensional Tree
    informationDict:feature is not null
    return:None
    '''
    informationDict = fillInfo(informationDict)
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'Demo-SystemAdmin', passwd = '666666', db = 'Demo-SystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    global root
    pt = root
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
    infoCnt = cur.execute("select * from user")
    infoCnt = infoCnt + 1
    if (root == 0):
        root = infoCnt
    if (sonTag != -1):
        if (sonTag == 1):
            cur.execute("update user set leftson = {} where idNo = {}".format(infoCnt, tmpId))
        else:
            cur.execute("update user set rightson = {} where idNo = {}".format(infoCnt, tmpId))
    informationDict['depth'] = dep + 1
    cur.execute("""
    insert into user(
        leftson,
        rightson,
        depth,
        photoAdd,
        name,
        pageAdd,
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
        tempFamiPeople0,
        tempFamiPeople1,
        tempFamiPeople2,
        tempFamiPeople3,
        tempFamiPeople4)
        values({}, {}, {}, '{}', '{}', '{}', {}, {} ,{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {});
    """.format(informationDict['leftson'],
               informationDict['rightson'],
               informationDict['depth'],
               informationDict['photoAdd'],
               informationDict['name'],
               informationDict['pageAdd'],
               informationDict['firstVisit'],
               informationDict['visit0'],
               informationDict['visit1'],
               informationDict['visit2'],
               informationDict['famiPeople0'],
               informationDict['famiPeople1'],
               informationDict['famiPeople2'],
               informationDict['famiPeople3'],
               informationDict['famiPeople4'],
               informationDict['famiPeople5'],
               informationDict['famiPeople6'],
               informationDict['famiPeople7'],
               informationDict['famiPeople8'],
               informationDict['famiPeople9'],
               informationDict['tempFamiPeople0'],
               informationDict['tempFamiPeople1'],
               informationDict['tempFamiPeople2'],
               informationDict['tempFamiPeople3'],
               informationDict['tempFamiPeople4']))
    cur.execute("create table if not exists feature" + str(infoCnt) +
    """(
        dim int not null primary key auto_increment,
        value float not null
    )auto_increment = 0;
    """)
    for i in range(0,512):
        cur.execute("insert into feature" + str(infoCnt) + "(value)VALUES({})".format(informationDict['feature'][i]))
    conn.commit()
    cur.close()
    conn.close()
    pass

def databaseFind(feature):
    '''
    feature(the normalized eigenvalue):numpy.ndarray
    find the nearest point to the feature on the K-dimensional Tree
    return:[{feature}, {}, {}, {}, {}]
    '''
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'Demo-SystemAdmin', passwd = '666666', db = 'Demo-SystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    global root
    pt = root
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
        if (tmpDist < 0.95):
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
                    if (tmpDist < dist[j]) and (tmpDist < 0.95):
                        for k in range(-3,-j+1):
                            ans[-k+1] = ans[-k]
                            dist[-k+1] = dist[-k]
                        ans[j] = i
                        dist[j] = tmpDist
                        break
        tmpDist = ((feature[tmpInfo[3]] - tmpDimFeature) ** 2)** 0.5
        if (tmpInfo[1] != 0 and not(tmpInfo[1] in que)):
            cur.execute("select * from feature" + str(tmpInfo[1]))
            tmpFeature = []
            for j in range(0,512):
                tmp = cur.fetchone()
                tmpFeature.append(tmp[1])
            tmpFeature = numpy.array(tmpFeature)
            if (len(dist) != 0) and ((featureDist(feature, tmpFeature) < dist[len(dist) - 1]) or (tmpDist < dist[len(dist) - 1])):
                que.append(tmpInfo[1])
        if (tmpInfo[2] != 0 and not(tmpInfo[2] in que)):
            cur.execute("select * from feature" + str(tmpInfo[2]))
            tmpFeature = []
            for j in range(0,512):
                tmp = cur.fetchone()
                tmpFeature.append(tmp[1])
            tmpFeature = numpy.array(tmpFeature)
            if (len(dist) != 0) and ((featureDist(feature, tmpFeature) < dist[len(dist) - 1]) or (tmpDist < dist[len(dist) - 1])):
                que.append(tmpInfo[2])
    return ans
    conn.commit()
    cur.close()
    conn.close()
    pass

def databaseRenew(informationDict):
    '''
    renew the information in the database.
    informationDict{(the renewed information needs to be wrote in the database), 'feature':[ Normalized Eigenvalue ]}
    return:None
    '''
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'Demo-SystemAdmin', passwd = '666666', db = 'Demo-SystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    commonList = databaseFind(informationDict['feature'])
    tmpId = 0
    tmpTrans = 0.55
    for i in commonList
        cur.execute("select * from feature" + str(i))
        tmpFeature = []
        for j in range(0,512):
            tmp = cur.fetchone()
            tmpFeature.append(tmp[1])
        tmpFeature = numpy.array(tmpFeature)
        trans = featureTransvection(informationDict['feature'], tmpFeature)
        if trans < tmpTrans:
            tmpTrans = trans
            tmpId = i
    if tmpId == 0:
        return
    cur.execute("update user set photoAdd = {} where idNo = {}".format(informationDict['photoAdd'], tmpId))
    cur.execute("update user set name = {} where idNo = {}".format(informationDict['name'], tmpId))
    cur.execute("update user set pageAdd = {} where idNo = {}".format(informationDict['pageAdd'], tmpId))
    conn.commit()
    cur.close()
    conn.close()
    pass

def databaseAppend(tempList):
    '''
    send the temporary list to the database once an hour.
    tempList{'Valid':True/False, 'data':[ {} {} … ]}
    list{'time':20170101170506, 'feature':[ Normalized Eigenvalue ]}
    return:None
    '''
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'Demo-SystemAdmin', passwd = '666666', db = 'Demo-SystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    conn.commit()
    cur.close()
    conn.close()
    pass

def databaseSearch(feature):
    '''
    search for information about the feature when the system gives a request.
    feature(the normalized eigenvalue):numpy.ndarray
    return:{'name':<str>, 'famiPeople':[{'name':<str>, 'photoAdd':<str>},{},{}], 'recentVisit':[int,int,int], 'firstVisit':int, 'pageAdd':<str>, 'photoAdd':<str>}
    if there's nothing about the feature, then try a null dict.
    '''
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'Demo-SystemAdmin', passwd = '666666', db = 'Demo-SystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    informationDict = dict()
    informationDict = fillInfo(informationDict)
    commonList = databaseFind(feature)
    tmpId = 0
    tmpTrans = 0.55
    for i in commonList
        cur.execute("select * from feature" + str(i))
        tmpFeature = []
        for j in range(0,512):
            tmp = cur.fetchone()
            tmpFeature.append(tmp[1])
        tmpFeature = numpy.array(tmpFeature)
        trans = featureTransvection(informationDict['feature'], tmpFeature)
        if trans < tmpTrans:
            tmpTrans = trans
            tmpId = i
    if tmpId == 0:
        return informationDict
    cur.execute("select * from user where idNo = {}".format(tmpId))
    tmpInfo = cur.fetchone()
    informationDict['photoAdd'] = tmpInfo[4]
    informationDict['name'] = tmpInfo[5]
    informationDict['pageAdd'] = tmpInfo[6]
    informationDict['firstVisit'] = tmpInfo[7]
    informationDict['visit0'] = tmpInfo[8]
    informationDict['visit1'] = tmpInfo[9]
    informationDict['visit2'] = tmpInfo[10]
    informationDict['famiPeople0'] = tmpInfo[11]
    informationDict['famiPeople1'] = tmpInfo[12]
    informationDict['famiPeople2'] = tmpInfo[13]
    informationDict['famiPeople3'] = tmpInfo[14]
    informationDict['famiPeople4'] = tmpInfo[15]
    informationDict['famiPeople5'] = tmpInfo[16]
    informationDict['famiPeople6'] = tmpInfo[17]
    informationDict['famiPeople7'] = tmpInfo[18]
    informationDict['famiPeople8'] = tmpInfo[19]
    informationDict['famiPeople9'] = tmpInfo[20]
    informationDict['tempFamiPeople0'] = tmpInfo[21]
    informationDict['tempFamiPeople1'] = tmpInfo[22]
    informationDict['tempFamiPeople2'] = tmpInfo[23]
    informationDict['tempFamiPeople3'] = tmpInfo[24]
    informationDict['tempFamiPeople4'] = tmpInfo[25]
    return informationDict
    conn.commit()
    cur.close()
    conn.close()
    pass

def databaseRequest():
    '''
    provide a request for the crawler to find new information.
    return:informationDict{(the information needs to be renewed is null), 'feature':[ Normalized Eigenvalue ]}
    '''
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'Demo-SystemAdmin', passwd = '666666', db = 'Demo-SystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    conn.commit()
    cur.close()
    conn.close()
    pass

if __name__=="__main__":
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'Demo-SystemAdmin', passwd = '666666', db = 'Demo-SystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    databaseInit()
    conn.commit()
    cur.close()
    conn.close()
