import pickle
from function_define import *
import random
import math

'''
N = 10000
vec = []
for i in range(0, N):
    t = []
    for j in range(0, VECTOR_SIZE):
        t.append(random.randint(-100, 101))
    tot = 0.0
    for j in range(0, VECTOR_SIZE):
        tot += t[j] * t[j]
    tot = math.sqrt(tot)
    for j in range(0, VECTOR_SIZE):
        t[j] = t[j] / tot
    vec.append(t)
    if i % 100 == 0:
        print(i)

outfile = open('vector.data', 'wb')
pickle.dump(vec, outfile)
outfile.close()

N = 100
vec = []
for i in range(0, N):
    t = []
    for j in range(0, VECTOR_SIZE):
        t.append(random.randint(-100, 101))
    tot = 0.0
    for j in range(0, VECTOR_SIZE):
        tot += t[j] * t[j]
    tot = math.sqrt(tot)
    for j in range(0, VECTOR_SIZE):
        t[j] = t[j] / tot
    vec.append(t)
    if i % 100 == 0:
        print(i)

outfile = open('vector_query.data', 'wb')
pickle.dump(vec, outfile)
outfile.close()
'''

N = 50
vec = []
for i in range(0, N):
    t = []
    for j in range(0, VECTOR_SIZE):
        t.append(random.randint(-100, 101))
    tot = 0.0
    for j in range(0, VECTOR_SIZE):
        tot += t[j] * t[j]
    tot = math.sqrt(tot)
    for j in range(0, VECTOR_SIZE):
        t[j] = t[j] / tot
    vec.append(t)
    if i % 100 == 0:
        print(i)

outfile = open('vector_hash.data', 'wb')
pickle.dump(vec, outfile)
outfile.close()
