from secret import *
from telebot import TeleBot
from connect import CreateConnectionPool

# ----- TODO LIST -----
# Обработчики событий коллбэков
# Адрес сделать в момент заказа
# Запрет на покупку одного бренда одним человеком на две недели
# Предложение при регистрации автозаполнение
# Редактировать профиль возможность


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
YES_NO_BTNS = ('Да ✅', 'Нет 🚫')
ADM_BTNS = ('🌀 Список неподтвержденных пользователей',)
MENU_BTNS = ('Обновить QR-код 🔄',
             'Мои выкупы 📦',
             'Мои данные ℹ️',
             'Новый выкуп 🛒',)
STATUS_BTNS = ('Ожидают выкупа ✔️',
               'Заказанные 🛒',
               'Приехавшие 🗂')
BOUGHT_BTNS = ('Заказал 🛒', 'Отмена 🚫')
BOUGHT_CLBK = ('ord_{}', 'del_{}')
BOUGHT_TEXT = 'Пора выкупать (инструкция)! 🛒\n'
BOUGHT_TIME = 60
ARRIVED_CLBK = ('arr_{}', 'los_{}')
ARRIVED_TEXT = '❓ Заказ приехал?'
ARRIVED_TIME = 60
FOUND_BTNS = ('Беру 📦',)
FOUND_CLBK = ('usr_{}_tks_{}',)
FOUND_TEXT = 'Появился новый выкуп 🔉'
FOUND_TIME = 60
CANCEL_BTN = ('Отмена ❌',)
VALIDATE_BTNS = ('Подтвердить 🟢', 'Отказать 🔴')
VALIDATE_CLBK = ('acc_table_{}_field_{}_id_{}_user_{}',
                 'rej_table_{}_field_{}_id_{}_user_{}')
ACCEPT_CLBK = ('accept_{}', 'reject_{}')
LONG_SLEEP = 20
MAX_LEN_NAME = 20
MAX_LEN_SURNAME = 25
AWARD_BUYOUT = 80
AWARD_FEEDBACK = 50
WB_WALLET_RATIO = 0.95
TIME_BEFORE_BUYOUT = 5
PENDING_TIME = 60
URL = 'https://card.wb.ru/cards/v2/detail'
DIR_MEDIA = 'media'
DRIVE_PATTERN = 'https://drive.google.com/file/d/{}/view?usp=sharing'
WB_PATTERN = 'https://www.wildberries.ru/catalog/{}/detail.aspx'
TIME_FORMAT = "%d.%m.%Y %H:%M"
POOL = CreateConnectionPool()
