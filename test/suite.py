import unittest, sys, os
sys.path.insert(0, '.')

from tradingtest import *
from talibtest import *
from backtest import *

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BackTest))
    suite.addTest(unittest.makeSuite(TradingTest))
    suite.addTest(unittest.makeSuite(TA_LIB_Test))
    unittest.TextTestRunner(verbosity=2).run(suite)
