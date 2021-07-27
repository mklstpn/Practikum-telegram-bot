import os
import time
import requests
import telegram
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG, format=(
    '%(asctime)s, %(levelname)s, %(name)s, %(message)s'),
    filename='main.log', filemode='w')

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    logging.debug(f'Homework name - {homework_name}')
    logging.debug(f'Homework status - {homework_status}')
    if homework_status == 'reviewing':
        verdict = 'На проверке.'
    if homework_status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    logging.debug(f'Homework check result - {verdict}')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(
        url, headers=headers, params=payload).json()
    logging.debug(f'Check JSON PRAKTIKUM - {homework_statuses}')
    return homework_statuses


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())
    logging.info('Bot starting')
    logging.info(bot)
    while True:
        try:
            requests.get(
                "https://praktikum.yandex.ru/api/user_api/homework_statuses/")
            logging.info('Server avalible')
            # timestamp for testing 1625764144
            homework = get_homeworks(current_timestamp)
            if len(homework['homeworks']) >= 1:
                homework = homework['homeworks'][0]
                message = parse_homework_status(homework)
                send_message(message)
            else:
                logging.info('Homeworks list is empty')
            time.sleep(5 * 60)

        except Exception as e:
            logging.error(e, exc_info=True)
            time.sleep(5)
            logging.error('Server unavalible')
            send_message('Server unavalible')


if __name__ == '__main__':
    main()
