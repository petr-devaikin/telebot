#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater
from telegram.ext.dispatcher import run_async
import telegram
import logging
import re
import cookielib, urllib2, sys
import urllib
import botan
import os
import parser


COLORS = ['white', 'black', 'gray', 'grey', 'red', 'pink', 'orange', 'yellow', 'green', 'blue', 'purple', 'brown']

PREFIX = os.environ.get('BOT_PREFIX')
URI = PREFIX + 'index.php?'

TOKEN = os.environ.get('BOT_TOKEN')
STAT_TOKEN = os.environ.get('BOT_STAT_TOKEN')

MESSAGES = {
    'hello': 'Hi! Send me a color and a logo of the candy or just a logo. ' +
             'For example, "green candy", "blue northface" or just "coca-cola"',
    'help': 'Send a color and a logo (or just a name) ' +
            'of the candy you whan to get info about',
    'notrecognized': 'Sorry what? Send me a color and a logo of the candy or just a logo. ' +
                'For ex. "green candy", "blue northface"',
    'notfound': 'Cannot find anything relevant. ' +
                'Try again in format color + logo or just logo',
    'info_start': 'That\'s what I found:',
    'info_more': 'For more information you can <a href="%s">check the full list</a>',
    'info_end': 'If you need something, just send me a new request ' +
                telegram.Emoji.WHITE_RIGHT_POINTING_BACKHAND_INDEX +
                telegram.Emoji.WHITE_RIGHT_POINTING_BACKHAND_INDEX
}


logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text=MESSAGES['hello'])


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text=MESSAGES['help'])

def getWords(text):
    return re.compile('[\w-]+').findall(text)

@run_async
def search(bot, update, **kwargs):
    botan.track(STAT_TOKEN, update.message.from_user, update.message.to_dict(), 'info request')

    words = getWords(update.message.text)

    color = ''
    logo = ''

    if len(words) < 1:
        bot.sendMessage(update.message.chat_id, text=MESSAGES['notrecognized'])
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

        items = parser.parse(content, PREFIX)

        if len(items) == 0:
            bot.sendMessage(update.message.chat_id, text=MESSAGES['notfound'])
        else:
            bot.sendMessage(update.message.chat_id, text=MESSAGES['info_start'])

            for idx, item in enumerate(items[:5]):
                # send name
                bot.sendMessage(
                    update.message.chat_id,
                    text='<a href="%s">%d. %s</a>' % (item['href'], 1 + idx, item['name'].upper()),
                    parse_mode=telegram.ParseMode.HTML)

                if 'img' in item:
                    bot.sendPhoto(chat_id=update.message.chat_id, photo=item['img'])

                text = ''
                if item['warning'] == 'yes':
                    text += ('%s <strong>WARNING</strong> %s\n' % (telegram.Emoji.WARNING_SIGN, telegram.Emoji.WARNING_SIGN))
                text += '<strong>%s — %s</strong> ' % (item['content'].title(), item['rating'])
                text += '(tested)\n' if item['tested'] == 'yes' else '(not tested)\n'
                text += telegram.Emoji.PILL + ' '
                text += (item['color'].title() + ' ') if item['color'] else ''
                text += ('%s (%s)\n' % (item['logo'].title(), item['shape'])) if item['shape'] else ('%s\n' % item['logo'].title())
                text += '%s%s\n' % (telegram.Emoji.ROUND_PUSHPIN, item['location'])
                text += '<a href="%s">More information</a>' % item['href']

                # send description
                bot.sendMessage(
                    update.message.chat_id,
                    text=text,
                    parse_mode=telegram.ParseMode.HTML)

            if len(items) > 5:
                bot.sendMessage(
                    update.message.chat_id,
                    text=MESSAGES['info_more'] % full_url,
                    parse_mode=telegram.ParseMode.HTML)

            bot.sendMessage(update.message.chat_id, text=MESSAGES['info_end'])


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(TOKEN)

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
