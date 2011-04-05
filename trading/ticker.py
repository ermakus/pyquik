# -*- coding: utf-8 -*-
from .order import Order, BUY, SELL, MARKET_PRICE
from talib.talib import TA_LIB, TA_Func
import numpy,datetime


ta_lib = TA_LIB()

class Serie:

    ALLOC_BLOCK=1024

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

class Indicator(Serie):

    def __init__(self,ticker, name, **kwargs):
        Serie.__init__(self,ticker,name)
        self.func = ta_lib.func( name )
        self.kwa = kwargs
        src = self.ticker("price").data()
        src_len = len(src)
        if src_len:
            self.buf.resize( src_len )
            self.size = src_len
            shift, num = self.func(0, src_len-1, src, self.buf)
            self.buf = numpy.roll( self.buf, shift )

    def push(self,value):
        Serie.push( self, 0.0 )
        src = self.ticker("price").data()
        idx = self.size-1
        self.func(idx, idx, src, self.buf[idx:], **self.kwa)

 
class Ticker:

    FIELDS =['seccode','classcode']

    SERIES = ['time','price','volume']

    def __init__(self,market,name):
        self.market = market
        self.seccode = name
        self.classcode = False
        self.series = {}
        self.orders = []
        self.on_tick = None
        for name in Ticker.SERIES:
            self.series[ name ] = Serie(self,name,dtype=(numpy.float if name != 'time' else datetime.datetime))

    def __iter__(self):
        return serie.__iter__()

    def __call__(self,name,stype=Serie, **kwargs):
        if name in self.series:
            return self.series[name]
        serie = self.series[name] = Indicator( self, name, **kwargs )
        return serie

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
        for name in self.series:
            self.series[name].push( getattr( self, name, None ) )
        if self.on_tick:
            self.on_tick( self )

    def ontick(self,callback):
        self.on_tick = callback

    def __repr__(self):
        return ";".join( [ "%s=%s" % ( x.upper(), getattr( self, x) ) for x in (Ticker.FIELDS + Ticker.SERIES) ]  )

