


from twisted.internet.protocol import DatagramProtocol
from eotudata.eotudata import eotudata
import json,sys
from dc_utils.dc_log import logging

'''
走 eotudata 协议，
STUN协议后续再补充，解析组装在stun data中
'''


class worker(DatagramProtocol):
    
    # tell user "I am working now"
    # def startProtocol(self):
    #     addr = ("192.168.1.1",1234)
    #     self.transport.connect(addr)
    #     print("now we can only send to host %s port %d" % addr)
    #     self.transport.write("hello") # no need for address

    reactor = None


    clients= {}

    def __init__(self,reactor):
        self.reactor = reactor



    def register_handle(self,reg_json,addr):
        try:
            self.clients[reg_json["uid"]] =  {
                "addr":addr,
                "channel":reg_json["channel"]
            }
            res = json.dumps(self.clients)
            logging.info(res)
            self.transport.write(b"ok",addr) # no need for address
        except Exception as e:
            logging.error(e)
            self.transport.write(b"error!",addr) # no need for address

    def ask_user_handle(self,reg_json,addr):
        try:
            ask_uid = reg_json["ask_uid"]
            if ask_uid in self.clients:
                res = json.dumps(self.clients[ask_uid])
                bytes_res=bytes(res,encoding="utf-8")
                logging.info(res)
                self.transport.write(bytes_res,addr) # no need for address
            else:
                self.transport.write(b"not found in server",addr) # no need for address
        except Exception as e:
            logging.error(e)
            self.transport.write(b"error!",addr) # no need for address 

    json_method_cb={
        "register":register_handle,
        "ask_user":ask_user_handle
    }


    def p2p_json_method_handle(self,reg_json,addr):
        if "method" in reg_json:
            method = reg_json["method"]
            if method in self.json_method_cb:
                try:
                    self.json_method_cb[method](self,reg_json,addr)
                except Exception as e:
                    print(e)
                    sys.exit(-1)
            else:
                logging.error("no method field in json_method_cb")
        else:
            logging.error("no method field in reg_json")


    def datagramReceived(self, data, addr):

        logging.info("CLIENT[%s:%d] visit now! " % (addr[0], addr[1]))
        logging.info(data)
        obj_recv = eotudata().get_content(data)
   
        if obj_recv == None:
            logging.error("eotudata parase is NONE")
            self.reactor.stop()
            return 

        if obj_recv[0] == 1:
            content = obj_recv[1]
            recv_json = json.loads(content)
            self.p2p_json_method_handle(recv_json,addr)
   


    # Possibly invoked if there is no server listening on the
    # address to which we are sending.
    def connectionRefused(self):
        print("No one listening")


