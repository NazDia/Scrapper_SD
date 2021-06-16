import zmq
import time
# import basic_chord
import chord
import myDB
from rpc import My_RPC
import sys

# IP = '127.0.0.1'
# port = 8080

# node = basic_chord.Node(basic_chord.getHash(IP + ":" + str(port)))
def start(IP, port, IP_dest=None, port_dest=None):
    node = chord.Node(chord.getHash(IP + str(port), 5))
    rpc = My_RPC((IP, port))
    rpc.register_class(chord.Node)
    name = rpc.register_name(node, 'Node')
    if not IP_dest is None and not port_dest is None:
        other = rpc.request_item((IP_dest, port_dest), 'Node')
        node.join(other)

    else:
        node.join(node)

    print('Waiting')
    while True:
        x = input()
        if x == '1':
            printNodes(node)

        elif x == '2':
            showFinger(node, 5)

        elif x == '3':
            node.leave()

def printNodes(node):
    print ('Ring nodes :')
    end = node
    print (node.get_id())
    while end != node.successor():
        node = node.successor()
        print (node.get_id())
    print ('-----------')

def showFinger(node, k):
    print ('Finger table of node ' + str(node.get_id()))
    print ('start:node')
    for i in range(k):
        print (str(node.start[i]) +' : ' +str(node.finger[i].get_id()))  
    print ('-----------')

if __name__ == "__main__":
    if len(sys.argv) <3:
        raise Exception()

    elif len(sys.argv) == 3:
        start(sys.argv[1], int(sys.argv[2]))

    else:
        start(sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]))



# context = zmq.Context()
# # Se crea un socket de tipo replay (REP)
# socket = context.socket(zmq.REP)
# # Asignarle al socket la dirección del server
# socket.bind("tcp://*:%s" % port)
# while True:
#     # Esperar por el próximo request de un cliente
#     message = socket.recv_multipart()
#     print ("Received request: ", message)
#     time.sleep (1) # Esperar un tiempo
#     # Responder mensaje al cliente
#     socket.send_string("World from %s" % port)