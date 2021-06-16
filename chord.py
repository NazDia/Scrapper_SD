
import random
import hashlib
k = 6
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

class Node:
    def __init__(self, idx):
        self.id = idx
        self.finger = {}
        self.start = {}
        # self.predecessor = self
        for i in range(k):
            self.start[i] = (self.id+(2**i)) % (2**k)

    def get_id(self):
        return self.id

    def get_pred(self):
        return self.predecessor

    def set_pred(self, value):
        self.predecessor = value
        return self.predecessor

    def set_finger(self, i, value):
        self.finger[i] = value
        return value

    def successor(self):
        return self.finger[0]
    
    def find_successor(self,id):  
        if betweenE(id,self.get_pred().get_id(),self.id):
            return self
        n = self.find_predecessor(id)
        return n.successor()
    
    def find_predecessor(self,id):
        if id == self.id:
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
                self.finger[i] = self
            self.predecessor = self
        else:
            self.init_finger_table(n1)
            self.update_others()  

        return self
          
            
    def init_finger_table(self,n1):
        self.finger[0] = n1.find_successor(self.start[0])
        self.predecessor = self.successor().get_pred()
        self.successor().set_pred(self)
        self.predecessor.set_finger(0, self)
        for i in range(k-1):
            if Ebetween(self.start[i+1],self.id,self.finger[i].get_id()):
                self.finger[i+1] = self.finger[i]
            else :
                self.finger[i+1] = n1.find_successor(self.start[i+1])

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

    def update_others_leave(self):
        for i in range(k):
            prev  = decr(self.id,2**i)
            p = self.find_predecessor(prev)
            p.update_finger_table(self.successor(),i)

        return 'OK'

    def leave(self):
        self.successor().set_pred(self.get_pred())
        self.predecessor.setSuccessor(self.successor())
        return self.update_others_leave()
        
    def setSuccessor(self,succ):
        self.finger[0] = succ
        return succ