import json

class MyDataBase:
    dicData = {}
    dataDir = 'data.json'
    nameList=[]
    def __init__(self):
        pass
    
    def addData(self,key,value):
       self.dicData[key]=value
    
    def removeData(self,key):
        self.dicData.pop(key)
    
    def saveData(self):
        with open(self.dataDir,'w') as file:
            json.dump(self.dicData,file,indent=4,ensure_ascii=False)
            file.close()
    def loadData(self):
        with open(self.dataDir) as file:
            data = json.load(file)
            file.close()
        return data

    def httpNameList(self):
        with open(self.dataDir) as file:
            data = json.load(file)
            file.close()
        return list(data.keys())






