# -*- coding: utf-8 -*-
import datetime
from trading import market
from trading.order import Order, BUY, SELL
from quik.quik import Quik
    
ORDER_OP = {"Купля":BUY,"Продажа":SELL}

class QuikMarket(market.Market):

    def __init__(self, path, dde):
        market.Market.__init__(self)

        self.conn = Quik( path, dde )

        self.conn.subscribe( "TICKERS", {
            "seccode":"Код бумаги",
            "classcode":"Код класса",
            "price":"Цена послед."
        }, self.ontick )

        self.conn.subscribe( "ORDERS", {
            "order_key":"Номер",
            "seccode":"Код бумаги",
            "operation":"Операция",
            "price":"Цена",
            "quantity":"Кол-во",
            "left":"Остаток",
            "state":"Состояние"
        }, self.onorder )
 
    def ontick(self,data):
        """ Quik tickers data handler """
        ticker = self.ticker( data["seccode"] )
        ticker.classcode = data["classcode"]
        ticker.time = datetime.datetime.now()
        ticker.price = data["price"]
        ticker.volume = 0
        ticker.tick()

    def onorder(self,data):
        state = data["state"]
        if state == "Снята": return
        ticker = self.__getattr__( data["seccode"] )
        order = ticker.order( int( data["order_key"] ) )
        order.operation = ORDER_OP[ data["operation"] ]
        order.price = float( data["price"] )
        order.quantity = int( data["quantity"] )
        order.quantity_left = int( data["left"] )
