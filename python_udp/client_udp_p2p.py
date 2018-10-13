# coding=utf-8 

import sys
import getopt
import socket
from eotudata.eotudata import eotudata
import json
from dc_utils.dc_log import logging

SERVER_ADDR = ('127.0.0.1',9001)
USERS={
    0:[(1,123),(2,123)],
    1:[(2,123),(1,123)]
}
TEST_USER = USERS[0]


client={}


class vistor():

    user_me = None
    socket_fd = None

    def __init__(self,user_me,server_addr):
        self.socket_fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_fd.connect(server_addr)
        self.user_me = user_me
        
    def register(self):
        regs = {
            "method":"register",
            "uid":self.user_me[0],
            "channel":self.user_me[1]
        }
        bytes_regs = bytes(json.dumps(regs),encoding="utf-8")
        bytes_send = eotudata().bytedata(1,bytes_regs)
        self.socket_fd.send(bytes_send)
        while True:
            data, server = self.socket_fd.recvfrom(4096)
            logging.debug('received {!r}'.format(data))
            return data

    def ask_user(self,user_op):
        logging.info("start to ask user")
        regs = {
            "method":"ask_user",
            "ask_uid":user_op[0],
            "channel":user_op[1]
        }
        bytes_regs = bytes(json.dumps(regs),encoding="utf-8")
        bytes_send = eotudata().bytedata(1,bytes_regs)
        self.socket_fd.send(bytes_send)
        while True:
            data, server = self.socket_fd.recvfrom(4096)
            logging.debug('received {!r}'.format(data))
            return data


def usage():
    pass

def set_options():
    global TEST_USER
    try:
        opts, _ = getopt.getopt(sys.argv[1:], "hu:", ["help", "user="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-u", "--user"):
            TEST_USER = USERS[int(a)]
        else:
            assert False, "unhandled option"
            usage()
    

def main():
    global TEST_USER
    set_options()
    user_me = TEST_USER[0]
    user_op = TEST_USER[1]
    a_visitor = vistor(user_me,SERVER_ADDR)
    a_visitor.register()
    a_visitor.ask_user(user_op)



if __name__ == "__main__":

    main()
