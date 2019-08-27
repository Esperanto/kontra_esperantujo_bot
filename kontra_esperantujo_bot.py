#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging, sys, datetime, jinja2, cairosvg, textwrap
from kartoj_kontraux_esperantujo.generate import generate_kartaro
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
        CallbackQueryHandler, ConversationHandler, InlineQueryHandler, ChosenInlineResultHandler)
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.utils.helpers import escape_markdown
from datumbazo import *

def karto_bildo_response(teksto, is_verda=True):
    print("a-1")
    bildo, fontkoloro = ["../kartoj_kontraux_esperantujo/img/verdaj_kartoj.png", "#008000"] if is_verda else \
                        ["../kartoj_kontraux_esperantujo/img/rugaj_kartoj.png", "#ce181e"]
    template_str = open("kartoj_kontraux_esperantujo/templates/sxablono_karto.svg.jinja2").read()
    t = jinja2.Template(template_str)
    r = t.render(k={"teksto": textwrap.wrap(teksto, 20)}, piedbildo=bildo, fontkoloro=fontkoloro)
    open('tmp/temp.svg', "w").write(r)
    cairosvg.svg2png(url='tmp/temp.svg', write_to='tmp/temp.png')

def elsxutu_kartaron(bot, update):
    kartaro = cxiujn_kartojn_por_printado()
    print("haka")
    generate_kartaro(kartaro)
    print("proka")

def kiu_kontribuis(bot, update):
    kontribuantoj = set([k.uzanto_nomo for k in cxiujn_kartojn()])
    print("a")
    respondo = "Jen la origina traduko ĉi tie https://lakt.uk/butiko/kartoj-kontrau-esperantujo/ estas de timsk.\n"
    respondo2 = "Plu kontribuis kartojn en tio servilo jenaj personoj (elŝutu pere de 'elsxutu_kartaron' a ekzemple 'elsxutu_kartaron_de_uzantoj timsk, kontibuanto2, [...]'):\n\n* " + \
        "\n *".join(kontribuantoj)
    print("a")
    update.message.reply_text(respondo)
    update.message.reply_text(respondo2)
    print("a")

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
    common = 'Via volis aldoni ruĝan karton kun {} breĉoj,' + \
             ' sed nur indikis {} breĉo(j)n...\n'.format(brecxoj) + \
             "Mi ne akceptos tiun karton, bvle korektu..."
    if rugxa_karto and brecxoj != 1:
        update.message.reply_text(common.format(1))
        return
    elif rugxa_duvorta_karto and brecxoj != 2:
        update.message.reply_text(common.format(2))
        return
    elif rugxa_trivorta_karto and brecxoj != 3:
        update.message.reply_text(common.format(3))
        return
    if message.strip() == "":
        update.message.reply_text("Bonvole ne forgesu la tekston de la karto ;)")
        return
    if not verda_karto:
        message = message.replace("*", "_______")

    aldonu_karton_al_db(
      teksto = message, grupnomo = grupnomo, uzanto_nomo=uzanto_nomo,
      uzanto_id=updict["message"]["from"]["id"], chat_id=updict["message"]["chat"]["id"],
      rugxa_karto=rugxa_karto, rugxa_duvorta_karto=rugxa_duvorta_karto,
      rugxa_trivorta_karto=rugxa_trivorta_karto, verda_karto=verda_karto
    )
    karto_bildo_response(message, verda_karto)
    bot.send_photo(update.message.chat.id, photo=open("tmp/temp.png", 'rb'))
    response = "Aldonis la karto al la datumbazo."
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
    dp.add_handler(CommandHandler("elsxutu_kartaron", elsxutu_kartaron))
    dp.add_handler(CommandHandler("elsxutu_kartaron_de_uzantoj", elsxutu_kartaron))
    dp.add_handler(CommandHandler("kiu_kontribuis", kiu_kontribuis))

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
