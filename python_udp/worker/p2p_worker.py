


from twisted.internet.protocol import DatagramProtocol
from eotudata.eotudata import eotudata
import json,sys
from dc_utils.dc_log import logging
from dc_utils.convert_utils import int_to_unsiged_array

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

    #   程序运行致命错误，调用reactor.stop()停止！
    reactor = None 

    #用户存储信息，后续加载到redius中
    clients= {}

    def __init__(self,reactor):
        self.reactor = reactor

    def transport_write_back(self,data,addr):
        
        res = b"UNEXCEPT for transport_write_back"
        if isinstance(data,str):
            res = bytes(data,encoding="utf-8")
        elif isinstance(data,dict) :
            tmp = json.dumps(self.clients)
            res = bytes(tmp,encoding="utf-8")
        elif isinstance(data,bytes):
            res = data
        elif isinstance(data,int):
            res = bytes(data,encoding="utf-8")
        else:
            res = b"SERVER INTER ERROR! What data type to send!"
            logging.error(res)

        logging.debug("SERVER RESPONSE:%s",res)
        self.transport.write(res,addr) 
        logging.debug("SERVER RESPONSE SEND END \n\n")

    def register_handle(self,reg_json,addr):
        #必须包含的字段！
        register_fields = ("uid","channel")

        try:
            if False in map(lambda x:True if x in reg_json else False, register_fields ):
                raise Exception("reg_json field ERROR")

            uid = reg_json["uid"]
            self.clients[uid] =  {
                "addr":addr,
                "channel":reg_json["channel"]
            }
            self.transport_write_back("ok",addr)
        except Exception as e:
            logging.error(str(e))
            self.transport_write_back(str(e),addr) 

    #将请求的用户信息返还
    def ask_user_handle(self,reg_json,addr):
        #必须包含的字段！
        register_fields = ("ask_uid","channel")

        try:
            if False in map(lambda x:True if x in reg_json else False, register_fields ):
                raise Exception("reg_json field ERROR")
            
            res = None
            ask_uid = reg_json["ask_uid"]
            if ask_uid in self.clients:
                res = self.clients[ask_uid]
                res["uid"] = ask_uid
                res = json.dumps(res)
                #res = json.dumps(self.clients[ask_uid])
            else:
                res = "error! user[%d] not found in server" % (ask_uid)
                logging.debug(res)
            self.transport_write_back(res,addr)

        except Exception as e:
            logging.error(str(e))
            self.transport_write_back(str(e),addr)

    #将请求的用户信息返还
    def ask_user_all_handle(self,reg_json,addr):
        try:
            self.transport_write_back(self.clients,addr)
        except BaseException as e:
            print(e)
            raise BaseException("SERVER INTER ERROR ! ask_user_all handle error")

    def turn_data_handle(self,json_data,stream_data,addr,org_data):

        turn_data_fields = ("to_uid","from_uid")
        try:
            if False in map(lambda x:True if x in json_data else False, turn_data_fields ):
                raise Exception("reg_json field ERROR")

            to_uid = json_data["to_uid"]
            if to_uid[0] in self.clients:
                to_addr = self.clients[to_uid[0]]["addr"]
                self.transport_write_back(org_data,to_addr)
                self.transport_write_back(b"turn ok",addr)
            else:
                self.transport_write_back(b"turn fail, user not registed!",addr)

        except Exception as e:
            logging.error(e)
            self.transport_write_back(e.__str__,addr)

    #
    #   method 回调函数
    #
    method_cb={
        "ask_user_all":ask_user_all_handle,
        "register":register_handle,
        "ask_user":ask_user_handle,
        "turn_data":turn_data_handle
    }

    prttwo_method_cb={
        "turn_data":turn_data_handle
    }

    """
        接收数据利用method_cb处理
    """
    def prtone_method_handle(self,reg_json,addr):
        res = "UNEXCEPT for prtone_method_handle"
        if "method" in reg_json:
            method = reg_json["method"]
            if method in self.method_cb:
                try:
                    self.method_cb[method](self,reg_json,addr)
                    return 
                except BaseException as e:
                    logging.error(e)
                    res = str(e)
            else:
                res ="method[%s] not support in reg_json" %method
        else:
            res ="no method field in reg_json"
        
        logging.error(res)
        self.transport_write_back(res,addr)


    def prttwo_method_handle(self,json_data,stream_data,addr,org_data=None):
        if "method" in json_data:
            method = json_data["method"]
            self.prttwo_method_cb[method](self,json_data,stream_data,addr,org_data)


    """
        接收数据
    """
    def datagramReceived(self, data, addr):

        logging.info("CLIENT[%s:%d] visit now! ----------- " % (addr[0], addr[1]))
        logging.debug("SERVER RECIEVED: %s" % data)
        protocol,pdata = eotudata().get_content(data)  # return (protocol, data)
   
        if protocol == 1:
            content = pdata
            recv_json = json.loads(content)
            self.prtone_method_handle(recv_json,addr)
        elif protocol == 2:
            try:
                json_data = json.loads(pdata[0].decode(encoding="utf-8"))
                logging.debug("turn data is %s" % pdata[1])
                self.prttwo_method_handle(json_data,pdata[1],addr,data)
            except Exception as e:
                logging.error(e)
                self.reactor.stop()



    # Possibly invoked if there is no server listening on the
    # address to which we are sending.
    def connectionRefused(self):
        logging.error("No one listening")


