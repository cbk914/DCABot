from configparser import ConfigParser
import logging

# load a given weekday's config
# the weekday is given as an integer:
# monday = 0, tuesday = 1, etc.
def loadConfig(weekday):
    config = ConfigParser()
    config.read('Config/config.ini')
    info = {}

    weekdays = [ "monday"
               , "tuesday"
               , "wednesday"
               , "thursday"
               , "friday"
               , "saturday"
               , "sunday"
               ]
    try:
        info["do_buy"]          = config['default'].getboolean("do_buy")
        info["pair"]            = config['default'].get("pair")
        info["amount"]          = config['default'].getfloat('amount')
        info["buy_time"]        = config['default'].getint('buy_time')

        today = weekdays[weekday]

        if today in config:
            do_buy = config[today].getboolean("do_buy")
            if do_buy: info["do_buy"] = do_buy
            pair = config[today].get("pair")
            if pair: info["pair"] = pair
            amount = config[today].getfloat('amount')
            if amount: info["amount"] = amount
            buy_time = config[today].getint('buy_time')
            if buy_time: info["buy_time"] = buy_time

    except Exception as exc:
        logging.critical("Exception " + str(exc.__class__.__name__) + " : " + str(exc))

    return info
