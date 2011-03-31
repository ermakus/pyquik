import unittest, datetime
from ticker import TickerFactory, Indicator

class TickerTest(unittest.TestCase):

    def setUp(self):
        self.factory = TickerFactory(None)
        self.ticker = self.factory("SBER")

    def testFactory(self):
        self.ticker.price = 1.0
        self.assertEquals(self.ticker.price, self.factory("SBER").price)

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

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TickerTest))
    unittest.TextTestRunner(verbosity=2).run(suite)
