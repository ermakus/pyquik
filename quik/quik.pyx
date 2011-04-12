# -*- coding: utf-8 -*-
import re, traceback, sys, logging
from time import sleep
from util import Hook, ReadyHook, cmd2str

log = logging.getLogger("quik")

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
        long result
        long errorCode
        long reply
        unsigned long tid
        double order
        
    cdef cppclass Market:
        Market(void(*callback)(MarketEvent*))

        long connect(char* dir)
        void disconnect()

        long sendAsync(char* cmd)

        long ddeConnect(char* ddeName)
        void ddeDisconnect()
        void run()
        void stop()

        char* errorMessage()

quik = None

class DataHandler:

    def __init__(self, name, fields, callback):
        self.name = name
        self.fields = fields
        self.headers = None
        self.indexes = None
        self.callback = callback

cdef class Quik:

    cdef Market* market
    cdef bytes path
    cdef bytes ddename
    cdef bytes last_cmd
    cdef bytes last_error

    cdef public dict handlers
    cdef public dict callbacks

    cdef public object onready
    cdef public object ondisconnect

    def __init__(self,path, ddename):
        """Connect to running quik instance
        path - Path to quik install
        ddename - DDE server name
        """
        global quik
        if quik: 
            raise Exception("Only one instance of Quik is permitted")
        quik = self
        self.market = new Market( quik_onevent )
        self.path = path.encode("utf-8")
        self.ddename = ddename.encode("utf-8")
        self.handlers = dict()
        self.callbacks = dict()

        self.onready = ReadyHook()
        self.ondisconnect = Hook()

        if self.market.ddeConnect(self.ddename):
            raise Exception( self.error() )

        if self.market.connect(self.path):
            raise Exception( self.error() )
        self.onready.start()

    def __del__(self):
        """Disconnect and free memory"""
        self.market.disconnect()
        self.market.ddeDisconnect()
        del self.market

    def subscribe(self,table,fields,callback):
        """Subscribe to DDE data
        table - Table name
        fields - dict { "key":"column title" }
        callback - function( row_as_dict )
        """
        self.onready.start()
        self.handlers[ table ] = DataHandler(table,fields,callback)

    def error(self):
        """Returns last error message"""
        self.last_error = self.market.errorMessage();
        return self.last_error.decode("utf-8")

    def run(self):
        """Start quik export and entering message loop
        win32gui package is required for DDE export autostart
        """
        try:
            import win32gui
            def callback (hwnd, hwnds):
                if win32gui.IsWindowVisible (hwnd) and win32gui.IsWindowEnabled (hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "QUIK (" in title: hwnds.append (hwnd)
                return True
            hwnds = []
            win32gui.EnumWindows (callback, hwnds)
            if not hwnds: 
                raise Exception("Quik window not found")
            for hwnd in hwnds:
                log.debug("Starting DDE export")
                win32gui.PostMessage( hwnd, 0x111, 0x0015C, 0x00 ) # WM_COMMAND 'Stop DDE export'
                sleep(0.5)
                win32gui.PostMessage( hwnd, 0x111, 0x1013F, 0x00 ) # WM_COMMAND 'Start DDE export'
        except Exception as ex:
            log.warn("Can't autostart DDE export (%s). Swich to Quik and press Ctrl+Shift+L to start" % ex)

        self.market.run()

    def stop(self):
        """Exit message loop"""
        self.market.stop()

    def execute(self,cmd,callback=None):
        """Exceute transaction (async)
        cmd - dict({"key":"value",..})
        callback - function(result_as_dict)
        """
        trans_id = int(cmd['trans_id'])
        self.last_cmd = cmd2str(cmd).encode("utf-8")
        self.callbacks[trans_id] =  callback
        log.info("Execute: %s" % self.last_cmd )
        self.market.sendAsync( self.last_cmd )


RE_TOPIC = re.compile("\\[(.*)\\](.*)");
RE_ITEM  = re.compile("R(\\d*)C(\\d*):R(\\d*)C(\\d*)");

cdef void quik_ondata(char* topic, char* item, Table* table):
    global quik
    cdef unicode title
    cdef unicode page
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

        if title in quik.handlers:
            handler = quik.handlers[ title ]
            # Init table header
            if row == 0:
                quik.onready.ready()
                top = 1
                try:
                    handler.headers = [ table.getString(0, c).decode("utf-8") for c in range( cols ) ]
                    handler.indexes = [ handler.headers.index( handler.fields[f].decode("utf-8") ) for f in handler.fields ]
                except ValueError:
                    raise Exception("Table '%s' header do not match column list" % title )
            else:
                top = 0
                if not handler.indexes:
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
    except:
        traceback.print_exc(file=sys.stdout)
        quik.stop()

cdef void quik_onevent( MarketEvent* event ):
    global quik
    if not quik: return
    try:
        msg = event.topic.decode("utf-8")
        if event.type == ET_CONNECT: 
            log.debug("Connected: %s" % msg )
            quik.onready.ready()
            quik.onready()
            return
        if event.type == ET_DISCONNECT: 
            log.debug("Disconnected: %s" % msg )
            quik.ondisconnect()
            return
        if event.type == ET_DATA: 
            quik_ondata( event.topic, event.item, event.table )
            quik.onready()
            return
        if event.type == ET_TRANS:
            log.debug("Transaction result: %s" % msg )
            tid = int(event.tid)
            if event.tid in quik.callbacks:
                callback = quik.callbacks[ tid ]
                del quik.callbacks[ tid ]
                if callback:
                    res = dict()
                    res["trans_id"] = tid 
                    res["order_key"] = int( event.order )
                    res["result"] = event.result
                    res["error"] = event.errorCode
                    res["status"] = event.reply
                    res["message"] = msg
                    callback( res )
            return
    except:
        traceback.print_exc(file=sys.stdout)
        quik.stop()
