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
from time import sleep
from random import randint
from os import remove

# Формат времени
# Убрать qr код ссылку
# Адрес сделать в момент заказа
# Подтягивать цену с вб в момент покупки
# Обновление qr кодов при доставке/с утра
# Уведомление (обновите куар, появился новый выкуп)
# Загрузка видео (верификация в обработке)
# Инструкция в закрепленное сообщение
# убрать ссылку в доступных выкупах
# статус убрать
# вторая кнопка беру, в начале избранных ее нет
# Наташа 100 метров от вас когда не активный юзер
# не запрещать выкупать, а просто не выдавать


BOT = TeleBot(TOKEN)
USER_STATES = {}
STATES = ('sex',
          'name',
          'surname',
          'phone',
          'city',
          'video',
          'wallet')
SEX_BTNS = ('М 🤵‍♂️', 'Ж 👱‍♀️')
WALLET_BTNS = ('Да ✅', 'Нет 🚫')
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
STATUSES_AND_BTNS = {'🔴 Не распределён': ('Беру!', 'choose_'),
                     '🟠 В избранном': ('Заказал!', 'order_'),
                     '🟡 Выкуплен': ('Приехал!', 'arrive_'),
                     '🟢 Доставлен': ('Забрал!', 'pickup_'),
                     '🔵 Забран': ('Оценить!', 'feedback_')}
STATUSES = tuple(STATUSES_AND_BTNS.keys())
CALLBACKS = tuple([btn[1] for btn in STATUSES_AND_BTNS.values()])


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


def ShowButtons(message: Message, buttons: tuple, answer: str) -> None:
    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    if len(buttons) % 2 == 0:
        for i in range(0, len(buttons), 2):
            row_buttons = buttons[i:i + 2]
            markup.row(*[KeyboardButton(btn) for btn in row_buttons])
    else:
        for i in range(0, len(buttons) - 1, 2):
            row_buttons = buttons[i:i + 2]
            markup.row(*[KeyboardButton(btn) for btn in row_buttons])
        markup.row(KeyboardButton(buttons[-1]))
    BOT.send_message(message.from_user.id, answer, reply_markup=markup, parse_mode='Markdown')


def InlineButtons(message: Message, buttons: tuple, answer: str, clbk_data: str = None) -> None:
    markup = InlineKeyboardMarkup()
    for btn in buttons:
        markup.add(InlineKeyboardButton(btn, callback_data=clbk_data + btn))
    BOT.send_message(message.from_user.id, answer, reply_markup=markup, parse_mode='Markdown')


def Sleep(timer: int, ratio: float = 0.0) -> None:
    rand_time = randint(int((1 - ratio) * timer), int((1 + ratio) * timer))
    Stamp(f'Sleeping {rand_time} seconds', 'l')
    sleep(rand_time)
