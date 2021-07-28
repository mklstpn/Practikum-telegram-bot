import logging
import os
import time
import datetime as dt

import requests
import telegram
from dotenv import load_dotenv


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

BOT = telegram.Bot(token=TELEGRAM_TOKEN)
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
VERDICTS = {'reviewing': 'На проверке.',
            'rejected': 'К сожалению, в работе нашлись ошибки.',
            'approved': 'Ревьюеру всё понравилось, работа зачтена!'}
ANSWER_TEXT = 'У вас проверили работу "{name}"!\n\n{verdict}'
BOT_START_MSG = 'Bot started'
NO_HOMEWORKS_MSG = 'Homeworks list is empty'
ERROR_MSG = 'Error: '


def parse_homework_status(homework):
    name = homework.get('homework_name')
    status = homework.get('status')
    try:
        verdict = VERDICTS[status]
    except ValueError as value_error:
        raise ValueError(ERROR_MSG + str(value_error))
    return ANSWER_TEXT.format(name=name, verdict=verdict)


def get_homeworks(current_timestamp):
    payload = {'from_date': current_timestamp}
    try:
        homework_get = requests.get(
            URL, headers=HEADERS, params=payload)
    except requests.exceptions.RequestException as request_error:
        raise ConnectionError(ERROR_MSG + str(request_error))
    homework_statuses = homework_get.json()
    # Но в получаемом JSON'e ведь нет ни "code" ни "error".
    # Или в чем-то подвох?
    return homework_statuses


def send_message(message):
    return BOT.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())

    logging.info(BOT_START_MSG)
    logging.info(BOT)
    while True:
        try:
            # timestamp for testing 1625764144
            homework = get_homeworks(current_timestamp)
            if len(homework['homeworks']) >= 1:
                homework = homework['homeworks'][0]
                current_timestamp = homework.get(
                    'current_date', int(time.time()))
                send_message(parse_homework_status(homework))
            else:
                logging.info(NO_HOMEWORKS_MSG)
            time.sleep(5 * 60)

        except Exception as error:
            logging.error(ERROR_MSG + str(error), exc_info=True)
            try:
                send_message(ERROR_MSG + str(error))
            except ConnectionError as connect_error:
                logging.error(ERROR_MSG + str(connect_error))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format=(
        '%(asctime)s, %(levelname)s, %(name)s, %(message)s'),
        filename=(__file__ + '.log'), filemode='w')
    main()
