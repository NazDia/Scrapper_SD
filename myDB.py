import json
from os import truncate
from typing import Counter

class MyDataBase:
    __dicData__ = {}
    my_data = 'DataBase/my_data'
    pred_data = 'DataBase/pred_data '
    nameList=[]
    cache_size = 5 
    cache_counter = 0
    cache_elems = []
    pop_item = None
    current_reading = None
    def __init__(self):
        # try:
        #     open(self.my_data,'r')
        #     open(self.pred_data,'r')
        # except:  
            open(self.my_data,'w')
            open(self.pred_data,'w')
        
    def dicData(self):
        return self.__dicData__

    def keys(self):
        return self.____dicData____.keys()

    def addData(self,key,value,self_data=True):
        dir = self.my_data if self_data else self.pred_data
        
        if len(self.__dicData__)>=self.cache_size:
            self.__dicData__.pop(self.cache_elems[self.cache_counter])
            self.cache_elems[self.cache_counter]=key
        else: 
            self.cache_elems.append(key)
        self.cache_counter = (self.cache_counter + 1) % self.cache_size
        self.__dicData__[key]=value
        
        with open(dir,'r+') as file:
            while  True:
                line = file.readline()
                if line == key+'\n':
                    file.close()
                    return 'ok'
                if not line:
                    break
            
            file.write(key+'\n')
            file.close()
        
        with open('DataBase/'+key,'w') as file:
            file.write(value)
            file.close()
        return 'ok'

    def contains(self,key):
        if key in self.__dicData__:
            return True
        else:
            with open(self.my_data,'r') as file:
                while  True:    
                    line = file.readline()
                    if line == key+'\n':
                        file.close()
                        return True
                    if not line:
                        break
                file.close()
            return False
            

    def get_http(self,key):
        try:
            dirx = 'DataBase/' + key
            with open(dirx,'r') as file:
                data = file.read()
                file.close()
                return data
        except:
            return 'not found'

    def merge_data(self):
        read = ''
        with open(self.pred_data,'r') as file:
            read = file.read()
            file.close()
        
        with open(self.my_data,'a') as file:
            file.write(read)
            file.close()
        return 'ok'

    def get_pred_data(self):
        if self.current_reading is None:
<<<<<<< HEAD
            file = open(self.pred_data,'r')
=======
            file =  open(self.pred_data,'r') 
>>>>>>> bd5a5e63cb4db5fe3164d922333d97f4bda20859
            self.current_reading = file

        line = self.current_reading.readline()
        if not line:
            self.current_reading.close()
            self.current_reading = None
            return ''

        line = line[0:-1]
        dir = 'DataBase/'+ line
        with open(dir,'r') as file2:
            ret=[line,file2.read()]
            file2.close()

        return ret

            
            # while  True:    
            #     line = file.readline()
            #     if not line:
            #         break
            #     line = line[0:-1]
            #     dir = 'DataBase/'+ line
            #     with open(dir,'r') as file2:
            #         ret=[line,file2.read()]
            #         file2.close()
            #         yield ret

            # file.close()
        
