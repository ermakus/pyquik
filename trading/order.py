# -*- coding: utf-8 -*-
import logging
log = logging.getLogger("order")

CLIENT_ACCOUNT="L01-00000F00"
CLIENT_CODE=52709

MARKET_PRICE=0
BUY="B"
SELL="S"

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

    LAST_ID = 0

    def __init__(self,ticker, operation=BUY, price=MARKET_PRICE, quantity=1):
        Order.LAST_ID +=1
        self.ticker = ticker
        self.trans_id = Order.LAST_ID
        self.account = CLIENT_ACCOUNT
        self.client_code = CLIENT_CODE
        self.operation = operation
        self.price = price
        self.quantity = quantity
        self.seccode = ticker.seccode
        self.classcode = ticker.classcode
        self.order_key = None
        self.onstatus = None

    def cmd_submit(self):
        keys = ['action','trans_id','seccode','classcode','account','client_code','operation','quantity','price']
        vals = [  getattr( self, x, None ) for x in keys ]
        vals[0] = 'NEW_ORDER'
        return dict( zip( keys, vals ) )

    def cmd_kill(self):
        Order.LAST_ID +=1
        if not self.order_key: raise Exception("Can't kill unregistered order")
        keys = ['action','trans_id','seccode','classcode','order_key']
        vals = [  getattr( self, x, None ) for x in keys ]
        vals[0] = 'KILL_ORDER'
        vals[1] = Order.LAST_ID
        return dict( zip( keys, vals ) )
 
    def submit(self):
        self.ticker.market.execute( self.cmd_submit(), self.status )

    def kill(self):
        self.ticker.market.execute( self.cmd_kill(), self.status )

    def status(self,res,err,rep,tid,order,msg):
#        print("Order status: res=%s err=%s rep=%s tid=%s ord=%s msg=%s" % ( res, err, rep, tid, order, msg ) )
        self.order_key = int(order)
        if self.onstatus: self.onstatus( self, err, msg )

    def __repr__(self):
        return "ORDER_KEY=%s;%s" % ( self.order_key, self.cmd_submit())

class StopOrder(Order):

    def __init__(self,ticker, operation=BUY, price=MARKET_PRICE, quantity=1):
        Order.__init__(self, ticker, operation, price, quantity)
        self.stopprice=100.0
        self.expiry_date="20110401"

    def fields(self):
        return Order.fields() + ['stopprice','expiry_date']

class OrderFactory:

    def __init__(self, quik):
        self.quik  = quik
        self.headers = False
        self.orders = {}

    OP_TYPE = {"Купля":BUY,"Продажа":SELL}

    def update( self, table, row ):
        ticker    = self.quik.TICKERS(table.getString(row,self.headers.index("Код бумаги")))
        op        = OrderFactory.OP_TYPE[table.getString(row,self.headers.index("Операция"))]
        price     = float(table.getDouble(row,self.headers.index("Цена")))
        quantity  = int(table.getDouble(row,self.headers.index("Кол-во")))
        order     = Order(ticker,op,price,quantity)
        order.order_key = int(table.getDouble(row,self.headers.index("Номер")))
        self.orders[ order.order_key ] = order
        if hasattr( self.quik, "onOrder" ):
            self.quik.onOrder( order )

