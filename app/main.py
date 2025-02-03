import os
import requests
import subprocess
import sys
import logging
import argparse

# Checking the existence of the `vk_api` library
try:
    import vk_api
    from vk_api.longpoll import VkLongPoll, VkEventType

except ImportError:
    print("vk_api не найден. Установка...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "vk_api"])

    import vk_api
    from vk_api.longpoll import VkLongPoll, VkEventType


# Here are the parser arguments added for our application
parser = argparse.ArgumentParser(prog='VK_ChatBot', description='A simple chatbot for VKontakte communities that mocks you with photos')
parser.add_argument('-nv','--no-visual', help="Запуск приложения без визуальной части")
args = parser.parse_args()


# Logger configuration for collecting information about application operation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d-%m-%y %H:%M:%S',
    handlers=[
        logging.FileHandler('VK_Chat_Bot.log', 'a', 'utf-8'), # Here we select a file to save logs
        #logging.StreamHandler() # Here we can uncomment this line and get the log output to the console
    ]
)
logger = logging.getLogger(__name__)


def get_env_variable(var_name):
    """Получение переменной окружения из .env или ввод пользователя"""
    env_path = '../.env'
    value = os.getenv(var_name)

    try:
        if not value and os.path.exists(env_path):
            with open(env_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if line.strip().startswith(f"{var_name}="):
                        value = line.strip().split('=')[1].strip()
                        logger.info(f"Переменная {var_name} загружена из {env_path}")
                        return value

        if not value:
            logger.warning(f"Переменная {var_name} не найдена. Запрашиваем у пользователя.")
            value = input(f"Введите значение для {var_name}: ").strip()

            try:
                with open(env_path, 'a') as file:
                    file.write(f'{var_name}={value}\n')
                    logger.info(f"Переменная {var_name} успешно записана в {env_path}")
            except Exception as e:
                logger.error(f"Ошибка при записи в {env_path}: {e}")

    except FileNotFoundError:
        logger.error(f"Файл {env_path} не найден.")
    except PermissionError:
        logger.error(f"Недостаточно прав для доступа к {env_path}.")
    except Exception as e:
        logger.exception(f"Неожиданная ошибка при работе с {env_path}: {e}")

    return value

# Here we write const variables
# Checking the existence environment variables
try:
    TOKEN = get_env_variable("VK_BOT_TOKEN")
    GROUP_ID = get_env_variable("VK_GROUP_ID")

    if not TOKEN or not GROUP_ID:
        raise ValueError("Обязательные переменные VK_BOT_TOKEN и VK_GROUP_ID не заданы")

except ValueError as e:
    logger.error(f"Ошибка: {e}")
    exit(1)
except Exception as e:
    logger.error(f"Непредвиденная ошибка: {e}")
    exit(1)


# Here we write all the variables that will be used in the program
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


def upload_photo(photo_urls, user_id):
    """Загрузка фото и отправка пользователю"""
    attachments = []

    for photo_url in photo_urls:
        try:
            photo_data = requests.get(photo_url).content
            upload_url = vk.photos.getMessagesUploadServer()["upload_url"]
            response = requests.post(upload_url, files={"photo": ("image.jpg", photo_data, "image/jpeg")}).json()

            if "photo" not in response or "server" not in response or "hash" not in response:
                logger.error(f"Ошибка загрузки фото: {response}")
                continue

            saved_photo = vk.photos.saveMessagesPhoto(
                photo=response["photo"], server=response["server"], hash=response["hash"]
            )[0]

            attachment = f'photo{saved_photo["owner_id"]}_{saved_photo["id"]}'
            attachments.append(attachment)

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка сети при загрузке фото: {e}")
        except Exception as e:
            logger.exception(f"Непредвиденная ошибка при загрузке фотографии: {e}")

    if attachments:
        vk.messages.send(user_id=user_id, attachment=",".join(attachments), random_id=0)
        logger.info(f"Фото успешно прикреплены к сообщению для пользователя {user_id}")
    else:
        logger.warning(f"Не удалось загрузить ни одной фотографии для пользователя {user_id}")


def process_event(event):
    """Обработчик событий для новых сообщений. Идет проверка, является ли сообщение фотографией (содержит ли ее)"""
    try:
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            message_data = vk.messages.getById(message_ids=[event.message_id])["items"][0]
            photo_urls = []

            if "attachments" in message_data and message_data["attachments"]:
                for attachment in message_data["attachments"]:
                    if attachment["type"] == "photo":
                        largest_photo = max(attachment["photo"]["sizes"], key=lambda x: x["width"])
                        photo_urls.append(largest_photo["url"])

                if photo_urls:
                    upload_photo(photo_urls, user_id)

                logger.info(f"Событие с отправкой фотографий выполнено успешон для пользователя {user_id}")


    except KeyError as e:
        logger.error(f"Ошибка KeyError: {e}")
    except Exception as e:
        logger.exception(f"Неизвестная ошибка при обработке события: {e}")


def main():
    logger.info("Бот запущен")
    for event in longpoll.listen():
        process_event(event)


if __name__ == "__main__":
    main()