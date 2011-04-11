# -*- coding: utf-8 -*-
from util.hook import *

def cmd2str(cmd):
    return ";".join( [ ("%s=%.2f" if name == "price" else "%s=%s") % ( name.upper(), cmd[name] ) for name in cmd ] )

def save_as_js(ticker,filename):
    def gen_js(ticker):
        yield("var datasets={")
        X = [ x for x in range(0,ticker('time').size) ]
        for sname in ticker.series:
            if not sname in ['volume','time']:
                yield('"%s":{' % sname )
                if sname == 'signal':
                    x = 'bars: { show: true },'
                else:
                    x =''
                yield('label: "%s", %s data: [' % (sname,x) )
                Y = ticker(sname).data()
                for i in range(0, len(X)):
                    yield("[%s,%s]," % (X[i],Y[i] if not x else 100*Y[i] ))
                yield("]},")
        for i in ticker.indicators.values():
            yield('"%s":{' % i.name )
            yield('label: "%s", data: [' % i.name )
            Y = i.data()
            for n in range(0, len(X)):
                yield("[%s,%s]," % (X[n],Y[n]))
            yield("]},")
        yield("};")
    js = open( filename, "w" )
    for line in gen_js( ticker ):
        js.write( line )
    js.close()

