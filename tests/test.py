from test_batoto import *
from test_cli import *
from test_dynastyscans import *
from test_madokami import *
from test_fumanhua import *
from test_c99comic import *
from test_c99manga import *
from test_c99mh import *
import sys
import unittest
import warnings

if __name__ == '__main__':
    sys.stdout = open(os.devnull, 'w')
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        unittest.main(verbosity=2)
        sys.stdout.close()
