import unittest, datetime
from trading.ticker import *
from trading.order import *

class TestQuik:
    
    def execute(self,cmd,order):
        self.last_cmd = cmd
        order.order_key = "OK-%s" % order.trans_id

class TickerTest(unittest.TestCase):

    def setUp(self):
        self.quik = TestQuik()
        self.factory = TickerFactory( self.quik )
        self.ticker = self.factory.SBER
        self.ticker.classcode = "SBERCC"

    def testFactory(self):
        self.ticker.price = 1.0
        self.assertEquals(self.ticker.price, self.factory.SBER.price)

    def testSeries(self):
        self.ticker.time = datetime.datetime.now()
        self.ticker.price = 10.0
        self.ticker.tick()
        self.assertEquals(self.ticker('time').data()[0], self.ticker.time )
        self.assertEquals(self.ticker('time').size, 1 )
        self.assertEquals(len(self.ticker('time').data()), 1 )
        self.assertEquals(self.ticker('price').data()[0], 10.0 )
        self.assertEquals(self.ticker('price').size, 1 )

    def testHistory(self):
        self.factory.load("test/testdata-1000.txt")
        self.assertEquals(self.ticker('time').size, 1000)

    def testIndicator(self):
        ind = self.ticker("MA", Indicator)
        self.factory.load("test/testdata-1000.txt")
        self.assertEquals(self.ticker('time').size, 1000)
        A = ind.data()
        del( self.ticker.series["MA"] )
        B = self.ticker("MA").data()
        for i in range( len(A) ): self.assertAlmostEqual( A[i], B[i] )


    def testOrder(self):
        Order.LAST_ID=0
        order = self.factory.SBER.buy(100,1)
        self.assertEquals( order.operation, BUY )
        self.assertEquals( order.price, 100 )
        self.assertEquals( order.quantity, 1 )
        self.assertEquals( self.quik.last_cmd, "ACTION=NEW_ORDER;TRANS_ID=1;SECCODE=SBER;CLASSCODE=SBERCC;ACCOUNT=L01-00000F00;CLIENT_CODE=52709;OPERATION=B;QUANTITY=1;PRICE=100.00" )
        order = self.factory.SBER.sell(MARKET_PRICE,10)
        self.assertEquals( self.quik.last_cmd, "ACTION=NEW_ORDER;TRANS_ID=2;SECCODE=SBER;CLASSCODE=SBERCC;ACCOUNT=L01-00000F00;CLIENT_CODE=52709;OPERATION=S;QUANTITY=10;PRICE=0.00" )
        order.kill()
        self.assertEquals( self.quik.last_cmd, "ACTION=KILL_ORDER;TRANS_ID=3;SECCODE=SBER;CLASSCODE=SBERCC;ORDER_KEY=OK-2" )

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TickerTest))
    unittest.TextTestRunner(verbosity=2).run(suite)
