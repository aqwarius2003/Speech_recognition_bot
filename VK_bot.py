import os
from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import random


def main():
    load_dotenv()
    vk_key_api = os.getenv('VK_KEY_API')
    vk_session = vk_api.VkApi(token=vk_key_api)
    vk = vk_session.get_api()

    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            print('Новое сообщение:')
            if event.to_me:
                print('Для меня от: ', event.user_id)
            else:
                print('От меня для: ', event.user_id)
            print('Текст:', event.text)

            # # Отправка ответа
            # vk.messages.send(
            #     peer_id=event.peer_id,
            #     message=f'Ваше сообщение {event.text} получено!',
            #     random_id=random.randint(1, 1e6)
            # )


if __name__ == '__main__':
    main()