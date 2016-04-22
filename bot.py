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
        'For ex. "green candy", "blue northface"')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')

def getWords(text):
    return re.compile('\w+').findall(text)

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
        bot.sendMessage(update.message.chat_id, text=msg)

        params = {
            'page': 'search_reports',
            'sent': 1,
            'name': '',
            'logo': logo,
            'colour': color,
            'region': 'all',
            'percent_rating': 0,
            'pp': 10,
            'submit.x': 75,
            'submit.y': 18,
            'submit': 'Search Reports'
        }

        bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        page = opener.open(URI + urllib.urlencode(params))
        page.addheaders = [('User-agent', 'Mozilla/5.0')]

        content = page.read()
        doc = pq(html.fromstring(content))
        items = doc('.contentBlock table.td_chromed')
        #items = []

        if len(items) == 0:
            bot.sendMessage(update.message.chat_id, text='Cannot find anything relevant')
        else:
            for item in items:
                text = ''

                header = item[0][0]
                description = item[0][1]

                header_links = pq(header)('a')
                href = PREFIX + header_links[0].get('href')
                name = header_links[0][0].text

                text += '<a href="%s">%s</a> ' % (href, name)

                meta = pq(item)('table table td')

                img = pq(meta[0])('img')

                for m in meta[1:]:
                    key = re.sub(' +',' ', m[0].text.strip())
                    value = re.sub(' +',' ', m[1].text.strip())
                    if value:
                        text += '%s %s; ' % (key, value)

                if img:
                    img = PREFIX + img[0].get('src')
                    #text += 'img: ' + img
                    bot.sendPhoto(chat_id=update.message.chat_id, photo=img)
                else:
                    img = None

                bot.sendMessage(update.message.chat_id, text=text, parse_mode=telegram.ParseMode.HTML)


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
