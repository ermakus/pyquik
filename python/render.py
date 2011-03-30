#!/usr/bin/python
import numpy, pylab, sys
from ticker import TickerFactory

if __name__ == "__main__":

    if len( sys.argv ) != 2:
        print("Usage: %s <series_file.txt>" % sys.argv[0])
        sys.exit(1)

    factory = TickerFactory()
    factory.load( sys.argv[1] )

    for name in factory.tickers:
        ticker = factory.ticker( name )
        X = ticker.series('time').data()
        for serie in ticker.series:
            if serie.name != 'time':
                pylab.plot(X, ticker.data(), 'b-', label=("%s (%s)" % (name, serie.name))

    pylab.legend()
    pylab.show()

