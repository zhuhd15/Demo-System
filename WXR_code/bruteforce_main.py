import pickle
import time
import random
import sys
sys.setrecursionlimit(20000)
from splay import *
from function_define import *

if __name__ == '__main__':
    infile = open('vector.data', 'rb')
    vector_list = pickle.load(infile)
    infile.close()
    infile = open('vector_query.data', 'rb')
    query_list = pickle.load(infile)
    infile.close()

    N = len(vector_list)
    outfile = open('result_bruteforce.txt', 'w')
    outfile.close()
    for i in query_list:
        start = time.clock()
        ans = {'dis' : 100, 'id' : -1}
        l = len(vector_list)
        for j in range(0, l):
            tmp = {'dis' : vector_dis(i, vector_list[j]), 'id' : j}
            if tmp['dis'] < ans['dis']:
                ans = tmp
        end = time.clock()
        outfile = open('result_bruteforce.txt', 'a')
        outfile.write(str(ans) + ' ' + str(round(end - start, 2)) + '\n')
        outfile.close()
        print(str(ans) + ' ' + str(round(end - start, 2)))

