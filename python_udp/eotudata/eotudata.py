from dc_utils.dc_log import logging
import sys

from dc_utils.convert_utils import *

'''
eotudata协议

    0	1	2	3
    协议（PROTOCOL）
    长度X（除去报头12位）
    校验位（从下一行到结束）
    数据(DATA)

'''

class eotudata:

    proto_json = 1      #json数据
    proto_stream = 2    #传输二进制流

    MESSAGE_MAX_LENGTH = 1024


    def __init__(self):
        pass

    #设置对应协议数据，序列化为eotudata
    def bytedata(self,protocol,hexdata,streamdata = None):
        if protocol == 1:
            return self.set_jsondata(hexdata)
        elif protocol == 2:
            return self.set_streamdata(hexdata,streamdata)
        else:
            logging.error("not support")
            return None

    #取出eotudata协议的数据内容
    #return (1,content)                 代表content数据为json string
    #return (2,(json_data,stream_data)) 代表content数据为(json_data,stream_data)

    def get_content(self,data):
        if isinstance(data,str):
            logging.info("data is alread string")
            return (0,data) #原始数据为字符串，protocol 为0,
        elif isinstance(data,bytes):
            protocol = bytes_to_int(data[0:4])
            # 待后续校验...
            # content_len = data[4:8] #数据长度
            # cs = data[8:12]         #校验值
            content = data[12:]
            if protocol == 1:
                r = (1,content.decode(encoding = "utf-8"))
                return r
            elif protocol == 2:
                json_data_len =bytes_to_int(data[12:16]) 
                json_data = data[16:(16 + json_data_len)]
                stream_data_len = bytes_to_int(data[(16 + json_data_len):(20 + json_data_len)]) 
                stream_data = data[(20 + json_data_len):(20  + json_data_len + stream_data_len)]
                return (2,(json_data,stream_data))
            else:
                logging.error("protocol not support!")
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
    def set_jsondata(self,hexdata, protocol =1):
        data_len = len(hexdata)
        msg_buf = bytearray(data_len + 12)
        set_int_to_msg_buf(msg_buf,0,protocol,4) # 协议值
        set_int_to_msg_buf(msg_buf,4,data_len,4)   #长度
        set_int_to_msg_buf(msg_buf,8,0,4)   #校验值 暂定为0
        set_buf_to_msg_buf(msg_buf,12,hexdata,data_len)    #放入

        return msg_buf

    def set_streamdata(self,json_bytes_data,stream_bytes_data, protocol = 2):
        json_data_len = len(json_bytes_data)
        stream_data_len = len(stream_bytes_data)
        data_len = json_data_len + stream_data_len
        msg_buf = bytearray(data_len + 20)
        set_int_to_msg_buf(msg_buf,0,protocol,4)        #协议值
        set_int_to_msg_buf(msg_buf,4,data_len,4)        #长度
        set_int_to_msg_buf(msg_buf,8,0,4)               #校验值 0->待补充
        set_int_to_msg_buf(msg_buf,12,json_data_len,4)                      #长度   json_data_len
        set_buf_to_msg_buf(msg_buf,16,json_bytes_data,json_data_len)        #放入   json_bytes_data
        set_int_to_msg_buf(msg_buf,16 + json_data_len,stream_data_len,4)    #长度   stream_data_len
        set_buf_to_msg_buf(msg_buf,20 + json_data_len, \
                                    stream_bytes_data,stream_data_len)      #放入    json_bytes_data

        return msg_buf



        
