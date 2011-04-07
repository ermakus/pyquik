from trading.market import Market
from util import ReadyHook

class Emulator:

    def __init__(self, market):
        self.onready = ReadyHook()
        self.market = market;

    def new_order(self,cmd):
        pass

    def kill_order(self,cmd):
        pass

    def execute(self,cmd, callback):
        print("Excec: %s" % cmd)
        res = dict()
        if cmd["action"] == "NEW_ORDER":
            self.new_order(cmd)
        if cmd["action"] == "KILL_ORDER":
            self.kill_order(cmd)

        res["order_key"] = cmd["trans_id"]
        if callback: callback( res )

class BacktestMarket(Market):

    def __init__(self):
        Market.__init__(self)
        self.conn = Emulator( self )

    def load(self, path):
        self.conn.onready()
        Market.load(self,path)
