import os

from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext


# class TelegramLogsHandler(logging.Handler):
#
#     def __init__(self, tg_bot, chat_id):
#         super().__init__()
#         self.chat_id = chat_id
#         self.tg_bot = tg_bot
#
#     def emit(self, record):
#         log_entry = self.format(record)
#         self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def send_message(bot, chat_id, message):
    bot.send_message(chat_id=chat_id, text=message)


def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)


def main():
    load_dotenv()
    tg_bot_token = os.getenv('TG_BOT_TOKEN')
    updater = Updater(tg_bot_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
