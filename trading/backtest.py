import logging
from trading.market import Market
from trading.order import *
from trading.broker import TRADE_EXIT
from util import ReadyHook

log = logging.getLogger("backtest")

class BacktestMarket(Market):

    def __init__(self):
        Market.__init__(self)
        self.balance = 0
        self.trades = 0
        self.profit_trades = 0
        self.buy_price = 0
        self.bag = []
        self.ticks = 0

    def execute(self, order, callback):
        if order.action == "NEW_ORDER":
            order.status = ACTIVE
            order.onregistered()
        if order.action == "KILL_ORDER":
            ko = order.ticker.order( order.order_key )
            ko.status = KILLED
            ko.onkilled()
            ko.delete()
            order.status = EXECUTED
            order.onexecuted()

        res = dict()
        res["order_key"] = order.trans_id
        if callback: callback( res )

    def load(self,filename):
        Market.load( self, filename )
        self.strategies = {}
        for paper in self.bag:
            log.info("Selling paper %s on exit", paper)
            paper.market.broker.trade(TRADE_EXIT,paper)
            self.tick(paper)
        log.info("Backtesting done. Ticks: %d, final balance: %.2f, trades: %d, profitable trades: %d (%.2f%%)", 
           self.ticks, self.balance, self.trades, self.profit_trades, 100.0 * (float(self.profit_trades) / self.trades)  )

    def tick(self,ticker):
        Market.tick(self,ticker)
        self.ticks += 1
        for order in ticker.orders:
            if order.action == "NEW_ORDER" and order.status == ACTIVE:
                if order.operation == BUY and order.price >= ticker.price:
                    order.status = EXECUTED
                    self.balance -= ticker.price
                    self.buy_price = ticker.price
                    self.bag.append(ticker)
                    self.trades += 1
                    log.info("Buy %s: balance: %.2f", ticker, self.balance )
                    order.onexecuted()
                    order.delete()
                if order.operation == SELL and order.price <= ticker.price:
                    order.status = EXECUTED
                    self.balance += ticker.price
                    profit = ticker.price - self.buy_price
                    if profit > 0:
                        self.profit_trades +=1
                    self.bag.remove(ticker)
                    log.info("Sell %s: balance: %.2f profit: %.2f", ticker, self.balance, profit )
                    order.onexecuted()
                    order.delete()
