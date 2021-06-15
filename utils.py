import array
from typing import KeysView
import urllib.request
import myDB

bd = myDB.MyDataBase()
# http = 'https://www.twitter.com/'
# datos = urllib.request.urlopen(http).read().decode()
# bd.addData(http,datos)
# http = 'https://www.facebook.com/'
# datos = urllib.request.urlopen(http).read().decode()
# bd.addData(http,datos)
# http = 'https://www.youtube.com/'
# datos = urllib.request.urlopen(http).read().decode()
# bd.addData(http,datos)
# bd.saveData()

load=bd.loadData()

keys=bd.httpNameList()
a=9
    