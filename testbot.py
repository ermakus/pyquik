from quik import Quik
from trading import Market, Order, Indicator

# Called every price change
def handle_tick( ticker ):
    print( "TICK: %s" % ticker )
    if ticker.price <= 109.14 and len(ticker.orders) == 0:
        ticker.buy( 109.14, 1 )
    if ticker.price >= 109.18 and len(ticker.orders) == 1:
        ticker.sell( 109.18, 1 )

market = Market( Quik("c:\\quik-bcs","QuikDDE") )
market.SBER03.ontick( handle_tick )
market.run()
