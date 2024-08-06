from common import ShowButtons, Stamp, InlineButtons, FormatTime, Sleep
from source import (BOT, ADM, MENU_BTNS, CANCEL_BTN, BOUGHT_BTNS,
                    ADM_BTNS, POOL, ADM_ID, TIME_BEFORE_BUYOUT,
                    PENDING_TIME, AWARD_BUYOUT, AWARD_FEEDBACK,
                    STATUS_BTNS, WB_PATTERN)
from telebot.types import Message, CallbackQuery
from registration import AcceptNewUser, ShowUserInfo
from management import ShowAvailableBuyouts, AfterOrder
from threading import Thread
from telebot import TeleBot
from traceback import format_exc
from qr import RefreshQR, FindOutDateQR
from connect import GetConCur


@ADM.message_handler(content_types=['text'])
def AdminHandler(message: Message) -> None:
    Stamp(f'Admin {message.from_user.id} requested {message.text}', 'i')
    if message.text == '/start':
        ADM.send_message(message.from_user.id, f'🥹 Здравствуйте, администратор {message.from_user.username}!'
                                               ' Сюда будут приходить уведомления о новых пользователях...')
        ShowButtons(ADM, message.from_user.id, ADM_BTNS, '❔ Выберите действие:')
    elif message.text == ADM_BTNS[0]:
        ShowUnconfirmedUsers()
    ShowButtons(ADM, message.from_user.id, ADM_BTNS, '❔ Выберите действие:')


@ADM.callback_query_handler(func=lambda call: call.data.startswith('accept_'))
def HandleAcceptUser(call: CallbackQuery) -> None:
    user_id = call.data.split('_')[1]
    try:
        with GetConCur(POOL) as (con, cur):
            cur.execute("UPDATE users SET conf_time = NOW() WHERE id = %s", (user_id,))
            con.commit()
            Stamp(f'User {user_id} accepted', 'i')
            BOT.send_message(user_id, '✅ Ваши данные подтверждены!')
            ADM.send_message(call.message.chat.id, f'✅ Пользователь {user_id} успешно принят!')
    except Exception as e:
        ADM.send_message(call.message.chat.id, '⚠️ Произошла ошибка при подтверждении пользователя!')
        Stamp(f'Error while handling accept callback: {str(e)}', 'e')


@ADM.callback_query_handler(func=lambda call: call.data.startswith('reject_'))
def HandleRejectUser(call: CallbackQuery) -> None:
    user_id = call.data.split('_')[1]
    try:
        Stamp(f'User {user_id} rejected', 'i')
        BOT.send_message(user_id, '❌ Ваши данные отклонены!')
        ADM.send_message(call.message.chat.id, f'❌ Пользователь {user_id} отклонен!')
    except Exception as e:
        ADM.send_message(call.message.chat.id, '⚠️ Произошла ошибка при отклонении пользователя!')
        Stamp(f'Error while handling reject callback: {str(e)}', 'e')


def ShowUnconfirmedUsers() -> None:
    with GetConCur(POOL) as (con, cur):
        cur.execute('SELECT id FROM users WHERE conf_time IS NULL')
        users = cur.fetchall()
        if not users:
            ADM.send_message(ADM_ID, '⚠️ Нет неподтвержденных пользователей!')
            return
        for user in users:
            InlineButtons(ADM, ADM_ID, ['✅ Принять', '❌ Отклонить'], ShowUserInfo(user[0]),
                          [f'accept_{user[0]}', f'reject_{user[0]}'])


@BOT.message_handler(commands=['start'])
def Start(message: Message) -> None:
    Stamp(f'User {message.from_user.id} is starting', 'i')
    AcceptNewUser(message)


@BOT.message_handler(content_types=['text'])
def MessageHandler(message: Message) -> None:
    Stamp(f'User {message.from_user.id} requested {message.text}', 'i')
    if message.text == MENU_BTNS[0]:
        ShowButtons(BOT, message.from_user.id, CANCEL_BTN, f'🔁 Последний раз QR-код был обновлён: '
                                                           f'{FindOutDateQR(message.from_user.id)}\n'
                                                           f'Загрузите изображение с новым QR-кодом...')
        BOT.register_next_step_handler(message, RefreshQR)
    elif message.text == MENU_BTNS[1]:
        ShowButtons(BOT, message.from_user.id, STATUS_BTNS, '❔ Выберите статус:')
    elif message.text == MENU_BTNS[2]:
        BOT.send_message(message.from_user.id, ShowUserInfo(message.from_user.id))
        ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')
    elif message.text == MENU_BTNS[3]:
        ShowAvailableBuyouts(message)
    elif message.text == BOUGHT_BTNS[0]:
        # ShowButtons(BOT, 729516819, BOUGHT_BTNS, text)
        BOT.register_next_step_handler(message, AfterOrder, 2, 123456789)
    else:
        BOT.send_message(message.from_user.id, '❌ Неизвестная команда...')
        ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')


def PendingBuyouts() -> None:
    while True:
        with GetConCur(POOL) as (con, cur):
            cur.execute("""
                        SELECT user_id, plan_time, pick_point_id, 
                        feedback, good_link, request, buyouts.id
                        FROM buyouts
                        JOIN plans ON buyouts.plan_id = plans.id
                        WHERE user_id IS NOT NULL
                        AND fact_time IS NULL
                        AND plan_time > NOW()
                        """, (TIME_BEFORE_BUYOUT,))
            buyouts = cur.fetchall()
        if not buyouts:
            return
        for buyout in buyouts:
            text = 'Пора выкупать (инструкция) ! 🛒\n'
            award = AWARD_BUYOUT
            if buyout[1]:
                text += f'🕘 Планируемое время выкупа: {FormatTime(buyout[1])}\n'
            if buyout[2]:
                text += f'📍 ID ПВЗ (скоро адрес): {buyout[2]}\n'
            if buyout[3]:
                text += f'🧨 Отзыв : {FormatTime(buyout[3])}\n'
                award += AWARD_FEEDBACK
            if buyout[4]:
                text += f'🔗 Ссылка на товар: {WB_PATTERN.format(buyout[4])}\n'
            if buyout[5]:
                text += f'📝 Запрос: {buyout[5]}\n'
            text += f'🎁 Вознаграждение: {award} руб.'
            ShowButtons(BOT, buyout[0], BOUGHT_BTNS, text)
            # BOT.register_next_step_handler(buyout[0], AfterOrder, buyout[6], buyout[4])
        Sleep(PENDING_TIME)


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
    t3 = Thread(target=PendingBuyouts)
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()


if __name__ == '__main__':
    Main()
