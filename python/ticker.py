# -*- coding: utf-8 -*-
from order import Order
import numpy,datetime


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
 
class Ticker:

    FIELDS =['seccode','classcode']

    SERIES = ['time','price','volume']

    def __init__(self,factory,name):
        self.factory = factory
        self.seccode = name
        self.classcode = False
        self.series = {}
        for name in Ticker.SERIES:
            self.series[ name ] = Serie(self,name,dtype=(numpy.float if name != 'time' else datetime.datetime))

    def __iter__(self):
        return serie.__iter__()

    def serie(self,name):
        if name in self.series:
            return self.series[name]
        serie = self.series[name] = Serie( self, name )
        return serie

    def order(self,action):
        o = Order(self,action)
        o.seccode = self.seccode
        o.classcode = self.classcode
        o.price = self.price
        return o

    def tick(self):
        for name in Ticker.SERIES:
            self.series[name].push( getattr( self, name, None ) )

    def __str__(self):
        return ";".join( [ "%s=%s" % ( x.upper(), getattr( self, x) ) for x in (Ticker.FIELDS + Ticker.SERIES) ]  )

class TickerFactory:

    def __init__(self, quik):
        self.quik    = quik
        self.tickers = {}
        self.headers = False

    def ticker(self, name):
        if name in self.tickers:
            return self.tickers[ name ]
        ticker = self.tickers[ name ] = Ticker( self, name )
        return ticker

    def update( self, table, r ):
        ticker = self.ticker(self, table.getString(r,self.headers.index("Код бумаги")))
        if not ticker.classcode:
            ticker.classcode = table.getString(r,self.headers.index("Код класса"))

        ticker.time = datetime.datetime()
        ticker.price =  float(table.getDouble(r,self.headers.index("Цена послед.")))
        ticker.volume = int(table.getDouble(r,self.headers.index("Оборот")))
        ticker.tick()

    def load(self, filename):
        fp = file( filename )
        try:
            headers = fp.next().rstrip().split(',')
            IDX_TICKER = headers.index( '<TICKER>' )
            IDX_DATE = headers.index( '<DATE>' )
            IDX_TIME = headers.index( '<TIME>' )
            IDX_LAST = headers.index( '<LAST>' )
            IDX_VOL  = headers.index( '<VOL>' )
            for line in fp:
                row = line.rstrip().split(',')
                ticker = self.ticker( row[ IDX_TICKER ] )
                ticker.time = datetime.datetime.strptime(row[ IDX_DATE ]+row[ IDX_TIME ], '%Y%m%d%H%M%S')
                ticker.price = float(row[ IDX_LAST ])
                ticker.volume = float(row[ IDX_VOL ])
                ticker.tick()
        finally:
            fp.close()

