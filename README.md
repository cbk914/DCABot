# Configurable DCA bot (for Raspberry Pi)
I have wanted to try out (crypto) dollar-cost averaging for quite some time now. However, Kraken (which is my exchange of choice) does not support automated daily orders, so I thought it would be a fun weekend project to actually make a bot that does this for me.

The bot blindly buys some amount of crypto every day. The following things can be configured:

* what time of day to buy,
* what crypto to buy, and
* how many euros to spend.

Further, each day of the week can be configured independently such that it will buy e.g. Bitcoin on four days of the week and Ethereum on the other three. Finally, it can be configured to not buy anything on specific weekdays.

Check the ```Config``` directory for an example configuration.

I have connected a small e-ink display as seen in the picture. A separate program will update this display with some stats from the DCA bot. The left half of the display shows the following:

* timestamp of last display update,
* how much XBT, ETH, and XTZ the bot has bought,
* how much I have spent in total,
* how much it's worth in total,
* the change in euro, and
* the change in percent.

The right half, on the other hand, shows the following:

* today's configuration (time, pair, amount),
* current balance on Kraken, and
* how many days of the current weekly configuration the balance allows.

As you see, if I add any more cryptos to my configuration I will need a larger display.

To do:
* Display timestamp of latest buy.

Any feedback and/or advice would be great.

# Setup
This bot has been written for the Raspberry Pi with the [https://shop.pimoroni.com/products/inky-phat?variant=12549254217811](inky pHAT e-ink display).

Install the Kraken API:
```pip3 install krakenex```

Install inky:
```pip3 install inky```

You may need to install other modules. You'll find out when you try to run it.

Make the database directory:
```mkdir Database```

Make the log directory:
```mkdir Log```

Create the API key file ```Config/kraken.key``` with the content:
```
Public API key
Private API key
```

# Usage
The actual DCA bot can be found in ```dcabot.py```. Run it by issuing the command ```python3 dcabot.py```.
The program that will fetch the DCA bot stats and display them on the screen is ```dcapoll.py```. Run it by issuing the command ```python3 dcapoll.py```.

If you run these on the Pi through SSH, you may want to use the ```nohup``` command. The Makefile in this repo will run them using ```nohup``` when you enter ```make run```. ```make kill``` will stop them.

When the bot buys some amount of crypto, the order details are saved in a local SQLite3 database. This way, any order you place manually will not interfere with the bot.

# Note
This was a quick project of mine, and I usually don't code Python. As such, some (or much) of the code may be a bit hacky.

# Credits
First off, this small project was inspired by [this project](https://www.reddit.com/r/CryptoCurrency/comments/d737wg/i_set_up_a_raspberry_pi_trading_bot_with_an_eink/) by u/brutang, and the background image was found on [this page](https://www.electromaker.io/project/view/taking-the-raspberry-pi-inky-phat-to-the-next-level), though it has been edited a bit.

I also got some code and ideas [this repo](https://github.com/Dodo33/btfd-bitcoin-bot) (e.g. config loading).
