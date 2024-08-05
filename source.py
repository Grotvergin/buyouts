from secret import *
from telebot import TeleBot
from connect import CreateConnectionPool

# ----- TODO LIST -----
# Вывод доступных выводов
# Вывод моих выкупов
# Адрес сделать в момент заказа
# Уведомления (обновите куар [доставка/с утра], появился новый выкуп)
# Ограничения (один бренд в течение получаса, один человек две недели одного бренда)
# Предложение при реге автозаполнение
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
WALLET_BTNS = ('Да ✅', 'Нет 🚫')
ADM_BTNS = ('🌀 Список неподтвержденных пользователей',)
MENU_BTNS = ('Обновить QR-код 🔄',
             'Мои выкупы 📦',
             'Мои данные ℹ️',
             'Новый выкуп 🛒',)
STATUS_BTNS = ('Избранные ✔️',
               'Заказанные 🛒',
               'Приехавшие 🚚',
               'Забранные 📤',
               'Мои выкупы 🗂',
               ' ️Мои данные ℹ️')
CANCEL_BTN = ('Отмена ❌',)
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
TIME_FORMAT = "%d.%m.%Y %H:%M"
POOL = CreateConnectionPool()
