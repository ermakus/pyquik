import unittest, datetime
from trading import *
from trading.backtest import BacktestMarket
from trading.broker import *
from util import Hook, ReadyHook, cmd2str


class TestConn:
    def __init__(self, market):
        self.market = market

    def execute( self, cmd, callback ):
        self.market.last_cmd = cmd2str(cmd)

class TestMarket(BacktestMarket):

    def __init__(self):
        BacktestMarket.__init__(self)
        self.conn = TestConn( self )

    def execute( self, cmd, callback ):
        Market.execute( self, cmd, callback )


class TradingTest(unittest.TestCase):

    def setUp(self):
        self.market = TestMarket()
        self.ticker = self.market["SBER"]
        self.ticker.classcode = "SBERCC"

    def callback(self, val):
        self.hooked = val

    def testHook(self):
        self.hooked = False
        h = Hook()
        h += self.callback
        h(True)
        self.assertTrue( self.hooked )
        h -= self.callback
        h(False)
        self.assertTrue( self.hooked )

        rh = ReadyHook(1)
        rh += self.callback
        rh(False)
        self.assertTrue( self.hooked )
        rh.ready()
        rh(False)
        self.assertFalse( self.hooked )
        rh.start()
        rh(True)
        self.assertFalse( self.hooked )

    def testTicker(self):
        self.ticker.price = 1.0
        self.assertEquals(self.ticker.price, self.market["SBER"].price)

    def testSeries(self):
        self.ticker.time = datetime.datetime.now()
        self.ticker.price = 10.0
        self.ticker.tick()
        self.assertEquals(self.ticker['time'].data()[0], self.ticker.time )
        self.assertEquals(self.ticker['time'].size, 1 )
        self.assertEquals(len(self.ticker['time'].data()), 1 )
        self.assertEquals(self.ticker['price'].data()[0], 10.0 )
        self.assertEquals(self.ticker['price'].size, 1 )

    def testHistory(self):
        self.market.load("test/testdata-1000.txt")
        self.assertEquals(self.ticker['time'].size, 1000)

    def testIndicator(self):
        ind = self.ticker.indicator("MA-30", "MA")
        self.market.load("test/testdata-1000.txt")
        self.assertEquals(self.ticker.indicator('MA-30').size, 1000)
        A = ind.data()
        del( self.ticker.indicators["MA-30"] )
        B = self.ticker.indicator("MA-30","MA").data()
        for i in range( len(A) ): self.assertAlmostEqual( A[i], B[i] )

    def testOrderCreation(self):
        o1 = self.market["SBER"].order( 100 )
        self.assertEquals( o1.order_key, 100 )
        o1.price = 555
        o2 = self.market["SBER"].order( 100 )
        self.assertEquals( o2.price, 555 )

    def testOrderExecution(self):
        Order.LAST_ID=0
        order = self.market["SBER"].buy(100,1)
        self.assertEquals( order.operation, BUY )
        self.assertEquals( order.price, 100 )
        self.assertEquals( order.quantity, 1 )
        order.submit()
        self.assertEquals( self.market.last_cmd, "ACCOUNT=L01-00000F00;CLASSCODE=SBERCC;PRICE=100.00;CLIENT_CODE=52709;ACTION=NEW_ORDER;OPERATION=B;SECCODE=SBER;TRANS_ID=1;QUANTITY=1")
        order = self.market["SBER"].sell(MARKET_PRICE,10)
        order.submit()
        self.assertEquals( self.market.last_cmd, "ACCOUNT=L01-00000F00;CLASSCODE=SBERCC;PRICE=0.00;CLIENT_CODE=52709;ACTION=NEW_ORDER;OPERATION=S;SECCODE=SBER;TRANS_ID=2;QUANTITY=10" )
        order.order_key = "OK-%s" % order.trans_id
        order.kill()
        self.assertEquals( self.market.last_cmd, "ACTION=KILL_ORDER;SECCODE=SBER;CLASSCODE=SBERCC;TRANS_ID=3;ORDER_KEY=OK-2" )

    def testBroker(self):
        Order.LAST_ID=0
        broker = Broker()
        self.ticker["price"].set(100.0)
        o = broker.trade( TRADE_SHORT, self.ticker )
        self.assertEquals( self.market.last_cmd, "ACCOUNT=L01-00000F00;CLASSCODE=SBERCC;PRICE=100.00;CLIENT_CODE=52709;ACTION=NEW_ORDER;OPERATION=S;SECCODE=SBER;TRANS_ID=1;QUANTITY=1" )
        o.submit_status({"order_key":"100"})
        broker.trade( TRADE_EXIT, self.ticker )
        self.assertEquals( self.market.last_cmd, "ACTION=KILL_ORDER;SECCODE=SBER;CLASSCODE=SBERCC;TRANS_ID=2;ORDER_KEY=100" )
        o = broker.trade( TRADE_LONG, self.ticker )
        self.assertEquals( self.market.last_cmd, "ACCOUNT=L01-00000F00;CLASSCODE=SBERCC;PRICE=100.00;CLIENT_CODE=52709;ACTION=NEW_ORDER;OPERATION=B;SECCODE=SBER;TRANS_ID=3;QUANTITY=1" )
        o.submit_status({"order_key":"101"})
        o.status = EXECUTED 
        o = broker.trade( TRADE_SHORT, self.ticker )
        self.assertEquals( self.market.last_cmd, "ACCOUNT=L01-00000F00;CLASSCODE=SBERCC;PRICE=100.00;CLIENT_CODE=52709;ACTION=NEW_ORDER;OPERATION=S;SECCODE=SBER;TRANS_ID=4;QUANTITY=2" )
        o.submit_status({"order_key":"102"})
        o.status = EXECUTED 
        o = broker.trade( TRADE_EXIT, self.ticker )
        self.assertEquals( self.market.last_cmd, "ACCOUNT=L01-00000F00;CLASSCODE=SBERCC;PRICE=100.00;CLIENT_CODE=52709;ACTION=NEW_ORDER;OPERATION=B;SECCODE=SBER;TRANS_ID=5;QUANTITY=1" )
 
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TradingTest))
    Funittest.TextTestRunner(verbosity=2).run(suite)
