from os import truncate
from platform import node
import time
import random
import hashlib
import threading
import myDB

k = 5
MAX = 2**k
BLOCKED = 'BLOCKED'
OK = 'OK'

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

        try:
            args[0].successor().get_id()

        except:
            args[0].setSuccessor(args[0].get_succ_succ())
            args[0].successor().get_legacy()
            args[0].successor().get_pred_from(args[0])

        args[0].update_others_leave()
        args[0].set_pred_pred(args[0].get_pred().get_pred())
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
        self._status = OK
        for i in range(k):
            self.start[i] = (self.id+(2**i)) % (2**k)

    @set_mutex
    def status(self):
        return self._status

    @set_mutex
    def set_status(self, status):
        self._status = status
        return status

    @set_mutex
    def data_base(self):
        return self.__data_base
    
    @set_mutex
    def filenameList(self):
        return self.__filenameList

    @set_mutex
    def set_filenamelist(self, data):
        self.__filenameList.append(data)
        return OK

    @set_mutex
    def set_succ_succ(self, elem):
        self.succ_succ = elem
        return elem

    @set_mutex
    def get_succ_succ(self):
        return self.succ_succ

    @except_handler
    def update_succ_succ(self):
        return self.set_succ_succ(self.successor().successor())

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
        pred_id = self.get_pred().get_id()
        if pred_id is None:
            self.set_pred(self.get_pred_pred())
            pred_id = self.get_pred().get_id()

        if betweenE(id,pred_id,self.id):
            return self

        n = self.find_predecessor(id)
        return n.successor()
    
    @except_handler
    def find_predecessor(self,id):
        if id == self.get_id:
            return self.get_pred()
        n1 = self
        n1_suc_id = n1.successor().get_id()
        if n1_suc_id is None:
            n1.setSuccessor(n1.get_succ_succ())
            n1_suc_id = n1.successor().get_id()

        while not betweenE(id,n1.get_id(),n1_suc_id):
            n1 = n1.closest_preceding_finger(id)
            # n1.setSuccessor(n1.get_succ_succ())
            n1_suc_id = n1.successor().get_id()
            if n1_suc_id is None:
                n1.setSuccessor(n1.get_succ_succ())
                n1_suc_id = n1.successor().get_id()

        return n1
    
    @except_handler
    def closest_preceding_finger(self,id):
        for i in range(k-1,-1,-1):
            if between(self.finger[i].get_id(),self.id,id):
                return self.finger[i]
        return self
        
    @except_handler
    def join(self,n1, resent=False):
        while n1.status() == BLOCKED:
            time.sleep(1)

        self._status = BLOCKED
        n1.set_status(BLOCKED)
        if self == n1:
            for i in range(k):
                self.set_finger(i, self)
                
            self.set_pred(self)
            self.succ_succ = self.successor().successor() 
            self.pred_pred = self.get_pred().get_pred()
            self._status = OK
            # n1.set_status(OK)
            return self

        n1_suc = n1.successor()
        n1_suc_id = n1_suc.get_id()
        if n1_suc_id is None:
            n1.setSuccessor(n1.get_succ_succ())
            n1.update_succ_succ()
            n1_suc = n1.successor()
            n1_suc_id = n1_suc.get_id()

        if not resent and Ebetween(self.id, n1.get_id(), n1_suc_id):
            if self.id == n1.get_id():
                self.id += 1
                if self.id == n1_suc_id:
                    n1.set_status(OK)
                    return self.join(n1_suc)


        elif not resent:
            n1_new = n1.find_predecessor(self.id)
            n1.set_status(OK)
            return self.join(n1_new, True)

        else:
            if not Ebetween(self.id, n1.get_id(), n1_suc_id):
                return self.join(n1_suc, True)


        self.init_finger_table(n1)
        self.update_others()
        self.succ_succ = self.successor().successor() 
        self.pred_pred = self.get_pred().get_pred()
        self._status = OK
        n1.set_status(OK)
        ret = n1.set_my_data_to(self)
        deleted, not_deleted = (ret[0], ret[1])
        print(not_deleted)
        self.successor().data_base().delete_from_my_data(deleted, False, self.get_pred() != self.successor())
        self.successor().data_base().delete_from_my_data(not_deleted, True, self.get_pred() != self.successor())
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

        return OK
    
    @except_handler
    def update_finger_table(self,s,i):
        semi = s.get_id()
        if Ebetween(semi,self.id,self.finger[i].get_id()) and self.id!=semi:
            self.set_finger(i, s)
            p = self.get_pred()
            p.update_finger_table(s,i)

        return OK

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

        return OK

    # @except_handler
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

        return OK

    @except_handler
    def leave(self):
        while self.status() == BLOCKED:
            pass
        self.give_legacy()
        suc = self.successor()
        suc.set_pred(self.get_pred())
        suc.get_pred_from()
        self.predecessor.setSuccessor(self.successor())

        
        return self.update_others_leave()

    @except_handler
    def give_legacy(self):
        suc = self.successor()
        return suc.get_legacy()
        
        # sucsuc = suc.successor()
        # suc.data_base().merge_data()
        # line = ''
        # while True:
        #     line = suc.data_base().get_pred_data()
        #     if line == '':
        #         break

        #     sucsuc.data_base().addData(line[0],line[1],False)

    @except_handler
    def get_legacy(self, other=None):
        suc = self.successor() if other is None else other
        self.data_base().merge_data()
        line = ''
        while True:
            line = self.data_base().get_pred_data()
            if line == '':
                break

            suc.data_base().addData(line[0], line[1], False)

        return OK

    @except_handler
    def set_my_data_to(self, other):
        db = self.data_base()
        other_db = other.data_base()
        other_id = other.get_id()
        other_suc = other.successor()
        other_suc_id = other_suc.get_id()
        if other_suc_id is None:
            if other_suc == other.get_succ_succ:
                return None

            other_suc = other.setSuccessor(other.get_succ_succ())
            other_suc_id = other_suc.get_id()
            self.update_others_leave()

        line = ''
        to_delete = []
        not_deleted = []
        while True:
            line = db.get_my_data()
            if line == '':
                break
            
            if Ebetween(getHash(line[0]), other_id, other_suc_id):
                not_deleted.append(line[0])
                other_db.addData(line[0], line[1])

            else:
                to_delete.append(line[0])
                other_db.addData(line[0], line[1], False)

        other_db.delete_from_my_data(to_delete)
        return [to_delete, not_deleted]

    @except_handler
    def get_pred_from(self, other=None):
        db = self.data_base()
        target = other if not other is None else self.get_pred()
        target_db = target.data_base()
        target_id = target.get_id()
        if (target_id is None or target_db is None) and other is None:
            if self.get_pred() == self.get_pred_pred():
                return None

            self.set_pred(self.get_pred_pred())
            self.pred_pred = self.pred_pred.get_pred()
            self.update_others_leave()
            return self.get_pred_from()

        elif (target_id is None or target_db is None) and not other is None:
            return None

        line = ''
        # deleted = []
        # to_delete = []
        while True:
            line = target_db.get_my_data()
            if line == '':
                break

            db.addData(line[0], line[1], False)

        return OK

            

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
        while self.status() == BLOCKED:
            pass

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

