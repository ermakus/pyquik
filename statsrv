#!/usr/bin/python
import os, web
import numpy, pylab, sys
from trading.ticker import TickerFactory, Indicator
import time

urls = (
    '/datasource.js(.*)', 'DataSource',
    '/(.*)', 'StaticFiles',
)

app = web.application(urls, globals())

factory = TickerFactory(None)
factory.load( "test/testdata.txt" )

class StaticFiles:
    def GET(self, path):
        if path == "":
            path = "index.html"
            web.header('Content-type','text/html')
        else:
            web.header('Content-type','application/javascript')
        try:
            return open( os.path.join("www",path), "r" ).read()
        except:
            return app.notfound()

def datasource( cut ):
    yield("var datasets={")
    for name in factory.tickers:
        ticker = factory( name )
        X = [ time.mktime( x.timetuple() ) for x in ticker('time').data()[cut:] ]
        ticker("MA", Indicator, optInTimePeriod=cut )
        for sname in ticker.series:
            if sname in ['price','MA']:
                yield('"%s":{' % sname )
                yield('label: "%s", data: [' % sname )
                Y = ticker(sname).data()[cut:]
                for i in range(0, len(X)):
                    yield("[%s,%s]," % (X[i],Y[i]))
                yield("]},")
    yield("};")


class DataSource:
    def GET(self, name):
        web.header('Content-type','application/javascript')
        web.header('Transfer-Encoding','chunked') 
        return datasource( 30 )

if __name__ == "__main__":
    app.run()
