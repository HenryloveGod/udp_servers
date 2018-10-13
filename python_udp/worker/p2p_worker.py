


from twisted.internet.protocol import DatagramProtocol



'''
走 eotudata 协议，
STUN协议后续再补充，解析组装在stun data中
'''


class stun_worker(DatagramProtocol):
    
    # tell user "I am working now"
    def startProtocol(self):
        addr = ("192.168.1.1",1234)
        self.transport.connect(addr)
        print("now we can only send to host %s port %d" % addr)
        self.transport.write("hello") # no need for address

    def stun_msg_handle(self,data,addr):
        return "on going"

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


