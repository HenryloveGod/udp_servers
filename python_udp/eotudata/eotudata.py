from dc_utils.dc_log import logging
import sys

from dc_utils.convert_utils import set_int_to_msg_buf,set_buf_to_msg_buf

'''
eotudata协议
'''

class eotudata:

    """
        0	1	2	3
        协议（PROTOCOL）
        长度X（除去报头12位）
        校验位（从下一行到结束）
        数据(DATA)
    """
    # protocol = 1 JSON格式
    # protocol = 2 传输文件流
    # protocol = 3 传输二进制流 
    proto_json = 1
    proto_file = 2
    proto_stream = 3

    MESSAGE_MAX_LENGTH = 1024

    msg_buf = None
    hexdata = None
    protocol = None
    """
        协议（PROTO_JSON）0x01
        长度X（除去报头12位）
        校验位（从下一行到结束）

        JSON数据
    """

    def jsondata(self,protocol,hexdata):
        data_len = len(self.hexdata)
        
        msg_buf = bytearray(data_len + 12)
        
        set_int_to_msg_buf(msg_buf,0,protocol,4) # 协议值
        set_int_to_msg_buf(msg_buf,4,data_len,4)   #长度
        set_int_to_msg_buf(msg_buf,8,0,4)   #校验值 暂定为0
        set_buf_to_msg_buf(msg_buf,12,hexdata,data_len)    #放入

        self.msg_buf = msg_buf

        return msg_buf

    """
        协议（PROTO_FILE）0x02
        长度X（除去报头12位）
        校验位（从下一行到结束）

        文件ID号
        总分段数量	当前分段序号
        数据长度（文件数据长度）	文件总大小
        待扩展....
        待扩展....
        文件数据
    """

    def filedata(self,protocol,hexdata):
        pass

    def streamdata(self,protocol,hexdata):
        pass

    data_build= {
        proto_json:jsondata,
        proto_file:filedata,
        proto_stream:streamdata
    }

    def __init__(self,max_len = MESSAGE_MAX_LENGTH):
        pass
  
    def to_stream(self,protocol,data):

        hexdata = None
        if isinstance(data,str):
            hexdata = bytes(data,encoding="utf-8")
        elif isinstance(data,bytes):
            hexdata = data
        else:
            logging.error("paras err ,not str or bytes but [%s]" % type(data))
            logging.error(data)
            logging.error("EXITING ...")
            sys.exit(-1)
        return  self.data_build[protocol](self,protocol,hexdata)

    def get_json(self,data):
        content = None
        if isinstance(data,str):
            logging.info("data is alread string")
            return data
        elif isinstance(data,bytes):
           
            protocol = data[0:4]
            content_len = data[4:8] #数据长度
            cs = data[8:12]         #校验值
            content = data[12:]
            if protocol == 1:
                return protocol,str(content)
            elif protocol == 2:
                logging.error("on going")
                sys.exit(-1)
        else:
            logging.error("paras err ,not str or bytes but [%s]" % type(data))
            logging.error(data)
            logging.error("EXITING ...")
            sys.exit(-1)


    def get_file(self,data):
        pass

    def get_stream(self,data):
        pass
        
