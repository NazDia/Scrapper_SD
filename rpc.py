import zmq
import threading
import inspect

class My_RPC:
    def __init__(self, address):
        self._inherited_classes = {}
        self.dic = {}
        self._address = address
        self.context = zmq.Context()
        self.router = self.context.socket(zmq.ROUTER)
        self.router.bind('tcp://%s:%s' % address)
        self.mutex = threading.Lock()
        self.requested = {}


    def requests_receive(self):
        poller = zmq.Poller()
        poller.register(self.router)
        while True:
            while True:
                self.mutex.acquire()
                if len(poller.poll(1000) == 0):
                    break

                self.mutex.release()

            msg = self.router.recv_multipart()
            self.mutex.release()
            addr = msg[0:2]
            current_call = msg[2:]
            threading.Thread(target=self.handler, args=[addr, current_call])
            

    def handler(self, addr, call):
        #
        # Solve call
        #
        ans = []
        self.mutex.acquire()
        self.router.send_multipart([addr + ans])
        self.mutex.release()

    def register_class(self, class_x):
        address = self._address
        dic = self.dic
        class RPC_sub(class_x):
            __rpc_address = address
            def __init__(self, other):
                method_names = [name for name in dir(class_x) if callable(getattr(class_x, name))]
                for name in method_names:
                    #Create new methods
                    pass

            def __serialize__(self):
                pass

            def __update__(self, other):
                for key in other.__dict__.keys():
                    attr = getattr(other, key)
                    if attr in dic:
                        attr = dic[attr]

                    setattr(self, key, attr)
            
        self._inherited_classes[class_x.__name__] = RPC_sub

    def register_name(self, val):
        self.dic[val] = self._inherited_classes[val.__class__.__name__](val)

