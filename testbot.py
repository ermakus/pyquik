from quik import Quik
from trading import Market, Order, Indicator
import threading

class TestBot:

    def __init__(self,ticker):
        self.ticker = ticker
        self.ticker.ontick( self.tick )

    def tick( self, tick ):
        order = market.SBER03.buy( 106.0, 1 )
        order.onstatus = self.order_status
        order.submit()

    def order_status( self, order, err, msg ):
        if len(self.ticker.orders) > 3:
            for order in market.SBER03.orders:
                if order.order_key: order.kill()


market = Market( Quik("c:\\quik-bcs","QuikDDE") )
robot  = TestBot( market.SBER03 )
market.conn.bind( "ready", lambda : print("Trading started") )
market.run()
