montar un varios server en consolas distintas,funciona en maquinas distintas tambien, en este caso va a ser un IP local

consola 1
$ python3 server.py 127.0.0.1 8080

consola 2
$ python3 server.py 127.0.0.1 4040 127.0.0.1 8080

consola 3
$python3 server.py 127.0.0.1 15456 127.0.0.1 4040

crear un cliente y conectarlo a cualquier nodo
python3 client.py 127.0.0.1 8080
insertar datos en el cliente con set http si lo desea o simplemente pedir una URL que exista en la internet, que en caso de que no este almacenada en el sistema se busca internet y automáticamente se guarda en la base de datos.

pude agregar tantos nodos de server y cliente como desee,si algun cliente deja de funcionar el sistema se estabilizará y no se perderá ningún dato.Para quitar un server simplemente cierre la consolo,haga un interrupcion con el teclado o pasele de input 3 a la consola del server




