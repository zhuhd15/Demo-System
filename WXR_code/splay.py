'''
需要在内存里保存所有节点的512维向量
Splay树用长整数作为索引
查询的时候查询一个区间
'''

from function_define import *
from function_define import *

class SplayTreeNode:
    '''
        __data_dict     这个节点的所有数据
        __val           这个节点的键值 用于排序和查找 long类型
    '''
    def __init__(self, val, data_dict):
        self.__data_dict = data_dict
        self.__val = val
        self.__lc = None
        self.__rc = None
        self.__fa = None

    def get_lc(self):
        return self.__lc
    def get_rc(self):
        return self.__rc
    def del_lc(self):
        self.__lc = None

    def print(self, mode = 0):
        '''
        如果mode = 1 只打印单个的点
        '''
        if mode == 0 and self.__lc != None:
            self.__lc.print()
        print('INF' if self.__val == INTEGER_INFINITY else \
                '-INF' if self.__val == -INTEGER_INFINITY else \
                self.__val, self.__data_dict)
        if mode == 0 and self.__rc != None:
            self.__rc.print()

    def insert(self, val, data_dict):
        if val > self.__val:
            if self.__rc == None:
                self.__rc = SplayTreeNode(val, data_dict)
                self.__rc.__fa = self
            else:
                self.__rc.insert(val, data_dict)
        else:
            if self.__lc == None:
                self.__lc = SplayTreeNode(val, data_dict)
                self.__lc.__fa = self
            else:
                self.__lc.insert(val, data_dict)

    def __rotate(self):
        global SPLAY_ROOT
        if self.__fa == None:
            return
        fa = self.__fa
        if fa == SPLAY_ROOT:
            SPLAY_ROOT = self
        self.__fa = fa.__fa
        if fa.__fa != None:
            if fa.__fa.__lc == fa:
                fa.__fa.__lc = self
            else:
                fa.__fa.__rc = self
        if fa.__lc == self:
            a = self.__rc
            fa.__lc = a
            self.__rc = fa
        else:
            a = self.__lc
            fa.__rc = a
            self.__lc = fa
        if a != None:
            a.__fa = fa
        fa.__fa = self

    def splay(self, toroot = 1):
        '''
        若toroot = 1 旋转到根
        若toroot = 0 旋转到根的孩子
        '''
        if toroot == 1:
            while self.__fa != None:
                self.__rotate()
        else:
            while self.__fa != None and self.__fa.__fa != None:
                self.__rotate()

    def query(self, val, specific = 0):
        '''
        若specific = 0 旋转并返回精确命中点
        若specific = -1 旋转并返回小于val的第一个点
        若specific = 1 旋转并返回大于val的第一个点
        '''
        def specific_solve(self, val, specific):
            if specific == 1:
                if self.__val > val:
                    return self
                t = self.__rc
                while t.__lc != None:
                    t = t.__lc
            else:
                if self.__val < val:
                    return self
                t = self.__lc
                while t.__rc != None:
                    t = t.__rc
            return t
        def rc_solve(self, val, specific):
            if self.__rc:
                return self.__rc.query(val, specific)
            else:
                if specific == 0:
                    return None
                else:
                    self.splay()
                    return specific_solve(self, val, specific)
        def lc_solve(self, val, specific):
            if self.__lc:
                return self.__lc.query(val, specific)
            else:
                if specific == 0:
                    return None
                else:
                    self.splay()
                    return specific_solve(self, val, specific)

        if specific == 0:
            if val == self.__val: 
                self.splay()
                return self
            elif val > self.__val:
                return rc_solve(self, val, specific)
            elif val < self.__val:
                return lc_solve(self, val, specific)
        elif specific == -1:
            if val > self.__val:
                return rc_solve(self, val, specific)
            else:
                return lc_solve(self, val, specific)
        elif specific == 1:
            if val < self.__val:
                return lc_solve(self, val, specific)
            else:
                return rc_solve(self, val, specific)

    def dfs_query(self, vec):
        ans = {'dis' : vector_dis(vec, self.__data_dict['vector']), 'id' : self.__data_dict['id']}
        if self.__lc:
            tmp = self.__lc.dfs_query(vec)
            if tmp['dis'] < ans['dis']:
                ans = tmp
        if self.__rc:
            tmp = self.__rc.dfs_query(vec)
            if tmp['dis'] < ans['dis']:
                ans = tmp
        return ans

class SplayTree:
    global INTEGER_INFINITY
    def __init__(self):
        global SPLAY_ROOT
        SPLAY_ROOT = None
        self.insert(INTEGER_INFINITY, {})
        self.insert(-INTEGER_INFINITY, {})

    def insert(self, val, data_dict):
        global SPLAY_ROOT
        if SPLAY_ROOT == None:
            SPLAY_ROOT = SplayTreeNode(val, data_dict)
        else:
            SPLAY_ROOT.insert(val, data_dict)

    def print(self):
        global SPLAY_ROOT
        try:
            SPLAY_ROOT.print()
        except:
            debug('[PRINT] Failed. The Splay Tree is empty.')

    def query(self, val, specific = 0):
        global SPLAY_ROOT
        return SPLAY_ROOT.query(val, specific)
        try:
            return SPLAY_ROOT.query(val, specific)
        except:
            debug('[QUERY] Failed. The Splay Tree is empty.')

    def set_interval(self, l, r):
        global SPLAY_ROOT
        p = self.query(l, -1)
        q = self.query(r, 1)
        p.splay()
        q.splay(0)
        try:
            return q.get_lc()
        except:
            debug('[INTERVAL_SET] Failed. The Interval is invalid.')

    def query_interval(self, l, r, vec):
        p = self.set_interval(l, r)
        try:
            return p.dfs_query(vec)
        except:
            #debug('[QUERY_INTERVAL] Failed. Vector Not Found.')
            return {'dis' : 100, 'id' : -1}

    def delete(self, val):
        global SPLAY_ROOT
        target = self.query_interval(val - 2*EPSILON, val + 2*EPSILON)
        SPLAY_ROOT.get_rc().del_lc()
        del target
