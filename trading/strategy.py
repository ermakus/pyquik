from trading.broker import *

class Strategy:

    def __init__(self,ticker,matype=0,period=13):
        self.ticker = ticker
        self.matype = matype
        self.period = period
        self.ma1 = ticker.indicator("MA1", "MA", optInTimePeriod=period, optInMAType=matype)
        self.signal = ticker["signal"]
        self.signal.set(0)

    def trade( self, ticker ):
        size = len(ticker)
        if size < self.period: 
            log.debug("Collecting data: %d/%d" ,size, self.period )
            return TRADE_KEEP

        if ticker.price < self.ma1.value():
            self.signal.set( 1 )
        else:
            self.signal.set( 0 )

        ssum = sum(self.signal.data()[-5:]) 
        if ssum == 5.0: 
            return TRADE_LONG
        if ssum == 0.0:
            return TRADE_EXIT

        return TRADE_KEEP

