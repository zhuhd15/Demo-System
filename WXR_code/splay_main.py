import pickle
import time
import random
import sys
sys.setrecursionlimit(20000)
from splay import *
from function_define import *

SPLAY_TREE = SplayTree()

def query_vector_nn(vec):
    bucket_code = 0
    for i in range(0, DIMENSION_EXTRACT):
        bucket_code *= 2
        if vec[i] > 0:
            bucket_code += 1
    min_dis = {'dis' : 100, 'id' : -1}
    if len(vector_bucket[bucket_code]) > 0:
        for i in vector_bucket[bucket_code]:
            tmp = {'dis' : vector_dis(vector_list[i], vec), 'id' : i}
            if tmp['dis'] < min_dis['dis']:
                min_dis = tmp
    else:
        min_dis = {'dis' : vector_dis(vec, vector_list[0]), 'id' : 0}

    for i in range(0, 2 ** DIMENSION_EXTRACT):
        check_flag = True
        for j in range(0, DIMENSION_EXTRACT):
            if vec[j] > 0 and i & (1 << j) == 0 and vec[j] > min_dis['dis']:
                check_flag = False
                break
            if vec[j] < 0 and i & (1 << j) == 1 and vec[j] < -min_dis['dis']:
                check_flag = False
                break
        if check_flag:
            tmp = SPLAY_TREE.query_interval(\
                i * 4 * DISTANCE_MULTIPLY + int((vector_dis(vec) - min_dis['dis']) * DISTANCE_MULTIPLY),\
                i * 4 * DISTANCE_MULTIPLY + int((vector_dis(vec) + min_dis['dis']) * DISTANCE_MULTIPLY),\
                vec)
            if tmp['dis'] < min_dis['dis']:
                min_dis = tmp
    return min_dis

if __name__ == '__main__':
    infile = open('vector.data', 'rb')
    vector_list = pickle.load(infile)
    infile.close()
    infile = open('vector_query.data', 'rb')
    query_list = pickle.load(infile)
    infile.close()

    vector_init()
    N = len(vector_list)
    for i in range(0, N):
        SPLAY_TREE.insert(code_calc(vector_list[i]), {'id' : i, 'vector' : vector_list[i]})
    #SPLAY_TREE.print()
    for i in query_list:
        start = time.clock()
        ans = query_vector_nn(i)
        end = time.clock()
        print (ans, round(end - start, 2))

