from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor


#   
#
#


class Helloer(DatagramProtocol):

    # def startProtocol(self):
    #     host = "192.168.1.1"
    #     port = 1234

    #     self.transport.connect(host, port)
    #     print("now we can only send to host %s port %d" % (host, port))
    #     self.transport.write("hello") # no need for address


    clients = {}


    def datagramReceived(self, data, addr):
        print("received %r from %s:%d" % (data, addr[0], addr[1]))

        # Join the multicast address, so we can receive replies:
        self.clients[addr[0]] = data
        self.transport.write(b"is ok",addr) # no need for address

    # Possibly invoked if there is no server listening on the
    # address to which we are sending.
    def connectionRefused(self):
        print("No one listening")

# 0 means any port, we don't care in this case
reactor.listenUDP(9001, Helloer())
reactor.run()
