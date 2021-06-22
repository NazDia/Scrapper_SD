import array
from typing import KeysView
import urllib.request
import myDB

#bd = myDB.MyDataBase()
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

a = {2:'3'}
b = {3:'3'}
for key in a.keys():
    if not key in b:
        b[key]=a[key]

for value in b.values():
    print(value)
    

