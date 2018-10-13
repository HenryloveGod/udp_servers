import socket


#   ip转化为4字节的int
def iptoint(self,ip):
    return int(socket.inet_aton(ip).encode('hex'),32)

#   ip整数转化为ip string
def inttoip(self,ip):
    return socket.inet_ntoa(hex(ip)[2:].decode('hex'))

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
