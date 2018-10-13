from twisted.internet import reactor
from worker.p2p_worker import worker
from dc_utils.dc_log import logging

import sys

port = 9001

logging.basicConfig(
    stream = sys.stdout,
    level=logging.DEBUG,
    format=' %(filename)s[%(funcName)s][line:%(lineno)d]: %(message)s',
    datefmt='%Y-%M-%D'
    )

def hello():
    logging.info("twist server start on port[%d]" %(port))


def main(port):
    # 0 means any port, we don't care in this case
    reactor.listenUDP(port, worker(reactor))
    reactor.callWhenRunning(hello)
    reactor.run()


if __name__ == "__main__":

    main(port)