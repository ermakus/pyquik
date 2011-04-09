# -*- coding: utf-8 -*-
from .order import Order, BUY, SELL, MARKET_PRICE
from talib.talib import TA_LIB, TA_Func
import numpy,datetime
from util import Hook

ta_lib = TA_LIB()

class Serie:

    ALLOC_BLOCK=65536

    def __init__(self,ticker, name, dtype=numpy.float):
        self.ticker = ticker
        self.name = name
        self.size = 0
        self.buf = numpy.array([], dtype=dtype)

    def push(self, value):
        if self.size >= len(self.buf):
            self.buf.resize( self.size + Serie.ALLOC_BLOCK )
        self.buf[ self.size ] = value
        self.size += 1

    def data(self):
        return self.buf[:self.size]

    def value(self,offset=0):
        return self.buf[self.size-1-offset]

    def set(self,value):
        if self.size > 0: self.buf[self.size-1] = value
        setattr( self.ticker, self.name, value )

class Indicator(Serie):

    def __init__(self,ticker, name, func, **kwargs):
        Serie.__init__(self,ticker,name)
        self.func = ta_lib.func( func )
        self.kwa = kwargs
        self.src = self.ticker("price")
        src_len = self.src.size
        if src_len:
            self.buf.resize( src_len )
            self.size = src_len
            shift, num = self.func(0, src_len-1, self.src.buf, self.buf)
            self.buf = numpy.array( numpy.roll( self.buf, shift ), copy=True )
            setattr( self.ticker, self.name, self.value() )

    def push(self,last_price):
        Serie.push( self, 0.0 )
        idx = self.size-1
        self.func(idx, idx, self.src.buf, self.buf[idx:], **self.kwa)
        setattr( self.ticker, self.name, self.buf[idx] )
 
class Ticker:

    SERIES = ['time','price','volume']

    def __init__(self,market,name):
        self.market = market
        self.name = self.seccode = name
        self.classcode = False
        self.series = {}
        self.indicators = {}
        self.orders = []
        self.price = 0.0
        self.ontick = Hook()
        for name in Ticker.SERIES:
            self.series[ name ] = Serie(self,name,dtype=(numpy.float if name != 'time' else datetime.datetime))

    def __iter__(self):
        return serie.__iter__()

    def __call__(self,name):
        if name in self.series:
            return self.series[name]
        serie = self.series[name] = Serie( self, name)
        return serie

    def indicator(self,name,func=None, **kwargs):
        if name in self.indicators:
            return self.indicators[name]
        if not func:
            raise Exception("Indicator function not set")
        ind = self.indicators[name] = Indicator( self, name, func, **kwargs )
        return ind

    def buy(self,price=MARKET_PRICE,quantity=1):
        o = Order(self,BUY, price, quantity)
        self.orders.append(o)
        return o

    def sell(self,price=MARKET_PRICE,quantity=1):
        o = Order(self, SELL, price, quantity)
        self.orders.append(o)
        return o

    def order(self, order_key):
        tmp = Order( self )
        tmp.order_key = order_key
        try:
            return self.orders[ self.orders.index( tmp ) ]
        except ValueError:
            self.orders.append( tmp )
            return tmp

    def tick(self):
        for serie in self.series.values():
            serie.push( getattr( self, serie.name, None ) )
        for ind in self.indicators.values():
            ind.push( self.price )
        self.ontick( self )

    def __repr__(self):
        return "%s: %.2f" % (self.name, self.price)
