# -*- coding: utf-8 -*-
import re, traceback, sys
from order import Order, OrderFactory
from ticker import Ticker, TickerFactory

if sys.platform == "win32":
    from trading import Market, MarketListener
else:
    from trading_stub import Market, MarketListener

TABLE_TOOLS="tools"
TABLE_ORDERS="orders"
TABLE_STOP_ORDERS="stop_orders"

class Quik(MarketListener):

    handlers = {}

    RE_TOPIC = re.compile("\\[(.*)\\](.*)");
    RE_ITEM  = re.compile("R(\\d*)C(\\d*):R(\\d*)C(\\d*)");

    def __init__(self, quikPath ):
        MarketListener.__init__(self)
        self.tickers = self.handlers[ TABLE_TOOLS ] = TickerFactory( self )
        self.orders = self.handlers[ TABLE_STOP_ORDERS ] = OrderFactory( self )
        self.market = Market()
        self.market.setDebug( True )
        self.market.addListener( self )
        self.quikPath = quikPath
        self.ready = False

    def __del__(self):
        self.market.disconnect()
        self.market.removeListener( self )
        print("Diconnected")

    def onTableData(self, topic, item, table): 
       try:
            tre = Quik.RE_TOPIC.match( topic )
            if not tre:
                raise Exception( "Invalid topic format: " + topic )

            ire = Quik.RE_ITEM.match( item )
            if not ire:
                raise Exception( "Invalid item format: " + item )

            title = tre.group(1);
            page  = tre.group(2);
            row   = int( ire.group(1) ) - 1;
            col   = int( ire.group(2) ) - 1;
            rows  = int( ire.group(3) ) - row;
            cols  = int( ire.group(4) ) - col;

            if table.cols() != cols or table.rows() != rows:
                raise Exception( "Table data don't match item format")

            if title in self.handlers:
                handler = self.handlers[ title ]
                # Init table header
                if row == 0:
                    top = 1
                    handler.headers = [ table.getString(0, c) for c in range( cols ) ]
                else:
                    top = 0
                    if not handler.headers:
                        raise Exception("Headers for table '%s' not found" % title )

                # Call handler for each table row
                for r in range(top,rows):
                    handler.update( table, r )

                # Fire onDataReady if all tables is loaded
                if row == 0:
                    wait = len( self.handlers )
                    for h in self.handlers:
                        if self.handlers[ h ].headers: 
                            wait -= 1
                    if wait == 0:
                        if not self.ready: self.onDataReady()
                        self.ready = True

       except:
            traceback.print_exc(file=sys.stdout)

    def onConnected(self):
        print("Connected to server")

    def onDisconnected(self):
        print("Disconnected from server")

    def onTransactionResult(self,result, errorCode, replyCode, transId, orderNum, replyMessage):
        try:
            Order.ORDERS[ transId ].executed( errorCode, replyCode, int(orderNum) )
        except:
            traceback.print_exc(file=sys.stdout)

    def onDataReady(self):
        print("*** DATA READY ***")
        if self.market.connect( self.quikPath ):
            raise Exception( self.market.errorMessage() )

        #sber = self.handlers[ TABLE_TOOLS ].ticker("SBER03")
        #order = sber.order('NEW_STOP_ORDER')
        #order.execute()

    def run(self):
        try:
            import win32gui
            def callback (hwnd, hwnds):
                if win32gui.IsWindowVisible (hwnd) and win32gui.IsWindowEnabled (hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "Информационно-торговая система QUIK" in title: hwnds.append (hwnd)
                return True
            hwnds = []
            win32gui.EnumWindows (callback, hwnds)
            if not hwnds: 
                raise Exception("Quik window not found")
            for hwnd in hwnds:
                win32gui.PostMessage( hwnd, 0x111, 0x0015C, 0x00 ) # WM_COMMAND 'Stop DDE export'
                win32gui.PostMessage( hwnd, 0x111, 0x1013F, 0x00 ) # WM_COMMAND 'Start DDE export'
        except Exception as ex:
            print("Can't autostart DDE export (%s). Swich to Quik and press Ctrl+Shift+L to start" % ex)

        self.market.run()

if __name__ == "__main__":

    quik = Quik("c:\\quik")

    quik.run()

