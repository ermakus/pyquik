from quik import Quik
from trading import Market, Order, Indicator

def order_status( order, err, msg ):
    print( "ORDER STATUS: %s %s %s" % ( order, err, msg ) )
    order.kill()

# Called every price change
def handle_tick( ticker ):
    print( "TICK: %s" % ticker )
#    if len(ticker.orders) == 0:
#        order = ticker.buy( 106.0, 1 )
#        order.onstatus = order_status
#        order.submit()

def data_ready():
    global market
    print("=== Existing orders ===")
    for  ticker in market.tickers.values():
        print("Ticker: %s" % ticker )
        for o in ticker.orders:
            print("Order: %s" % o )

market = Market( Quik("c:\\quik-bcs","QuikDDE") )
market.conn.bind( "ready", data_ready )
market.conn.bind( "restart", data_ready )
market.SBER03.ontick( handle_tick )
market.run()
