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

bot = telegram.Bot(token=TELEGRAM_TOKEN)
url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
statuses = {'reviewing': 'На проверке.',
            'rejected': 'К сожалению, в работе нашлись ошибки.',
            'approved': 'Ревьюеру всё понравилось, работа зачтена!'}
ANSWER_TEXT = 'У вас проверили работу "{name_key}"!\n\n{verdict_key}'


def parse_homework_status(homework):
    name = homework.get('homework_name')
    status = homework.get('status')
    logging.debug(f'Homework name - {name}')
    logging.debug(f'Homework status - {status}')
    try:
        verdict = statuses[status]
    except KeyError:
        raise KeyError('Got unkown status')
    logging.debug(f'Homework check result - {verdict}')
    return ANSWER_TEXT.format(name_key=name, verdict_key=verdict)


def get_homeworks(current_timestamp):
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            url, headers=headers, params=payload).json()
    except ConnectionError:
        raise ConnectionError('Connection error')
    except TypeError:
        raise TypeError('Got wrong data')
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
            # timestamp for testing 1625764144
            current_timestamp = current_timestamp or int(time.time())
            homework = get_homeworks(current_timestamp)
            if len(homework['homeworks']) >= 1:
                homework = homework['homeworks'][0]
                current_timestamp = homework.get('date_updated')
                current_timestamp = time.mktime(
                    dt.datetime.strptime(
                        current_timestamp, "%Y-%m-%dT%H:%M:%SZ").timetuple())
                message = parse_homework_status(homework)
                send_message(message)
            else:
                logging.info('Homeworks list is empty')
            time.sleep(5 * 60)

        except Exception as error:
            logging.error('Error: ' + str(error), exc_info=True)
            time.sleep(5 * 60)
            try:
                send_message('Bot died. You need to help him.')
            except ConnectionError:
                logging.error('Message not sent')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format=(
        '%(asctime)s, %(levelname)s, %(name)s, %(message)s'),
        filename=(__file__ + '.log'), filemode='w')
    main()
