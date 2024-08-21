from common import FormatTime, ShowButtons
from telebot.types import Message, CallbackQuery
from common import Stamp, HandlePhoto, GetPositionByOffice
from connect import GetConCur
from source import (BOT, STATUS_BTNS, MENU_BTNS,
                    POOL, TIME_BEFORE_BUYOUT, WB_PATTERN)


def ShowAvailableBuyouts(message: Message | CallbackQuery) -> None:
    with GetConCur(POOL) as (con, cur):
        cur.execute('SELECT conf_time FROM users WHERE id = %s', (message.from_user.id,))
        conf_time = cur.fetchone()[0]
        if not conf_time:
            BOT.send_message(message.from_user.id, '🕦 Подождите, пока ваш профиль рассмотрят!')
            return
        cur.execute('SELECT * FROM available')
        buyout = cur.fetchone()
        if buyout:
            AssignBuyout(message.from_user.id, buyout[0])
        else:
            BOT.send_message(message.from_user.id, '🫤 Нет доступных выкупов!')
            ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')


def AssignBuyout(user_id: int, buyout_id: int) -> None:
    Stamp(f'User {user_id} is assigning buyout {buyout_id}', 'i')
    with GetConCur(POOL) as (con, cur):
        already_taken_num = cur.execute("""SELECT COUNT(*)
                                           FROM buyouts
                                           WHERE user_id = %s
                                           AND fact_time IS NULL""",
                                        (user_id,))
        if already_taken_num:
            BOT.send_message(user_id, '❌ Вы уже записаны на выкуп!')
            ShowButtons(BOT, user_id, MENU_BTNS, '❔ Выберите действие:')
            return
        cur.execute('SELECT plan_time FROM buyouts WHERE id = %s', (buyout_id,))
        planned_time = cur.fetchone()[0]
        cur.execute('UPDATE buyouts SET user_id = %s WHERE id = %s', (user_id, buyout_id))
        con.commit()
        BOT.send_message(user_id, f'✅ Вы успешно записаны на выкуп, который состоится  {FormatTime(planned_time)}.\n'
                                               f'🕒 За {TIME_BEFORE_BUYOUT} минут до выкупа я пришлю подробную инструкцию!')


def AcceptHistory(message: Message, buyout_id: int) -> None:
    Stamp(f'User {message.from_user.id} uploading history photo', 'i')
    HandlePhoto(message, 'buyouts', 'photo_hist_link', 'hist', buyout_id)
    BOT.send_message(message.from_user.id, '🖼 Отправьте фото заказанного товара')
    BOT.register_next_step_handler(message, AcceptGood, buyout_id)


def AcceptGood(message: Message, buyout_id: int) -> None:
    Stamp(f'User {message.from_user.id} uploading good photo', 'i')
    HandlePhoto(message, 'buyouts', 'photo_good_link', 'good', buyout_id)
    ShowButtons(BOT, message.from_user.id, MENU_BTNS, '🔄 Спасибо, выкуп отправлен на проверку!')


def AcceptArrival(message: Message, buyout_id: int) -> None:
    Stamp(f'User {message.from_user.id} uploading arrival photo', 'i')
    HandlePhoto(message, 'buyouts', 'photo_arrival_link', 'arrival', buyout_id)
    ShowButtons(BOT, message.from_user.id, MENU_BTNS, '🔄 Спасибо, выкуп отправлен на проверку!')


def ShowMyBuyouts(message: Message) -> None:
    base = """SELECT pick_point_id, plan_time, delivery_time,
              feedback, price, good_id, request
              FROM buyouts JOIN plans on buyouts.plan_id = plans.id
              WHERE user_id = %s"""
    with GetConCur(POOL) as (con, cur):
        if message.text == STATUS_BTNS[0]:
            cur.execute(base + 'AND fact_time IS NULL', (message.from_user.id,))
        elif message.text == STATUS_BTNS[1]:
            cur.execute(base +
                        'AND fact_time IS NOT NULL ' +
                        'AND delivery_time IS NULL', (message.from_user.id,))
        elif message.text == STATUS_BTNS[2]:
            cur.execute(base + 'AND delivery_time IS NOT NULL', (message.from_user.id,))
        else:
            BOT.send_message(message.from_user.id, '❌ Неизвестная команда...')
            ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')
            return
        buyouts = cur.fetchall()
    if not buyouts:
        BOT.send_message(message.from_user.id, '💤 Таких выкупов нет...')
        ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')
        return
    for buyout in buyouts:
        text = ''
        if buyout[0]:
            text += f'📍 Адрес ПВЗ: {GetPositionByOffice(buyout[0])}\n'
        if buyout[1]:
            text += f'🕘 Планируемое время выкупа: {FormatTime(buyout[1])}\n'
        if buyout[2]:
            text += f'🕘 Время доставки: {FormatTime(buyout[2])}\n'
        if buyout[3]:
            text += f'🧨 Отзыв : {FormatTime(buyout[3])}\n'
        if buyout[4]:
            text += f'💰 Цена: {buyout[4]}\n'
        if buyout[5]:
            text += f'🔗 Ссылка на товар: {WB_PATTERN.format(buyout[5])}\n'
        if buyout[6]:
            text += f'📝 Запрос: {buyout[6]}\n'
        BOT.send_message(message.from_user.id, text)
    ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')
