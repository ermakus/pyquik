# -*- coding: utf-8 -*-
import datetime
from trading.ticker import Ticker


class Account:
    def __init__(self,account_id,balance=0.0):
        self.account_id = account_id
        self.balance = balance

class Market:
    """ The root class to access all market data """

    def __init__(self):
        self.tickers = {}

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
                ticker.tick()
        finally:
            fp.close()

    def execute(self,cmd,callback=None):
        """ Execute transaction """
        self.conn.execute( cmd, callback )

    def run( self ):
        """ Start message loop """
        self.conn.run()
