import unittest
import talib
from numpy import array

class TA_LIB_Test(unittest.TestCase):

    def setUp(self):
        self.lib = talib.TA_LIB()

    def testLists(self):
        groups = self.lib.group_list()
        self.assertTrue( len(groups) > 0 )
        functs = self.lib.func_list( groups[0] )
        self.assertTrue( len(functs) > 0 )

    def testCall(self):
        MA = self.lib.func("MA")
        self.assertEquals( str(MA),"MA(inReal,outReal,optInTimePeriod=30.0,optInMAType=0.0)")

        inarr=array([1,2,3,4,5,6,6,5,4,3,2,1],dtype=float)
        outarr=array([],dtype=float)
        MA(inarr, outarr, optInTimePeriod=2, optInMAType=0)
        print( "-> %s" % inarr )
        print( "<- %s" % outarr )
        expect=array([1.5,  2.5,  3.5,  4.5,  5.5,  6. ,  5.5,  4.5,  3.5,  2.5,  1.5, 0.0],dtype=float)
        self.assertEquals(outarr,expect)

#        print( self.lib.MA(inarr, begIdx=0, endIdx=len(inarr)-1, optInTimePeriod=2, optInMAType=0) )

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TA_LIB_Test))
    unittest.TextTestRunner(verbosity=2).run(suite)
