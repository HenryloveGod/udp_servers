# coding=utf-8 


import json,socket
import os,sys
from time import sleep
from optparse import OptionParser


sys.path.insert(1, os.path.realpath(os.path.pardir))

from dc_utils.dc_log import logging
from eotudata.eotudata import eotudata


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
        logging.info("start to register user [%d]" % self.user_me[0])
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

    def ask_user(self,user_op,try_times = 10):

        logging.info("start to ask user [%d]" % user_op[0])
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
            if b"error" in data:
                try_times = try_times - 1
                sleep(3)
                self.ask_user(user_op)
            else:
                logging.debug('received {!r}'.format(data))
                return 1,data

            if try_times ==0:
                return -1,"not found"

    def ask_user_all(self):
        logging.info("start to ask user_all")
        regs = {
            "method":"ask_user_all"
        }
        bytes_regs = bytes(json.dumps(regs),encoding="utf-8")
        bytes_send = eotudata().bytedata(1,bytes_regs)
        self.socket_fd.send(bytes_send)
        while True:
            data, server = self.socket_fd.recvfrom(4096)
            logging.debug('received {!r}'.format(data))
            return data


    def turn_data_to_uid(self,turndata,to_uid):
        logging.info("start to turn_data_to_uid")
        json_regs = {
            "method":"turn_data",
            "to_uid":to_uid,
            "from_uid":self.user_me
        }   
        bytes_json_regs = bytes(json.dumps(json_regs),encoding="utf-8")
        bytes_stream_data = bytes(turndata,encoding="utf-8")

        bytes_send = eotudata().bytedata(2,bytes_json_regs,bytes_stream_data)
        self.socket_fd.send(bytes_send)
        while True:
            data, server = self.socket_fd.recvfrom(4096)
            logging.debug('received {!r}'.format(data))
            return data


    def loop(self):
        while True:
            data, server = self.socket_fd.recvfrom(4096)
            logging.debug('received {!r}'.format(data))
   

def usage():
    pass

def set_options():
    global TEST_USER


    parser = OptionParser(add_help_option=False)
    parser.add_option("-u", "--user_no", dest="user_no",
                    default=0,help="select user_group number")

    parser.add_option("-h", "--help",action="help")

    (options, args) = parser.parse_args()

    user_no = int(options.user_no)
    if user_no in USERS:
        TEST_USER = USERS[user_no]



def main():
    global TEST_USER
    set_options()
    user_me = TEST_USER[0]
    user_op = TEST_USER[1]
    a_visitor = vistor(user_me,SERVER_ADDR)
    
    a_visitor.register()
    a_visitor.ask_user(user_op)

    a_visitor.turn_data_to_uid("hello try to miss you",user_op)

    a_visitor.loop()

if __name__ == "__main__":

    main()
