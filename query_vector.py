import pickle, time, random, sys, threading, queue
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

MINSIM = 0
find_people_queue = None
class find_people_thread(threading.Thread):
    def __init__(self, vec, begin, length):
        threading.Thread.__init__(self)
        self.vec, self.begin, self.length = vec, begin, length
    def run(self):
        global find_people_queue
        vec, begin, length = self.vec, self.begin, self.length
        maxsim = vector_cosine_dis(vec, vector_list[begin]['n']['vector'])
        maxsim_id = begin
        LEN = len(vec)
        for i in range(begin + 1, min(begin + length, LEN)):
            t = vector_cosine_dis(vec, vector_list[i]['n']['vector'])
            if t > maxsim:
                maxsim = t
                maxsim_id = vector_list[i]['n']['id']
        #print(maxsim_id)
        if maxsim < MINSIM:
            find_people_queue.put(None)
        else:
            find_people_queue.put(maxsim_id)

def find_people(vec, THREAD_COUNT = 1):
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
    global find_people_queue
    find_people_queue = queue.Queue()
    th = [None for i in range(THREAD_COUNT)]
    ans = list()
    length = len(vec) // THREAD_COUNT
    cur = 0
    for i in range(THREAD_COUNT):
        th[i] = find_people_thread(vec, cur, length)
        cur += length
    ans_id = None
    for i in range(THREAD_COUNT):
        th[i].start()
        th[i].join()
    while not find_people_queue.empty():
        ans.append(find_people_queue.get())
    for i in range(THREAD_COUNT):
        ans_id = ans[i] if ans_id == None or ans[i] != None and \
            vector_cosine_dis(vec, vector_list[ans_id]['n']['vector']) <\
            vector_cosine_dis(vec, vector_list[ans[i]]['n']['vector']) else ans_id
    return ans_id

if __name__ == '__main__':
    read_data()
    random.seed(1)
    vec = random_vector()
    print (find_people(vec))
