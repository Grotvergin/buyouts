from secret import *
from telebot import TeleBot
from connect import CreateConnectionPool
from telebot.types import BotCommand

# ----- TODO LIST -----
# Запрет на покупку одного бренда одним человеком на две недели
# Оптимизировать код и структуру проекта
# Система хранения медиа в виде дерева по датам


BOT = TeleBot(TOKEN_BOT)
BOT.set_my_commands([BotCommand('/start', 'Начать регистрацию')])
ADM = TeleBot(TOKEN_ADM)
ADM_ID = MY_ID
USER_STATES = {}
REG_STATES = ('sex',
              'name',
              'surname',
              'phone',
              'video',
              'wallet',
              'confirm_name',
              'confirm_phone|{}',
              'manual_phone_input')
SEX_BTNS = ('М 🤵‍♂️', 'Ж 👱‍♀️')
YES_NO_BTNS = ('Да ✅', 'Нет 🚫')
ADM_BTNS = ('🌀 Список неподтвержденных пользователей',)
MENU_BTNS = ('Обновить QR-код 🔄',
             'Мои выкупы 📦',
             'Мои данные ℹ️',
             'Новый выкуп 🛒',
             'Помощь 🆘')
STATUS_BTNS = ('Ожидают выкупа ✔️',
               'Заказанные 🛒',
               'Приехавшие 🗂')
BOUGHT_BTNS = ('Заказал 🛒', 'Отмена 🚫')
BOUGHT_CLBK = ('bou|pos|{}', 'bou|neg|{}')
BOUGHT_TEXT = '🛒 Пора выкупать (инструкция)!\n'
BOUGHT_TIME = 60
ARRIVED_CLBK = ('arr|pos|{}', 'arr|neg|{}')
ARRIVED_TEXT = '❓ Заказ приехал?\n'
ARRIVED_TIME = 60
FOUND_BTNS = ('Беру 📦',)
FOUND_CLBK = ('new',)
FOUND_TEXT = 'Появился новый выкуп 🔉'
FOUND_TIME = 60
QR_BTNS = ('Обновить 🔄',)
QR_CLBK = ('qr',)
QR_TEXT = '⚡️ Нужно обновить QR-код'
QR_TIME = 60
CANCEL_BTN = ('Отмена ❌',)
VALIDATE_BTNS = ('Подтвердить 🟢', 'Отказать 🔴')
VALIDATE_CLBK = ('val|pos|{}|{}|{}|{}', 'val|neg|{}|{}|{}|{}')
ACCEPT_CLBK = ('usr|pos|{}', 'usr|neg|{}')
LONG_SLEEP = 20
MAX_LEN_NAME = 20
MAX_LEN_SURNAME = 25
AWARD_BUYOUT = 80
AWARD_FEEDBACK = 50
WB_WALLET_RATIO = 0.95
TIME_BEFORE_BUYOUT = 5
PENDING_TIME = 60
URL_PRICE = 'https://card.wb.ru/cards/v2/detail'
DIR_MEDIA = 'media'
DRIVE_PATTERN = 'https://drive.google.com/file/d/{}/view?usp=sharing'
WB_PATTERN = 'https://www.wildberries.ru/catalog/{}/detail.aspx'
URL_GET_COORD = 'https://pvz-map-backend.wildberries.ru/api/v1/office/location'
URL_GET_ADDR = 'https://geocode-maps.yandex.ru/1.x'
TIME_FORMAT = "%d.%m.%Y %H:%M"
POOL = CreateConnectionPool()
