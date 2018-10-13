from dc_utils.dc_log import logging
import sys

from dc_utils.convert_utils import *

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



    def __init__(self):
        pass


    def bytedata(self,protocol,hexdata):
        if protocol == 1:
            return self.set_jsondata(protocol,hexdata)

    def get_content(self,data):
        if isinstance(data,str):
            logging.info("data is alread string")
            return data
        elif isinstance(data,bytes):
            protocol = bytes_to_int(data[0:4])
            # content_len = data[4:8] #数据长度
            # cs = data[8:12]         #校验值
            content = data[12:]
            if protocol == 1:
                r = (protocol,content.decode(encoding = "utf-8"))
                return r
            elif protocol == 2:
                logging.error("protocol = 2 is on going")
                return None
        else:
            logging.error("paras err ,not str or bytes but [%s] EXITING .." % type(data))
            return None    
  

    """
        协议（PROTO_JSON）0x01
        长度X（除去报头12位）
        校验位（从下一行到结束）

        JSON数据
    """

    def set_jsondata(self,protocol,hexdata):
        data_len = len(hexdata)
        msg_buf = bytearray(data_len + 12)
        set_int_to_msg_buf(msg_buf,0,protocol,4) # 协议值
        set_int_to_msg_buf(msg_buf,4,data_len,4)   #长度
        set_int_to_msg_buf(msg_buf,8,0,4)   #校验值 暂定为0
        set_buf_to_msg_buf(msg_buf,12,hexdata,data_len)    #放入

        return msg_buf






        
