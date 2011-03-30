#!/usr/bin/python
import numpy, pylab, sys
from ticker import TickerFactory

if __name__ == "__main__":

    if len( sys.argv ) != 2:
        print("Usage: %s <series_file.txt>" % sys.argv[0])
        sys.exit(1)

    factory = TickerFactory(None)
    factory.ticker("SBER").indicator("MA")
    factory.load( sys.argv[1] )

    for name in factory.tickers:
        ticker = factory.ticker( name )
        X = ticker.serie('time').data()
        for sname in ticker.series:
            if sname in ['price1','MA']:
                pylab.plot(X, ticker.serie(sname).data(), 'b-', label=("%s (%s)" % (name, sname)))

    pylab.legend()
    pylab.show()

