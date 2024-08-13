from common import (ShowButtons, Stamp, InlineButtons,
                    FormatTime, Sleep, FormatCallback,
                    GetPriceGood)
from source import (BOT, ADM, MENU_BTNS, CANCEL_BTN, BOUGHT_BTNS,
                    ADM_BTNS, POOL, ADM_ID, AWARD_BUYOUT, AWARD_FEEDBACK,
                    STATUS_BTNS, WB_PATTERN, BOUGHT_CLBK, BOUGHT_TEXT, BOUGHT_TIME,
                    ARRIVED_CLBK, ARRIVED_TEXT, YES_NO_BTNS, ARRIVED_TIME,
                    FOUND_BTNS, FOUND_CLBK, FOUND_TEXT, FOUND_TIME)
from telebot.types import Message, CallbackQuery
from registration import AcceptNewUser, ShowUserInfo
from management import (ShowAvailableBuyouts, AcceptHistory,
                        AssignBuyout, ShowMyBuyouts)
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


@ADM.callback_query_handler(func=lambda call: call.data.startswith('accept|'))
def HandleAcceptUser(call: CallbackQuery) -> None:
    user_id = call.data.split('|')[1]
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
            InlineButtons(ADM, ADM_ID, ('✅ Принять', '❌ Отклонить'), ShowUserInfo(user[0]),
                          (f'accept_{user[0]}', f'reject_{user[0]}'))


@BOT.message_handler(commands=['start'])
def Start(message: Message) -> None:
    Stamp(f'User {message.from_user.id} is trying to register', 'i')
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
        BOT.register_next_step_handler(message, ShowMyBuyouts)
    elif message.text == MENU_BTNS[2]:
        BOT.send_message(message.from_user.id, ShowUserInfo(message.from_user.id))
        ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')
    elif message.text == MENU_BTNS[3]:
        ShowAvailableBuyouts(message)
    else:
        BOT.send_message(message.from_user.id, '❌ Неизвестная команда...')
        ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')


def SendNotification(query: str, text_template: str, buttons: tuple, clbk_data: tuple, interval: int) -> None:
    while True:
        text = text_template
        Stamp(f'Pending notifications for {text}', 'i')
        with GetConCur(POOL) as (con, cur):
            cur.execute(query)
            buyouts = cur.fetchall()
        for one in buyouts:
            award = AWARD_BUYOUT
            if one[1]:
                text += f'🕘 Планируемое время выкупа: {FormatTime(one[1])}\n'
            if one[2]:
                text += f'📍 ID ПВЗ (скоро адрес): {one[2]}\n'
            if one[3]:
                text += f'🧨 Отзыв: {one[3]}\n'
                award += AWARD_FEEDBACK
            if one[4]:
                text += f'🔗 Ссылка на товар: {WB_PATTERN.format(one[4])}\n'
            if one[5]:
                text += f'📝 Запрос: {one[5]}\n'
            text += f'🎁 Вознаграждение: {award} ₽'
            InlineButtons(BOT, one[0], buttons, text, FormatCallback(clbk_data, (one[6],)))
        Sleep(interval)


@BOT.callback_query_handler(func=lambda call: call.data.startswith('bou|'))
def ConfirmBuyout(call: CallbackQuery) -> None:
    _, decision, buyout_id = call.data.split('|')
    with GetConCur(POOL) as (con, cur):
        if decision == 'pos':
            Stamp(f'User {call.from_user.id} confirmed buyout {buyout_id}', 'i')
            cur.execute('SELECT p.good_link FROM buyouts AS b JOIN plans AS p ON p.id = b.plan_id WHERE b.id = %s', (buyout_id,))
            barcode = cur.fetchone()[0]
            cur.execute('UPDATE buyouts SET fact_time = NOW(), price = %s WHERE id = %s', (GetPriceGood(barcode), buyout_id))
            con.commit()
            message = BOT.send_message(call.from_user.id, 'Отправьте фото истории просмотров 💾')
            BOT.register_next_step_handler(message, AcceptHistory, buyout_id)
        else:
            Stamp(f'User {call.from_user.id} rejected buyout {buyout_id}', 'i')
            cur.execute('UPDATE buyouts SET user_id = NULL, plan_time = NULL WHERE id = %s', (buyout_id,))
            con.commit()
            BOT.send_message(call.from_user.id, '❌ Отмена выкупа!')
            ShowButtons(BOT, call.from_user.id, MENU_BTNS, '❔ Выберите действие:')


@BOT.callback_query_handler(func=lambda call: call.data.startswith('arr|'))
def ConfirmArrival(call: CallbackQuery) -> None:
    _, decision, buyout_id = call.data.split('|')
    with GetConCur(POOL) as (con, cur):
        if decision == 'pos':
            Stamp(f'User {call.from_user.id} confirmed arrival of buyout {buyout_id}', 'i')
            cur.execute('UPDATE buyouts SET delivery_time = NOW() WHERE id = %s', (buyout_id,))
            con.commit()
            BOT.send_message(call.from_user.id, '✅ Спасибо за подтверждение! Нужно отправить фото????')

        else:
            Stamp(f'User {call.from_user.id} rejected arrival of buyout {buyout_id}', 'i')
            BOT.send_message(call.from_user.id, 'Увынск!')
            ShowButtons(BOT, call.from_user.id, MENU_BTNS, '❔ Выберите действие:')


@BOT.callback_query_handler(func=lambda call: call.data.startswith('new|'))
def NewBuyout(call: CallbackQuery) -> None:
    _, buyout_id = call.data.split('|')
    with GetConCur(POOL) as (con, cur):
        cur.execute('SELECT plan_time FROM buyouts WHERE id = %s', (buyout_id,))
    planned_time = cur.fetchone()[0]
    AssignBuyout(call.from_user.id, buyout_id, planned_time)


@ADM.callback_query_handler(func=lambda call: call.data.startswith('val|'))
def ValidateMedia(call: CallbackQuery) -> None:
    _, decision, table, column, id = call.data.split('|')
    if decision == 'pos':
        Stamp(f'Admin {call.from_user.id} accepted media {id}', 'i')
        ADM.send_message(call.message.chat.id, '✅ Подтверждено!')
    else:
        Stamp(f'Admin {call.from_user.id} rejected media {id}', 'i')
        ADM.send_message(call.message.chat.id, '❌ Отклонено!')
        with GetConCur(POOL) as (con, cur):
            cur.execute(f'UPDATE {table} SET {column} = NULL WHERE id = %s', (id,))
            con.commit()


def RunBot(bot: TeleBot):
    while True:
        try:
            bot.polling(none_stop=True, interval=1)
        except Exception as e:
            Stamp(f'{e}', 'e')
            Stamp(format_exc(), 'e')


def Main():
    notif_order = Thread(target=SendNotification,
                         args=('SELECT * FROM notif_order',
                               BOUGHT_TEXT,
                               BOUGHT_BTNS,
                               BOUGHT_CLBK,
                               BOUGHT_TIME))
    notif_arrive = Thread(target=SendNotification,
                          args=('SELECT * FROM notif_arrive',
                                ARRIVED_TEXT,
                                YES_NO_BTNS,
                                ARRIVED_CLBK,
                                ARRIVED_TIME))
    notif_found = Thread(target=SendNotification,
                         args=('SELECT * FROM notif_found',
                               FOUND_TEXT,
                               FOUND_BTNS,
                               FOUND_CLBK,
                               FOUND_TIME))
    threads = (Thread(target=RunBot, args=(BOT,)),
               Thread(target=RunBot, args=(ADM,)),
               notif_order,
               notif_arrive,)
               # notif_found)
    for t in threads:
        t.start()
        Sleep(2)
    for t in threads:
        t.join()


if __name__ == '__main__':
    Main()
