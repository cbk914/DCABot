from PIL import Image, ImageFont, ImageDraw
from inky import InkyPHAT
from datetime import datetime, timedelta
from time import time, sleep
import subprocess
from KrakenAPI import KrakenAPI
from SQLiteAPI import Orders
from Utils import loadConfig

def main():

    api = KrakenAPI()

    # choose font
    font_path = "resources/Coder's Crux.ttf"
    font = ImageFont.truetype(font_path, 16)

    # no color for now, updates faster
    inkyphat = InkyPHAT('black')
    inkyphat.set_border(inkyphat.BLACK)

    while True:

        # set background
        img = Image.open("resources/bg.png")

        # make canvas
        draw = ImageDraw.Draw(img)

        # load configs of all weekdays
        configs = [loadConfig(i) for i in range(7)]

        # get today's config
        today = datetime.today().weekday()
        config = configs[today]

        # fetch closed orders
        with Orders() as orders:
            allOrders = orders.getOrders()
            latestOrder = orders.getLatestOrder()

        # set timestamp
        timestamp = datetime.now()

        # draw current timestamp
        datetimestr = timestamp.strftime("%d-%m-%Y %H:%M")
        draw.text((7, 8), datetimestr, inkyphat.BLACK, font=font)

        # count crypto buys and costs
        xbtCost = 0; xbtSum = 0
        ethCost = 0; ethSum = 0
        xtzCost = 0; xtzSum = 0

        for order in allOrders:
            txid = order[0]
            curr = order[1]
            vol  = order[2]
            cost = order[3]

            if curr == "XBT":
                xbtCost += cost
                xbtSum += vol
            elif curr == "ETH":
                ethCost += cost
                ethSum += vol
            elif curr == "XTZ":
                xtzCost += cost
                xtzSum += vol

        # center and show 'today' header
        # also write '(bought)' if the bot has already bought
        todaystr = 'TODAY'
        if latestOrder and (latestOrder[1] + timedelta(hours=1)).date() == timestamp.date():
            todaystr += ' (bought)'
        today_w, today_h = font.getsize(todaystr)
        today_x = (inkyphat.WIDTH - 10) / 4 * 3 + 5 - today_w / 2
        draw.text((today_x, 8), todaystr, inkyphat.WHITE, font=font)

        # underline the header
        for y in range(18,20):
            for x in range(108, 203):
                img.putpixel((x, y), inkyphat.YELLOW)

        # show config info
        y_offset = 22
        if config['do_buy']:
            buy_time = "time {0:>0} H".format(config['buy_time'])
            pair     = "pair {0:>0}".format(config['pair'])
            amount   = "amnt {0:>0,.2f} €".format(config['amount'])

            draw.text((110, y_offset), buy_time, inkyphat.WHITE, font=font)
            draw.text((110, y_offset+8), pair, inkyphat.WHITE, font=font)
            draw.text((110, y_offset+16), amount, inkyphat.WHITE, font=font)
        else:
            draw.text((110, y_offset), 'Not buying -.-', inkyphat.WHITE, font=font)

        # show buys
        y_offset = 22
        xbt_info = "XBT {0:>12,.4f}".format(xbtSum)
        eth_info = "ETH {0:>12,.4f}".format(ethSum)
        xtz_info = "XTZ {0:>12,.4f}".format(xtzSum)
        draw.text((7, y_offset),    xbt_info, inkyphat.BLACK, font=font)
        draw.text((7, y_offset+8),  eth_info, inkyphat.BLACK, font=font)
        draw.text((7, y_offset+16), xtz_info, inkyphat.BLACK, font=font)

        # compute spent, worth, change
        xbtPrice = api.getSecondBestAskPrice("XXBTZEUR")
        ethPrice = api.getSecondBestAskPrice("XETHZEUR")
        xtzPrice = api.getSecondBestAskPrice("XTZEUR")

        spent = xbtCost + ethCost + xtzCost
        worth = xbtSum * xbtPrice + ethSum * ethPrice + xtzSum * xtzPrice
        change = worth - spent

        if spent > 0:
            percent = change / spent * 100
        else:
            percent = 0

        # show stats
        offset = 54
        draw.text((7, offset),    "spent {0:>8,.2f} €".format(spent), inkyphat.BLACK, font=font)
        draw.text((7, offset+8),  "worth {0:>8,.2f} €".format(worth), inkyphat.BLACK, font=font)
        draw.text((7, offset+16), "chnge {0:>8,.2f} €".format(change), inkyphat.BLACK, font=font)

        # center and show change percentage
        percentstr = "{0:.2f}%".format(percent)
        percent_w, percent_h = font.getsize(percentstr)
        percent_x = inkyphat.WIDTH / 4 - percent_w / 2
        draw.text((percent_x, 89), "{0:.2f}%".format(percent), inkyphat.WHITE, font=font)

        # draw separating line
        for y in range(86, 99):
            for x in range(106,107):
                img.putpixel((x, y), inkyphat.YELLOW)

        # get balance and compute days left
        # NOTE: change ZEUR to ZUSD here and in the config
        # you want the bot to use euro
        balance = api.getBalance("ZEUR")
        to_spend = balance
        days = 0
        # compute days left.
        # NOTE: the order timestamp (latestOrder[1]) is one hour behind my local time,
        # so I have to add an hour to it.
        if latestOrder and (latestOrder[1] + timedelta(hours=1)).date() == timestamp.date():
            today = (today + 1) % 7
        while to_spend > 0:
            to_spend -= configs[today]['amount']
            days += 1
            today = (today + 1) % 7
        days -= 1

        # show balance and days left
        offset = 54
        draw.text((110, offset), "blce {0:>0,.2f} €".format(balance), inkyphat.WHITE, font=font)
        draw.text((110, offset+8), "days {0:>0}".format(days), inkyphat.WHITE, font=font)

        # show local (ssh) ip
        from subprocess import check_output
        ipstr = check_output(['hostname', '-I']).decode('ascii').strip()
        draw.text((110, 89), ipstr, inkyphat.WHITE, font=font)

        # finally rotate and show picture
        flipped = img.rotate(180)
        inkyphat.set_image(flipped)
        inkyphat.show()

        # sleep until the nearest 10 min mark
        end = datetime.now()
        sleep_time = (timedelta(minutes=10, seconds=30) - timedelta(minutes=end.minute % 10, seconds=end.second)).total_seconds()
        if sleep_time > 0:
            sleep(sleep_time)

if __name__ == "__main__":
    main()
