import os, pickle, random
from py2neo import *
from function_define import *
from random import randint
'''The unique ID count for people'''
ID_count = 0

'''The labels of nodes'''
Node_LabelSet = ['label', 'id']
''' When mergeing nodes, some of the labels do not append. 
    While other labels take lists to storage, and are easy
    to append data after it.'''
Node_UniqueLabelSet = ['Gender', 'length', 'name', 'id']

Database = Graph(
    "http://localhost:7474"
)

class Error(Exception):
    '''Base class for Exceptions.'''
    def __init__(self, string=''):
        self.string = string
    def __str__(self):
        return repr(self.string)

class NotFoundError(Error):
    '''Raised when vector is not found in the database.'''
    pass

class InvalidInputError(Error):
    '''Raised when input is invalid.'''
    pass

class DatabaseIOError(Error):
    '''Raised when database is out of service.'''
    pass

def init():
    '''To initalize variables.

    Raises:
        IOError:
    '''
    global ID_count
    try:
        idfile = open('../data/id.data', 'rb')
        ID_count = pickle.load(idfile)
        idfile.close()
    except:
        raise IOError

def save():
    '''To save variables.

    Raises:
        IOError:
    '''
    global ID_count
    try:
        idfile = open('../data/id.data', 'wb')
        pickle.dump(ID_count, idfile)
        idfile.close()
    except:
        raise IOError

def delete_all():
    '''Delete all the graph.'''
    Database.run('match (a)-[r]-(b) delete r')
    Database.run('match (a) delete a')
    global ID_count
    ID_count = 0

def find_id(vec):
    '''To get the unique ID of the 512-D vector

    Args:
        vec:    The vector

    Returns:
        An integer indicates the ID

    Raises:
        NotFoundError:  Vector not found in the database
        InvalidInputError:  vec is not an vector
    '''
    if type(vec) != type([]):
        raise InvalidInputError('In [find_id]: vec is not an vector.')
    if len(vec) != VECTOR_SIZE:
        raise InvalidInputError('In [find_id]: vec is not an %d-D vector.' % VECTOR_SIZE)
    pass

def get_info(index):
    '''To get the information of people who has id of index.

    Args:
        index:  The ID

    Returns:
        A Node that include all the information.

    Raises:
        InvalidInputError:  index is not an integer.
        NotFoundError:  ID doesn't exist.
    '''
    if type(index) != int:
        raise InvalidInputError('In [get_info]: index is not an integer')
    res = Database.find_one(
            label = 'Person', 
            property_key = 'id', 
            property_value = index)
    if res == None:
        raise NotFoundError('In [get_info]: Index not found.')
    return res

def set_info(index, modify_info):
    '''To set the information of people who has id of index.

    Args:
        index:  The ID
        modify_info:    A dict that include keys and values to be changed.

    Raises:
        InvalidInputError:  index is not an integer.
        NotFoundError:  ID doesn't exist.
    '''
    if type(index) != int:
        raise InvalidInputError('In [set_info]: index is not an intger.')
    if type(modify_info) != dict:
        raise InvalidInputError('In [set_info]: modify_info is not a dict.')
    tar = Database.find_one(
            label = 'Person', 
            property_key = 'id', 
            property_value = index)
    if tar == None:
        raise NotFoundError('In [set_info]: Index not found.')
    for details in modify_info:
        tar[details] = modify_info[details]
    Database.push(tar)

def add_relationship(id1, id2, det=1):
    '''To add relationship value between two people.
    Relationship is a bidirectional link. On the link, there is
    a number indicates the strength of the relationship.
    The key of the strength has a name of 'mag'

    Args:
        id1, id2:   Two people
        det:    Delta of relationship value

    Raises:
        InvalidInputError:  id1 or id2 is not integer.
        NotFoundError:  ID doesn't exist.
    '''
    if type(id1) != int or type(id2) != int:
        raise InvalidInputError('In [add_relationship]: id is not an integer.')
    if id1 == id2:
        raise InvalidInputError('In [add_relationship]: id1 and id2 is the same.')
    res1 = Database.find_one(
            label = 'Person', 
            property_key = 'id', 
            property_value = id1)
    res2 = Database.find_one(
            label = 'Person', 
            property_key = 'id', 
            property_value = id2)
    if res1 == None or res2 == None:
        raise NotFoundError('In [merge_people]: Id does not exist.')
    relres = Database.match_one(start_node=res1, end_node=res2, 
            bidirectional=True)
    if relres != None:
        relres['mag'] += det
        Database.push(relres)
    else:
        tmp_rel = Relationship(res1, res2)
        tmp_rel['mag'] = det
        Database.create(tmp_rel)

def new_people(info):
    '''To add a people into the database.

    Args:
        info:   A dict that include the information of the people

    Raises:
        InvalidInputError: info is not a dict
    '''
    global ID_count
    if type(info) != type({}):
        raise InvalidInputError('In [new_people]: info is not a dict.')
    tmp_node = Node('Person', id = ID_count)
    for details in info:
        tmp_node[details] = info[details]
    Database.create(tmp_node)
    ID_count += 1

def merge_people(id1, id2):
    '''To merge two people and their infomation.

    Args:
        id1, id2:   Two id numbers of people to be merged.

    Raises:
        NotFoundError:  ID doesn't exist.
        InvalidInputError: id1 or id2 is not an integer.
    '''
    if type(id1) != int or type(id2) != int:
        raise InvalidInputError('In [merge_people]: Id is not an integer.')
    res1 = Database.find_one(
            label = 'Person', 
            property_key = 'id', 
            property_value = id1)
    res2 = Database.find_one(
            label = 'Person', 
            property_key = 'id', 
            property_value = id2)
    if res1 == None or res2 == None:
        raise NotFoundError('In [merge_people]: Id does not exist.')

    relres = Database.match(start_node=res2, bidirectional=True)
    for r in relres:
        #Cut all the relationship (res2)-(XXX), and add them to (res1)-(XXX)
        if r.start_node() == res2:
            XXX = r.end_node()
        else:
            XXX = r.start_node()
        if XXX == res1:
            continue
        rel = Database.match_one(start_node=res1, end_node=XXX, 
                bidirectional=True)
        if rel == None:
            tmp_rel = Relationship(res1, XXX)
            tmp_rel['mag'] = r['mag']
            Database.create(tmp_rel)
        else:
            rel['mag'] += r['mag']
            Database.push(rel)
    Database.run('match (a)-[r:TO]-(b{id:%d}) delete r' % res2['id'])

    for details in res2:
        if details not in res1:
            res1[details] = res2[details]
        elif details in Node_UniqueLabelSet:
            pass
        else:
            res1[details].append(res2[details])
    Database.push(res1)
    Database.delete(res2)

def near_people_list(index):
    NEAR_LIST_SIZE = 10
    '''To find the top [SIZE] people who has the highest relationship 
        strength with people who has an id of index.

    Args:
        index:  The id of people

    Returns:
        A list that includes at most [SIZE] pairs of (id, magnitude).

    Raises:
        InvalidInputError: index is not an integer.
        NotFoundError:  index is not in the graph.
    '''
    if type(index) != int:
        raise InvalidInputError('In [near_people_list]: index is not an integer.')
    res = Database.find_one(
            label = 'Person', 
            property_key = 'id', 
            property_value = index)
    if res == None:
        raise NotFoundError('In [near_people_list]: ID does not exist.')
    rel = Database.run('match (a{id:%d})-[r]-(b) return r, b' % index)
    rel = sorted(rel, key=lambda p : -p['r']['mag'])
    ans = []
    for i in range(0, min(NEAR_LIST_SIZE, len(rel))):
        ans.append((rel[i]['b']['id'], rel[i]['r']['mag']))
    return ans

def read_all_nodes():
    '''To read all the nodes in the database.

    Returns:
        A list that includes all the nodes.
        element of list: [id, vector]

    Raises:
        DatabaseIOError: Database is not in service.
    '''
    t = Database.run('match (n) return n')
    ret = []
    for i in t:
        ret.append(i)
    return ret

##########################################################################

def TEST_new_people(num):
    '''To add some people into the graph for testing.
    Args:
        num:    The number of people
    '''
    for i in range(0, num):
        new_people({'name': '%d'%i, 'vector': random_vector()})
        if i % 100 == 0:
            print(i)

if __name__ == '__main__':
    init()
    delete_all()
    TEST_new_people(1000)
    '''
    for i in range(0, 15):
        try:
            add_relationship(i, 0, i+1)
        except:
            pass
    ans =  near_people_list(0)
    for i in ans:
        print (i)
    '''
    save()
