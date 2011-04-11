import unittest,sys,datetime
from trading.backtest import BacktestMarket
from trading.strategy import Strategy
from trading.evolver import Evolver
import random

class BackTest(unittest.TestCase):

    def setUp(self):
        self.market = BacktestMarket()

    def testStrategy(self):
        candle = self.market["SBER"].candle( datetime.timedelta( minutes=1 ) )
        candle.strategy( Strategy )
        self.market.load( "test/sber-1000.csv" )
        self.assertEquals( self.market.ticks, 1000 )
        self.assertEquals( self.market.trades, 23 ) 
        self.assertAlmostEqual( self.market.balance, 1.31 ) 

    def testEvolve(self):
        random.seed(10)
        evolver = Evolver( "test/sber-1000.csv", 4, 4 )
        evolver.run()
        self.assertEquals( evolver.best[0], 2 )
        self.assertEquals( evolver.best[1], 71 )
