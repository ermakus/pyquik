ctypedef int TA_RetCode

cdef extern from "ta_libc.h":
    enum: TA_SUCCESS
    TA_RetCode TA_MA(int startIdx, int endIdx, double inReal[], int optInTimePeriod, int optInMAType, int *outBegIdx, int *outNbElement, double outReal[])
    TA_RetCode TA_Initialize()
    TA_RetCode TA_Shutdown()

from libc.stdlib cimport *

def moving_average(inarr, int begIdx=0, int endIdx=-1, int optInTimePeriod=1, int optInMAType=0):

    retCode =  TA_Initialize()

    if retCode != TA_SUCCESS:
        raise Exception("Cannot initialize TA-Lib: %d" % retCode)

    outarr = []
    n = len(inarr)

    cdef double* inreal = <double*>malloc( n * sizeof( double ) )
    cdef double* outreal = <double*>malloc( n * sizeof( double ) )
    cdef int outbegidx = 0
    cdef int outnbelement = 0

    try:
        for i in range(n):
            inreal[i] = float(inarr[i])

        retCode =  TA_MA(begIdx, endIdx, <double *>inreal, optInTimePeriod, optInMAType, &outbegidx, &outnbelement, <double *>outreal)

        if retCode != TA_SUCCESS:
            raise Exception("TA-Lib call error: %d" % retCode)

        for i in range(outnbelement):
            outarr.append( float(outreal[i]) )

    finally:
        free( inreal )
        free( outreal )
        TA_Shutdown()
    
    return (retCode, outbegidx, outnbelement, outarr)