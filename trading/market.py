# -*- coding: utf-8 -*-
import datetime
from trading.ticker import Ticker

class Market:
    """ The root class to access all market data """

    def __init__(self, conn):
        self.tickers = {}
        self.conn = conn

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


    def ontick(self,data):
        """ Quik tickers data handler """
        ticker = self.__getattr__( data["seccode"] )
        ticker.classcode = data["classcode"]
        ticker.time = datetime.datetime.now()
        ticker.price = data["price"]
        ticker.volume = 0
        ticker.tick()

    def execute(self,cmd,callback=None):
        self.conn.execute( cmd, callback )

    def run( self ):
        """ Start message loop """
        self.conn.register( "TICKERS", {"seccode":"Код бумаги","classcode":"Код класса","price":"Цена послед."}, self.ontick )
        self.conn.run()

