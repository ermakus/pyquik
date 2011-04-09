# -*- coding: utf-8 -*-
import logging
from trading.ticker import Ticker
from trading.broker import Broker
from util import cmd2str

log = logging.getLogger("market")

class Market:
    """ The root class to access all market data """

    def __init__(self):
        self.tickers = {}
        self.strategies = {} 
        self.broker = Broker()

    def __getitem__(self,name):
        """ Helper method to access ticker as attribute """ 
        return self.ticker( name )

    def ticker(self,name):
        """ Return or create ticker by name """
        if not name in self.tickers: 
            self.tickers[name] = Ticker( self, name )
        return self.tickers[name]

    def add_strategy(self,strategy):
        self.strategies[ strategy.name ] = strategy

    def tick(self, ticker):
        ticker.tick()
        for strategy in self.strategies.values():
            if ticker in strategy.tickers:
                position = strategy.trade( ticker )
                #log.debug("Strategy: %s -> %s", strategy.name, "IDLE" if position != 0 else ("LONG" if position > 0 else "SHORT") )
                self.broker.trade( position, ticker )

    def execute(self,order,callback=None):
        """ Execute transaction """
        vals = [ getattr( order, x, None ) for x in order.keys ]
        cmd = dict( zip( order.keys, vals ) )
        self.conn.execute( cmd, callback )

    def run( self ):
        """ Start message loop """
        self.conn.run()
