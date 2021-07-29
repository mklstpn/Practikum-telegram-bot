import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
VERDICTS = {'reviewing': 'На проверке.',
            'rejected': 'К сожалению, в работе нашлись ошибки.',
            'approved': 'Ревьюеру всё понравилось, работа зачтена!'}
ANSWER_TEXT = 'У вас проверили работу "{name}"!\n\n{verdict}'
BOT_START = 'Bot started'
NO_HOMEWORKS = 'Homeworks list is empty'
KEY_ERROR = 'Got undefined status from API: {status}'
NETWORK_ERROR = (
    'Network error: {error}\n\nURL: {url}\nHeader: {headers}\nParams: {params}'
)
JSON_ERROR = (
    'Server error: {error}\n\nURL: {url}\nHeader: {headers}\nParams: {params}')
TELEGRAM_ERROR = 'Error while trying to send message telegram bot: {error}'
ERROR = 'Error: {error}'
HELLO_TEXT = 'Hello'


def parse_homework_status(homework):
    status = homework['status']
    if status not in VERDICTS:
        raise ValueError(KEY_ERROR.format(status=status))
    return ANSWER_TEXT.format(name=homework['homework_name'],
                              verdict=VERDICTS[status])


def get_homeworks(current_timestamp):
    payload = {'from_date': current_timestamp}
    request_data = dict(url=URL, headers=HEADERS, params=payload)
    try:
        homework_get = requests.get(**request_data)
    except requests.exceptions.RequestException as request_error:
        raise ConnectionError(NETWORK_ERROR.format(
            error=request_error, **request_data))
    homework_statuses = homework_get.json()
    error_keys = ['code', 'error']
    for error in error_keys:
        if error in homework_statuses:
            raise RuntimeError(JSON_ERROR.format(
                error=homework_statuses[error], **request_data))
    return homework_statuses


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())

    logging.info(BOT_START)
    logging.info(bot)
    bot.send_message(CHAT_ID, HELLO_TEXT)
    while True:
        try:
            # timestamp for testing 1625764144
            homework = get_homeworks(current_timestamp)
            if len(homework['homeworks']) >= 1:
                current_timestamp = homework.get(
                    'current_date', current_timestamp)
                send_message(parse_homework_status(homework['homeworks'][0]))
            else:
                logging.info(NO_HOMEWORKS)
            time.sleep(5 * 60)

        except Exception as error:
            logging.error(ERROR.format(error=error), exc_info=True)
            try:
                send_message(ERROR.format(error=error))
            except Exception as send_error:
                logging.error(TELEGRAM_ERROR.format(error=send_error))
            # чтобы сообщения не валились кучей
            time.sleep(5 * 60)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format=(
        '%(asctime)s, %(levelname)s, %(name)s, %(message)s'),
        filename=(__file__ + '.log'), filemode='w')
    main()
