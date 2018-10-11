
import struct
import socket
import ipaddress
import sys
import logging
import os, signal



MESSAGE_MAX_LENGTH = (10240)  #报文最大长度 10kb
STUN_HEADER_LENGTH = (20)   #报文头 长度 20


FAMILY_IPV4 = 0x0001    # IPV4

'''
设置log参数
'''

logging.basicConfig(
    stream = sys.stdout,
    level=logging.DEBUG,
    format=' %(filename)s[%(funcName)s][line:%(lineno)d] %(message)s',
    datefmt='%Y-%M-%D'
    )

def timeout_handle(num,b):
    logging.error("TIME OUT ")

'''
获取本机IP
'''

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

MY_LOCAL_IP = get_host_ip()


'''
    int类型转化为unsigned char array
@num    int位数
@value  int值
'''

def int_to_unsiged_array(value,num=1):
    pack_type = {
        1:">B",
        2:">H",
        4:">L",
        8:">Q"
    }
    if not num in pack_type:
        return None

    if not isinstance(value,int):
        print("error !!!!!!!!!!!!!!!!!")
        print(value)
        

    return struct.pack(pack_type[num], value)    


'''
任意长度bytes转发为 int -->不要太大～～
'''

def bytes_to_int(data_bytes):
    r = 0
    for i in data_bytes:
        r = r * 256 + i

    return r



'''
    拼接一个int到msg_buf，int位数由bit_num决定
@msg_buf
@sttp       msg_buf起始位置
@endp       msg_buf结束位置
@src        要拼接的int
@bit_num    int的位数
'''
def set_int_to_msg_buf(msg_buf,sttp,src,bit_num):
    src_array = int_to_unsiged_array(src,bit_num)
    for i in range(0,bit_num,1):
        msg_buf[sttp+i]=src_array[i]
    return msg_buf

'''
 拼接buf到msg_buf中，
@msg_buf    
@sttp       msg_buf起始位置
@src        要拼接的内容
@bit_num    要拼接内容的长度 
'''

def set_buf_to_msg_buf(msg_buf,sttp,src,bit_num):

    for i in range(bit_num):
        msg_buf[sttp+i]=src[i]
    return msg_buf

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

#   ip转化为4字节的int
def iptoint(ip):
    return int(socket.inet_aton(ip).encode('hex'),32)

#   ip整数转化为ip string
def inttoip(ip):
    return socket.inet_ntoa(hex(ip)[2:].decode('hex'))



'''
    获取一个socket连接
@addr (ip,port) 要连接的server
    return (local_addr,s) local_addr 为本地的(ip,port),s 为socket连接
'''
def get_new_socket(allocation_times = 0 ,port=12345,connect_server_addr = None,timeout = 0):
    
    port = port +allocation_times
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #s.setblocking(0)
    s.bind((MY_LOCAL_IP,port))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if timeout >0:
        s.settimeout(timeout)
    if connect_server_addr:
        s.connect(connect_server_addr)
    local_addr = (MY_LOCAL_IP,s.getsockname()[1])
    #logging.debug("GET NEW SOCKET listening [%s:%d]" % (s.getsockname()[0],s.getsockname()[1]))
    return local_addr,s


'''
    获取一个socket连接
@addr (ip,port) 要连接的server
    return (local_addr,s) local_addr 为本地的(ip,port),s 为socket连接
'''
def get_new_connect_socket(addr,port=8888):

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(addr)
    local_addr = (s.getsockname()[0],s.getsockname()[1])
    logging.debug("GET NEW SOCKET connecting [%s:%d] with local[%s:%d]" % (addr[0],addr[1],local_addr[0],local_addr[1]))
    return local_addr,s






'''
=============================================

    METHOD 消息类型处理

=============================================
'''

# def stun_method_binding_handle():
#     pass

# def stun_method_allocation_handle():
#     pass

# def stun_method_eotu_ask_user_handle():
#     pass


# def stun_method_refresh_handle():
#     pass

# def stun_method_send_handle():
#     pass

# def stun_method_data_handle():
#     pass

# def stun_method_create_permission_handle():
#     pass
# def stun_method_connect_handle():
#     pass

# def stun_method_unknow():
#     pass



'''
=============================================

    DATA数据类型处理

=============================================
'''

pass


'''
=============================================

    DATA拼装数据处理

=============================================
'''
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
        logging.error("attr data function [%s] not found" %(data_des[data_type]))
        return None





class stun_allocation_class:

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
        logging.debug("method_send_start start to send \n[%s]" % msg_to_send.hex())

        #开始发送
        self.server_socket_fd.sendto(msg_to_send,self.coturn_server)
        while True:
            data,recv_addr = self.server_socket_fd.recvfrom(MESSAGE_MAX_LENGTH)
            logging.debug("recieved from[%s:%d] [%s]" %(recv_addr[0],recv_addr[1],data.hex()))

            return data



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

        #开始发送
        self.server_socket_fd.sendto(msg_buf,self.coturn_server)
        while True:
            data,recv_addr = self.server_socket_fd.recvfrom(MESSAGE_MAX_LENGTH)
            logging.debug("recieved from [%s:%d] data[%s]" %(recv_addr[0],recv_addr[1], data.hex()))

            return data


    def method_refresh_start(self,wait_recv = 1):
        #初始化报头
        msg_buf = bytearray(STUN_HEADER_LENGTH)
        msg_buf_header = stun_init_header(STUN_METHOD_REFRESH,self.my_user)       
        msg_buf = set_buf_to_msg_buf(msg_buf,0,msg_buf_header,STUN_HEADER_LENGTH)

        #开始发送
        self.server_socket_fd.sendto(msg_buf,self.coturn_server)
        if wait_recv ==1 :
            while True:
                data,recv_addr = self.server_socket_fd.recvfrom(MESSAGE_MAX_LENGTH)
                logging.debug("recieved from [%s:%d] data[%s]" %(recv_addr[0],recv_addr[1], data.hex()))
                return data
        




    '''
        中转数据，server为空，则直接p2p发送，否则server中转
    @ server  coturn_server服务器地址
    @ peer_addr peer地址
    
    '''

    def method_send_start(self,send_data,ask_user,server = None,is_wait = 1):

        #初始化报头
        msg_buf = bytearray(MESSAGE_MAX_LENGTH)
        msg_buf_header = stun_init_header(STUN_METHOD_SEND,self.my_user)       
        msg_buf = set_buf_to_msg_buf(msg_buf,0,msg_buf_header,STUN_HEADER_LENGTH)

        #添加peer地址
        #msg = set_data_to_msg_buf(msg_buf,STUN_HEADER_LENGTH,STUN_ATTRIBUTE_XOR_PEER_ADDRESS,peer_addr)
    
        if ask_user !=None:
            print("METHOD SEND 现在改peer addr 为 askuser")
        
        msg = set_data_to_msg_buf(msg_buf,STUN_HEADER_LENGTH,STUN_ATTRIBUTE_ASK_USERID_INFO,ask_user)


        #添加发送的数据
        msg = set_data_to_msg_buf(msg_buf,msg[1],STUN_ATTRIBUTE_DATA,send_data)
   
        #设置msg_buf长度值
        msg_to_send = set_msg_buf_size_final(msg)


        # if is_wait == 0:
        #     return None
        while True:
            try:
                #开始发送
                if server !=None:
                    self.server_socket_fd.sendto(msg_to_send,server)
                    logging.debug("METHOD SEND  server[%s:%d] with ask_user[%d:%d] data[%s] " %
                        (
                            server[0],server[1],
                            ask_user[0],ask_user[1],
                            msg_to_send.hex()) 
                        )
                else:
                    print("METHOD SEND NO SERVER")
                    sys.exit()

                self.server_socket_fd.settimeout(5)
                data,recv_addr = self.server_socket_fd.recvfrom(MESSAGE_MAX_LENGTH)
                if server !=None:
                    logging.debug("RECIEVED from[%s:%d] [%s]" %(recv_addr[0],recv_addr[1], data.hex()))
                else:
                    logging.debug("P2P SEND recieved from[%s:%d]\n[%s]" %(recv_addr[0],recv_addr[1], data.hex()))

                method_send_gain = method_send_callback(data)
                return method_send_gain
            except Exception as e:
                logging.error(e)
                continue



    def method_eotu_ask_user_start(self,sequence = 0,ask_user=None):
        logging.debug("###############EOTU ASK USER server[%s:%d] times[%d]" % (self.coturn_server[0],self.coturn_server[1],sequence))
        new_socket = self.server_socket_fd 
        if new_socket  == None:
            self.local_addr,new_socket  = get_new_socket()
            self.server_socket_fd = new_socket
            logging.debug("get local addr [%s:%d]" %(self.local_addr[0],self.local_addr[1]) )
        #初始化报头
        msg_buf = bytearray(MESSAGE_MAX_LENGTH)
        msg_buf_header = stun_init_header(STUN_METHOD_EOTU_ASK_USER,self.my_user)       
        msg_buf = set_buf_to_msg_buf(msg_buf,0,msg_buf_header,STUN_HEADER_LENGTH)

        if ask_user ==None:
            ask_user = self.ask_user

        if ask_user !=None:
            msg = set_data_to_msg_buf(msg_buf,STUN_HEADER_LENGTH,STUN_ATTRIBUTE_ASK_USERID_INFO,ask_user)
            logging.debug("Add ask user (%d %d)" % ask_user)
        else:
            logging.error("ask user is None ,exiting ....")
            sys.exit()

        #设置msg_buf长度值
        msg_to_send = set_msg_buf_size_final(msg)
        logging.debug("EOTU_ASK_USER START ! send data [%s]" %msg_to_send.hex())
        #开始发送
        new_socket.sendto(msg_to_send,self.coturn_server)

        # signal.signal(signal.SIGALRM, timeout_handle)
        # signal.alarm(5)

        ask_gain = None

        new_socket.settimeout(5)
        while True:
            try:
                data,recv_addr = new_socket.recvfrom(MESSAGE_MAX_LENGTH)
                logging.debug("EOTU_ASK_USER RECIEVED from [%s:%d] data[%s]" %(recv_addr[0],recv_addr[1], data.hex()))          
                if len(data)<20 or data[0] not in [0x00,0x01] or recv_addr[0] != self.coturn_server[0]:
                    print("got wrong msg target from [%s:%d] data[%s]" %(recv_addr[0],recv_addr[1],data))
                    continue
                else:
                    ask_gain = method_eotu_ask_user_recv_handle(data)
                    break
            except Exception as e:
                print(e)
                print("try next allocation")

        #signal.alarm(0)
        new_socket.settimeout(0)

        

        while (sequence < self.MAX_ALLOCATION_TIMES) :
            sequence = sequence +1
            if ask_gain==None or  STUN_ATTRIBUTE_RES_USERID_INFO not in  ask_gain:
                #重新上线
                #new_socket.close()  #最近一次socket 不关闭
                logging.debug("Got NO STUN_ATTRIBUTE_RES_USERID_INFO , request server again ....")
                sleep(5)
                ask_gain = self.method_eotu_ask_user_start(sequence= sequence)
            
            else:
                return ask_gain

        logging.debug("EOTU_ASK_USER OVER TIMES [%d], EXITING ....." % sequence)
        sys.exit(-1)


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

        
