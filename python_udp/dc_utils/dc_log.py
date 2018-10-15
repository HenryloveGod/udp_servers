import logging
import sys


'''
设置log参数
'''

logging.basicConfig(
    stream = sys.stdout,
    level=logging.DEBUG,
    format=' [%(filename)s:%(lineno)d]%(levelname)s: %(message)s',
    datefmt='%Y-%M-%D'
    )