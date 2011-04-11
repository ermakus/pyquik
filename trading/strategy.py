from trading.broker import *

class Strategy:

    def __init__(self,ticker):
        self.start_gap = 13 
        self.ticker = ticker
        self.ma1 = ticker.indicator("MA1", "MA", optInTimePeriod=self.start_gap)
        self.signal = ticker["signal"]
        self.signal.set(0)

    def trade( self, ticker ):
        size = len(ticker)
        if size < self.start_gap: 
            log.debug("Collecting data: %d/%d" ,size, self.start_gap )
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

