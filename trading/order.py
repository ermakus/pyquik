# -*- coding: utf-8 -*-
import logging
from util import Hook, ReadyHook

log = logging.getLogger("order")

CLIENT_ACCOUNT="L01-00000F00"
CLIENT_CODE=52709

MARKET_PRICE=0
BUY="B"
SELL="S"

# Order statuses
NEW="NEW"
EXECUTED="EXECUTED"
ACTIVE="ACTIVE"
KILLED="KILLED"
ERROR="ERROR"

class BaseOrder:

    LAST_ID = 0

    def __init__(self,ticker):
        Order.LAST_ID +=1
        self.ticker = ticker
        self.trans_id = Order.LAST_ID
        self.order_key = None
        self.account = CLIENT_ACCOUNT
        self.client_code = CLIENT_CODE
        self.seccode = ticker.seccode
        self.classcode = ticker.classcode
        self.status = NEW
        self.onstatus = Hook()
        self.onexecuted = ReadyHook()
        self.onregistered = ReadyHook()
        self.onkilled = ReadyHook()
        self.keys = ['action','trans_id','seccode','classcode','account','client_code']

    def __eq__(self, other):
        if not isinstance(other, Order): raise NotImplementedError
        return self.order_key==other.order_key

    def __repr__(self):
        return "%s: %s" % ( self.action, self.status)

    def submit(self):
       self.ticker.market.execute( self, self.submit_status )

    def submit_status(self,status):
        self.order_key = status["order_key"]
        if not self.order_key:
            raise Exception( status["message"] )
        self.status = ACTIVE
        self.onregistered()

    def delete(self):
        idx = self.ticker.orders.index( self )
        del self.ticker.orders[ idx ]

class Order(BaseOrder):

    def __init__(self, ticker, operation=BUY, price=MARKET_PRICE, quantity=1):
        BaseOrder.__init__(self,ticker)
        self.action = "NEW_ORDER"
        self.operation = operation
        self.price = price
        self.quantity = quantity
        self.keys += ['operation','quantity','price']

    def kill(self):
        o = KillOrder(self)
        o.submit()

    def __repr__(self):
        return "%s: %s (type: %s price: %.2f)" % ( self.action, self.status, self.operation, self.price)


class KillOrder(BaseOrder):

    def __init__(self, order):
        BaseOrder.__init__(self, order.ticker)
        assert order.action == "NEW_ORDER"
        assert not order.order_key is None
        self.action = "KILL_ORDER"
        self.order_key = order.order_key
        self.keys = ['action','trans_id','seccode','classcode','order_key']

class StopOrder(Order):

    def __init__(self, ticker):
        Order.__init__(self, ticker)
        self.stopprice=100.0
        self.expiry_date="20110401"
        self.action = "NEW_STOP_ORDER"
        self.keys += ['operation','quantity','price']

class KillStopOrder(KillOrder):

    def __init__(self, order):
        KillOrder._init__(self, order)
        assert order.action == "NEW_STOP_ORDER"
        self.action = "KILL_STOP_ORDER"
