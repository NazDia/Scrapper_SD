from tkinter.constants import TRUE
import zmq
from tkinter import filedialog as FileDialog
import sys

IP = '127.0.0.1'
PORT = 8080

class Client:
    def __init__(self,IP,port):
        self.sock = zmq.Context().socket(zmq.REQ)
        self.severIP =IP
        self.port = port
        b=self.sock.connect(f'tcp://{IP}:{port}')
        

    def getHTTP(self,url):
        self.sock.send_multipart([b'0',url.encode()])
        http=self.sock.recv_string()
        return http
        

    def setHTTP(self,http,url):
        self.sock.send_multipart([b'1',http.encode(),url.encode()])
        status=self.sock.recv_string()
        if not status:
            pass
        return status

def openDialog():
    fichero = FileDialog.askopenfilename(title="Impor json")
    return fichero

def printMenu():
    print("\n1. Get HTTP \n2 Set HTTP\n")


if len(sys.argv)>=3:
    IP = sys.argv[1]
    PORT=int(sys.argv[2])

try:
    client=Client(IP,PORT)
    print('connect\n')
except:
    print('Failed to connect\n')
    pass

url = ''
url_HTTP = ''
importDir = ''

httpOut = ''

while True:
    
    printMenu()
    choice = input()
    if choice == '1':
        url = input('Write url\n')
        httpOut  =  client.getHTTP(url)
        print (f'httpOut :{httpOut}')
    
    if choice == '2':
        choice = input('1 Write pair <url>:<HTTP>\n2 import json\n')
        if choice == '1':
            url_HTTP = input('<url>:<HTTP>\n')
        if choice == '2':
            importDir = openDialog()
        
        status = client.setHTTP('asd','asd')
        print ('status : %s'% status)
            




