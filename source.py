from secret import *
from colorama import Fore, Style, init
from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime
from traceback import format_exc
from psycopg2 import connect
from re import match
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from ssl import SSLEOFError
from socket import gaierror
from httplib2.error import ServerNotFoundError
from googleapiclient.discovery import Resource, build
from google.oauth2.service_account import Credentials
from time import sleep, strptime, strftime
from random import randint
from os import remove
from threading import Thread
from requests import get, ConnectionError

# товары одного бренда в течение получаса
# один человек две недели одного бренда
# Адрес сделать в момент заказа
# Обновление qr кодов при доставке/с утра
# Уведомление (обновите куар, появился новый выкуп)
# вторая кнопка беру, в начале избранных ее нет
# Наташа 100 метров от вас когда не активный юзер
# не запрещать выкупать, а просто не выдавать
# информация о пвз по id
# предложение номера телефона и др
# редактировать профиль возможность


BOT = TeleBot(TOKEN_BOT)
ADM = TeleBot(TOKEN_ADM)
USER_STATES = {}
REG_STATES = ('sex',
              'name',
              'surname',
              'phone',
              'video',
              'wallet')
SEX_BTNS = ('М 🤵‍♂️', 'Ж 👱‍♀️')
WALLET_BTNS = ('Да ✅', 'Нет 🚫')
ADM_BTNS = ('🌀 Список неподтвержденных пользователей',)
MENU_BTNS = ('Доступные 💭',
             'Избранные ✔️',
             'Заказанные 🛒',
             'Приехавшие 🚚',
             'Забранные 📤',
             'Мои выкупы 🗂',
             ' ️Мои данные ℹ️')
CREDS = Credentials.from_service_account_file('keys.json', scopes=['https://www.googleapis.com/auth/drive.file'])
LONG_SLEEP = 20
MAX_LEN_NAME = 20
MAX_LEN_SURNAME = 25
AWARD_BUYOUT = 80
AWARD_FEEDBACK = 50
WB_WALLET_RATIO = 0.95
STATUSES_AND_BTNS = {'🔴 Не распределён': ('Беру!', 'choose_'),
                     '🟠 В избранном': ('Заказал!', 'order_'),
                     '🟡 Выкуплен': ('Приехал!', 'arrive_'),
                     '🟢 Доставлен': ('Забрал!', 'pickup_'),
                     '🔵 Забран': ('Оценить!', 'feedback_')}
STATUSES = tuple(STATUSES_AND_BTNS.keys())
CALLBACKS = tuple([btn[1] for btn in STATUSES_AND_BTNS.values()])
URL = 'https://card.wb.ru/cards/v2/detail'
DRIVE_PATTERN = 'https://drive.google.com/file/d/{}/view?usp=sharing'
WB_PATTERN = 'https://www.wildberries.ru/catalog/{}/detail.aspx'


def GetPriceGood(barcode: int) -> int:
    Stamp(f'Trying to get price for barcode: {barcode}', 'i')
    raw = GetDataWhileNotCorrect(barcode, 3)
    if raw:
        Stamp(f'Got price for barcode: {barcode}', 's')
        price = raw['data']['products'][0]['sizes'][0]['price']['total']
        price = round((float(price) / 100 * WB_WALLET_RATIO))
        return price
    else:
        Stamp(f'Failed to get price for barcode: {barcode}', 'e')
        return 0


def GetDataWhileNotCorrect(barcode: int, max_attempts: int) -> dict | None:
    attempts = 0
    while attempts < max_attempts:
        raw_data = GetData(barcode)
        if BarcodeIsValid(raw_data):
            return raw_data
        attempts += 1
        Stamp(f'Attempt {attempts} failed, retrying', 'w')
    Stamp(f'Exceeded maximum attempts ({max_attempts}) for barcode: {barcode}', 'e')
    return


def BarcodeIsValid(raw: dict) -> bool:
    if 'data' in raw and 'products' in raw['data'] and raw['data']['products']:
        if 'sizes' in raw['data']['products'][0] and raw['data']['products'][0]['sizes']:
            if raw['data']['products'][0]['sizes'][0] and 'price' in raw['data']['products'][0]['sizes'][0]:
                if raw['data']['products'][0]['sizes'][0]['price'] and 'total' in raw['data']['products'][0]['sizes'][0]['price']:
                    if raw['data']['products'][0]['sizes'][0]['price']['total']:
                        return True
    return False


def GetData(barcode: int) -> dict:
    Stamp(f'Trying to connect {URL}', 'i')
    HEADERS['Referer'] = f'https://www.wildberries.ru/catalog/{barcode}/detail.aspx'
    PARAMS['nm'] = barcode
    try:
        response = get(URL, params=PARAMS, headers=HEADERS)
    except ConnectionError:
        Stamp(f'Connection on {URL}', 'e')
        Sleep(LONG_SLEEP)
        raw = GetData(barcode)
    else:
        if str(response.status_code)[0] == '2':
            Stamp(f'Status = {response.status_code} on {URL}', 's')
            if response.content:
                raw = response.json()
            else:
                Stamp('Response is empty', 'w')
                raw = {}
        else:
            Stamp(f'Status = {response.status_code} on {URL}', 'e')
            Sleep(LONG_SLEEP)
            raw = GetData(barcode)
    return raw


def AuthorizeDatabase():
    conn = connect(
        dbname=DB_NAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )
    cursor = conn.cursor()
    return cursor, conn


def RunBot(bot: TeleBot):
    while True:
        try:
            bot.polling(none_stop=True, interval=1)
        except Exception as e:
            Stamp(f'{e}', 'e')
            Stamp(format_exc(), 'e')


def Main():
    t1 = Thread(target=RunBot, args=(BOT,))
    t2 = Thread(target=RunBot, args=(ADM,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()


def BuildService() -> Resource:
    Stamp(f'Trying to build service', 'i')
    try:
        service = build('drive', 'v3', credentials=CREDS)
    except (HttpError, TimeoutError, ServerNotFoundError, gaierror, SSLEOFError) as err:
        Stamp(f'Status = {err} on building service', 'e')
        Sleep(LONG_SLEEP)
        BuildService()
    else:
        Stamp('Built service successfully', 's')
        return service


def Stamp(message: str, level: str) -> None:
    time_stamp = datetime.now().strftime('[%m-%d|%H:%M:%S]')
    match level:
        case 'i':
            print(Fore.LIGHTBLUE_EX + time_stamp + '[INF] ' + message + '.' + Style.RESET_ALL)
        case 'w':
            print(Fore.LIGHTMAGENTA_EX + time_stamp + '[WAR] ' + message + '!' + Style.RESET_ALL)
        case 's':
            print(Fore.LIGHTGREEN_EX + time_stamp + '[SUC] ' + message + '.' + Style.RESET_ALL)
        case 'e':
            print(Fore.RED + time_stamp + '[ERR] ' + message + '!!!' + Style.RESET_ALL)
        case 'l':
            print(Fore.WHITE + time_stamp + '[SLE] ' + message + '...' + Style.RESET_ALL)
        case 'b':
            print(Fore.LIGHTYELLOW_EX + time_stamp + '[BOR] ' + message + '.' + Style.RESET_ALL)
        case _:
            print(Fore.WHITE + time_stamp + '[UNK] ' + message + '?' + Style.RESET_ALL)


def ShowButtons(bot: TeleBot, message: Message, buttons: tuple, answer: str) -> None:
    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    if len(buttons) % 3 == 0:
        row_size = 3
    elif len(buttons) % 2 == 0:
        row_size = 2
    else:
        row_size = 1
    for i in range(0, len(buttons), row_size):
        row_buttons = buttons[i:i + row_size]
        markup.row(*[KeyboardButton(btn) for btn in row_buttons])
    bot.send_message(message.from_user.id, answer, reply_markup=markup, parse_mode='Markdown')


def InlineButtons(bot: TeleBot, user_id: int, buttons: list, answer: str, clbk_data: list) -> None:
    markup = InlineKeyboardMarkup()
    if len(buttons) % 3 == 0:
        row_size = 3
    elif len(buttons) % 2 == 0:
        row_size = 2
    else:
        row_size = 1
    for i in range(0, len(buttons), row_size):
        row_buttons = [InlineKeyboardButton(btn, callback_data=clbk_data[j]) for j, btn in enumerate(buttons[i:i + row_size], start=i)]
        markup.row(*row_buttons)
    bot.send_message(user_id, answer, reply_markup=markup, parse_mode='Markdown')


def Sleep(timer: int, ratio: float = 0.0) -> None:
    rand_time = randint(int((1 - ratio) * timer), int((1 + ratio) * timer))
    Stamp(f'Sleeping {rand_time} seconds', 'l')
    sleep(rand_time)
