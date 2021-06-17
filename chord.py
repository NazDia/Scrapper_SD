from os import truncate
from platform import node
import time
import random
import hashlib
import threading
import myDB
k = 5
MAX = 2**k

def getHash(key, m=MAX):
    result = hashlib.sha1(key.encode())
    return int(result.hexdigest(), 16) % m


def decr(value,size):
    if size <= value:
        return value - size
    else:
        return MAX-(size-value)

def between(value,init,end):
    if init == end:
        return True
    elif init > end :
        shift = MAX - init
        init = 0
        end = (end +shift)%MAX
        value = (value + shift)%MAX
    return init < value < end

def Ebetween(value,init,end):
    if value == init:
        return True
    else:
        return between(value,init,end)

def betweenE(value,init,end):
    if value == end:
        return True
    else:
        return between(value,init,end)


mutex = threading.Lock()

def set_mutex(method):
    def f(*args):
        mutex.acquire()
        ret = method(*args)
        mutex.release()
        return ret

    return f



class Node:
    def __init__(self, idx):
        self.__data_base = myDB.MyDataBase()
        self.__data_base.loadData()
        self.id = idx
        self.finger = {}
        self.start = {}
        self.__filenameList = self.__data_base.httpNameList()
        for i in range(k):
            self.start[i] = (self.id+(2**i)) % (2**k)

        # fingers = threading.Thread(target=self.fix_fingers_loop)
        # fingers.start()

    def data_base(self):
        return self.__data_base
    
    def filenameList(self):
        return self.__filenameList
        

    @set_mutex
    def setSuccessor(self,succ):
        self.finger[0] = succ
        return succ

    @set_mutex
    def get_id(self):
        return self.id

    @set_mutex
    def get_pred(self):
        return self.predecessor

    @set_mutex
    def set_pred(self, value):
        self.predecessor = value
        return self.predecessor

    @set_mutex
    def set_finger(self, i, value):
        self.finger[i] = value
        return value

    @set_mutex
    def successor(self):
        return self.finger[0]
    
    def find_successor(self,id):  
        if betweenE(id,self.get_pred().get_id(),self.id):
            return self
        n = self.find_predecessor(id)
        return n.successor()
    
    def find_predecessor(self,id):
        if id == self.get_id:
            return self.get_pred()
        n1 = self
        while not betweenE(id,n1.get_id(),n1.successor().get_id()):
            n1 = n1.closest_preceding_finger(id)
        return n1
    
    def closest_preceding_finger(self,id):
        for i in range(k-1,-1,-1):
            if between(self.finger[i].get_id(),self.id,id):
                return self.finger[i]
        return self
        
    
    def join(self,n1):
        if self == n1:
            for i in range(k):
                self.set_finger(i, self)
            self.set_pred(self)
        else:
            self.init_finger_table(n1)
            self.update_others()  

        return self
          
            
    def init_finger_table(self,n1):
        self.set_finger(0, n1.find_successor(self.start[0]))
        self.set_pred(self.successor().get_pred())
        self.successor().set_pred(self)
        self.predecessor.set_finger(0, self)
        for i in range(k-1):
            if Ebetween(self.start[i+1],self.id,self.finger[i].get_id()):
                self.set_finger(i+1, self.finger[i])
            else :
                self.set_finger(i+1, n1.find_successor(self.start[i+1]))

        return self

    def update_others(self):
        for i in range(k):
            prev  = decr(self.id,2**i)
            p = self.find_predecessor(prev)
            if prev == p.successor().get_id():
                p = p.successor()
            p.update_finger_table(self,i)

        return 'OK'
            
    def update_finger_table(self,s,i):
        semi = s.get_id()
        if Ebetween(semi,self.id,self.finger[i].get_id()) and self.id!=semi:
            self.set_finger(i, s)
            p = self.get_pred()
            p.update_finger_table(s,i)

        return 'OK'

    def update_finger_table_leave(self):
        for i in self.start.keys():
            # entryId = (self.id + (2 ** i)) % 2**k
            entryId = self.start[i]
            # If only one node in network
            if self.successor() == self:
                self.set_finger(i, self)
                continue
            # If multiple nodes in network, we find succ for each entryID
            self.set_finger(i, self.find_successor(entryId))

        return 'OK'

    def update_others_leave(self):
        current = self.successor()
        end = self.successor()
        changed = False
        while current != end or not changed:
            current.update_finger_table_leave()
            current = current.successor()
            changed = True

        return 'OK'

    def leave(self):
        suc = self.successor()
        suc.set_pred(self.get_pred())
        self.predecessor.setSuccessor(self.successor())

        self.give_legacy()
        suc.give_legacy()

        return self.update_others_leave()

    def give_legacy(self):
        suc = self.successor() 
        for key in self.data_base.keys():
            if not key in suc.data_base().keys():
                suc.data_base().addData(key , self.data_base().get_http(key)) 

    def lookup(self, key):
        
        if self.successor()==self:
            return self

        if between(key, self.get_pred().get_id(), ( self.get_id() + 1) % MAX ) :
            return self
        successor = self.find_successor(key)
        return successor.lookup(key)
    
    def save_file(self,filename,body):
        key = getHash(filename)
        node = self.lookup(key)
        if filename in node.filenameList():
            return False

        node.filenameList().append(filename)
        node.data_base().addData(filename,body)
        node.data_base().saveData()        
        return True
    
  

    def get_file(self,filename):
        node = self.lookup(filename)
        if filename in node.filenameList():
            return node.data_base().get_http(filename)
        return 'ok'

    """
    SaveFile
    LookupId
    GetFile
    """


def printNodes(node):
    print ('Ring nodes :')
    end = node
    print (node.get_id())
    while end != node.successor() and node.successor() != node:
        node = node.successor()
        print (node.get_id())
    print ('-----------')

def showFinger(node, k):
    print ('Finger table of node ' + str(node.get_id()))
    print ('start:node')
    for i in range(k):
        print (str(node.start[i]) +' : ' +str(node.finger[i].get_id()))  
    print ('-----------')
