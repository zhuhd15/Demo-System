import pickle, time, random, sys, threading
from function_define import *
from database_IO import *

'''
线程3并不每一时刻都存在 只需要完成如下操作：
在整个系统开始运行时，调用read_data，把数据库中所有的人的向量全部存下来放在内存里。#这是主线程干的事情，实际操作的时候可以再开一个线程。
在需要查询一个向量的信息时，开启一个新的线程，调用find_people方法即可。find_people的返回值可以在线程之间进行传递。
'''

vector_list = []
vector_list_lock = threading.Lock()

def read_data():
    '''
        To read data from database.
        vector_list stores all the map relationships.

    Raises:
        IOError:

    '''
    vector_list_lock.acquire()
    global vector_list_flag, vector_list
    try:
        vector_list = read_all_nodes()
    except:
        raise IOError
    vector_list_lock.release()

MINSIM = 0.45
def find_people(vec):
    '''
        For a certain query of vector, find a people who has the nearest distance from the query.
        When called, you should put it in a new thread.
        ###The more two vectors looks alike, the bigger vector_cosine_dis is.###

    Args:
        vec:    A vector denotes the query

    Returns:
        None:   If the nearest people is still too far from query(MINSIM)
        id:     If the nearest people is near enough.
    '''
    maxsim = 0
    maxsim_id = -1
    for i in vector_list:
        t = vector_cosine_dis(vec, i['n']['vector'])
        print(t)
        if t > maxsim:
            maxsim = t
            maxsim_id = i['n']['id']
    if maxsim < MINSIM:
        return None
    return maxsim_id

if __name__ == '__main__':
    read_data()
    print(find_people(random_vector()))
