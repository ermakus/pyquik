from trading import Market, MarketListener
import re, traceback, sys

CLIENT_ACCOUNT="L01-00000F00"
CLIENT_CODE=52709


TABLE_TOOLS="tools"
TABLE_ORDERS="orders"
TABLE_STOP_ORDERS="stop_orders"

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

    FIELDS =['trans_id','action','seccode','classcode','account','client_code','operation','quantity','stopprice','price','expiry_date']

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
        if self.ticker.factory.quik.market.sendAsync( str( self ) ):
            raise Exception( self.ticker.factory.market.errorMessage() )

    def executed(self, result, status, serverId):
        self.server_id = serverId
        self.status = status
        print( "Order %s/%s result %s/%s" % ( self.trans_id, self.server_id, result, status ) )

    def __str__(self):
        return ";".join( [ "%s=%s" % ( x.upper(), getattr( self, x) ) for x in Order.FIELDS ] )

class OrderFactory:

    def __init__(self, quik):
        self.quik  = quik
        self.headers = False
        self.orders = {}

    def update( self, table, row ):
        order = Order(self)
        order.server_id = int(table.getString(row,self.headers.index("Номер")))
        self.orders[ order.server_id ] = order
        print( order )

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


class Quik(MarketListener):

    handlers = {}

    RE_TOPIC = re.compile("\\[(.*)\\](.*)");
    RE_ITEM  = re.compile("R(\\d*)C(\\d*):R(\\d*)C(\\d*)");

    def __init__(self, quikPath ):
        MarketListener.__init__(self)
        self.handlers[ TABLE_TOOLS ]      = TickerFactory( self )
        self.handlers[ TABLE_STOP_ORDERS ] = OrderFactory( self )
        self.market = Market()
        self.market.setDebug( True )
        self.market.addListener( self )
        self.quikPath = quikPath

    def __del__(self):
        self.market.disconnect()
        self.market.removeListener( self )
        print("Diconnected")

    def onTableData(self, topic, item, table): 
       try:
            tre = Quik.RE_TOPIC.match( topic )
            if not tre:
                raise Exception( "Invalid topic format: " + topic )

            ire = Quik.RE_ITEM.match( item )
            if not ire:
                raise Exception( "Invalid item format: " + item )

            title = tre.group(1);
            page  = tre.group(2);
            row   = int( ire.group(1) ) - 1;
            col   = int( ire.group(2) ) - 1;
            rows  = int( ire.group(3) ) - row;
            cols  = int( ire.group(4) ) - col;

            if table.cols() != cols or table.rows() != rows:
                raise Exception( "Table data don't match item format")

            if title in self.handlers:
                handler = self.handlers[ title ]
                # Init table header
                if row == 0:
                    top = 1
                    handler.headers = [ table.getString(0, c) for c in range( cols ) ]
                else:
                    top = 0
                    if not handler.headers:
                        raise Exception("Headers for table '%s' not found" % title )

                # Call handler for each table row
                for r in range(top,rows):
                    handler.update( table, r )

                # Fire onDataReady if all tables is loaded
                if row == 0:
                    wait = len( self.handlers )
                    for h in self.handlers:
                        if self.handlers[ h ].headers: 
                            wait -= 1
                    if wait == 0: 
                        self.onDataReady()

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

    def onDataReady(self):
        print("Data is ready - connecting")
        if self.market.connect( self.quikPath ):
            raise Exception( self.market.errorMessage() )

        sber = self.handlers[ TABLE_TOOLS ].ticker("SBER03")
        order = tool.order('NEW_STOP_ORDER') 
        print( sber )
        print( order )

    def run(self):
        try:
            import win32gui
            hwnd = win32gui.FindWindow( "InfoClass", "[bcst2709  UID: 54622] Информационно-торговая система QUIK (версия 5.17.0.165)" )
            if hwnd:
                win32gui.PostMessage( hwnd, 0x111, 0x0015C, 0x00 ) # WM_COMMAND 'Stop DDE export'
                win32gui.PostMessage( hwnd, 0x111, 0x1013F, 0x00 ) # WM_COMMAND 'Start DDE export'
            else:
                raise Exception("Quik window not found")
        except Exception as ex:
            print("Can't autostart DDE export (%s). Swich to Quik and press Ctrl+Shift+L to start" % ex)

        self.market.run()

if __name__ == "__main__":

    quik = Quik("c:\\quik")

    quik.run()

