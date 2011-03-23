from trading import Market, MarketListener
import re

RE_TOPIC = re.compile("\\[(.*)\\](.*)");
RE_ITEM  = re.compile("R(\\d*)C(\\d*):R(\\d*)C(\\d*)");

TOOLS = {}

class Ticker:

    def __init__(self,name):
        self.name = name
        self.price = 0.0
        self.volume = 0.0
        self.balance = 0.0

    def __str__(self):
        return "Ticker=%s,price=%s,volume=%s,balance=%s" % ( self.name, self.price, self.volume, self.balance )

class TickerFactory:

    tickers = {}

    def __init__(self,onupdate=None):
        self.onupdate = onupdate

    def update( self, row, col, rows, cols, table ):
        for r in range(1, rows):
            ticker = Ticker( table.getString(r,1) )
            ticker.price = table.getDouble(r,5)
            cumulativeAsk = int(table.getDouble(r,6))
            cumulativeBid = int(table.getDouble(r,7))
            summ = cumulativeBid + cumulativeAsk
            ticker.volume = table.getDouble(r,8)
            if summ != 0:
                ticker.balance = 100.0 * (cumulativeBid - cumulativeAsk) / summ
            
            self.tickers[ ticker.name ] = ticker
            if self.onupdate: self.onupdate( ticker )


class QuikListener(MarketListener):

    handlers = {}

    def __init__(self):
        MarketListener.__init__(self)

    def onTableData(self, topic, item, table): 
        try:
            tre = RE_TOPIC.match( topic )
            if not tre:
                raise Exception( "Invalid topic format: " + topic )

            ire = RE_ITEM.match( item )
            if not ire:
                raise Exception( "Invalid item format: " + item )

            title = tre.group(1);
            page  = tre.group(2);
            row   = int( ire.group(1) ) - 1;
            col   = int( ire.group(2) ) - 1;
            rows  = int( ire.group(3) ) - row;
            cols  = int( ire.group(4) ) - col;

            if table.cols() != cols or table.rows() != rows:
                raise Exception( "Table data do not match item format")

            if title in self.handlers:
                self.handlers[ title ].update( row, col, rows, cols, table )

        except Exception as ex:
            print( "Market data error: %s" % ex )

    def onConnected(self):
        print("Connected to server")

    def onDisconnected(self):
        print("Disconnected from server")

    def onTransactionResult(result, errorCode, replyCode, transId, orderNum, replyMessage):
        print("Tansaction result: %s %s %s %s %s %s" % (result, errorCode, replyCode, transId, orderNum, replyMessage))

class Quik:

    def __init__(self, onticker=None):
        self.market = Market()
        self.listener = QuikListener()
        self.tickers  = TickerFactory(onticker)
        self.listener.handlers["tools"] = self.tickers
        self.market.addListener( self.listener )

    def __del__(self):
        self.market.removeListener( self.listener )
        print("Diconnected")

    def run(self, quickDir):
        print("Connecting to Quik")
        if self.market.connect( quickDir ):
            raise Exception( self.market.errorMessage() )

        if self.market.sendAsync( "hatza!" ):
            raise Exception( self.market.errorMessage() )

        self.market.run()
        self.market.disconnect()

def ticker(tick):
    print( tick )

q = Quik( ticker )
q.run("C:\\work\\quik")
