import math, numpy, random
from scipy.spatial.distance import pdist
VECTOR_SIZE = 512
SPLAY_ROOT = None
INTEGER_INFINITY = 10 ** 15
EPSILON = 1e-12
DIMENSION_EXTRACT = 5
DISTANCE_MULTIPLY = 10 ** 10
vector_bucket = [[] for i in range(0, 2 ** DIMENSION_EXTRACT)]
vector_list = []

HASHING_MOD = 10000007
HASHING_VECTOR_SIZE = 4

def debug(st):
    print(st)

def code_calc(vec):
    bucket_code = 0
    dis = 0
    for i in range(0, DIMENSION_EXTRACT):
        bucket_code *= 2 
        if vec[i] > 0:
            bucket_code += 1
        dis += vec[i] * vec[i]
    return int(math.sqrt(dis) * DISTANCE_MULTIPLY) + bucket_code * 4 * DISTANCE_MULTIPLY

def vector_init():
    global vector_list
    N = len(vector_list)
    for i in range(0, N):
        t = 0
        for j in range(0, DIMENSION_EXTRACT):
            t = t * 2
            if vector_list[i][j] > 0:
                t = t + 1
        vector_bucket[t].append(i)

def vector_dis(vec1, vec2 = [0 for i in range(0, VECTOR_SIZE)]):
    dis = 0
    for i in range(0, VECTOR_SIZE):
        dis += (vec1[i] - vec2[i]) * (vec1[i] - vec2[i])
    return math.sqrt(dis)

def abs(a):
    if a > 0:
        return a
    return -a

def vector_cosine_dis(vec1, vec2 = [0 for i in range(0, VECTOR_SIZE)]):
    return abs(pdist(numpy.vstack([vec1, vec2]), 'cosine') - 1)

def random_vector():
    li = [1 - random.random() * 2 for i in range(0, VECTOR_SIZE)]
    t = 0
    for i in range(0, VECTOR_SIZE):
        t = t + li[i] * li[i]
    t = math.sqrt(t)
    return [li[i] / t for i in range(0, VECTOR_SIZE)]
