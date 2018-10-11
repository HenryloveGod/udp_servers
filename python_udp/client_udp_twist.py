# coding=utf-8 
from twisted.internet.protocol import ClientFactory, Protocol 
from twisted.internet import reactor 


"""
注册

"""



class Sender(Protocol): 
    def connectionMade(self): 
        """连接成功后调用""" 
        self.send_command() 
        
    def send_command(self): 
        """连接成功后调用他向服务端发送数据""" 
        self.transport.write(b"hello") 
        
    def dataReceived(self, data): 
        """进行数据的接受""" 
        print("DATA", data) 
        
        
class BasicClientFactory(ClientFactory): 
    def __init__(self, protocol): 
        self.protocol = protocol 
        
    def clientConnectionLost(self, connector, reason): 
        print('Lost connection: %s' % reason.getErrorMessage() )
        
        
PORT = 9001 
HOST = '127.0.0.1'
        
# 实例化工厂对象 
test = BasicClientFactory(Sender) 

# 连接服务器 
reactor.connectUDP(HOST, PORT, test) 
reactor.run()

