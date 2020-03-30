from KrakenAPI import KrakenAPI
from SQLiteAPI import Orders
from Utils import loadConfig
from datetime import datetime, timedelta

class BotStats:
    def __init__(self, fiat):
        self.__api = KrakenAPI()
        self.__fiat = fiat

    def get_weekday_info(self, weekday):
        configs = [loadConfig(i) for i in range(7)]
        weekday_config = configs[weekday]

        with Orders() as orders:
            latest_order = orders.getLatestOrder()

        bought_today = False
        latest = latest_order[1] if latest_order else None
        if latest and (latest + timedelta(hours=1)).date() == datetime.now().date():
            weekday = (weekday + 1) % 7
            bought_today = True
        days = -1
        to_spend = -1
        balance = self.__api.getBalance("Z" + self.__fiat)
        # make sure user spends money
        for config in configs:
            if config['do_buy'] and config['amount'] > 0:
                to_spend = balance
                break
        # if he does, calculate days remaining
        while to_spend >= 0:
            to_spend -= configs[weekday]['amount'] if configs[weekday]['do_buy'] else 0
            days += 1
            weekday = (weekday + 1) % 7

        return { 'bought_today' : bought_today
               , 'latest'       : latest
               , 'do_buy'       : weekday_config['do_buy']
               , 'buy_time'     : weekday_config['buy_time']
               , 'curr'         : weekday_config['curr']
               , 'amount'       : weekday_config['amount']
               , 'balance'      : balance
               , 'left'         : days
               }

    def get_bought_and_spent(self, cryptos):
        bought = { c : 0 for c in cryptos }
        spent  = { c : 0 for c in cryptos }

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

        pairs  = { c : self.__api.getTradePair(c, self.__fiat) for c in cryptos }
        price  = { c : self.__api.getSecondBestAskPrice(pairs[c]) for c in cryptos }
        worth  = { c : bought[c] * price[c] for c in cryptos }

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
