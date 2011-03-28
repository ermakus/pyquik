from order import Order

class Ticker:

    FIELDS =['seccode','classcode','price','volume','balance']

    def __init__(self,factory,name):
        self.factory = factory
        self.seccode = name
        self.classcode = "EQBR"
        self.price = 0.0
        self.volume = 0.0
        self.balance = 0.0

    def order(self,action):
        o = Order(self,action)
        o.seccode = self.seccode
        o.classcode = self.classcode
        o.price = self.price
        return o

    def __str__(self):
        return ";".join( [ "%s=%s" % ( x.upper(), getattr( self, x) ) for x in Ticker.FIELDS ]  )

class TickerFactory:

    def __init__(self, quik):
        self.quik    = quik
        self.headers = False
        self.tickers = {}

    def update( self, table, r ):
        ticker = Ticker(self, table.getString(r,self.headers.index("Код бумаги")))
        ticker.classcode = table.getString(r,self.headers.index("Код класса"))
        ticker.price =  float(table.getDouble(r,self.headers.index("Цена послед.")))
        cumulativeAsk = int(table.getDouble(r,self.headers.index("Общ. спрос")))
        cumulativeBid = int(table.getDouble(r,self.headers.index("Общ. предл.")))
        ticker.volume = int(table.getDouble(r,self.headers.index("Оборот")))
        summ = cumulativeBid + cumulativeAsk
        if summ != 0:
            ticker.balance = 100.0 * (cumulativeBid - cumulativeAsk) / summ
            
        self.tickers[ ticker.seccode ] = ticker
        print("Ticker: %s" % ticker )

    def ticker(self, name):
        return self.tickers[ name ]

