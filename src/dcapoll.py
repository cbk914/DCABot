from PIL import Image, ImageFont, ImageDraw
from inky import InkyPHAT
from datetime import datetime, timedelta
from time import time, sleep
from subprocess import check_output
import logging

from BotStats import BotStats

def main():

    # define FIAT currency
    # TODO: take as command-line arg
    fiat = "EUR"

    # define supported FIAT symbols
    fiat_symbols = { "EUR" : '€'
                   , "USD" : '$'
                   , "CAD" : '$'
                   # TODO: more?
                   }

    # set symbol to use on display
    fiat_symbol = (' ' + fiat_symbols[fiat]) if fiat in fiat_symbols else ''

    # define cryptos to count and to show on display
    cryptos_to_count = ["XBT", "XTZ", "ETH"]
    cryptos_to_show  = cryptos_to_count

    # set logging format
    logging.basicConfig( filename = "log/poll.log"
                       , format='%(asctime)s %(levelname)s: %(message)s'
                       , datefmt='%d/%m/%Y %H:%M:%S'
                       , level = logging.INFO
                       )

    # choose font
    font_path = "resources/Coder's Crux.ttf"
    font = ImageFont.truetype(font_path, 16)

    # no color for now, updates faster
    inkyphat = InkyPHAT('black')
    inkyphat.set_border(inkyphat.BLACK)

    logging.info("Let's start drawing!")

    while True:

        # set background
        img = Image.open("resources/bg.png")

        try:

            ####################
            ### getting info ###
            ####################

            # get stats objects
            stats = BotStats(fiat)

            # get today's info
            today = datetime.today().weekday()
            todays_info = stats.get_weekday_info(today)

            # get bought and spent for given cryptos
            bought_and_spent = stats.get_bought_and_spent(cryptos_to_count)

            # get timestamp
            datetimestr = datetime.now().strftime("%d-%m-%Y %H:%M")

            # get local (ssh) ip
            ipstr = check_output(['hostname', '-I']).decode('ascii').strip()

            #####################
            ### begin drawing ###
            #####################

            # make canvas
            draw = ImageDraw.Draw(img)

            ## DRAW current timestamp
            draw.text((7, 8), datetimestr, inkyphat.BLACK, font=font)

            ## DRAW bought and spent
            y_offset = 22
            for (c, b) in bought_and_spent['bought'].items():
                if c in cryptos_to_show:
                    infostr = "{0:<4} {1:>11,.4f}".format(c, b)
                    draw.text((7, y_offset), infostr, inkyphat.BLACK, font=font)
                    y_offset += 8

            y_offset = 54
            draw.text((7, y_offset),    "spent {0:>8,.2f}{1}".format(bought_and_spent['spent_sum'],   fiat_symbol), inkyphat.BLACK, font=font)
            draw.text((7, y_offset+8),  "worth {0:>8,.2f}{1}".format(bought_and_spent['worth_sum'],   fiat_symbol), inkyphat.BLACK, font=font)
            draw.text((7, y_offset+16), "chnge {0:>8,.2f}{1}".format(bought_and_spent['euro_change'], fiat_symbol), inkyphat.BLACK, font=font)

            ## DRAW percent centered
            percentstr = "{0:.2f}%".format(bought_and_spent['perc_change'])
            (percent_w, _) = font.getsize(percentstr)
            percent_x = inkyphat.WIDTH / 4 - percent_w / 2
            draw.text((percent_x, 89), percentstr, inkyphat.WHITE, font=font)

            ## DRAW today header centered
            todaystr = 'TODAY' + (' (bought)' if todays_info['bought_today'] else '')
            (today_w, _) = font.getsize(todaystr)
            today_x = (inkyphat.WIDTH - 10) / 4 * 3 + 5 - today_w / 2
            draw.text((today_x, 8), todaystr, inkyphat.WHITE, font=font)

            ## DRAW config info
            y_offset = 22
            if todays_info['do_buy']:
                buy_timestr = "time {}".format(todays_info['buy_time'].strftime("%H:%M"))
                pairstr     = "curr {0:>0}".format(todays_info['curr'])
                amountstr   = "amnt {0:>0,.2f}{1}".format(todays_info['amount'], fiat_symbol)

                draw.text((110, y_offset),    buy_timestr, inkyphat.WHITE, font=font)
                draw.text((110, y_offset+8),  pairstr,     inkyphat.WHITE, font=font)
                draw.text((110, y_offset+16), amountstr,   inkyphat.WHITE, font=font)
            else:
                draw.text((110, y_offset), 'Not buying -.-', inkyphat.WHITE, font=font)

            ## DRAW balance and days left
            y_offset = 54
            draw.text((110, y_offset),   "blce {0:>0,.2f}{1}".format(todays_info['balance'], fiat_symbol), inkyphat.WHITE, font=font)
            draw.text((110, y_offset+8), "days {0:>0}".format(todays_info['left']), inkyphat.WHITE, font=font)

            ## DRAW (SSH) IP
            draw.text((110, 89), ipstr, inkyphat.WHITE, font=font)

        except Exception as exc:
            logging.critical("Exception " + str(exc.__class__.__name__) + " : " + str(exc))

        # finally rotate and show picture
        flipped = img.rotate(180) # NOTE: depends on Pi's orientation
        inkyphat.set_image(flipped)
        inkyphat.show()

        # sleep until the nearest 10:30 min mark
        # because the DCA bot will buy at the 10:00 min mark
        end = datetime.now()
        sleep_time = (timedelta(minutes=10, seconds=30) - timedelta(minutes=end.minute % 10, seconds=end.second)).total_seconds()
        if sleep_time > 0:
            sleep(sleep_time)

if __name__ == "__main__":
    main()
