import os
import logging

from dotenv import load_dotenv
from google.cloud import dialogflow
from telegram import Bot, Update, ForceReply
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler

logger = logging.getLogger(__name__)


def detect_intent_texts(project_id, session_id, texts, language_code):
    """
    Возвращает результат обнаружения намерений с текстами в качестве входных данных.

    Использование одного и того же `session_id` между запросами позволяет продолжать
    разговор.
    """

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    print("Session path: {}\n".format(session))

    for text in texts:
        text_input = dialogflow.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        return response.query_result.fulfillment_text


def send_message(bot, chat_id, message):
    bot.send_message(chat_id=chat_id, text=message)


def respond_to_message(update: Update, context: CallbackContext) -> None:
    """
        Обрабатывает текстовые сообщения от пользователей и отправляет ответ от Dialogflow.

        Параметры:

        update (Update): Объект, содержащий информацию о входящем обновлении от Telegram.

        context (CallbackContext): Контекст, предоставляющий доступ к боту и другим данным.

        Функция извлекает текст сообщения пользователя, отправляет его в Dialogflow для
        определения намерения и получает ответ. Затем отправляет полученный ответ обратно
        пользователю в Telegram.
    """

    user_text = update.message.text
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
    session_id = str(update.message.chat_id)
    language_code = "ru"

    response = detect_intent_texts(project_id, session_id, [user_text], language_code)


    send_message(context.bot, update.message.chat_id, response)


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot_token, tg_chat_id):
        super().__init__()
        self.bot = Bot(tg_bot_token)
        self.tg_chat_id = tg_chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.tg_chat_id, text=log_entry)


def start(update, context):
    update.message.reply_text('Привет! Я бот, который умеет общаться с Dialogflow!')


def main():
    load_dotenv()
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
    tg_chat_id = os.getenv('TG_CHAT_ID')
    tg_bot_token = os.getenv('TG_BOT_TOKEN')

    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s")
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(tg_bot_token, tg_chat_id))
    logger.info("The bot has started")

    try:
        updater = Updater(tg_bot_token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler('start', start))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, respond_to_message))
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logging.exception(e)


if __name__ == '__main__':
    main()
