
from dc_utils.convert_utils import set_int_to_msg_buf, \
                    set_buf_to_msg_buf,bytes_to_int

import ipaddress

from dc_utils.dc_log import logging
import sys


MESSAGE_MAX_LENGTH = (10240)    #报文最大长度 10kb
STUN_HEADER_LENGTH = (20)       #报文头 长度 20

FAMILY_IPV4 = 0x0001            #IPV4


'''
    拼装addr={ip_str,port_int}成8字节
    FAMILI 2  PORT 2
    ADDR 4
'''
def covert_addr_to_buf_array(addr):
    buf = bytearray(8)
    buf = set_int_to_msg_buf(buf,0,FAMILY_IPV4,2)
    buf = set_int_to_msg_buf(buf,2,addr[1],2)
    ip_int = int(ipaddress.IPv4Address(addr[0]))
    buf = set_int_to_msg_buf(buf,4,ip_int,4)
    return buf


'''
    拼接数据到msg_buf中
@msg_buf 
@sttp       msg_buf起始位置
@data_type  数据类型
@addr       (ip,port)
    return (msg_buf,length+header)
'''

def set_addr_to_msg_buf(msg_buf,sttp,data_type,addr):

    length = 8
    addr_buf = covert_addr_to_buf_array(addr)
    data_buf = set_data_type_buf_array(data_type,length,addr_buf)
    msg_buf = set_buf_to_msg_buf(msg_buf,sttp,data_buf,12)

    return (msg_buf,sttp+12)


def set_method_data_to_msg_buf(msg_buf,sttp,data_type,buf):

    buf_len = len(buf)  # no more than 256
    if buf_len >255:
        print("error ! method send data length over 255 %d ,exiting ...." % buf_len)
        sys.exit(-1)
    
    msg_buf = set_int_to_msg_buf(msg_buf,sttp,data_type,2)
    msg_buf = set_int_to_msg_buf(msg_buf,sttp+2,buf_len,2)
    msg_buf = set_buf_to_msg_buf(msg_buf,sttp+4,buf,buf_len)

    return (msg_buf,sttp+ 4 + buf_len)


'''
    拼接数据类型为整型的数据到msg_buf中
@msg_buf 
@sttp       msg_buf起始位置
@data_type  数据类型
@value      int
@bit_num    
    return (msg_buf,length+header)
'''

def set_data_int_to_msg_buf(msg_buf,sttp,data_type,value,bit_num):

    msg_buf = set_int_to_msg_buf(msg_buf,sttp,data_type,2)
    msg_buf = set_int_to_msg_buf(msg_buf,sttp+2,bit_num,2)
    msg_buf = set_int_to_msg_buf(msg_buf,sttp+4,value,bit_num)

    return (msg_buf,sttp+4+bit_num)

'''
    同上，设定整数类型位数4
'''
def set_data_int32_to_msg_buf(msg_buf,sttp,data_type,value):
    return set_data_int_to_msg_buf(msg_buf,sttp,data_type,value,4)


'''
    拼接数据类型为整型的数据到msg_buf中
@msg_buf 
@sttp       msg_buf起始位置
@data_type  数据类型
@user       (user_id,user_pwd)    
    return (msg_buf,length+header)
'''

def set_ask_user_to_msg_buf(msg_buf,sttp,data_type,user):

    length = 8
    msg_buf = set_int_to_msg_buf(msg_buf,sttp,data_type,2)
    msg_buf = set_int_to_msg_buf(msg_buf,sttp+2,length,2)
    msg_buf = set_int_to_msg_buf(msg_buf,sttp+4,user[0],4)
    msg_buf = set_int_to_msg_buf(msg_buf,sttp+8,user[1],4)
    return (msg_buf,sttp+12)


## 拼装数据类型，长度，value，
def set_data_type_buf_array(data_type,length,value_buf):

    buf = bytearray(length + 4)
    set_int_to_msg_buf(buf,0,data_type,2)
    set_int_to_msg_buf(buf,2,length,2)
    set_buf_to_msg_buf(buf,4,value_buf,length)
    return buf


'''
    设置报文长度，最终结果
@msg    (msg_buf,长度-含STUN_HEADER_LENGTH)
'''
def set_msg_buf_size_final(msg):

    msg_buf = set_int_to_msg_buf(msg[0],2,msg[1]-STUN_HEADER_LENGTH,2)

    return msg_buf[:msg[1]]


'''
    报头初始化
@user_id    用户id
@pwd        用户密码
    return msg_buf_header 返回报头20个字节
'''
def stun_init_header(msg_type,my_user,set_random = None):
    #logging.debug("stun init with user[%d:%d]"%my_user)
    msg_buf_header=bytearray(STUN_HEADER_LENGTH)
    msg_buf_header=set_int_to_msg_buf(msg_buf_header,0,msg_type,2)    #消息类型
    if set_random !=None:
        msg_buf_header=set_int_to_msg_buf(msg_buf_header,8,set_random,4)
    msg_buf_header=set_int_to_msg_buf(msg_buf_header,12,my_user[0],4)   #用户ID
    msg_buf_header=set_int_to_msg_buf(msg_buf_header,16,my_user[1],4)       #用户密码

    return msg_buf_header


'''
=============================================

    DATA拼装数据处理

=============================================
'''
# METHOD 消息类型

STUN_METHOD_BINDING =(0x0001)           #
STUN_METHOD_ALLOCATE =(0x0003)          #用户请求服务器分配资源，建立连接
STUN_METHOD_REFRESH =(0x0004)           #用户刷新，相当于心跳
STUN_METHOD_EOTU_ASK_USER =(0x0005)     #请求对方信息
STUN_METHOD_SEND =(0x0006)              #用户转发数据到服务器
STUN_METHOD_DATA =(0x0007)              #服务器转发数据给用户
STUN_METHOD_CREATE_PERMISSION =(0x0008) #用户许可其他用户连接
STUN_METHOD_CHANNEL_BIND =(0x0009)      #
STUN_METHOD_CONNECT=0x000a              #用户之间检测是否可以通信

msg_des={
    STUN_METHOD_BINDING:"STUN_METHOD_BINDING",
    STUN_METHOD_ALLOCATE:"STUN_METHOD_ALLOCATE",
    STUN_METHOD_REFRESH:"STUN_METHOD_REFRESH",
    STUN_METHOD_EOTU_ASK_USER:"STUN_METHOD_EOTU_ASK_USER",
    STUN_METHOD_SEND:"STUN_METHOD_SEND",
    STUN_METHOD_DATA:"STUN_METHOD_DATA",
    STUN_METHOD_CREATE_PERMISSION:"STUN_METHOD_CREATE_PERMISSION",
    STUN_METHOD_CHANNEL_BIND:"STUN_METHOD_CHANNEL_BIND",
    STUN_METHOD_CONNECT:"STUN_METHOD_CONNECT"
}
# ATTRIBUTE 数据类型

STUN_ATTRIBUTE_ERROR_CODE = 0x0009
STUN_ATTRIBUTE_XOR_PEER_ADDRESS = 0x0012            #需要中转的peer addr
STUN_ATTRIBUTE_DATA = 0x0013                        #需要中转的数据
STUN_ATTRIBUTE_REALM = 0x0014
STUN_ATTRIBUTE_NONCE = 0x0015
STUN_ATTRIBUTE_XOR_RELAYED_ADDRESS = 0x0016         #服务器返回NAT地址
STUN_ATTRIBUTE_LIFETIME = 0x000d


STUN_ATTRIBUTE_REQUESTED_TRANSPORT = 0x0019         #udp 通信默认17
STUN_ATTRIBUTE_XOR_MAPPED_ADDRESS = 0x0020          #服务器返回的客户端映射地址
STUN_ATTRIBUTE_REQUESTED_ADDRESS_FAMILY = 0x0017    #ipv4 默认值 0x001
STUN_ATTRIBUTE_EOTU_USERID = 0x0e01                 #已取消，改用包头
STUN_ATTRIBUTE_EOTU_PWD = (0x0e02)                  #已取消，改用包头
STUN_ATTRIBUTE_EOTU_LOCAL_ADDR = (0x0e03)           #用户上报ip port
STUN_ATTRIBUTE_ASK_USERID_INFO = 0x0e11             #咨询某用户信息
STUN_ATTRIBUTE_RES_USERID_INFO = (0x0e12)           #服务器返回用户信息
STUN_ATTRIBUTE_RES_USER_INFO_MAPEED_ADDR = (0x0e13)  #服务器返回咨询用户的本地地址，服务器检测的反射地址
STUN_ATTRIBUTE_RES_USER_INFO_RELAYED_ADDR = (0x0e14)    #服务器返回用户NAT地址
STUN_ATTRIBUTE_RES_USER_INFO_REAL_ADDR = (0x0e15)   #服务器返回用户上报的本地地址
STUN_ATTRIBUTE_SEND_DATA_TYPE = 0x0e16              #发送的数据类型
STUN_ATTRIBUTE_SEND_IS_RESPONSE = 0x0e17            #发送的数据是否需要回复

data_des={

    STUN_ATTRIBUTE_XOR_RELAYED_ADDRESS:"STUN_ATTRIBUTE_XOR_RELAYED_ADDRESS",
    STUN_ATTRIBUTE_NONCE:"STUN_ATTRIBUTE_NONCE",
    STUN_ATTRIBUTE_REALM:"STUN_ATTRIBUTE_REALM",
    STUN_ATTRIBUTE_ERROR_CODE:"STUN_ATTRIBUTE_ERROR_CODE",
    STUN_ATTRIBUTE_XOR_MAPPED_ADDRESS:"STUN_ATTRIBUTE_XOR_MAPPED_ADDRESS",
    STUN_ATTRIBUTE_LIFETIME:"STUN_ATTRIBUTE_LIFETIME",
    STUN_ATTRIBUTE_XOR_PEER_ADDRESS : "STUN_ATTRIBUTE_XOR_PEER_ADDRESS",
    STUN_ATTRIBUTE_DATA :"STUN_ATTRIBUTE_DATA",
    STUN_ATTRIBUTE_SEND_DATA_TYPE:"STUN_ATTRIBUTE_SEND_DATA_TYPE",
    STUN_ATTRIBUTE_SEND_IS_RESPONSE:"STUN_ATTRIBUTE_SEND_IS_RESPONSE",
    
    STUN_ATTRIBUTE_REQUESTED_ADDRESS_FAMILY:"STUN_ATTRIBUTE_REQUESTED_ADDRESS_FAMILY",
    STUN_ATTRIBUTE_REQUESTED_TRANSPORT:"STUN_ATTRIBUTE_REQUESTED_TRANSPORT",
    STUN_ATTRIBUTE_EOTU_USERID:"STUN_ATTRIBUTE_EOTU_USERID",
    STUN_ATTRIBUTE_EOTU_PWD:"STUN_ATTRIBUTE_EOTU_PWD",
    STUN_ATTRIBUTE_EOTU_LOCAL_ADDR:"STUN_ATTRIBUTE_EOTU_LOCAL_ADDR",
    STUN_ATTRIBUTE_ASK_USERID_INFO:"STUN_ATTRIBUTE_ASK_USERID_INFO",
    STUN_ATTRIBUTE_RES_USERID_INFO:"STUN_ATTRIBUTE_RES_USERID_INFO",
    STUN_ATTRIBUTE_RES_USER_INFO_MAPEED_ADDR:"STUN_ATTRIBUTE_RES_USER_INFO_MAPEED_ADDR",
    STUN_ATTRIBUTE_RES_USER_INFO_RELAYED_ADDR:"STUN_ATTRIBUTE_RES_USER_INFO_RELAYED_ADDR",
    STUN_ATTRIBUTE_RES_USER_INFO_REAL_ADDR:"STUN_ATTRIBUTE_RES_USER_INFO_REAL_ADDR"
}

# #消息类型处理 函数

# msg_handle_funcs={
#     STUN_METHOD_BINDING:stun_method_binding_handle,
#     STUN_METHOD_ALLOCATE:stun_method_allocation_handle,
#     STUN_METHOD_REFRESH:stun_method_refresh_handle,
#     STUN_METHOD_SEND:stun_method_send_handle,
#     STUN_METHOD_DATA:stun_method_data_handle,
#     STUN_METHOD_CREATE_PERMISSION:stun_method_create_permission_handle,
#     STUN_METHOD_CONNECT : stun_method_connect_handle,
#     STUN_METHOD_EOTU_ASK_USER : stun_method_eotu_ask_user_handle,
# }

'''
    设置数据类型set函数-拼装数据类型处理函数
'''

data_set_func={
        STUN_ATTRIBUTE_EOTU_LOCAL_ADDR:set_addr_to_msg_buf,
        STUN_ATTRIBUTE_REQUESTED_TRANSPORT:set_data_int32_to_msg_buf,
        STUN_ATTRIBUTE_REQUESTED_ADDRESS_FAMILY:set_data_int32_to_msg_buf,
        STUN_ATTRIBUTE_ASK_USERID_INFO:set_ask_user_to_msg_buf,
        STUN_ATTRIBUTE_XOR_PEER_ADDRESS:set_addr_to_msg_buf,
        STUN_ATTRIBUTE_DATA:set_method_data_to_msg_buf

    }


'''
    拼接数据到msg_buf中
@msg_buf 
@sttp       msg_buf起始位置
@data_type  数据类型
@value      数据的值（可能为各种数据)，根据数据类型设定
    return (msg_buf,length+header)
'''

def set_data_to_msg_buf(msg_buf,sttp,data_type,value):

    if data_type in data_set_func:
        return data_set_func[data_type](msg_buf,sttp,data_type,value)
    else:
        return None





class stun_message_class:

    coturn_server = None
    my_user = None
    ask_user = None
    local_addr = None
 
    def __init__(self,coturn_server,my_user=(10,1),ask_user=(11,1)):
        self.coturn_server = coturn_server
        self.my_user = my_user
        self.ask_user = ask_user

    def method_create_permission_start(self,peer_addr):
        #初始化报头
        msg_buf = bytearray(MESSAGE_MAX_LENGTH)
        msg_buf_header = stun_init_header(STUN_METHOD_CREATE_PERMISSION,self.my_user)       
        msg_buf = set_buf_to_msg_buf(msg_buf,0,msg_buf_header,STUN_HEADER_LENGTH)

        #添加peer地址
        msg = set_data_to_msg_buf(msg_buf,STUN_HEADER_LENGTH,STUN_ATTRIBUTE_XOR_PEER_ADDRESS,peer_addr)
   
        #设置msg_buf长度值
        msg_to_send = set_msg_buf_size_final(msg)
        
        return msg_to_send



    '''
        中转数据，server为空，则直接p2p发送，否则server中转
    @ server  coturn_server服务器地址
    @ peer_addr peer地址
    
    '''

    def method_bind_start(self):
        #初始化报头
        msg_buf = bytearray(STUN_HEADER_LENGTH)
        msg_buf_header = stun_init_header(STUN_METHOD_BINDING,self.my_user)       
        msg_buf = set_buf_to_msg_buf(msg_buf,0,msg_buf_header,STUN_HEADER_LENGTH)

        return msg_buf


    def method_refresh_start(self):
        #初始化报头
        msg_buf = bytearray(STUN_HEADER_LENGTH)
        msg_buf_header = stun_init_header(STUN_METHOD_REFRESH,self.my_user)       
        msg_buf = set_buf_to_msg_buf(msg_buf,0,msg_buf_header,STUN_HEADER_LENGTH)

        return msg_buf
        




    '''
        中转数据，server为空，则直接p2p发送，否则server中转
    @ server  coturn_server服务器地址
    @ peer_addr peer地址
    
    '''

    def method_send_start(self,send_data,ask_user):

        #初始化报头
        msg_buf = bytearray(MESSAGE_MAX_LENGTH)
        msg_buf_header = stun_init_header(STUN_METHOD_SEND,self.my_user)       
        msg_buf = set_buf_to_msg_buf(msg_buf,0,msg_buf_header,STUN_HEADER_LENGTH)

        #添加peer地址
        #msg = set_data_to_msg_buf(msg_buf,STUN_HEADER_LENGTH,STUN_ATTRIBUTE_XOR_PEER_ADDRESS,peer_addr)

        msg = set_data_to_msg_buf(msg_buf,STUN_HEADER_LENGTH,STUN_ATTRIBUTE_ASK_USERID_INFO,ask_user)

        #添加发送的数据
        msg = set_data_to_msg_buf(msg_buf,msg[1],STUN_ATTRIBUTE_DATA,send_data)
   
        #设置msg_buf长度值
        msg_to_send = set_msg_buf_size_final(msg)


        return msg_to_send



    def method_eotu_ask_user_start(self,ask_user=None):
        logging.debug("###############EOTU ASK USER server[%s:%d]" % (self.coturn_server[0],self.coturn_server[1]))


        #初始化报头
        msg_buf = bytearray(MESSAGE_MAX_LENGTH)
        msg_buf_header = stun_init_header(STUN_METHOD_EOTU_ASK_USER,self.my_user)       
        msg_buf = set_buf_to_msg_buf(msg_buf,0,msg_buf_header,STUN_HEADER_LENGTH)

        if ask_user ==None:
            ask_user = self.ask_user

        if ask_user !=None:
            msg = set_data_to_msg_buf(msg_buf,STUN_HEADER_LENGTH,STUN_ATTRIBUTE_ASK_USERID_INFO,ask_user)
        else:
            logging.error("ask user is None ,exiting ....")
            sys.exit()

        #设置msg_buf长度值
        msg_to_send = set_msg_buf_size_final(msg)
        
        return msg_to_send
        




    def allocation_msg(self,allocation_times = 0):

        logging.debug("################ALLOCATION START !  server[%s:%d]" % (self.coturn_server[0],self.coturn_server[1]))
        
        #初始化报头
        msg_buf = bytearray(MESSAGE_MAX_LENGTH)
        if allocation_times ==0:
            msg_buf_header = stun_init_header(STUN_METHOD_ALLOCATE,self.my_user,set_random=0xffffffff)
        else:
            msg_buf_header = stun_init_header(STUN_METHOD_ALLOCATE,self.my_user)       
        msg_buf = set_buf_to_msg_buf(msg_buf,0,msg_buf_header,STUN_HEADER_LENGTH)

        #添加本地地址
        if self.local_addr !=None:
            msg = set_data_to_msg_buf(msg_buf,STUN_HEADER_LENGTH,STUN_ATTRIBUTE_EOTU_LOCAL_ADDR,self.local_addr)

        #设置REQUESTED_TRANSPORT  默认UDP ， 值为17
        msg = set_data_to_msg_buf(msg_buf,msg[1],STUN_ATTRIBUTE_REQUESTED_TRANSPORT,0x11000000)
        msg = set_data_to_msg_buf(msg_buf,msg[1],STUN_ATTRIBUTE_REQUESTED_ADDRESS_FAMILY,0x01000000)


        #设置msg_buf长度值
        msg_to_send = set_msg_buf_size_final(msg)
        logging.debug("ALLOCATION DATA [%s]" %msg_to_send.hex())

        return msg_to_send





'''
=============================================

    DATA拼装数据处理

=============================================
'''

import json

class addr_attr:
    ipbytes = None
    ipstr = None
    portbytes = None
    family = None
    length = None
    des = None
    type_bytes = None

    def __init__(self,length,addr_data,data_type_int,data_type):
        self.family = addr_data[0:2]
        self.portbytes = addr_data[2:4]
        self.port = bytes_to_int(self.portbytes)
        self.ipbytes = addr_data[4:8]
        self.ipstr = ".".join(list(map(str,self.ipbytes)))
        self.length = length
        self.des = data_des[data_type_int]
        self.type_bytes = data_type.hex()

    def __str__(self):

        j = {
            "ip":self.ipstr,
            "port":self.port,
            #"family":self.family.hex(),
            "des":self.des,
            "type":self.type_bytes
            }
        return json.dumps(j)


class user_info_attr:
    user_id = None
    user_pwd = None
    length = None
    des = None
    type_bytes = None

    def __init__(self,length,data,data_type_int,data_type):
        self.user_id = data[:4]
        self.user_pwd = data[4:8]
        self.des = data_des[data_type_int]
        self.type_bytes = data_type.hex()

    def __str__(self):

        j = {
            "user_id":self.user_id.hex(),
            "user_pwd":self.user_pwd.hex(),
            "des":self.des,
            "type":self.type_bytes
        }
 
        return json.dumps(j)

class value_info_attr:
    value = None
    length = None
    des = None
    type_bytes = None

    def __init__(self,length,data,data_type_int,data_type):
        self.value=data
        self.length = length
        self.des = data_des[data_type_int]
        self.type_bytes = data_type.hex()

    def __str__(self):
        des_str = None
        try:
            des_str = self.value.decode("utf-8")
        except:
            des_str = self.value.hex()
        j =  {
            "value":des_str,
            "value_bytes":self.value.hex(),
            "des":self.des,
            "type":self.type_bytes
        }
        return json.dumps(j)

class error_code_attr:
    code = None
    string = None
    des = None
    type_bytes = None

    def __init__(self,length,data,data_type_int,data_type):
        self.code = bytes_to_int(data[0:4])
        

        try:
            self.string = data[4:].decode('utf-8')
            print("error code %08x ,error[%s]" % (self.code,self.string) )
            print(self.string)
        except Exception as e:
            print(e)
            sys.exit()
            self.string = data[4:].hex()
        self.length = length
        self.des = data_des[data_type_int]
        self.type_bytes = data_type.hex()

    def __str__(self):
        j =  {
            "code":self.code,
            "string":self.string,
            "des":self.des,
            "type":self.type_bytes
        }
        return json.dumps(j)

data_attr_funcs={
    STUN_ATTRIBUTE_EOTU_LOCAL_ADDR:addr_attr,
    STUN_ATTRIBUTE_RES_USER_INFO_MAPEED_ADDR:addr_attr,
    STUN_ATTRIBUTE_RES_USER_INFO_RELAYED_ADDR:addr_attr,
    STUN_ATTRIBUTE_RES_USER_INFO_REAL_ADDR:addr_attr,
    STUN_ATTRIBUTE_RES_USERID_INFO:user_info_attr,
    STUN_ATTRIBUTE_ERROR_CODE:error_code_attr,
    STUN_ATTRIBUTE_XOR_RELAYED_ADDRESS:addr_attr,
    STUN_ATTRIBUTE_XOR_MAPPED_ADDRESS:addr_attr,
    STUN_ATTRIBUTE_NONCE:value_info_attr,
    STUN_ATTRIBUTE_REALM:value_info_attr,
    STUN_ATTRIBUTE_LIFETIME:value_info_attr,
    STUN_ATTRIBUTE_XOR_PEER_ADDRESS:addr_attr,
    STUN_ATTRIBUTE_DATA:value_info_attr,
    STUN_ATTRIBUTE_REQUESTED_TRANSPORT:value_info_attr,
    STUN_ATTRIBUTE_REQUESTED_ADDRESS_FAMILY:value_info_attr,
}


class dismessage:

    msg_type = None
    user_id = None
    msg_length = None
    data_list = {}

    def __init__(self,data):
        self.msg_type = data[0:2]
        self.msg_length = data[2:4]
        self.user_id = data[12:16]
        self.user_pwd = data[16:20]
        self.data_list = {}

        if bytes_to_int(self.msg_length)+20 != len(data):
            self.data_list["err"] = "stun length not right"
            self.data_list["data_str"] = str(data)
            self.data_list["data_hex"] = data.hex()
        else:
            self.get_data_list(data)


    def get_data_type(self,next_data):

        if len(next_data) <5:
            logging.error("illegle")
            sys.exit()

        data_type = next_data[0:2]
        data_type_int = bytes_to_int(next_data[0:2])

        data_length = bytes_to_int(next_data[2:4])

        if len(next_data) < 4 + data_length:
            logging.error("total len [%d]" % len(next_data))
            logging.error("message demand len [%d]" % (4+data_length))
            logging.error("get data type length error [%s] ,Exiting ...." % next_data.hex())
            #sys.exit(-1)
            return (data_type_int,next_data,None)

        data_value = next_data[4:(data_length + 4)]
        data_attr = None
        
        if data_type_int in data_attr_funcs:
            func = data_attr_funcs[data_type_int]
            if func is not None:
                data_attr = data_attr_funcs[data_type_int](data_length,data_value,data_type_int,data_type)
            else:
                data_attr = [data_value]
        else:
            logging.error("ATTR[%s] no function to get value [%s]" %(data_type.hex(),data_value.hex()))
            data_attr = data_value.hex()

        next_data = next_data[(data_length + 4):]
        return (data_type_int,data_attr,next_data)

    def get_data_list(self,data):
        next_data = data[20:]
        while(next_data):
            data_type_int,data_attr,next_data = self.get_data_type(next_data)
            if None in (data_type_int,data_attr):
                break
            if not data_type_int in self.data_list:
                self.data_list[data_type_int]=[]
                self.data_list[data_type_int].append(data_attr)
            else:
                self.data_list[data_type_int].append(data_attr)

    def print_msg(self):
    
        j={}
        for d in self.data_list:
            if d == None:
                logging.error("get nothing for recieved data")
                sys.exit()
            j[d]=[]
            dobj = self.data_list[d]
            if isinstance(dobj,list):
                for obj_c in dobj:
                    if isinstance(obj_c,object):
                        try:
                            j[d].append(json.loads(str(obj_c)))
                        except Exception as e:
                            logging.info(e)
                            j[d].append(obj_c)
                    else:
                        print("================what error !?")
                        j[d].append(obj_c)                
            else:
                print("================what error !?")
                j[d].append(json.loads(dobj))

        print(json.dumps(j,indent = 2))
        return j

def debug_recv(msg):

    j={}
    for d in msg.data_list:
        if d == None:
            logging.error("get nothing for recieved data")
            sys.exit()
        j[d]=[]
        dobj = msg.data_list[d]
        if isinstance(dobj,list):
            for obj_c in dobj:
                if isinstance(obj_c,object):
                    try:
                        j[d].append(json.loads(str(obj_c)))
                    except Exception as e:
                        logging.info(e)
                        j[d].append(obj_c)
                else:
                    print("================what error !?")
                    j[d].append(obj_c)                
        else:
            print("================what error !?")
            j[d].append(json.loads(dobj))

    print(json.dumps(j,indent = 2))
    return j

def get_json_from_msg_data(data):

    msg = dismessage(data)
    return debug_recv(msg)

def addr_attrs_set_to_gain(gain,addr_attr_list,addr_type):
    is_ok = 0
    for attr in addr_attr_list:
        if attr.ipstr != "0.0.0.0":
            gain[addr_type].append(attr)
            logging.info("GET %s addr[%s:%d]" %(addr_type,attr.ipstr,attr.port))
            is_ok = 1

    return gain,is_ok



'''
    allocate recv 处理
'''
def allocation_recv_handle(data):

    logging.debug("ready to format recieved data")
    msg = dismessage(data)
    return debug_recv(msg)

'''
    方法同allocation_recv_handle
'''

def method_send_callback(data):
    
    return allocation_recv_handle(data)

#   EOTU ASK USER

def method_eotu_ask_user_recv_handle(data):
    return allocation_recv_handle(data) 
