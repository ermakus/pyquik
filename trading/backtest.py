from trading.market import Market
from util import Hook

class Emulator:

    def __init__(self):
        self.onready = Hook()

    def execute(self,cmd, callback):
        print("Excec: %s" % cmd)
        res = dict()
        res["order_key"] = cmd["trans_id"]
        if callback: callback( res )

class BacktestMarket(Market):
    def __init__(self):
        Market.__init__(self)
        self.conn = Emulator()

