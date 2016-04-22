from telegram.ext import Updater
from telegram.ext.dispatcher import run_async
import telegram
import logging
import re
from lxml import html
from pyquery import PyQuery as pq
import cookielib, urllib2, sys
import urllib


COLORS = ['white', 'black', 'gray', 'grey', 'red', 'pink', 'orange', 'yellow', 'green', 'blue', 'purple', 'brown']
URI = 'http://www.pillreports.net/index.php?'
PREFIX = 'http://www.pillreports.net/'


logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi! Send me a color and a logo of the candy or just a logo. ' +
        'For example, "green candy", "blue northface" or just "coca-cola"')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Send a color and a logo (or just a name) ' +
        'of the candy you whan to get info about')

def getWords(text):
    return re.compile('[\w-]+').findall(text)

@run_async
def search(bot, update, **kwargs):
    words = getWords(update.message.text)

    color = ''
    logo = ''

    if len(words) < 1:
        bot.sendMessage(update.message.chat_id, text='Sorry what? Send me a color and a logo of the candy or just a logo. ' +
            'For ex. "green candy", "blue northface"')
    else:
        if len(words) == 1:
            logo = words[0].lower()
        else:
            if (words[0].lower() in COLORS):
                color = words[0].lower()
                logo = ' '.join(words[1:]).lower()
            else:
                logo = ' '.join(words).lower()

        msg = ('Looking for %s' % logo)
        if color:
            msg += ' (%s color)' % color
        msg += '. Wait a few seconds pls...'

        # send wait message
        bot.sendMessage(update.message.chat_id, text=msg)
        bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

        params = {
            'page': 'search_reports',
            'sent': 1,
            'name': '',
            'logo': logo,
            'colour': color,
            'region': 'all',
            'percent_rating': 0,
            'pp': 6,
            'submit.x': 75,
            'submit.y': 18,
            'submit': 'Search Reports'
        }

        full_url = URI + urllib.urlencode(params)


        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        page = opener.open(full_url)
        page.addheaders = [('User-agent', 'Mozilla/5.0')]

        content = page.read()
        doc = pq(html.fromstring(content))
        items = doc('.contentBlock table.td_chromed')
        #items = []

        if len(items) == 0:
            bot.sendMessage(update.message.chat_id, text='Cannot find anything relevant. ' +
                'Try again in format color + logo or just logo')
        else:
            bot.sendMessage(update.message.chat_id, text='That\'s what I found:')

            for idx, item in enumerate(items[:5]):
                header = item[0][0]
                description = item[0][1]

                header_links = pq(header)('a')
                href = PREFIX + header_links[0].get('href')
                name = header_links[0][0].text

                # send name
                bot.sendMessage(
                    update.message.chat_id,
                    text='<a href="%s">%d. %s</a>' % (href, 1 + idx, name.upper()),
                    parse_mode=telegram.ParseMode.HTML)


                text = ''

                meta = pq(item)('table table td')

                img = pq(meta[0])('img')
                if img:
                    img = PREFIX + img[0].get('src').replace('thumbnails', 'fullsize')
                    #text += 'img: ' + img

                    # send photo
                    bot.sendPhoto(chat_id=update.message.chat_id, photo=img)


                logo = meta[1][1].text.strip() #
                location = meta[2][1].text.strip()
                color = meta[3][1].text.strip() #
                tested = meta[4][1].text.strip()
                shape = meta[5][1].text.strip() #
                content = meta[6][1].text.strip() #
                report_quality = meta[7][1].text.strip()
                rating = meta[8][1].text.strip() #
                warning = meta[9][1].text.strip() #


                text += ('%s <strong>WARNING</strong> %s\n' % (telegram.Emoji.WARNING_SIGN, telegram.Emoji.WARNING_SIGN)) if warning == 'yes' else ''
                text += '%s<strong>%s (%s)</strong>. ' % (telegram.Emoji.SMILING_FACE_WITH_SUNGLASSES, content.title(), rating)
                text += ('%s Tested\n' % telegram.Emoji.OK_HAND_SIGN) if tested == 'yes' else 'Not tested\n'
                text += (color.title() + ' ') if color else ''
                text += ('%s%s (%s)\n' % (telegram.Emoji.PILL, logo.title(), shape)) if shape else ('%s\n' % logo.title())
                text += '%s%s\n' % (telegram.Emoji.ROUND_PUSHPIN, location)
                text += '<a href="%s">More information</a>' % href

                # send description
                bot.sendMessage(
                    update.message.chat_id,
                    text=text,
                    parse_mode=telegram.ParseMode.HTML)

            if len(items) > 5:
                bot.sendMessage(
                    update.message.chat_id,
                    text='For more information you can <a href="%s">check the full list</a>' % full_url,
                    parse_mode=telegram.ParseMode.HTML)

            bot.sendMessage(
                update.message.chat_id,
                text='Anything else? ' +
                    telegram.Emoji.WHITE_RIGHT_POINTING_BACKHAND_INDEX +
                    telegram.Emoji.WHITE_RIGHT_POINTING_BACKHAND_INDEX)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater("196843169:AAHMi5qHiNCpMK4uhGQZff2qKpsm-pox72c")

    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.addTelegramCommandHandler("start", start)
    dp.addTelegramCommandHandler("help", help)

    dp.addTelegramMessageHandler(search)

    dp.addErrorHandler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
