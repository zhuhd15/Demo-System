import MySQLdb
import numpy
import random
import time
#import sys
#sys.path.append('/home/luka/PycharmProjects/Github/Demo-System')
#import spider,caffe
#import spider2

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
    '''
    database init
    set up table user
    '''
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    cur.execute("""
    create table if not exists user
    (
        idNo smallint not null primary key auto_increment,
        leftson smallint,
        rightson smallint,
        depth smallint,
        img_path varchar(2000) not null,
        name varchar(2000),
        address varchar(2000),
        tel varchar(2000),
        fax varchar(2000),
        email varchar(2000),
        academic varchar(2000),
        url varchar(2000),
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
    )auto_increment = 1 character set utf8;
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
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
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
        tempFamiPeople0,
        tempFamiPeople1,
        tempFamiPeople2,
        tempFamiPeople3,
        tempFamiPeople4)
        values({}, {}, {}, "{}", "{}", "{}", "{}", "{}", "{}", "{}", {}, {} ,{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {});
    """.format(informationDict['leftson'],
               informationDict['rightson'],
               informationDict['depth'],
               informationDict['img_path'],
               informationDict['name'],
               informationDict['address'],
               informationDict['tel'],
               informationDict['fax'],
               informationDict['email'],
               #informationDict['academic'],
               informationDict['url'],
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
        cur.execute("insert into feature" + str(infoCnt) + "(value)values({})".format(informationDict['feature'][i]))
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
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
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
    print(que)
    print(ans)
    print(dist)
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
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    informationDict = fillInfo(informationDict)
    commonList = databaseFind(informationDict['feature'])
    if len(commonList) == 0:
        information['firstVisit'] = information['visit0']
        databaseInsert(informationDict)
        return
    tmpId = 0
    tmpTrans = 0.55
    for i in commonList:
        cur.execute("select * from feature" + str(i))
        tmpFeature = []
        for j in range(0,512):
            tmp = cur.fetchone()
            tmpFeature.append(tmp[1])
        tmpFeature = numpy.array(tmpFeature)
        trans = featureTransvection(informationDict['feature'], tmpFeature)
        if trans > tmpTrans:
            tmpTrans = trans
            tmpId = i
    if tmpId == 0:
        return
    if informationDict['img_path'] != '':
        cur.execute("update user set img_path = {} where idNo = {}".format(informationDict['img_path'], tmpId))
    if informationDict['name'] != '':
        cur.execute("update user set name = {} where idNo = {}".format(informationDict['name'], tmpId))
    if informationDict['address'] != '':
        cur.execute("update user set address = {} where idNo = {}".format(informationDict['address'], tmpId))
    if informationDict['tel'] != '':
        cur.execute("update user set tel = {} where idNo = {}".format(informationDict['tel'], tmpId))
    if informationDict['fax'] != '':
        cur.execute("update user set fax = {} where idNo = {}".format(informationDict['fax'], tmpId))
    if informationDict['email'] != '':
        cur.execute("update user set email = {} where idNo = {}".format(informationDict['email'], tmpId))
    if informationDict['academic'] != '':
        cur.execute("update user set academic = {} where idNo = {}".format(informationDict['academic'], tmpId))
    if informationDict['url'] != '':
        cur.execute("update user set url = {} where idNo = {}".format(informationDict['url'], tmpId))
    if information['visit0'] != 0:
        cur.execute("select * from user where idNo = {}",tmpId)
        tmpInfo = cur.fetchonr()
        cur.execute("update user set visit2 = {} where idNo = {}".format(tmpInfo[14], tmpId))
        cur.execute("update user set visit1 = {} where idNo = {}".format(tmpInfo[13], tmpId))
        cur.execute("update user set visit0 = {} where idNo = {}".format(information['visit0'], tmpId))
        if tmpInfo[12] == 0:
            cur.execute("update user set firstVisit = {} where idNo = {}".format(information['visit0'], tmpId))
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
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    for i in tempList:
        informationDict = dict()
        informationDict = fillInfo(informationDict)
        informationDict['feature'] = i['feature']
        informationDict['visit0'] = i['time']
        databaseRenew(informationDict)
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
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
    cur = conn.cursor()
    informationDict = dict()
    informationDict = fillInfo(informationDict)
    commonList = databaseFind(feature)
    tmpId = 0
    tmpTrans = 0.55
    for i in commonList:
        cur.execute("select * from feature" + str(i))
        tmpFeature = []
        for j in range(0,512):
            tmp = cur.fetchone()
            tmpFeature.append(tmp[1])
        tmpFeature = numpy.array(tmpFeature)
        trans = featureTransvection(feature, tmpFeature)
        if trans > tmpTrans:
            tmpTrans = trans
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
    informationDict['tempFamiPeople0'] = tmpInfo[26]
    informationDict['tempFamiPeople1'] = tmpInfo[27]
    informationDict['tempFamiPeople2'] = tmpInfo[28]
    informationDict['tempFamiPeople3'] = tmpInfo[29]
    informationDict['tempFamiPeople4'] = tmpInfo[30]
    return informationDict
    conn.commit()
    cur.close()
    conn.close()
    pass

def DatabaseBase():
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
    tmpList = spider.Spider(caffemodel)

    conn = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='666666', db='DemoSystemDatabase', charset='utf8')
    cur = conn.cursor()
    databaseInit()
    for i in tmpList:
        if ('academic' in i.keys()) and (type(i['academic']) is list):
            tmpStr = ''
            for j in i['academic']:
                tmpStr += j + '$'
            i['academic'] = tmpStr
        if 'feature' in i.keys():
            databaseRenew(i)
    conn.commit()
    cur.close()
    conn.close()

if __name__=="__main__":
    DatabaseBase()
    '''conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '666666', db = 'DemoSystemDatabase', charset = 'utf8')
    cur = conn.cursor()'''
    '''information = {'name': "['张志军']", 'address': ['???'], 'email': "['电子邮箱：??']",
                   'feature': [6.73086708e-03, -2.94301827e-02, 1.45628629e-02,
                               1.83323175e-02, 3.12993526e-02, 3.68274823e-02,
                               -5.73405959e-02, -5.09380102e-02, -6.85696723e-03,
                               -9.19026136e-03, 3.61816883e-02, 3.98671068e-03,
                               1.93181429e-02, -2.10391805e-02, 3.68980132e-02,
                               -5.48064522e-03, -1.05138496e-02, -2.47119460e-02,
                               1.73759516e-02, -5.59557788e-02, 4.44681523e-03,
                               -7.41454735e-02, -2.63592824e-02, 6.80855736e-02,
                               -8.32661390e-02, 7.39095658e-02, 1.16308155e-02,
                               4.82669733e-02, 2.43654530e-02, 3.12886238e-02,
                               6.24769479e-02, -6.36307299e-02, 4.28298488e-02,
                               -2.79480647e-02, -6.89153820e-02, 3.87214050e-02,
                               4.06248271e-02, 5.34901917e-02, 1.12777829e-01,
                               4.76565445e-03, 1.20948674e-02, -1.10205598e-02,
                               -1.80388018e-02, 2.65284125e-02, -3.13562602e-02,
                               2.57509924e-03, 6.90454170e-02, 3.36628268e-03,
                               4.61370423e-02, 2.59142332e-02, 3.29599865e-02,
                               -4.05383073e-02, 1.35945082e-02, 2.32415553e-03,
                               -5.09171747e-02, 1.33676315e-02, -5.10375574e-03,
                               -3.17887478e-02, -3.08070630e-02, -1.23769911e-02,
                               -1.96930896e-02, 1.76682677e-02, 1.56885237e-02,
                               4.43000682e-02, 4.84952778e-02, 1.83967985e-02,
                               2.23374087e-02, 1.07381314e-01, 2.34353729e-03,
                               -3.97765404e-03, -3.58772799e-02, 4.52539092e-03,
                               6.05667643e-02, 3.65946926e-02, -4.14976142e-02,
                               3.98748741e-02, -9.65051576e-02, -4.54890653e-02,
                               -5.54353073e-02, 4.18050662e-02, 1.50044833e-03,
                               2.48108059e-02, -3.51064131e-02, 1.78025998e-02,
                               -4.06294614e-02, 5.36608929e-03, -1.24338202e-01,
                               1.92881785e-02, -6.42301217e-02, -1.03756767e-02,
                               -3.52392793e-02, -4.83942032e-02, 3.46364602e-02,
                               -2.51202751e-02, 1.67029053e-02, 1.94565356e-02,
                               -4.24611010e-02, -4.36482802e-02, 4.71577309e-02,
                               -1.97684355e-02, 4.81892079e-02, 2.52425745e-02,
                               1.93801913e-02, 5.00888377e-02, 4.96191867e-02,
                               -1.14566796e-02, -1.31107541e-02, -4.36267070e-02,
                               -3.62377241e-02, 8.15830231e-02, 2.26670001e-02,
                               -1.27674658e-02, 7.33955726e-02, -6.04191795e-03,
                               -7.73720592e-02, -6.21486194e-02, 3.99936028e-02,
                               3.23405489e-02, -2.81365365e-02, 1.79489180e-02,
                               2.50870106e-03, -1.15597798e-02, -3.14883627e-02,
                               -3.86883728e-02, 1.28462969e-03, -5.50674386e-02,
                               8.66154302e-03, 7.23376591e-03, 6.19910937e-03,
                               2.04048939e-02, 2.46340688e-02, -4.29610088e-02,
                               6.89437687e-02, -7.49863451e-03, 1.87198557e-02,
                               -5.68335224e-03, 4.79151495e-02, 7.28356615e-02,
                               -4.10671681e-02, -3.71318720e-02, -4.27427031e-02,
                               -7.38984048e-02, 7.30128139e-02, -3.80222052e-02,
                               -2.94176247e-02, 1.71365943e-02, 1.01640485e-02,
                               2.11970359e-02, -4.76328749e-03, -1.19259860e-02,
                               -2.15869676e-02, -5.80632761e-02, -3.83093916e-02,
                               2.00355370e-02, -3.70897017e-02, -3.86573859e-02,
                               -1.87054779e-02, -5.02685532e-02, 2.19346453e-02,
                               2.26766206e-02, 7.04408213e-02, -4.00829092e-02,
                               -6.79347068e-02, -1.08407266e-01, 1.11914771e-02,
                               3.54182795e-02, -4.66443552e-03, -2.55451035e-02,
                               -5.55332825e-02, -5.74690141e-02, -3.29162553e-03,
                               -5.37678425e-04, -4.43524569e-02, 8.60468077e-04,
                               7.41606858e-03, -4.47724350e-02, 3.59006077e-02,
                               2.29794942e-02, 2.77149621e-02, 9.28640068e-02,
                               3.17951888e-02, 3.78747210e-02, -2.36180751e-03,
                               -6.83198348e-02, 2.01514876e-03, 1.59106478e-02,
                               -3.89336497e-02, -8.50734860e-02, -2.59205848e-02,
                               -1.91784739e-01, -1.47017715e-02, 3.82660404e-02,
                               -1.00710839e-02, -2.35921633e-03, -2.27355002e-03,
                               4.27107587e-02, 1.05156571e-01, -5.15448377e-02,
                               6.02331106e-03, 8.97434913e-03, 7.43116885e-02,
                               -5.20565696e-02, -1.81006524e-03, -2.64808927e-02,
                               4.02310528e-02, -4.56563272e-02, -3.63261765e-03,
                               6.84758974e-03, 4.58915271e-02, -3.45880073e-03,
                               -1.37378173e-02, -2.32979450e-02, 3.61537114e-02,
                               -3.69074531e-02, -2.05637179e-02, 5.73105551e-02,
                               -3.20997313e-02, -3.93821439e-03, -4.75018546e-02,
                               1.31095098e-02, -6.90061301e-02, 2.18694955e-02,
                               -1.41384508e-02, -4.68547307e-02, 5.08792810e-02,
                               -3.24053457e-03, -1.52940778e-02, -5.35534136e-02,
                               -4.25966009e-02, 4.94808052e-03, -1.86370704e-02,
                               -7.67818242e-02, 4.51534092e-02, 7.14136288e-02,
                               5.76046817e-02, -2.83318739e-02, 6.71081468e-02,
                               -8.49447846e-02, 6.07815720e-02, 5.40368184e-02,
                               4.59306389e-02, -2.02329792e-02, -7.33955503e-02,
                               -7.73938373e-02, 7.65464008e-02, 6.65198267e-02,
                               -7.24360272e-02, -2.72260774e-02, -2.28394456e-02,
                               -1.52881555e-02, 3.79300527e-02, -2.52969190e-02,
                               -4.50866893e-02, 2.59067235e-03, 1.69761628e-02,
                               -7.16275647e-02, 2.85739098e-02, 5.29297367e-02,
                               4.89551853e-03, -4.40959781e-02, -1.88653786e-02,
                               5.01667857e-02, 1.17949292e-03, 4.87342365e-02,
                               -3.84358577e-02, 2.72358526e-02, 4.09651510e-02,
                               5.57704456e-02, -2.82040183e-02, -5.64720333e-02,
                               -4.75442111e-02, -6.26633391e-02, -7.63500109e-02,
                               -3.39279845e-02, -6.98818639e-02, -6.28806353e-02,
                               -2.30420772e-02, 6.03814460e-02, 4.54551205e-02,
                               2.02868190e-02, -1.82840787e-02, -2.59453338e-03,
                               -8.70001987e-02, 5.05006220e-03, -6.03069959e-04,
                               -3.32380198e-02, 3.06874458e-02, 9.19784009e-02,
                               1.18212979e-02, 7.75002129e-03, -6.09237738e-02,
                               -3.03128995e-02, -4.90321685e-03, -5.93016595e-02,
                               3.95998545e-02, 1.54991383e-02, 9.64512210e-03,
                               2.59207059e-02, -2.25530472e-02, -2.45276205e-02,
                               -2.14263313e-02, 3.17289904e-02, -8.65958109e-02,
                               7.10390955e-02, 6.75831363e-02, -4.06231843e-02,
                               6.78821728e-02, 7.06873182e-03, 5.60809411e-02,
                               1.51192723e-03, -5.91973737e-02, 3.99504900e-02,
                               1.71808545e-02, 5.20870537e-02, 5.97743951e-02,
                               1.29669318e-02, 2.06763148e-02, 5.40933013e-02,
                               -2.80925096e-03, -5.45007922e-02, 1.28601879e-01,
                               -6.25106767e-02, -8.88793729e-03, 2.87321303e-02,
                               -3.52688879e-02, 9.98077076e-03, 9.25896782e-03,
                               -1.26403170e-02, 3.31691206e-02, 1.11367062e-01,
                               5.28096966e-02, 4.13753018e-02, 6.87546656e-02,
                               7.58808404e-02, 8.48198123e-03, 7.86152706e-02,
                               1.24239887e-03, -7.37212924e-03, 3.95744480e-02,
                               3.28333117e-03, -1.41533306e-02, 1.08314883e-02,
                               7.01383352e-02, -2.53236536e-02, 5.44047281e-02,
                               -2.09017470e-02, -1.07216641e-01, -2.24451162e-02,
                               3.91361816e-03, 4.91617471e-02, -9.38450824e-03,
                               7.68807307e-02, -1.98643841e-02, 4.84972931e-02,
                               6.02341816e-03, 2.46985927e-02, -3.65012069e-03,
                               -3.66932526e-02, -2.89552696e-02, 3.91362868e-02,
                               1.43644689e-02, 3.88031900e-02, -2.25609131e-02,
                               1.09167444e-02, 2.62328424e-02, -7.63828978e-02,
                               5.52295074e-02, 1.96868442e-02, -1.05432430e-02,
                               4.49799118e-05, -2.13553719e-02, -1.93250668e-03,
                               1.49910329e-02, 1.09923678e-02, 4.45025116e-02,
                               -5.92797995e-02, 4.67666751e-03, 3.61543382e-03,
                               3.20543535e-02, -3.05566173e-02, 3.40715088e-02,
                               9.04456377e-02, -4.61067678e-03, 1.47137756e-03,
                               7.15495795e-02, -1.63266659e-02, -9.92763340e-02,
                               -3.72165591e-02, -3.78872547e-03, -6.44522207e-03,
                               6.12584427e-02, 1.39892800e-02, -3.49581093e-02,
                               -3.55244949e-02, 3.25619094e-02, -6.60414947e-03,
                               7.19019994e-02, -2.96380371e-02, -7.64355436e-03,
                               -1.71777233e-02, -2.05337852e-02, -7.66668096e-02,
                               6.46559671e-02, 1.13752969e-02, -1.19766062e-02,
                               1.31874047e-02, 2.64917873e-02, 1.85914040e-02,
                               -7.00949167e-04, 4.76376899e-02, 1.94561891e-02,
                               3.11776102e-02, 1.32506993e-02, 1.24940062e-02,
                               -3.13807353e-02, 4.76723828e-04, -7.54705770e-03,
                               -8.40000249e-03, 4.89070313e-03, -4.80160341e-02,
                               4.21047769e-02, 5.11926413e-02, 1.54927922e-02,
                               5.12672737e-02, 5.34350658e-03, 2.60794396e-03,
                               5.61702205e-03, 3.99596207e-02, 5.23508936e-02,
                               -5.22502325e-02, 5.03775179e-02, -1.83829328e-03,
                               5.65930679e-02, -5.91964982e-02, 1.69529300e-02,
                               2.12711357e-02, 2.62868553e-02, -5.74460812e-02,
                               4.75092717e-02, 3.91144082e-02, -3.99841517e-02,
                               4.10010526e-03, -3.40937860e-02, 5.64233139e-02,
                               -2.75911894e-02, -9.44606960e-02, -4.10288498e-02,
                               -2.93575693e-02, -1.99856237e-02, 7.39237294e-02,
                               -5.87126352e-02, 4.88568060e-02, 8.12605023e-02,
                               -8.92232805e-02, -3.52021903e-02, -4.78064120e-02,
                               -5.95240518e-02, 8.00767764e-02, -4.60182615e-02,
                               -5.46263717e-03, -6.12969045e-03, -4.62199040e-02,
                               -2.12397296e-02, 6.53318539e-02, 4.75921594e-02,
                               4.89275716e-02, 3.78907546e-02, -2.28312127e-02,
                               -7.77202770e-02, -7.22896867e-03, 1.89303905e-02,
                               -6.76713437e-02, 4.22497001e-03, -4.37928177e-02,
                               -3.11760493e-02, 1.87209267e-02, -1.54944323e-02,
                               4.66332724e-03, 4.68296148e-02, -6.22479990e-02,
                               -3.02057359e-02, 4.52510081e-02, -2.31964011e-02,
                               -1.58325024e-02, 3.47425267e-02, 3.16667594e-02,
                               -7.82963336e-02, -9.66563914e-03, 1.16355363e-02,
                               -7.26174936e-02, -4.42587957e-02, -6.44550398e-02,
                               1.73911080e-02, 3.00390199e-02, 7.79711828e-02,
                               -2.33790111e-02, 1.36430021e-02, -8.42198431e-02,
                               3.73488367e-02, -3.02923080e-02, 4.16007601e-02,
                               4.30523045e-02, -3.54150757e-02, 1.84170040e-03,
                               2.37869993e-02, -3.47432904e-02, -3.63558754e-02,
                               4.52818256e-03, -7.45410696e-02, -2.78840936e-03,
                               -9.60513651e-02, 6.60470724e-02]}'''
    '''cur.execute("select * from feature31")
    tmpFea = []
    for i in range(0,512):
        tmp = cur.fetchone()
        tmpFea.append(tmp[1])
    print(featureTransvection(tmpFea,information['feature']))
    print(featureDist(tmpFea, information['feature']))
    info = databaseSearch(information['feature'])
    print(info)
    databaseInit()
    tmpList = spider.Spider()
    for i in tmpList:
        if ('academic' in i.keys()) and (type(i['academic']) is list):
            tmpStr = ''
            for j in i['academic']:
                tmpStr += j + ';'
            i['academic'] = tmpStr
        #print(i)
        if 'feature' in i.keys():
            databaseInsert(i)
    conn.commit()
    cur.close()
    conn.close()'''
