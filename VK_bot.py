import os
from dotenv import load_dotenv
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
import random


def echo(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=f'Вы отправили мне сообщение с текстом: "{event.text}"',
        random_id=random.randint(1, 1000)
    )


def main():
    load_dotenv()
    vk_key_api = os.getenv('VK_KEY_API')
    vk_session = vk.VkApi(token=vk_key_api)
    vk_api = vk_session.get_api()

    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            echo(event, vk_api)


if __name__ == '__main__':
    main()
