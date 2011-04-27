# -*- coding: utf-8 -*-
from util.hook import *

def cmd2str(cmd):
    return ";".join( [ ("%s=%.2f" if name == "price" else "%s=%s") % ( name.upper(), cmd[name] ) for name in cmd ] )

def gen_js(ticker):
    yield("draw( {")
    X = [ x for x in xrange(0, len(ticker))]
    for sname in ticker.series:
        if not sname in ['volume','time']:
            yield('"%s":{' % sname )
            yield('label: "%s",' % sname )
            if sname == 'signal':
                yield('bars: { show: true },')
                bar=True
            else:
                bar=False
            yield('data: [')
            yield("]},")
    yield("});\n")

    for i in xrange(0, len(X)):
        yield("tick([%s," % X[i] )
        for sname in ticker.series:
            if not sname in ['volume','time']:
                Y = ticker[sname].data()
                yield("%s," % Y[i] )
        yield("]);\n")
  
def save_as_js(ticker,filename):
   js = open( filename, "w" )
   for line in gen_js( ticker ):
       js.write( line )
   js.close()

