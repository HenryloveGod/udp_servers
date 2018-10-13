import logging
import sys


'''
设置log参数
'''

logging.basicConfig(
    stream = sys.stdout,
    level=logging.DEBUG,
    format=' %(filename)s[%(funcName)s][line:%(lineno)d] %(message)s',
    datefmt='%Y-%M-%D'
    )