import re, traceback, sys

cdef extern from "quikdde.h":
    cdef cppclass Table:
        int cols()
        int rows()
        char*  getString(int r, int c)
        double getDouble(int r, int c)

    enum: ET_CONNECT
    enum: ET_DISCONNECT
    enum: ET_DATA
    enum: ET_TRANS

    cdef cppclass MarketEvent:
        int type
        char* topic
        char* item
        Table* table
        
    cdef cppclass Market:
        Market(void(*callback)(MarketEvent*))

        long connect(char* dir)
        void disconnect()

        long sendAsync(char* cmd)

        long ddeConnect(char* ddeName)
        void ddeDisconnect()
        void run()

        char* errorMessage()

quik = None

class DataHandler:

    def __init__(self, name, fields, callback):
        self.name = name
        self.fields = fields
        self.callback = callback

cdef class Quik:

    cdef Market* market
    cdef bytes path
    cdef bytes ddename
    cdef int   ready
    cdef dict  handl

    def __init__(self,path, ddename):
        global quik
        if quik: 
            raise Exception("Only one instance of Quik is permitted")
        quik = self
        self.market = new Market( quik_onEvent )
        self.path = path.encode("utf-8")
        self.ddename = ddename.encode("utf-8")
        self.ready = 0
        self.handl = dict()

        if self.market.ddeConnect(self.ddename):
            raise Exception( self.error() )

        if self.market.connect(self.path):
            raise Exception( self.error() )

    def __del__(self):
        self.market.disconnect()
        self.market.ddeDisconnect()
        del self.market

    def register(self,table,fields,callback):
        self.handl[ table ] = DataHandler(table,fields,callback)

    def handlers(self):
        return self.handl

    def is_ready(self):
        return self.ready

    def error(self):
        return self.market.errorMessage()

    def run(self):
        self.market.run()

    def onDataReady(self):
        if self.ready:
            print( "Import restarted" )
        else:
            self.ready = 1
            print( "Data ready" )

    def onConnect( self ):
        print( "Connected" )

    def onDisconnect( self ):
        print( "Disconnected" )

    def onTrans( self ):
        print( "Transaction" )

RE_TOPIC = re.compile("\\[(.*)\\](.*)");
RE_ITEM  = re.compile("R(\\d*)C(\\d*):R(\\d*)C(\\d*)");

cdef void quik_onData(char* topic, char* item, Table* table):
    global quik
    cdef str title
    cdef str page
    cdef int row
    cdef int col
    cdef int rows
    cdef int cols
    cdef int top
    cdef int c
    cdef int r
    cdef dict data

    try:
        tre = RE_TOPIC.match( topic.decode("utf-8") )
        if not tre:
            raise Exception( "Invalid topic format: %s" % topic )

        ire = RE_ITEM.match( item.decode("utf-8") )
        if not ire:
            raise Exception( "Invalid item format: %s" % item )

        title = tre.group(1);
        page  = tre.group(2);
        row   = int( ire.group(1) ) - 1;
        col   = int( ire.group(2) ) - 1;
        rows  = int( ire.group(3) ) - row;
        cols  = int( ire.group(4) ) - col;

        if table.cols() != cols or table.rows() != rows:
            raise Exception( "Table data don't match item format")

        if title in quik.handlers():
            handler = quik.handlers()[ title ]
            # Init table header
            if row == 0:
                top = 1
                handler.headers = [ table.getString(0, c).decode("utf-8") for c in range( cols ) ]
                handler.indexes = [ handler.headers.index( handler.fields[f] ) for f in handler.fields ]
            else:
                top = 0
                if not handler.headers:
                    raise Exception("Headers for table '%s' not found" % title )

            # Call handler for each table row
            for r in range(top,rows):
                data = dict()
                c = 0
                for f in handler.fields:
                    index = handler.indexes[c]
                    val = table.getString(r, index).decode("utf-8")
                    if val == "DOUBLE":
                        val = float(table.getDouble(r, index))
                    data[ f ] = val
                    c += 1
                handler.callback( data )

            # Fire onDataReady if all tables is loaded
            if row == 0:
                wait = len( quik.handlers() )
                for h in quik.handlers():
                    if quik.handlers()[ h ].headers:
                        wait -= 1
                if wait == 0:
                    quik.onDataReady()

    except:
        traceback.print_exc(file=sys.stdout)


cdef void quik_onEvent( MarketEvent* event ):
    global quik
    if not quik: return
    if event.type == ET_CONNECT: quik.onConnect()
    if event.type == ET_DISCONNECT: quik.onDisconnect()
    if event.type == ET_DATA: quik_onData( event.topic, event.item, event.table )
    if event.type == ET_TRANS: quik.onTrans()

