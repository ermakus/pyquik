import logging
from trading.order import *

TRADE_IDLE=0
TRADE_LONG=1
TRADE_SHORT=-1

log = logging.getLogger("broker")

class Broker:

    def __init__(self):
        self.position = TRADE_IDLE
        self.handlers = { TRADE_IDLE: self.trade_idle, TRADE_LONG: self.trade_long, TRADE_SHORT:self.trade_short }
        self.long_order = None
        self.short_order = None

    def trade_idle( self, ticker ):
        pass

    def trade_cancel( self, ticker ):
        log.info("Exiting %s" % self )
        if self.short_order and self.short_order.status in [NEW,ACTIVE]:
            self.short_order.kill()
            self.short_order = None
        if self.long_order and self.long_order.status in [NEW,ACTIVE]:
            self.long_order.kill()
            self.long_order = None

    def trade_long( self, ticker ):
        log.info("Entering long: %s" % self)
        if self.short_order:
            self.long_order = ticker.buy( ticker.price, self.short_order.quantity + 1 )
            self.short_order = None
        else:
            self.long_order = ticker.buy( ticker.price )
        self.long_order.submit()
        return self.long_order

    def trade_short( self, ticker ):
        log.info("Entering short: %s" % self )
        if self.long_order:
            self.short_order = ticker.sell( ticker.price, self.long_order.quantity + 1 )
            self.long_order = None
        else:
            self.short_order = ticker.sell( ticker.price )
        self.short_order.submit()
        return self.short_order

    def trade( self, position, ticker ):
        """Trade position
        position:
            TRADE_LONG  - Open long position
            TRADE_SHORT - Open short position
            TRADE_IDLE  - Keep current positions
        ticker:
            Ticker instance to trade
        """
        if self.position == position:
            return

        self.position = position

        self.trade_cancel( ticker )
        return self.handlers[ position ]( ticker )

    def __repr__(self):
        return "Short: %s Long: %s" % ( self.short_order, self.long_order )
