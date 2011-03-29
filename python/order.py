# -*- coding: utf-8 -*-

CLIENT_ACCOUNT="L01-00000F00"
CLIENT_CODE=52709

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
        order.server_id = int(table.getDouble(row,self.headers.index("Номер")))
        self.orders[ order.server_id ] = order
        print( order )

