from os import truncate
from platform import node
import time
import random
import hashlib
import threading
import myDB
k = 5
MAX = 2**k

def getHash(key, m=k):
    result = hashlib.sha1(key.encode())
    return int(result.hexdigest(), 16) % 2**m


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


def except_handler(method):
    def f(*args):
        count = 3
        while count > 0:
            try:
                ret = method(*args)
                break
            except Exception as exc:
                print(exc)
                print('An error ocurred, trying again...')
                count -= 1
                if count == 0:
                    ret = None

        if not ret is None:
            return ret

        for i in range(1, k):
            if args[0].finger[i] == args[0].finger[0]:
                args[0].finger[i] = args[0].succ_succ

        args[0].finger[0] = args[0].succ_succ
        args[0].predecessor = args[0].pred_pred
        args[0].update_finger_table_leave()
        return method(*args)

    return f


def set_mutex(method):
    @except_handler
    def f(*args):
        mutex.acquire()
        ret = method(*args)
        mutex.release()
        return ret

    return f



class Node:
    def __init__(self, idx):
        self.__data_base = myDB.MyDataBase()
        self.id = idx
        self.succ_succ = None
        self.pred_pred = None
        self.finger = {}
        self.start = {}
        self.__filenameList = []
        for i in range(k):
            self.start[i] = (self.id+(2**i)) % (2**k)


    @set_mutex
    def data_base(self):
        return self.__data_base
    
    @set_mutex
    def filenameList(self):
        return self.__filenameList

    @set_mutex
    def set_filenamelist(self, data):
        self.__filenameList.append(data)
        return 'ok'

    @set_mutex
    def set_succ_succ(self, elem):
        self.succ_succ = elem
        return elem

    @set_mutex
    def get_succ_succ(self, elem):
        return self.succ_succ

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
    def get_pred_pred(self):
        return self.pred_pred

    @set_mutex
    def set_pred_pred(self, value):
        self.pred_pred = value
        return self.pred_pred

    @set_mutex
    def set_finger(self, i, value):
        self.finger[i] = value
        return value

    @set_mutex
    def successor(self):
        return self.finger[0]
    
    @except_handler
    def find_successor(self,id):  
        if betweenE(id,self.get_pred().get_id(),self.id):
            return self
        n = self.find_predecessor(id)
        return n.successor()
    
    @except_handler
    def find_predecessor(self,id):
        if id == self.get_id:
            return self.get_pred()
        n1 = self
        while not betweenE(id,n1.get_id(),n1.successor().get_id()):
            n1 = n1.closest_preceding_finger(id)
        return n1
    
    @except_handler
    def closest_preceding_finger(self,id):
        for i in range(k-1,-1,-1):
            if between(self.finger[i].get_id(),self.id,id):
                return self.finger[i]
        return self
        
    @except_handler
    def join(self,n1):
        if self == n1:
            for i in range(k):
                self.set_finger(i, self)
            self.set_pred(self)
        else:
            self.init_finger_table(n1)
            self.update_others() 

        self.succ_succ = self.successor().successor() 
        self.pred_pred = self.get_pred().get_pred()
        return self
          
    @except_handler
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

    @except_handler
    def update_others(self):
        for i in range(k):
            prev  = decr(self.id,2**i)
            p = self.find_predecessor(prev)
            if prev == p.successor().get_id():
                p = p.successor()
            p.update_finger_table(self,i)

        return 'OK'
    
    @except_handler
    def update_finger_table(self,s,i):
        semi = s.get_id()
        if Ebetween(semi,self.id,self.finger[i].get_id()) and self.id!=semi:
            self.set_finger(i, s)
            p = self.get_pred()
            p.update_finger_table(s,i)

        return 'OK'

    @except_handler
    def update_finger_table_leave(self):
        for i in self.start.keys():
            entryId = self.start[i]
            # If only one node in network
            if self.successor() == self:
                self.set_finger(i, self)
                continue
            # If multiple nodes in network, we find succ for each entryID
            self.set_finger(i, self.find_successor(entryId))

        return 'OK'

    @except_handler
    def update_others_leave(self):
        current = self.successor()
        end = self.successor()
        changed = False
        while current != end or not changed:
            current.update_finger_table_leave()
            current = current.successor()
            changed = True

        changed = False
        while current != end or not changed:
            current.set_succ_succ(current.successor().successor())
            current.set_pred_pred(current.get_pred().get_pred())
            changed = True

        return 'OK'

    @except_handler
    def leave(self):
        self.give_legacy()
        suc = self.successor()
        suc.set_pred(self.get_pred())
        self.predecessor.setSuccessor(self.successor())

        
        return self.update_others_leave()

    @except_handler
    def give_legacy(self):
        suc = self.successor() 
        sucsuc = suc.successor()
        suc.data_base().merge_data()
        line = ' '
        while True:
            line = suc.data_base().get_pred_data()
            if line == '':
                break

            sucsuc.data_base().addData(line[0],line[1],False)


        # for item in suc.data_base().get_pred_data():
        #     sucsuc.data_base().addData(item[0],item[1],False)
            

    @except_handler
    def lookup(self, key):
        
        if self.successor()==self:
            return self

        if between(key, self.get_pred().get_id(), ( self.get_id() + 1) % MAX ) :
            return self
        successor = self.find_successor(key)
        return successor.lookup(key)
    
    @except_handler
    def save_file(self,filename,body):
        key = getHash(filename)
        node = self.lookup(key)
        
        if node.data_base().contains(filename):
            return False

        node.data_base().addData(filename,body)
        node.successor().data_base().addData(filename,body,False)
        return True
  
    @except_handler
    def get_file(self,filename):
        node = self.lookup(getHash(filename))
        return node.data_base().get_http(filename)

