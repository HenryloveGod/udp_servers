from twisted.internet import reactor
from worker.p2p_worker import worker
from dc_utils.dc_log import logging

import sys

port = 3490



def hello():
    logging.info("TWISTED SERVER start on port[%d]\r\n\r\n" %(port))


def main(port):
    # 0 means any port, we don't care in this case
    reactor.listenUDP(port, worker(reactor))
    reactor.callWhenRunning(hello)
    reactor.run()


if __name__ == "__main__":

    main(port)