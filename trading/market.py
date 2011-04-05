# -*- coding: utf-8 -*-
import datetime
from trading.ticker import Ticker
from trading.order import Order, BUY, SELL

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

    def execute(self,cmd,callback=None):
        self.conn.execute( cmd, callback )


    def ontick(self,data):
        """ Quik tickers data handler """
        ticker = self.ticker( data["seccode"] )
        ticker.classcode = data["classcode"]
        ticker.time = datetime.datetime.now()
        ticker.price = data["price"]
        ticker.volume = 0
        ticker.tick()

    ORDER_OP = {"Купля":BUY,"Продажа":SELL}

    def onorder(self,data):
        state = data["state"]
        if state == "Снята": return
        ticker = self.__getattr__( data["seccode"] )
        order = ticker.order( int( data["order_key"] ) )
        order.operation = Market.ORDER_OP[ data["operation"] ]
        order.price = float( data["price"] )
        order.quantity = int( data["quantity"] )
        order.quantity_left = int( data["left"] )

    def run( self ):
        """ Start message loop """
        self.conn.register( "TICKERS", {"seccode":"Код бумаги","classcode":"Код класса","price":"Цена послед."}, self.ontick )
        self.conn.register( "ORDERS", {"order_key":"Номер","seccode":"Код бумаги","operation":"Операция","price":"Цена","quantity":"Кол-во","left":"Остаток","state":"Состояние"}, self.onorder )
        self.conn.run()

