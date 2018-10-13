


from twisted.internet.protocol import DatagramProtocol

from .stun_utils import *



class stun_worker(DatagramProtocol):
    
    # # tell user "I am working now"
    # def startProtocol(self):
    #     host = "192.168.1.1"
    #     port = 1234
    #     self.transport.connect(host, port)
    #     print("now we can only send to host %s port %d" % (host, port))
    #     self.transport.write("hello") # no need for address


    clients = {}

    '''
    =============================================
        METHOD 消息类型处理
    =============================================
    '''

    def stun_method_binding_handle(self,stun_recv):
        pass


    def stun_method_allocation_handle(self,stun_recv):
        pass
        return 1,b"ok"

    def stun_method_eotu_ask_user_handle(self,stun_recv):
        return 1,b"no user now"

    def stun_method_refresh_handle(self,stun_recv):
        pass

    def stun_method_send_handle(self,stun_recv):
        pass

    def stun_method_data_handle(self,stun_recv):
        pass

    def stun_method_create_permission_handle(self,stun_recv):
        pass
    def stun_method_connect_handle(self,stun_recv):
        pass

    def stun_method_unknow(self,stun_recv):
        pass


# #消息类型处理 函数

    msg_handle_funcs={
        STUN_METHOD_BINDING:stun_method_binding_handle,
        STUN_METHOD_ALLOCATE:stun_method_allocation_handle,
        STUN_METHOD_REFRESH:stun_method_refresh_handle,
        STUN_METHOD_SEND:stun_method_send_handle,
        STUN_METHOD_DATA:stun_method_data_handle,
        STUN_METHOD_CREATE_PERMISSION:stun_method_create_permission_handle,
        STUN_METHOD_CONNECT : stun_method_connect_handle,
        STUN_METHOD_EOTU_ASK_USER : stun_method_eotu_ask_user_handle,
    }




    def stun_msg_handle(self,data,addr):

        stun_recv = dismessage(data)
        
        if stun_recv.user_id not in self.clients:
            self.clients[stun_recv.user_id] = addr
        print((stun_recv.msg_type))
        
        stun_method = bytes_to_int(stun_recv.msg_type)

        if stun_method in self.msg_handle_funcs:
            try:
                result,response = self.msg_handle_funcs[stun_method](self,stun_recv)
                if result == 1:
                    return response
                else:
                    return None
            except Exception as e:
                print(e)
                logging.error("on going to handle")
        else:
            logging.error("stun method not found [%s]" %(stun_recv.msg_type.hex()))


    def datagramReceived(self, data, addr):
        print("received %r from %s:%d" % (data, addr[0], addr[1]))

        # Join the multicast address, so we can receive replies:

        response = self.stun_msg_handle(data,addr)

        if response:
            self.transport.write(response,addr) # no need for address

    # Possibly invoked if there is no server listening on the
    # address to which we are sending.
    def connectionRefused(self):
        print("No one listening")


