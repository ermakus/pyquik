# -*- coding: utf-8 -*-
import unittest,sys
sys.path.insert(0, '.')

def print_data(x):
    print(x)

class QDDETest(unittest.TestCase):

    def setUp(self):
        self.quik = quik.Quik("C:\\quik-bcs","QuikDDE")
        self.quik.subscribe( "TICKERS",{"code":"Код бумаги","name":"Бумага","price":"Цена послед."}, print_data )

    def testRun(self):
        self.assertTrue(self.quik.error(),"OK")
        self.quik.execute({"trans_id":"1"}, print_data )
        self.quik.run()

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(QDDETest))
    unittest.TextTestRunner(verbosity=2).run(suite)
