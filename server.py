import zmq
import time
# import basic_chord
import chord
import myDB
from rpc import My_RPC
import sys
import urllib.request
# IP = '127.0.0.1'
# port = 8080

# node = basic_chord.Node(basic_chord.getHash(IP + ":" + str(port)))
def start(IP, port, IP_dest=None, port_dest=None):
    node = chord.Node(chord.getHash(IP + str(port), 5))
    rpc = My_RPC((IP, port))#, method_dec=chord.check_none)
    rpc.register_class(chord.Node)
    rpc.register_class(myDB.MyDataBase)
    name = rpc.register_name(node, 'Node')
    name2 = rpc.register_name(node.data_base(), 'DB')
    if not IP_dest is None and not port_dest is None:
        other = rpc.request_item((IP_dest, port_dest), 'Node')
        node.join(other)

    else:
        node.join(node)

    # context = zmq.Context()
    # # Se crea un socket de tipo replay (REP)
    # socket = context.socket(zmq.REP)
    # # Asignarle al socket la dirección del server
    # socket.bind("tcp://*:%s" % (port+1))
    # while True:
    #     # Esperar por el próximo request de un cliente
    #     message = socket.recv_multipart()

    #     request_type = message[0].decode()
    #     http = message[1].decode()

    #     #get http request 
    #     if request_type == '0':
    #         send_data = node.get_file()
    #         if  send_data is None:
    #             send_data = urllib.request.urlopen(http).read().decode()
    #         time.sleep (1) # Esperar un tiempo
    #         socket.send_string(send_data)
        
    #     # set http request    
    #     else:
    #         body = message [2]
            
    #         send_data = 'save file ok'
    #         if not node.save_file(http,body):
    #             send_data = 'the file already exist'
            
    #         socket.send_string(send_data)

    http = 'https://www.prueba2.com'
    body =  '112121jdgwejdg'
    print('Waiting')
    while True:
        x = input()
        if x == '1':
            printNodes(node)

        elif x == '2':
            showFinger(node, 5)

        elif x == '3':
            node.leave()
        
        elif x == '4':
            print('Input Name:')
            name = input()
            print('Input Body:')
            body = input()
            node.save_file(name,body)
        
        elif x == '5':
            print('Get Name:')
            name = input()
            data = node.get_file(name)
            print (data)

def printNodes(node):
    print ('Ring nodes :')
    end = node
    print (node.get_id())
    while end != node.successor():
        node = node.successor()
        try:
            print (node.get_id())
        except:
            print ('not reached')
            break
    print ('-----------')

def showFinger(node, k):
    print ('Finger table of node ' + str(node.get_id()))
    print ('start:node')
    for i in range(k):
        print (str(node.start[i]) +' : ' +str(node.finger[i].get_id()))  
    print ('-----------')

if __name__ == "__main__":
    if len(sys.argv) <3:
        start('192.168.1.101',8080)
        raise Exception()

    elif len(sys.argv) == 3:
        start(sys.argv[1], int(sys.argv[2]))

    else:
        start(sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]))



  