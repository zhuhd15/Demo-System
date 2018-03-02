import pickle
import time
import random
from function_define import *

hashing_vector = []
hashing_coefficient = []
# hashing_bucket = [[] for i in range(0, HASHING_MOD)]
hashing_bucket = [[] for i in range(0, 2**HASHING_VECTOR_SIZE)]
for i in range(0, HASHING_VECTOR_SIZE):
    t = []
    for j in range(0, VECTOR_SIZE):
        t.append(random.randint(-100, 101))
    tot = 0.0
    for j in range(0, VECTOR_SIZE):
        tot += t[j] * t[j]
    tot = math.sqrt(tot)
    for j in range(0, VECTOR_SIZE):
        t[j] = t[j] / tot
    hashing_vector.append(t)

for i in range(0, HASHING_VECTOR_SIZE):
    hashing_coefficient.append(random.randint(0, HASHING_MOD))

def sign(d):
    if d > 0:
        return 1
    return 0

def hash_code(vec, mode = 0):
    code_list = []
    for i in range(0, HASHING_VECTOR_SIZE):
        if i % 2 == 0:
            continue
        code_list.append(sign(vector_dot_product(vec, hashing_vector[i])) ^\
                sign(vector_dot_product(vec, hashing_vector[i - 1])))
    code = 0
    for i in range(0, HASHING_VECTOR_SIZE // 2):
        #code = (code + hashing_coefficient[i] * code_list[i]) % HASHING_MOD
        code = code*2 + code_list[i]
    if mode:
        print (code_list)
    return code

if __name__ == '__main__':
    infile = open('vector.data', 'rb')
    vector_list = pickle.load(infile)
    infile.close()
    infile = open('vector_query.data', 'rb')
    query_list = pickle.load(infile)
    infile.close()

    for i in range(0, len(vector_list)):
        hashing_bucket[hash_code(vector_list[i])].\
            append({'vector':vector_list[i], 'id':i})
        if i % 100 == 0:
            print (i)

    outfile = open('result_lsh.txt', 'w')
    outfile.close()

    totcnt = 0
    for i in query_list:
        code = hash_code(i)
        start = time.clock()
        ans = {'dis' : 100, 'id' : -1}
        for j in hashing_bucket[code]:
            tmp = {'dis':vector_dis(j['vector'], i), 'id':j['id']}
            if tmp['dis'] < ans['dis']:
                ans = tmp
        end = time.clock()
        cnt = 0
        for k in range(0, len(vector_list)):
            if vector_dis(vector_list[k], i) <= ans['dis']:
                cnt += 1
        outfile = open('result_lsh.txt', 'a')
        outfile.write(str(ans) + '\t' + '%.2f' % round(end - start, 2) + '\t' + str(cnt) + '\n')
        outfile.close()
        totcnt += 1
        print(totcnt)
