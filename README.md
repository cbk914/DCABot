
# Configurable DCA bot for crypto
I have wanted to try out dollar cost averaging (DCA) for quite some time now. However, Kraken---which is my exchange of choice---does not support automated daily orders, so I thought it would be a fun weekend project to actually make a bot that does this for me.

## What exactly does it do?
From [Binance Academy](https://www.binance.vision/glossary/dollar-cost-averaging):
>Dollar cost averaging refers to the practice of investing fixed amounts at regular intervals (for instance, $20 every week). This is a strategy used by investors that wish to reduce the influence of volatility over their investment and, therefore, reduce their risk exposure.

Simply put, the bot blindly buys some amount of crypto every day. The following things can be configured:
* **What time of day to buy**
* **What crypto to buy**
* **How many euros to spend**

Further, each day of the week can be configured independently such that it will buy e.g. Bitcoin for 20€ on some weekdays, and Tezos for 10€ on the other weekdays. Finally, it can be configured to not buy anything at all on specific weekdays.

Check `src/config/config.ini` directory for an example configuration.

## Hardware
![My RPi setup](https://raw.githubusercontent.com/LarsVadgaard/DCABot/master/images/setup1.jpg)
I wrote this bot for my Raspberry Pi, but it should be able to run on any machine with Python 3 installed. If you want my exact setup, you will need:
* Raspberry Pi (I use 3 B+) with Raspbian and power supply
* [Pimoroni Inky pHAT](https://shop.pimoroni.com/products/inky-phat?variant=12549254905939)
* [Pibow 3 B+ Coupé](https://shop.pimoroni.com/products/pibow-coupe-for-raspberry-pi-3-b-plus?variant=2601027993610)

If you choose to run the bot on this setup, you can run a separate monitor program `dcapoll.py` to show some stats on the Inky pHAT display as seen in the picture---with 10 minute intervals. The left half of the display will show the following:
* Timestamp of last display update
* How much XBT, ETH, and XTZ the bot has bought
* How much I have spent in total
* How much it's worth in total
* The change in euro
* The change in percent

The right half, on the other hand, will show the following:
* Today's configuration (time, pair, amount)
* Current balance on Kraken
* How many days are left based on the weekly configuration
* The local (SSH) IP address

The `BotStats` class in `src/BotStats.py` makes it simple to write other monitor programs such as for the Inky wHAT or the terminal.

## Installation
The bot uses the `krakenex` Kraken API. The monitor uses the `inky` and `Pillow` packages. Install all by running `pip3 install -r requirements.txt` in the root directory of the repo.

Make the database directory by running `mkdir src/database`.

Make the log directory by running `mkdir src/log`.

[Generate an API key on Kraken](https://support.kraken.com/hc/en-us/articles/360022839451-Generate-API-Keys) and create the API key file ```src/config/kraken.key``` with the following content:
```
Public API key
Private API key
```
The API key should allow the following:
* Fetching public information (prices, etc.)
* Fetching private information (balance, order information)
* Placing orders

## Usage
The actual DCA bot can be found in `src/dcabot.py`. Run it by issuing the command `python3 src/dcabot.py`. It will write debug info to `src/log/dca.log`.

The monitor program that will fetch the DCA bot stats and display them on the screen is, as mentioned, `src/dcapoll.py`. Run it by issuing the command ```python3 src/dcapoll.py```. It will write debug info to `src/log/poll.log`.

If you want to run these on the Pi through SSH, you may want to use the ```nohup``` command. Entering `make run` in the `src/` directory will run them using `nohup` and save their PIDs to individual dotfiles. Conversely, `make kill` will kill the processes using these dotfiles.

When the bot buys some amount of crypto, the order details are saved in a local SQLite3 database, `src/database/orders.db`. This way, any order you place manually (or with another bot) will not interfere with this bot.

## Note
I see myself as a functional programmer. This was a quick project of mine, and I usually don't code Python. As such, some (or much) of the code may be unelegant.

Also, the bot was written with Euro as the currency to buy with. If you want to use another currency, you'd have to change the following:
* The `"EUR"` parameter in the `api.getTradePair()` call in `src/dcabot.py`
* The call to the `BotStats` constructor in `src/dcapoll.py`
* The euro symbols in `src/dcapoll.py`

If you want the display to show other cryptos than XBT, ETH, and XTZ, you'd have to change `src/dcapoll.py` accordingly.

Finally, though I have the yellow/black/white Inky pHAT display, I have set it to be black/white only for faster update times. If you want some color on the display, you must update the code and graphics accordingly yourself.

**Use this bot at your own risk**.

## TO DO
* Display timestamp of latest buy (no room on Inky pHAT display)
* Perhaps handle exceptions in a more elegant manner
* Split bot and monitor up in different folders
* Make the cryptos shown on the display configurable
* A Shell script to run (and perhaps install) everything
* Give the color (red, yellow, or black) for the display as a command-line flag

## Feedback
For any feedback and/or suggestions, contact me at larsvadgaard \*at\* gmail \*dot\* com.

## Credits
First off, this small project was inspired by [this project](https://www.reddit.com/r/CryptoCurrency/comments/d737wg/i_set_up_a_raspberry_pi_trading_bot_with_an_eink/) by u/brutang, and the background image was found on [this page](https://www.electromaker.io/project/view/taking-the-raspberry-pi-inky-phat-to-the-next-level), though it has been edited a bit. I also got some code and ideas from [this repo](https://github.com/Dodo33/btfd-bitcoin-bot) (e.g. config loading).

## Donate
This isn't a grand project but if you feel like it, I would appreciate small donations.
```
Tezos    (XTZ)   @ tz1RWPDoMABjLect6dkETjPWgva5SRMtWGVw
Bitcoin  (BTC)   @ 38TM7xJnN4tV2U2La8bh5Rcu2muASkyQZn
Ethereum (ETH)   @ 0x6e9644FaD57F93b58573bAdEe3Cb0596F32C9852
Litecoin (LTC)   @ MUyMZejFyJsVpmZ5omg8yzh6nRQwhdQM5U
Dogecoin (DOGE)  @ DG82bQUFRTVyfkExwLwoSj8k6zQRoTCC6h
Stratis  (STRAT) @ SYWpro6QK8gbAfivNAkmiHy6wCuUs6qLjQ
Dash     (DASH)  @ Xe6VHQi5DPdufsGSSWRg5ZmPkiU4oBxebQ
```
