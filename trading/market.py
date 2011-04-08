# -*- coding: utf-8 -*-
import datetime, logging
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

    def __getattr__(self,name):
        """ Helper method to access ticker as attribute """ 
        return self.ticker( name )

    def ticker(self,name):
        """ Return or create ticker by name """
        if not name in self.tickers: 
            self.tickers[name] = Ticker( self, name )
        return self.tickers[name]

    def load(self, filename):
        """ Load backtest data """
        fp = open( filename )
        try:
            headers = fp.readline().rstrip().split(',')
            IDX_TICKER = headers.index( '<TICKER>' )
            IDX_DATE = headers.index( '<DATE>' )
            IDX_TIME = headers.index( '<TIME>' )
            IDX_LAST = headers.index( '<LAST>' )
            IDX_VOL  = headers.index( '<VOL>' )
            while True:
                line = fp.readline()
                if not line: break
                row = line.rstrip().split(',')
                ticker = self.__getattr__( row[ IDX_TICKER ] )
                ticker.time = datetime.datetime.strptime(row[ IDX_DATE ]+row[ IDX_TIME ], '%Y%m%d%H%M%S')
                ticker.price = float(row[ IDX_LAST ])
                ticker.volume = float(row[ IDX_VOL ])
                self.tick(ticker)
        finally:
            fp.close()

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
