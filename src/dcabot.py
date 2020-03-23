from time import time, sleep
from datetime import datetime, timedelta
import logging

from KrakenAPI import KrakenAPI
from SQLiteAPI import Orders
from Utils import loadConfig

# update the local database to contain the order
def close_order(api, closed_orders, txid):
    with Orders() as orders:
        curr = closed_orders[txid]['descr']['pair'][:3] # which crypto?
        vol = closed_orders[txid]['vol_exec']           # volume bought
        cost = closed_orders[txid]['cost']              # cost
        orders.insertOrder(txid, curr, vol, cost)       # update database

        price = float(closed_orders[txid]['price'])     # average price
        logging.info("{0}: Bought {1} {2} @ market ({3:.2f})".format(txid, vol, curr, price))

# place a market order based on today's config
# if the order isn't closed after 10 seconds,
# cancel it and place a new one
def buy(api, pair, amount): #config):
    logging.info("Attempting to buy...")
    while True:
        (txid, _) = api.openMarketBuyOrder(pair, amount)
        if txid != 0:
            sleep(10) # give the order 10 seconds to close
            closed_orders = api.getClosedOrders()['result']['closed']
            if txid in closed_orders:
                close_order(txid, closed_orders, txid)
                return True
            else:
                api.cancelOrder(txid) # cancel order
                openOrders = api.getOpenOrders()['result']['open']
                # wait until order is not open anymore
                while txid in openOrders:
                    sleep(10)
                    openOrders = api.getOpenOrders['result']['open']
                closed_orders = api.getClosedOrders()['result']['closed']
                # save information if it closed after all
                if closed_orders[txid]['status'] == 'closed':
                    close_order(txid, closed_orders, txid)
                    return True
                # otherwise it's cancelled; try again
        else: # not enough money, terminate
            return False

# get the timestamp of latest order
def getLastBuyDatetime():
    with Orders() as orders:
        latest = orders.getLatestOrder()
        if latest:
            return latest[1]
        else:
            return datetime.now() - timedelta(days=1)

def main():

    # define FIAT currency
    # TODO: take as command-line arg
    fiat = "EUR"

    # set logging format
    logging.basicConfig( filename = "log/dca.log"
                       , format='%(asctime)s %(levelname)s: %(message)s'
                       , datefmt='%d/%m/%Y %H:%M:%S'
                       , level = logging.DEBUG
                       )

    logging.info("Let's start buying!")

    api = KrakenAPI()

    lastBuyDatetime = getLastBuyDatetime()

    while True:

        try:
            # get today's config
            weekday = datetime.today().weekday()
            config = loadConfig(weekday)

            # date of last order
            lastBuyDate = lastBuyDatetime.date()

            # current date and time
            currentDatetime = datetime.now()
            currentDate = currentDatetime.date()

            # did we already buy today?
            bought_today = lastBuyDate == currentDate

            # buy if criteria are met
            if config['do_buy'] and not bought_today:
                # get current time
                currentTime = currentDatetime.time()

                # if it's larger than or equal to buy_time, buy!
                if currentTime >= config['buy_time']:
                    # get asset pair
                    pair = api.getTradePair(config['curr'], fiat)

                    # buy, and set last buy time if successful
                    if buy(api, pair, config['amount']):
                        lastBuyDatetime = datetime.now()

                else: logging.info("No action this time around.")

            else: logging.info("No action this time around.")

        except Exception as exc:
            logging.critical("Exception " + str(exc.__class__.__name__) + " : " + str(exc))

        # sleep until next 10 min mark
        end = datetime.now()
        sleep_time = (timedelta(minutes=10) - timedelta(minutes=end.minute % 10, seconds=end.second)).total_seconds()
        if sleep_time > 0:
            sleep(sleep_time)

if __name__ == "__main__":
    main()
