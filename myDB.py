import json

class MyDataBase:
    dicData = {}
    dataDir = 'data.json'
    nameList=[]
    def __init__(self):
        pass
    
    def keys(self):
        return self.dicData.keys()

    def addData(self,key,value):
        self.dicData[key]=value
        return 'ok'
    def removeData(self,key):
        self.dicData.pop(key)
        return 'ok'

    def get_http(self,key):
        return self.dicData[key]


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






