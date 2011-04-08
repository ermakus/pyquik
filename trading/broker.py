import logging
from trading.order import *

TRADE_KEEP=None
TRADE_EXIT=0
TRADE_LONG=1
TRADE_SHORT=-1

log = logging.getLogger("broker")

class Broker:

    def __init__(self):
        self.position = TRADE_EXIT
        self.handlers = { TRADE_EXIT: self.trade_exit, TRADE_LONG: self.trade_long, TRADE_SHORT:self.trade_short }
        self.order = None

    def trade_cancel( self, ticker ):
        if self.order and self.order.status in [NEW,ACTIVE]:
            log.info("Kill %s", self.order )
            self.order.kill()
            self.order = None

    def trade_exit( self, ticker ):
        if self.order:
            if self.order.operation == BUY:
                self.order = ticker.sell( ticker.price )
                self.order.submit()
                log.debug("Exit %s", self.order )
                return self.order
            if self.order.operation == SELL:
                self.order = ticker.buy( ticker.price )
                self.order.submit()
                log.debug("Exit %s", self.order )
                return self.order
        return self.order

    def trade_long( self, ticker ):
        log.info("Enter long: %s" % self)
        if self.order:
            if self.order.operation == SELL:
                self.order = ticker.buy( ticker.price, self.order.quantity + 1 )
                self.order.submit()
            else:
                raise Exception("Invalid state - open long twice")
        else:
            self.order = ticker.buy( ticker.price )
            self.order.submit()
        return self.order

    def trade_short( self, ticker ):
        log.info("Enter short: %s" % self)
        if self.order:
            if self.order.operation == BUY:
                self.order = ticker.sell( ticker.price, self.order.quantity + 1 )
                self.order.submit()
            else:
                raise Exception("Invalid state - open short twice")
        else:
            self.order = ticker.sell( ticker.price )
            self.order.submit()
        return self.order

    def trade( self, position, ticker ):
        """Trade position
        position:
            TRADE_LONG  - Open long position
            TRADE_SHORT - Open short position
            TRADE_IDLE  - Keep current positions
        ticker:
            Ticker instance to trade
        """
        if position == TRADE_KEEP:
            return

        if self.position == position:
            return

        self.position = position
        self.trade_cancel( ticker )
        return self.handlers[ position ]( ticker )

    def __repr__(self):
        return "Order: %s" % ( self.order )
