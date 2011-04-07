import logging
from trading.order import *


TRADE_IDLE=0
TRADE_LONG=1
TRADE_SHORT=-1

log = logging.getLogger("broker")

class Broker:

    def __init__(self,ticker):
        self.ticker = ticker
        self.position = TRADE_SHORT
        self.handlers = { TRADE_IDLE: self.trade_idle, TRADE_LONG: self.trade_long, TRADE_SHORT:self.trade_short }
        self.long_order = None
        self.short_order = None

    def trade_idle( self, price ):
        pass

    def trade_exit( self ):
        log.info("Exiting %s" % self )
        if self.short_order and self.short_order.status in [NEW,ACTIVE]:
            self.short_order.kill()
        if self.long_order and self.long_order.status in [NEW,ACTIVE]:
            self.long_order.kill()
        self.long_order = None
        self.short_order = None

    def trade_long( self, price ):
        log.info("Entering long: %s" % self)
        self.long_order = self.ticker.buy( price )
        self.long_order.submit()

    def trade_short( self, price ):
        log.info("Entering short: %s" % self )
        self.short_order = self.ticker.sell( price )
        self.short_order.submit()

    def trade( self, position, price ):
        """Trade position
        position:
            TRADE_LONG  - Open long position
            TRADE_SHORT - Open short position
            TRADE_IDLE  - Keep current positions
        """
        if self.position == position:
            return

        self.trade_exit()
        self.position = position
        self.handlers[ position ](price)

    def __repr__(self):
        return "%s: short: %s long: %s" % ( self.ticker.seccode, self.short_order, self.long_order )
