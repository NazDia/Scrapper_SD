import json
from os import truncate

class MyDataBase:
    dicData = {}
    my_data = 'DataBase/my_data'
    prec_data = 'DataBase/prec_data '
    nameList=[]
    def __init__(self):
        try:
            open(self.my_data,'r')
            open(self.prec_data,'r')
        except:  
            open(self.my_data,'w')
            open(self.prec_data,'w')
        
    
    def keys(self):
        return self.dicData.keys()

    def addData(self,key,value,self_data=True):
        dir = self.my_data if self_data else self.prec_data

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

    def get_http(self,key):
        try:
            with open(key,'r') as file:
                data = file.read()
                file.close()
                return data
        except:
            return 'not found'

    def merge_data(self):
        read = ''
        with open(self.prec_data,'r') as file:
            read = file.read()
            file.close()
        
        with open(self.my_data,'a') as file:
            file.write(read)
            file.close()
        return 'ok'



    def removeData(self,key):
        self.dicData.pop(key)
        return 'ok'

    


    def saveData(self):
        with open(self.dataDir,'w') as file:
            json.dump(self.dicData,file,indent=4,ensure_ascii=False)
            file.close()
        return 'ok'
            
    def loadData(self):
        with open(self.dataDir) as file:
            data = json.load(file)
            file.close()
        
        self.dicData = data
        return data

    def httpNameList(self):
        with open(self.dataDir) as file:
            data = json.load(file)
            file.close()
        return list(data.keys())




