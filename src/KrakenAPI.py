import krakenex
import datetime
import logging
from time import time, sleep

# simple Kraken interface
# NOTE: remember to put yout Kraken keys in Config/kraken.key
class KrakenAPI:
    def __init__(self):
        self.kraken = krakenex.API()
        self.kraken.load_key('config/kraken.key')

    def openLimitBuyOrder(self, pair, amount, price):
        if self.getBalance(pair[-4:]) < amount:
            logging.warning("Not enough " + pair[-3:] + ". Order not placed.")
            return 0

        btcAmount = amount / price
        result = self.__sendQuery('AddOrder', { 'pair'     : pair
                                              , 'type'     : 'buy'
                                              , 'ordertype': 'limit'
                                              , 'price'    : str(price)
                                              , 'volume'   : str(btcAmount)
                                              }, public = False)
        return result['result']['txid'][0]

    # return order ID
    def openMarketBuyOrder(self, pair, amount):
        if self.getBalance(pair[-4:]) < amount:
            logging.warning("Not enough " + pair[-3:] + ". Order not placed.")
            return (0, 0)

        bestAskPrice = self.getSecondBestBidPrice(pair)
        btcAmount = amount / float(bestAskPrice)
        result = self.__sendQuery('AddOrder', { 'pair'     : pair
                                              , 'type'     : 'buy'
                                              , 'ordertype': 'market'
                                              , 'volume'   : str(btcAmount)
                                              }, public = False)
        return (result['result']['txid'][0], bestAskPrice)

    def cancelOrder(self, txid):
        return self.__sendQuery('CancelOrder', { 'txid' : txid }, public=False)

    def getOrderBook(self, pair, count = 10):
        response = self.__sendQuery('Depth', {'pair': pair, 'count': str(count)})
        return response['result'][pair]

    def getSecondBestAskPrice(self, pair):
        return float(self.getOrderBook(pair)['asks'][1][0])

    def getSecondBestBidPrice(self, pair):
        return float(self.getOrderBook(pair)['bids'][1][0])

    def getOpenOrders(self):
        return self.__sendQuery("OpenOrders", public=False)

    def getClosedOrders(self):
        return self.__sendQuery("ClosedOrders", public=False)

    def getBalance(self, currency):
        response = self.__sendQuery("Balance", public = False)
        return float(response['result'][currency])

    # private query wrapper
    def __sendQuery(self, query, params = None, public = True):
        while True:
            if public: response = self.kraken.query_public(query, params)
            else:      response = self.kraken.query_private(query, params)
            if "result" in str(response):
                break
            logging.warning("The response does not contain the result field. Will retry in 10.")
            logging.warning("Problem: {}".format(response['error']))
            sleep(10)
        return response
