from PIL import Image, ImageFont, ImageDraw
from inky import InkyPHAT
from datetime import datetime, timedelta
from time import time, sleep
from subprocess import check_output

from BotStats import BotStats

def main():

    # choose font
    font_path = "Resources/Coder's Crux.ttf"
    font = ImageFont.truetype(font_path, 16)

    # no color for now, updates faster
    inkyphat = InkyPHAT('black')
    inkyphat.set_border(inkyphat.BLACK)

    # display alt color
    alt_color = inkyphat.YELLOW

    while True:

        ### getting info

        # get stats objects
        stats = BotStats()

        # get today's info
        today = datetime.today().weekday()
        todays_info = stats.get_weekday_info(today)
        # get bought and spent
        bought_and_spent = stats.get_bought_and_spent()

        # get timestamp
        datetimestr = datetime.now().strftime("%d-%m-%Y %H:%M")

        # get local (ssh) ip
        ipstr = check_output(['hostname', '-I']).decode('ascii').strip()


        ### begin drawing

        # set background
        img = Image.open("Resources/bg.png")

        # make canvas
        draw = ImageDraw.Draw(img)

        ## DRAW current timestamp
        draw.text((7, 8), datetimestr, inkyphat.BLACK, font=font)

        ## DRAW bought and spent
        y_offset = 22
        xbt_infostr = "XBT {0:>12,.4f}".format(bought_and_spent['bought']['XBT'])
        eth_infostr = "ETH {0:>12,.4f}".format(bought_and_spent['bought']['ETH'])
        xtz_infostr = "XTZ {0:>12,.4f}".format(bought_and_spent['bought']['XTZ'])
        draw.text((7, y_offset),    xbt_infostr, inkyphat.BLACK, font=font)
        draw.text((7, y_offset+8),  eth_infostr, inkyphat.BLACK, font=font)
        draw.text((7, y_offset+16), xtz_infostr, inkyphat.BLACK, font=font)

        offset = 54
        draw.text((7, offset),    "spent {0:>8,.2f} €".format(bought_and_spent['spent_sum']),   inkyphat.BLACK, font=font)
        draw.text((7, offset+8),  "worth {0:>8,.2f} €".format(bought_and_spent['worth_sum']),   inkyphat.BLACK, font=font)
        draw.text((7, offset+16), "chnge {0:>8,.2f} €".format(bought_and_spent['euro_change']), inkyphat.BLACK, font=font)

        ## DRAW percent centered
        percentstr = "{0:.2f}%".format(bought_and_spent['perc_change'])
        (percent_w, _) = font.getsize(percentstr)
        percent_x = inkyphat.WIDTH / 4 - percent_w / 2
        draw.text((percent_x, 89), percentstr, inkyphat.WHITE, font=font)

        ## DRAW today header centered
        todaystr = 'TODAY'
        if todays_info['bought_today']:
            todaystr += ' (bought)'
        (today_w, _) = font.getsize(todaystr)
        today_x = (inkyphat.WIDTH - 10) / 4 * 3 + 5 - today_w / 2
        draw.text((today_x, 8), todaystr, inkyphat.WHITE, font=font)

        ## DRAW header line
        # TODO: make part of bakcground?
        for y in range(18,20):
            for x in range(108, 203):
                img.putpixel((x, y), alt_color)

        ## DRAW config info
        y_offset = 22
        if todays_info['do_buy']:
            buy_timestr = "time {0:>0} H".format(todays_info['buy_time'])
            pairstr     = "pair {0:>0}".format(todays_info['pair'])
            amountstr   = "amnt {0:>0,.2f} €".format(todays_info['amount'])

            draw.text((110, y_offset),    buy_timestr, inkyphat.WHITE, font=font)
            draw.text((110, y_offset+8),  pairstr,     inkyphat.WHITE, font=font)
            draw.text((110, y_offset+16), amountstr,   inkyphat.WHITE, font=font)
        else:
            draw.text((110, y_offset), 'Not buying -.-', inkyphat.WHITE, font=font)

        ## DRAW balance and days left
        offset = 54
        draw.text((110, offset),   "blce {0:>0,.2f} €".format(todays_info['balance']), inkyphat.WHITE, font=font)
        draw.text((110, offset+8), "days {0:>0}".format(todays_info['left']),          inkyphat.WHITE, font=font)

        ## DRAW (SSH) IP
        draw.text((110, 89), ipstr, inkyphat.WHITE, font=font)

        ## DRAW line separating percent and IP
        # TODO: make part of bakcground?
        for y in range(86, 99):
            for x in range(106,107):
                img.putpixel((x, y), alt_color)

        # finally rotate and show picture
        flipped = img.rotate(180)
        inkyphat.set_image(flipped)
        inkyphat.show()

        # sleep until the nearest 10:30 min mark
        # because the DCA bot will buy at the 20 min mark
        end = datetime.now()
        sleep_time = (timedelta(minutes=10, seconds=30) - timedelta(minutes=end.minute % 10, seconds=end.second)).total_seconds()
        if sleep_time > 0:
            sleep(sleep_time)

if __name__ == "__main__":
    main()
