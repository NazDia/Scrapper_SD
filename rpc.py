import zmq
import threading
import inspect
import time

CALL = b'CALL'
ERROR = b'ERROR'
ANSWER = b'ANSWER'
REQUEST = b'REQUEST'
SENT = 'SENT'
RECEIVED_ERR = 'RECEIVED_ERR'
TIMEOUT = 'TIMEOUT'

def raiser(*args):
    raise Exception(*args)

def default_err_handler(*args):
    if args[0] == TIMEOUT:
        # print('Error Handler')
        return None

    elif args[0] == RECEIVED_ERR:
        raise Exception(*args[1:])

class My_RPC_Serializable:
    def __rpc_serialize__(self):
        pass


class My_RPC:
    def __init__(self, address, timeout=1000, to_count=3, error_handler=default_err_handler):
        self._inherited_classes = {}
        self.val_dic = {}
        self.ival_dic = {}
        self.poller = zmq.Poller()
        self.dic = {}
        self.idic = {}
        self.timeout = timeout
        self.to_count = to_count
        self.error_handler = error_handler
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
        timeout = self.timeout
        counter = self.to_count
        ival_dic = self.ival_dic
        handler_err = self.error_handler
        class RPC_sub(class_x):
            __rpc_broken = False
            __rpc_context = context
            __rpc_address = None
            __rpc_mutex = None
            __rpc_class_name = ''
            __rpc_name = ''
            __rpc_dics = (dic, idic)
            def __init__(self, class_name, name, addressx=None):
                self.__rpc_error_handler = handler_err
                self.__rpc_count = counter
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
                        # if self.__rpc_broken:
                        #     print('Broken')
                        #     return None

                        f_args = []
                        for i in args:
                            f_args.append(serialize(i))
                            
                        sock = context.socket(zmq.REQ)
                        sock.connect('tcp://%s:%s' % self.__rpc_address)
                        sock.send_multipart([CALL, bytes(self.__rpc_name, 'utf-8'), bytes(name, 'utf-8')] + [ x for x in f_args])
                        my_poller = zmq.Poller()
                        my_poller.register(sock, zmq.POLLIN)
                        counter = self.__rpc_count
                        while True:
                            # print('Polling')
                            poll_res = dict(my_poller.poll(timeout))
                            if poll_res.get(sock) is None or poll_res.get(sock) & zmq.POLLIN != zmq.POLLIN:
                                if counter <= 0:
                                    my_poller.unregister(sock)
                                    sock.close()
                                    # self.__rpc_broken = True
                                    # print('Unable to reach the address')
                                    ret = self.__rpc_error_handler(TIMEOUT)
                                    # print(ret)
                                    return ret

                                counter -= 1
                                continue
                            
                            time.sleep(0.1)
                            ret = sock.recv_multipart()
                            mutex.acquire()
                            if ret[0] == ANSWER:
                                my_poller.unregister(sock)
                                sock.close()
                                mutex.release()
                                return deserialize(ret[1])

                            if ret[0] == ERROR:
                                my_poller.unregister(sock)
                                sock.close()
                                mutex.release()
                                return self.error_handler(RECEIVED_ERR, self.deserialize(ret[1]))

                return f


            def __update__(self, other):
                dicx = self.__rpc_dics[0]
                for key in other.__dict__.keys():
                    attr = getattr(other, key)
                    if attr in dicx:
                        attr = dicx[attr]

                    setattr(self, key, attr)

            def __rpc_serialize__(self):
                return bytes(self.__rpc_class_name, 'utf-8') + b'~' + bytes(self.__rpc_name, 'utf-8')
            
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
        semi_ret = new_obj.split('~')
        if semi_ret[0] == 'int':
            return int(semi_ret[1])

        elif semi_ret[0] == 'float':
            return float(semi_ret[1])

        elif semi_ret[0] == 'str':
            return semi_ret[1]

        elif semi_ret[0] == 'list':
            temp = '~'.join(semi_ret[1:])[1:-1]
            end = []
            count = 0
            end.append('')
            for i in temp:
                if i == ']':
                    count -= 1
                    end[-1] += i

                elif i == '[':
                    count += 1
                    end[-1] += i

                elif i == ',' and count == 0:
                    end.append('')

                elif i == ' ':
                    pass

                else:
                    end[-1] += i

            for i in end:
                if len(i) == 0:
                    end.remove(i)

            ret = [ self.deserialize(x.encode('utf-8')) for x in end ]
            return ret


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
            raise NotImplementedError()

    def serialize(self, obj):
        if obj.__class__.__name__ in self._inherited_classes.keys() and obj in self.ival_dic.keys():
            return self.ival_dic[obj].__rpc_serialize__()

        elif obj.__class__.__name__ == 'RPC_sub':
            return obj.__rpc_serialize__()

        elif obj.__class__.__name__ == 'int':
            return b'int~' + bytes(str(obj), 'utf-8')

        elif obj.__class__.__name__ == 'str':
            return b'str~' + bytes(obj, 'utf-8')

        elif obj.__class__.__name__ == 'float':
            raise NotImplementedError()

        elif obj.__class__.__name__ == 'list':
            ret = b'list~['
            for i in obj:
                ret += self.serialize(i) + b','

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
        count = self.to_count
        while True:
            poll = dict(poller.poll(self.timeout))
            if poll.get(req) is None or poll.get(req) & zmq.POLLIN != zmq.POLLIN:
                if count <= 0:
                    req.close()
                    return self.error_handler(TIMEOUT)

                count -= 1
                continue

            time.sleep(0.1)
            ret = req.recv_multipart()
            req.close()

            return self.deserialize(ret[1])

rpc = My_RPC(('127.0.0.1', 8000))
a = rpc.serialize(50000)
print(a)
b = rpc.deserialize(a)
print(b)