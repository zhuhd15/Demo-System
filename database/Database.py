import MySQLdb
index = 0.03829

def databaseInit():
    #database init
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'Demo-SystemAdmin', passwd = '666666', db = 'Demo-SystemDatabase', charset = 'utf8')
    cur = conn.cursor()
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
    conn.commit()
    cur.close()
    conn.close()
    pass

if __name__=="__main__":
    databaseInit()
