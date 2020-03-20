from configparser import ConfigParser
from datetime import datetime

# load a given weekday's parser
# the weekday is given as an integer:
# monday = 0, tuesday = 1, etc.
def loadConfig(weekday):
    parser = ConfigParser()
    parser.read('Config/config.ini')
    config = {}

    weekdays = [ "monday"
               , "tuesday"
               , "wednesday"
               , "thursday"
               , "friday"
               , "saturday"
               , "sunday"
               ]

    config["do_buy"]   = parser['default'].getboolean("do_buy")
    config["pair"]     = parser['default'].get("pair")
    config["amount"]   = parser['default'].getfloat('amount')
    config["buy_time"] = datetime.strptime(parser['default'].get('buy_time'), "%H:%M").time()

    today = weekdays[weekday]

    if today in parser:
        do_buy = parser[today].getboolean("do_buy")
        if do_buy: config["do_buy"] = do_buy
        pair = parser[today].get("pair")
        if pair: config["pair"] = pair
        amount = parser[today].getfloat('amount')
        if amount: config["amount"] = amount
        buy_time = parser[today].getint('buy_time')
        if buy_time: config["buy_time"] = buy_time

    return config
