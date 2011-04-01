import unittest
from quik import Quik

class QDDETest(unittest.TestCase):

    def setUp(self):
        self.quik = Quik("C:\\quik-bcs","QuikDDE")
        self.quik.register( "TICKERS",{"code":"Код бумаги","name":"Бумага","price":"Цена послед."}, lambda x: print(x) )

    def testRun(self):
        self.assertTrue(self.quik.error(),"OK")
        self.quik.execute("GARBAGE", lambda res,err,rep,tid,order,msg: print(msg) )
        self.quik.run()

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(QDDETest))
    unittest.TextTestRunner(verbosity=2).run(suite)
