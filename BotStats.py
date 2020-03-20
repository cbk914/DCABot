from KrakenAPI import KrakenAPI
from SQLiteAPI import Orders
from Utils import loadConfig
from datetime import datetime, timedelta

class BotStats:
    def __init__(self):
        self.__api = KrakenAPI()

    def get_weekday_info(self, weekday):
        configs = [loadConfig(i) for i in range(7)]
        config = configs[weekday]

        with Orders() as orders:
            latest_order = orders.getLatestOrder()

        latest = None
        if latest_order:
            latest = latest_order[1]

        balance = self.__api.getBalance("ZEUR")
        to_spend = balance
        days = -1
        bought_today = False
        if latest and (latest + timedelta(hours=1)).date() == datetime.now().date():
            weekday = (weekday + 1) % 7
            bought_today = True
        while to_spend >= 0:
            to_spend -= configs[weekday]['amount']
            days += 1
            weekday = (weekday + 1) % 7

        return { 'bought_today' : bought_today
               , 'latest'       : latest
               , 'do_buy'       : config['do_buy']
               , 'buy_time'     : config['buy_time']
               , 'pair'         : config['pair']
               , 'amount'       : config['amount']
               , 'balance'      : balance
               , 'left'         : days
               }

    def get_bought_and_spent(self):
        bought = { c : 0 for c in ['XBT', 'ETH', 'XTZ'] }
        spent  = { c : 0 for c in ['XBT', 'ETH', 'XTZ'] }

        with Orders() as orders:
            allOrders = orders.getOrders()

        for order in allOrders:
            txid = order[0]
            curr = order[1]
            vol  = order[2]
            cost = order[3]

            if curr in bought:
                bought[curr] += vol
                spent[curr]  += cost

        price = { 'XBT' : self.__api.getSecondBestAskPrice("XXBTZEUR")
                , 'ETH' : self.__api.getSecondBestAskPrice("XETHZEUR")
                , 'XTZ' : self.__api.getSecondBestAskPrice("XTZEUR")
                }
        worth  = { c : bought[c] * price[c] for c in ['XBT', 'ETH', 'XTZ'] }

        spent_sum = sum(spent.values())
        worth_sum = sum(worth.values())

        euro_change = worth_sum - spent_sum
        perc_change = euro_change / spent_sum * 100 if spent_sum > 0 else 0

        return { 'price'       : price
               , 'bought'      : bought
               , 'spent'       : spent
               , 'spent_sum'   : spent_sum
               , 'worth'       : worth
               , 'worth_sum'   : worth_sum
               , 'euro_change' : euro_change
               , 'perc_change' : perc_change
               }
