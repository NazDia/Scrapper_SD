import zmq
import time
import basic_chord
import myDB

IP = '127.0.0.1'
port = 8080

node = basic_chord.Node(basic_chord.getHash(IP + ":" + str(port)))


context = zmq.Context()
# Se crea un socket de tipo replay (REP)
socket = context.socket(zmq.REP)
# Asignarle al socket la dirección del server
socket.bind("tcp://*:%s" % port)
while True:
    # Esperar por el próximo request de un cliente
    message = socket.recv_multipart()
    print ("Received request: ", message)
    time.sleep (1) # Esperar un tiempo
    # Responder mensaje al cliente
    socket.send_string("World from %s" % port)