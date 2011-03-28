from trading import Market, MarketListener
import re, traceback, sys
import win32api, win32gui

CLIENT_ACCOUNT="L01-00000F00"
CLIENT_CODE=52709


TABLE_TOOLS="tools"
TABLE_ORDERS="orders"

class Order:

    """
	NEW_ORDER - новая заявка,
	NEW_NEG_DEAL - новая заявка на внебиржевую сделку,
	NEW_REPO_NEG_DEAL – новая заявка на сделку РЕПО,
	NEW_EXT_REPO_NEG_DEAL - новая заявка на сделку модифицированного РЕПО (РЕПО-М),
	NEW_STOP_ORDER - новая стоп-заявка,
	KILL_ORDER - снять заявку,
	KILL_NEG_DEAL - снять заявку на внебиржевую сделку или заявку на сделку РЕПО,
	KILL_STOP_ORDER - снять стоп-заявку,
	KILL_ALL_ORDERS – снять все заявки из торговой системы,
	KILL_ALL_STOP_ORDERS – снять все стоп-заявки,
	KILL_ALL_NEG_DEALS – снять все заявки на внебиржевые сделки и заявки на сделки РЕПО,
	KILL_ALL_FUTURES_ORDERS - снять все заявки на рынке FORTS,
	KILL_RTS_T4_LONG_LIMIT - удалить лимит открытых позиций на спот-рынке RTS Standard, 
	KILL_RTS_T4_SHORT_LIMIT - удалить лимит открытых позиций клиента по спот-активу на рынке RTS Standard,
	MOVE_ORDERS - переставить заявки на рынке FORTS,
	NEW_QUOTE - новая безадресная заявка,
	KILL_QUOTE - снять безадресную заявку,
	NEW_REPORT - новая  заявка-отчет о подтверждении транзакций в режимах РПС и РЕПО,
	SET_FUT_LIMIT - новое ограничение по фьючерсному счету
    """

    LAST_ID = 1

    FIELDS = ['trans_id','action','seccode','classcode','account','client_code','operation','quantity','stopprice','price','expiry_date']

    ORDERS = {}

    def __init__(self,ticker,action="NEW_STOP_ORDER"):
        Order.LAST_ID +=1
        self.ticker = ticker
        self.trans_id = Order.LAST_ID
        self.action = action
        self.seccode=None
        self.classcode=None
        self.account = CLIENT_ACCOUNT
        self.client_code = CLIENT_CODE
        self.operation = "S"
        self.quantity = 1
        self.stopprice=100.0
        self.price=100.0
        self.expiry_date="20110401"
        Order.ORDERS[ self.trans_id ] = self

    def execute(self):
        if self.ticker.factory.market.sendAsync( str( self ) ):
            raise Exception( self.ticker.factory.market.errorMessage() )

    def executed(self, result, status, serverId):
        self.server_id = serverId
        self.status = status
        print( "Order %s/%s result %s/%s" % ( self.trans_id, self.server_id, result, status ) )

    def __str__(self):
        return ";".join( [ "%s=%s" % ( x.upper(), getattr( self, x) ) for x in Order.FIELDS ] )


class Ticker:

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
        return ";".join( [ "%s=%s" % ( x.upper(), getattr( self, x) ) for x in self.__dict__ ]  )

class QuikListener(MarketListener):

    handlers = {}

    RE_TOPIC = re.compile("\\[(.*)\\](.*)");
    RE_ITEM  = re.compile("R(\\d*)C(\\d*):R(\\d*)C(\\d*)");


    def __init__(self):
        MarketListener.__init__(self)

    def onTableData(self, topic, item, table): 
       try:
            tre = QuikListener.RE_TOPIC.match( topic )
            if not tre:
                raise Exception( "Invalid topic format: " + topic )

            ire = QuikListener.RE_ITEM.match( item )
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

       except:
            traceback.print_exc(file=sys.stdout)

    def onConnected(self):
        print("Connected to server")

    def onDisconnected(self):
        print("Disconnected from server")

    def onTransactionResult(self,result, errorCode, replyCode, transId, orderNum, replyMessage):
        try:
            Order.ORDERS[ transId ].executed( errorCode, replyCode, int(orderNum) )
        except:
            traceback.print_exc(file=sys.stdout)

class TickerFactory:

    def __init__(self,quikPath,onupdate=None):
        self.headers = False
        self.onupdate = onupdate
        self.tickers = {}
        self.market = Market()
        self.market.setDebug( True )
        self.listener = QuikListener()
        self.listener.handlers[ TABLE_TOOLS ] = self
        self.market.addListener( self.listener )
        if self.market.connect( quikPath ): 
            raise Exception( self.market.errorMessage() )

    def __del__(self):
        self.market.disconnect()
        self.market.removeListener( self.listener )
        print("Diconnected")

    def update( self, row, col, rows, cols, table ):
        top = 0

        if row == 0:
            self.headers = [ table.getString(0, c) for c in range( cols ) ]
            print( self.headers )
            top = 1

        if not self.headers:
            raise Exception("Headers not set")

        for r in range(top, rows):
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
            if self.onupdate: self.onupdate( ticker )

        def ticker(self, name):
            return self.tickers[ name ]


    def run(self):
        self.market.run()

def ticker( tool ):
    print( tool )
#    order = tool.order('NEW_STOP_ORDER') 
#    print( order )
#    order.execute()

if __name__ == "__main__":
#    hwnd = win32gui.FindWindow( "InfoClass", "Информационная система QUIK (версия 5.17.0.165)" )
#    win32gui.PostMessage( hwnd, 0x111, 0x64, 0x200EA )
#    hwnd = win32gui.FindWindow( 0, "Идентификация пользователя" )
#    print( hwnd )

    market = TickerFactory("c:\\quik",ticker)
    market.run()

