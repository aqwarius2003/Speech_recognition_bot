import os
from dotenv import load_dotenv
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from google.cloud import dialogflow
import random
import logging

logger = logging.getLogger(__name__)


def detect_intent_texts(project_id, session_id, texts, language_code):
    """
    Возвращает результат обнаружения намерений с текстами в качестве входных данных.

    Использование одного и того же `session_id` между запросами позволяет продолжать
    разговор.
    """

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    for text in texts:
        text_input = dialogflow.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        if response.query_result.intent.is_fallback:
            logger.info(f'Обнаружен запасной вариант для текста: "{text}"')
            return None
        return response.query_result.fulfillment_text



def send_message(event, vk_api, message):
    """
        Отправляет сообщение пользователю через VK API.

        Параметры:

        event: объект события, содержащий информацию о пользователе.

        vk_api: объект API для взаимодействия с VK.

        message (str): текст сообщения для отправки.
    """

    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        random_id=random.randint(1, 1000)
    )



def main():
    logging.basicConfig(
        level=logging.INFO,  # Устанавливаем уровень логирования
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler()]  # Добавляем StreamHandler
    )

    logger.info('Бот для ВК запущен')

    load_dotenv()
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
    vk_key_api = os.getenv('VK_KEY_API')
    vk_session = vk.VkApi(token=vk_key_api)
    vk_api = vk_session.get_api()

    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            try:
                session_id = str(event.user_id)
                language_code = "ru"
                respond = detect_intent_texts(project_id, session_id, [event.text], language_code)
                if respond:
                    send_message(event, vk_api, respond)
                else:
                    logger.info(f'Бот не понял сообщение от пользователя {event.user_id} и смолчал)')

            except Exception as e:
                logger.error(f'Ошибка при обработке сообщения от пользователя {event.user_id}: {e}')
if __name__ == '__main__':
    main()
