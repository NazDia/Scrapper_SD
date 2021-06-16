import zmq
import threading
import inspect
import time

CALL = b'CALL'
ERROR = b'ERROR'
ANSWER = b'ANSWER'
REQUEST = b'REQUEST'

class My_RPC_Serializable:
    def __rpc_serialize__(self):
        pass


class My_RPC:
    def __init__(self, address):
        self._inherited_classes = {}
        self.val_dic = {}
        self.ival_dic = {}
        self.poller = zmq.Poller()
        self.dic = {}
        self.idic = {}
        self._address = address
        self._address_str = address[0] + '@' + str(address[1])
        self.context = zmq.Context()
        self.router = self.context.socket(zmq.ROUTER)
        self.router.bind('tcp://*:' + str(address[1]))
        self.poller.register(self.router)
        self.mutex = threading.Lock()
        self.requested = {}
        receiver = threading.Thread(target=self.requests_receive, args=[])
        receiver.start()

    def requests_receive(self):
        while True:
            while True:
                self.mutex.acquire()
                poller_res = dict(self.poller.poll(1000))
                if poller_res.get(self.router) & zmq.POLLIN == zmq.POLLIN:
                    # self.mutex.release()
                    break

                self.mutex.release()

            msg = self.router.recv_multipart()
            self.mutex.release()
            addr = msg[0:2]
            current_call = msg[2:]
            # for i in self._inherited_classes.keys():
            #     print(i)
            handler = threading.Thread(target=self.handler, args=[addr, current_call])
            handler.start()
            

    def handler(self, addr, call):
        if call[0] == CALL:
            self.handler_call(addr, call)

        elif call[0] == REQUEST:
            self.handler_request(addr, call)

    def handler_request(self, addr, call):
        obj = self.idic[call[1].decode('utf-8')]
        ans = [ ANSWER, self.serialize(obj) ]
        while True:
            self.mutex.acquire()
            poller_res = dict(self.poller.poll(1000))
            if not poller_res.get(self.router) is None and poller_res.get(self.router) & zmq.POLLOUT == zmq.POLLOUT:
                break

            self.mutex.release()

        self.router.send_multipart(addr + ans)
        self.mutex.release()
        
    def handler_call(self, addr, call):
        obj = self.idic[call[1].decode('utf-8')]
        params = [ self.deserialize(x) for x in call[3:] ]
        semi_ans = getattr(obj, call[2].decode('utf-8'))(*params)
        ans = [ ANSWER, self.serialize(semi_ans) ]
        while True:
            self.mutex.acquire()
            poller_res = dict(self.poller.poll(1000))
            if not poller_res.get(self.router) is None and poller_res.get(self.router) & zmq.POLLOUT == zmq.POLLOUT:
                break

            self.mutex.release()

        self.router.send_multipart(addr + ans)
        # print('sent')
        self.mutex.release()

    def register_class(self, class_x):
        address = self._address
        address_str = self._address_str
        dic = self.dic
        idic = self.idic
        inh_classes = self._inherited_classes
        deserialize = self.deserialize
        serialize = self.serialize
        mutex = self.mutex
        poller = self.poller
        context = self.context
        ival_dic = self.ival_dic
        class RPC_sub(class_x):
            __rpc_context = None
            __rpc_address = None
            __rpc_mutex = None
            __rpc_class_name = ''
            __rpc_name = ''
            __rpc_dics = (dic, idic)
            def __init__(self, class_name, name, addressx=None):
                self.__rpc_name = name
                self.__rpc_class_name = class_name
                self.__rpc_address = addressx if not addressx is None else address
                method_names = [name for name in dir(class_x) if callable(getattr(class_x, name))]
                for name in method_names:
                    #Create new methods
                    f = self.__create_func__(name)
                    try:
                        setattr(self, name, f)

                    except TypeError:
                        pass

            def __create_func__(self, name):
                if name[0] == '_':
                    def f(*args):
                        raise Exception("Can't call private methods.")

                else:
                    def f(*args):
                        f_args = []
                        for i in args:
                            # print(i.__class__.__name__)
                            f_args.append(serialize(i))
                            # if i.__class__.__name__ in inh_classes.keys():
                            #     if i in ival_dic.keys():
                            #         f_args.append(ival_dic[i].__rpc_serialize())
                            #     # f_args.append(inh_classes[i.__class__.__name__](i).__rpc_serialize__())

                            # elif i.__class__.__name__ == 'int':
                            #     f_args.append(b'int:' + bytes([i]))

                            # elif i.__class__.__name__ == 'string':
                            #     f_args.append(b'string:' + bytes(i, 'utf-8'))

                            # elif i.__class__.__name__ == 'float':
                            #     raise NotImplementedError()

                            # else:
                            #     raise NotImplementedError()
                            
                        sock = zmq.Context().socket(zmq.REQ)
                        sock.connect('tcp://%s:%s' % self.__rpc_address)
                        sock.send_multipart([CALL, bytes(self.__rpc_name, 'utf-8'), bytes(name, 'utf-8')] + [ x for x in f_args])
                        # poller = zmq.Poller()
                        # poller.register(sock, zmq.POLLIN)
                        my_poller = zmq.Poller()
                        my_poller.register(sock, zmq.POLLIN)
                        counter = 3
                        while True:
                            poll_res = dict(my_poller.poll(1000))
                            if not poll_res.get(sock) is None and poll_res.get(sock) & zmq.POLLIN != zmq.POLLIN:
                                if counter <= 0:
                                    my_poller.unregister(sock)
                                    print('Unable to reach the address')
                                    # raise Exception('Unable to reach the address\'s process')

                                counter -= 1
                                continue
                            
                            # print('receiving')
                            time.sleep(0.1)
                            ret = sock.recv_multipart()
                            mutex.acquire()
                            if ret[0] == ANSWER:
                                my_poller.unregister(sock)
                                mutex.release()
                                return deserialize(ret[1])

                            if ret[0] == ERROR:
                                my_poller.unregister(sock)
                                mutex.release()
                                raise Exception()
                                # For error handling

                return f


            def __update__(self, other):
                dicx = self.__rpc_dics[0]
                for key in other.__dict__.keys():
                    attr = getattr(other, key)
                    if attr in dicx:
                        attr = dicx[attr]

                    setattr(self, key, attr)

            def __rpc_serialize__(self):
                return bytes(self.__rpc_class_name, 'utf-8') + b':' + bytes(self.__rpc_name, 'utf-8')
            
        self._inherited_classes[class_x.__name__] = RPC_sub

    def register_name(self, val, xname, address=None):
        if address is None:
            name = self._address_str + '$' + xname

        else:
            name = address[0] + '@' + str(address[1]) + '$' + xname
            
        self.dic[name] = self._inherited_classes[val.__class__.__name__](val.__class__.__name__, name, address)
        self.idic[name] = val
        self.val_dic[self.dic[name]] = val
        self.ival_dic[val] = self.dic[name]
        return name

    def deserialize(self, obj):
        new_obj = obj.decode('utf-8')
        semi_ret = new_obj.split(':')
        if semi_ret[0] == 'int':
            ret = int.from_bytes(bytes(semi_ret[1], 'utf-8'), 'big')
            return ret

        elif semi_ret[0] == 'float':
            return float(semi_ret[1])

        elif semi_ret[0] == 'str':
            return semi_ret[1]

        elif semi_ret[0] in self._inherited_classes.keys():
            try:
                temp = self.dic[semi_ret[1]]
            
            except KeyError:
                a1 = semi_ret[1].split('$')[0].split('@')
                addr = (a1[0], int(a1[1]))
                temp = self._inherited_classes[semi_ret[0]](semi_ret[0], semi_ret[1], addr)
                self.dic[semi_ret[1]] = temp

            try:
                ret = self.val_dic[temp]

            except KeyError:
                ret = temp

            return ret

        else:
            raise Exception()

    def serialize(self, obj):
        if obj.__class__.__name__ in self._inherited_classes.keys() and obj in self.ival_dic.keys():
            return self.ival_dic[obj].__rpc_serialize__()

        elif obj.__class__.__name__ == 'RPC_sub':
            return obj.__rpc_serialize__()

        elif obj.__class__.__name__ == 'int':
            return b'int:' + bytes([obj])

        elif obj.__class__.__name__ == 'str':
            return b'str:' + bytes(obj, 'utf-8')

        elif obj.__class__.__name__ == 'float':
            raise NotImplementedError()

        elif obj.__class__.__name__ == 'list':
            ret = b'['
            for i in obj:
                ret += self.serialize(i)

            ret += b']'
            return ret

        else:
            raise NotImplementedError()

    def request_item(self, address, name):
        req = self.context.socket(zmq.REQ)
        req.connect("tcp://%s:%s" % address)
        req.send_multipart([REQUEST, bytes(address[0], 'utf-8') + b'@' + bytes(str(address[1]), 'utf-8') + b'$' + bytes(name, 'utf-8')])
        poller = zmq.Poller()
        poller.register(req, zmq.POLLIN)
        count = 10
        while True:
            poll = dict(poller.poll(1000))
            if poll.get(req) is None or poll.get(req) & zmq.POLLIN != zmq.POLLIN:
                if count <= 0:
                    raise Exception()

                count -= 1
                continue

            time.sleep(0.1)
            ret = req.recv_multipart()

            return self.deserialize(ret[1])

