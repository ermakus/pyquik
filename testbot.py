from quik.market import QuikMarket
from trading import Market, Order, Indicator
import threading
import logging

logging.basicConfig(level=logging.DEBUG)

class Strategy:

    def __init__(self,ticker):
        self.ticker = ticker
        self.ticker.ontick( self.tick )
        self.ticker.market.conn.onready += self.start

    def tick( self, tick ):
        print("Tick: %s" % tick )

    def order_status( self, order, err, msg ):
        print("Order: %s: %s" % ( order, msg ))
        order.kill()

    def start( self ):
        print("Trading started")
        order = self.ticker.buy( 106.0, 1 )
        order.onstatus = self.order_status
        order.submit()

market = QuikMarket( "c:\\quik-bcs","QuikDDE" )
market.conn.onready += lambda: print("OnReady")

strategy  = Strategy( market.SBER03 )
market.run()
