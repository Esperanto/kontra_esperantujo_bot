#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging, sys, datetime
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
        CallbackQueryHandler, ConversationHandler, InlineQueryHandler, ChosenInlineResultHandler)
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.utils.helpers import escape_markdown
from datumbazo import *

go = None

def aldonu_karton(bot, update):
    updict = update.to_dict()
    print("bot=",bot,"\n\n")
    print("update=",updict,"\n\n")

    private = updict["message"]["chat"]["type"] == "private" # else it's a group
    grupnomo = "private" if private else updict["message"]["chat"]["title"]

    uzanto_nomo = ""
    if "username" in updict["message"]["from"]:
        uzanto_nomo = updict["message"]["from"]["username"]
    else:
        if 'first_name' in updict["message"]["from"]:
            uzanto_nomo += updict["message"]["from"]['first_name']
        if 'last_name'  in updict["message"]["from"]:
            uzanto_nomo += updict["message"]["from"]['last_name']

    command, message = updict["message"]["text"].split(" ", 1)
    rugxa_karto, rugxa_duvorta_karto, rugxa_trivorta_karto, verda_karto = 4*[False]
    if "rugxa_trivorta" in command:
        rugxa_trivorta_karto = True
    elif "rugxa_duvorta" in command:
        rugxa_duvorta_karto = True
    elif "rugxa" in command:
        rugxa_karto = True
    else: # "verda" in command:
        verda_karto = True

    brecxoj = message.split().count("*")
    common = 'Via volis aldoni ruĝan karton kun unu breĉoj, sed nur indikis {} breĉo(j)n...\n'.format(brecxoj) + \
             "Mi ne akceptos tiun karton, bvle korektu..."
    if rugxa_karto and brecxoj != 1:
        update.message.reply_text(common)
        return
    elif rugxa_duvorta_karto and brecxoj != 2:
        update.message.reply_text(common)
        return
    elif rugxa_trivorta_karto and brecxoj != 3:
        update.message.reply_text(common)
        return

    aldonu_karton_al_db(
      teksto = message, grupnomo = grupnomo, uzanto_nomo=uzanto_nomo,
      uzanto_id=updict["message"]["from"]["id"], chat_id=updict["message"]["chat"]["id"],
      rugxa_karto=rugxa_karto, rugxa_duvorta_karto=rugxa_duvorta_karto,
      rugxa_trivorta_karto=rugxa_trivorta_karto, verda_karto=verda_karto
    )
    print("db added", command, rugxa_karto, rugxa_duvorta_karto, rugxa_trivorta_karto, verda_karto)

    response = "g_nomo: {grupnomo}, uzanto_nomo={uzanto_nomo}, r_karto={rugxa_karto}," + \
               "r_duvorta_karto={rugxa_duvorta_karto}, r_trivorta_karto={rugxa_trivorta_karto}," + \
               "v_karto={verda_karto}".format(
                        grupnomo=grupnomo, uzanto_nomo=uzanto_nomo, rugxa_karto=rugxa_karto, rugxa_duvorta_karto=rugxa_duvorta_karto, rugxa_trivorta_karto=rugxa_trivorta_karto, verda_karto=verda_karto
                  )
    print("fff added")
    update.message.reply_text(response, parse_mode = ParseMode.MARKDOWN)

def error(bot, update, error):
    logger.warning('updict "%s" caused error "%s"', update, error)

def main():
    global update_id
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(open("SEKRETO.txt").read().strip())

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("aldonu_rugxa", aldonu_karton))
    dp.add_handler(CommandHandler("aldonu_rugxa_duvorta", aldonu_karton))
    dp.add_handler(CommandHandler("aldonu_rugxa_trivorta", aldonu_karton))
    dp.add_handler(CommandHandler("aldonu_verda", aldonu_karton))

    # log all errors
    dp.add_error_handler(error)
    # Start the Bot
    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    if 'genDB' in sys.argv:
        createDB();
    main()