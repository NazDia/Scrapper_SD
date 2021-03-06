# Scrapper_SD
> Autors:
> Adrian Hernández Pérez
> Damian Ohallorans


## Ejecucion
### Server
Para ejecutar el server 
$python3 server.py <IP> <PUERTO>
eso  crea un nodo de server con esa direccion

Si queremos unir otro nodo de servidor ponemos
$python3 server.py <IP> <PUERTO> <IP_JOIN> <PUERTO_JOIN>

siempre que exista un servidor ejecutandose con ese ip puerto se va a poder unir,eso crea un sistema chord distribuido 

### Cliente
Para ejecutar cliente 
$python3 client.py <SERVER_IP> <SERVER_PORT>

ahi se ven las opciones get http y set http,se teclea el numero de lo que se desea hacer y se siguen las instrucciones que te da la consola 
## Detalles de implementación
### My_RPC:
My_RPC es una clase que se encarga simular los "Remote Procedure Calls", en el caso nuestro se logra creando clases 'vacias' con los mismos metodos de las clases registradas, pero modificando estos para que, en vez de llamar el metodo localmente, busque en la red la ubicacion donde esta el recurso real para que a su vez, sea el quien ejecute dicho metodo y envie la respuesta de vuelta por la red, devolviendo asi, los metodos modificados la respuesta dada por el objeto original (que recibimos de la red) con los mismos parametros que se le enviaron (se envian por la red al nodo donde se encuentra el recurso original) al metodo modificado.

Nuestra clase My_RPC es la que se encarga de la mayor parte del trabajo con las redes en nuestro proyecto, y para lograr esto, esta usa un patron "Dispatcher-Worker", cada metodo modificado envia un 'request' para hacer un llamado al metodo original, ante lo cual el nodo al que pertenece el recurso llamado creara un trabajador (un hilo nuevo) que resolvera dicho 'request' y le respondera. El patron "Dispatcher-Worker" en este caso fue simulado con la biblioteca py-zmq esando sockets REQ (de los cuales pueden haber muchos por cada clase My_RPC) enviando 'requests' a sockets ROUTER (solo existe uno por clase My_RPC, que dado los 'requests' que recibe crea un hilo para resolver dicho 'request').

Para lograr una abstraccion en gran medida de el trabajo en la red con My_RPC, My_RPC crea una clase RPC_Sub(classx) por cada clase que se registre, la cual hereda de la clase registrada; al registrar un nombre se crea una instancia de dicha clase que al crearse tambien modificara todos sus atributos llamables (para tomar los metodos) de tal forma que su nueva funcionalidad sea llamar al nodo en el cual se encuentra el recurso original usando el patron "Dispatcher-Worker" y recibira como respuesta lo que devolvio el objeto original o en caso de un timeout (el cual por defecto ocurrira despues de 9 segundos) u otro tipo de error que se reciba por la red el error handler del rpc tomara accion (el cual es modificable).

Para poder enviar los parametros y respuestas de los llamados por la red es necesario un serializado, en el caso de algunas clases basicas del lenguaje se usa la biblioteca pickle para realizar dicho serializado, en caso contrario, si es una clase registrada y el nombre (ambos atributos enviados por la red) recibido esta registrado el serializado devolvera la clase original, en caso de que la clase este registrada y el nombre no, se devolvera una instancia de la clase RPC_Sub que herede de la clase recibida y que dirija sus llamados a la red a la direccion correcta, en caso de que la clase recibida no este registrada se lanzara una exepcion, el deserializado es la operacion inversa, por lo cual la explicacion es similar.

A pesar de las comodidades que nos brinda la clase My_RPC, con esta nos es completamente imposible acceder a los atributos de la clase original, por tanto, queda por parte de quien use My_RPC crear los metodos get y set por cada atributo para acceder a ellos de esta forma.

//Comentario : Hay mucho codigo comentado en la clase My_RPC :|

### Chord:
En el script de chord hemos hecho la implementacion basica de Chord casi que olvidandonos completamente de que se trabajara en una red (lo cual es posible gracias a la clase My_RPC), implementando los metodos get y set de cada atributo y ademas un error handling en caso de que los llamados de RPC devuelvan None o lanzen un error, no logramos implementar el metodo de abandonar el chord enviando solo $O(log^2N)$ mensajes, por lo que decidimos hacerlo enviando $O(N)$ mensajes.

Los metodos give_legacy, get_legacy, al igual que get_pred_from y set_my_data_to son usados en los casos en los que un nodo abandona o es perdido del sistema distribuido, estos ayudan a reordenar los datos de la base de datos y colocarlos donde es debido. Es posible obtener los datos de un nodo caido debido que cada nodo va a guardar los datos propios y los datos de su predecesor, en caso de que un nodo caiga, su sucesor, al darse cuenta, tomara los datos guardados del nodo caido (que ya tenia guardados como medida preventiva) como propios y despues de actualizarse su predecesor, tomara los datos de este para el caso en que algun otro nodo caiga (Notar que en dicho sistema no es posible recuperarse de la caida de dos nodos tales que uno es sucesor del otro chord/base de datos).

Otro uso de los metodos get_pred_from y set_my_data_to es en el join de un nodo nuevo, a dicho nodo podrian pertenecerle algunos datos que ya estan presentes en la base de datos (los cuales se encontraran en su predecesor por el algoritmo de chord) por los cuales estos metodos se usan para otorgarle dichos datos al nuevo nodo.

Los nodos de Chord tienen dos formas de darse cuenta de que falta un nodo, la primera que el deje el sistema voluntariamente, en cuyo caso todo el sistema sera notificado y la otra sera mediante el metodo ping, el cual intentara tomar el estado del sucesor y el predecesor del nodo actual y hara los cambios necesarios en el caso de no encontrar alguno.

//Comentario # 2 : A pesar de la tarea de Chord, en este script nos pasamos mas del 70% del tiempo dedicado al proyecto :|

### myDB:
La clase myDB es la encargada de hacer la gestion con los datos, simulando una base de datos, los datos son guardados en el disco, pero tenemos una cache implementada con un algoritmo de reemplazo de datos LIFO que guarda una determinada cantidad de datos en RAM que si esta el dato en cache se obtendría el dato mas rápido, el tamaño de la cache es seteable según los recursos de la PC en la que se esta ejecutando el servidor.
