from quik.market import QuikMarket
from trading import Market, Order, Indicator
import threading
import logging

log = logging.getLogger("strategy")

class Strategy:

    def __init__(self,ticker):
        self.ticker = ticker
        self.ticker.ontick += self.tick
        self.ticker.market.conn.onready += self.start

    def tick( self, tick ):
        log.debug("Tick: %s" % tick )

    def order_status( self, order, status ):
        log.info("Order: %s: %s" % ( order, status ))
        # Kill executed order immediately
        order.kill()

    def start( self ):
        log.info("Trading started")
        # Kill existing orders
        for o in self.ticker.orders:
            o.kill()
        # Create new buy order
        order = self.ticker.buy( 106.0, 1 )
        order.onstatus = self.order_status
        order.submit()

logging.basicConfig(level=logging.DEBUG)

market = QuikMarket( "c:\\quik-bcs","QuikDDE" )
strategy = Strategy( market.SBER03 )
market.run()
