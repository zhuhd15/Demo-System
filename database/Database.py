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
        if len(ans) < 5:
            ans.append(i)
            dist.append(tmpDist)
            for j in range(0,len(ans) - 1):
                for k in range(j+1,len(ans)):
                    if dist[j] > dist[k]:
                        ans[j], ans[k] = ans[k], ans[j]
                        dist[j], dist[k] = dist[k], dist[j]
        else:
            for j in range(0,5):
                if tmpDist < dist[j]:
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
            if (featureDist(feature, tmpFeature) < dist[len(dist) - 1]) or (tmpDist < dist[len(dist) - 1]):
                que.append(tmpInfo[1])
        if (tmpInfo[2] != 0 and not(tmpInfo[2] in que)):
            cur.execute("select * from feature" + str(tmpInfo[2]))
            tmpFeature = []
            for j in range(0,512):
                tmp = cur.fetchone()
                tmpFeature.append(tmp[1])
            tmpFeature = numpy.array(tmpFeature)
            if (featureDist(feature, tmpFeature) < dist[len(dist) - 1]) or (tmpDist < dist[len(dist) - 1]):
                que.append(tmpInfo[2])
    tmpList = []
    for i in range(1,n + 1):
        cur.execute("select * from feature" + str(i))
        tmpFeature = []
        for j in range(0,512):
            tmp = cur.fetchone()
            tmpFeature.append(tmp[1])
        tmpFeature = numpy.array(tmpFeature)
        tmpList.append(featureDist(feature, tmpFeature))
    tmpList.sort()
    for i in range(0,10):
        print(tmpList[i])
    print(ans)
    print(dist)
    print(len(que))
    print(que)
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
    infoCnt = cur.execute("select * from user")
    info = cur.fetchmany(infoCnt)
    for i in info:
        if (i[2] == None) or (i[3] == None):
            cur.execute("select * from feature" + str(i[0]))
            feature = []
            for j in range(0,512):
                tmp = cur.fetchone()
                feature.append(tmp[1])
            feature = numpy.array(feature)
            informationDict = dict()
            informationDict['name'] = [i[2]]
            informationDict['pageAdd'] = [i[3]]
            informationDict['feature'] = [feature]
            return informationDict
    conn.commit()
    cur.close()
    conn.close()
    pass

if __name__=="__main__":
    n = 100
    databaseInit()
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'Demo-SystemAdmin', passwd = '666666', db = 'Demo-SystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    s = []
    for k in range(0,n):
        a = []
        length = 0
        for i in range(0,512):
            a.append(random.uniform(-1,1))
            length += a[i]*a[i]
        length = length ** 0.5
        for i in range(0,512):
            a[i] /= length
        a = numpy.array(a)
        s.append(a)
        info = dict()
        info['name'] = 'HaHaTa' + str(k)
        info['firstVisit'] = 20170719101600 + random.randint(0,60)
        info['feature'] = a
        databaseInsert(info)
        print("feature" + str(k+1) + " inserted!")
    a = s[0]
    databaseFind(a)
    conn.commit()
    cur.close()
    conn.close()
