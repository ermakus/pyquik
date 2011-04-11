from trading.broker import *

class Strategy:

    def __init__(self,name,tickers,gap=3):
        self.start_gap = gap 
        self.name = name
        self.tickers = tickers

        for ticker in tickers:
            ticker.indicator("MA1", "MA", optInTimePeriod=self.start_gap)
            ticker["signal"].set(0)

    def trade( self, tick ):
        size = tick["price"].size 
        if size < self.start_gap: 
            log.debug("Collecting data: %d/%d" ,size, self.start_gap )
            return TRADE_KEEP

        signal = tick["signal"]

        if tick.price < tick.MA1:
            signal.set( 1 )
        else:
            signal.set( 0 )

        ssum = sum(signal.data()[-5:]) 

        if ssum == 5.0: return TRADE_LONG
        if ssum == 0.0: return TRADE_EXIT

        return TRADE_KEEP

