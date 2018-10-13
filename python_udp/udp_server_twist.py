from twisted.internet import reactor
from twistworker.stunworker import stun_worker

import logging 
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
    reactor.listenUDP(port, stun_worker())
    reactor.callWhenRunning(hello)
    reactor.run()


if __name__ == "__main__":

    main(port)