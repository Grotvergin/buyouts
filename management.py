from common import FormatTime, ShowButtons
from telebot.types import Message
from common import Stamp, GetPriceGood, HandleMedia
from connect import GetConCur
from source import (BOT, WALLET_BTNS,
                    STATUS_BTNS,
                    MENU_BTNS, BOUGHT_BTNS,
                    POOL, TIME_BEFORE_BUYOUT,
                    WB_PATTERN)


def ShowAvailableBuyouts(message: Message) -> None:
    with GetConCur(POOL) as (con, cur):
        cur.execute('SELECT * FROM available')
        buyout = cur.fetchone()
        if buyout:
            already_taken_num = cur.execute("""
                                        SELECT COUNT(*)
                                        FROM buyouts
                                        WHERE user_id = %s
                                        AND fact_time IS NULL
                                        """, (message.from_user.id,))
            if already_taken_num:
                BOT.send_message(message.from_user.id, '❌ Вы уже записаны на выкуп!')
                ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')
                return
            buyout_id, planned_time = buyout
            message_text = f'🕘 Ближайший выкуп запланирован на: {FormatTime(planned_time)}\n' \
                           f'Готовы взять?'
            ShowButtons(BOT, message.from_user.id, WALLET_BTNS, message_text)
            BOT.register_next_step_handler(message, TakeBuyout, buyout_id)
        else:
            BOT.send_message(message.from_user.id, '🫤 Нет доступных выкупов!')
            ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')


def TakeBuyout(message: Message, buyout_id: int) -> None:
    if message.text == WALLET_BTNS[0]:
        try:
            with GetConCur(POOL) as (con, cur):
                cur.execute("UPDATE buyouts SET user_id = %s WHERE id = %s", (message.from_user.id, buyout_id))
                con.commit()
            BOT.send_message(message.from_user.id, '✅ Вы успешно записаны на выкуп!\n'
                                                   f'За {TIME_BEFORE_BUYOUT} минут до выкупа я напомню вам!')
        except Exception as e:
            BOT.send_message(message.from_user.id, '❌ Произошла ошибка при записи на выкуп!')
            Stamp(f'Error while taking buyout: {str(e)}', 'e')
    else:
        BOT.send_message(message.from_user.id, '❌ Вы отменили запись на выкуп!')
        ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')


def AfterOrder(message: Message, buyout_id: int, nmid: int) -> None:
    if message.text == BOUGHT_BTNS[0]:
        # with GetConCur(POOL) as (con, cur):
        #     cur.execute("UPDATE buyouts SET fact_time = NOW() WHERE id = %s", (buyout_id,))
        BOT.send_message(message.from_user.id, 'Отправьте фото истории просмотров 💾')
        BOT.register_next_step_handler(message, AcceptHistory)
    else:
        BOT.send_message(message.from_user.id, '❌ Отмена заказа!')
        ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')


def AcceptHistory(message: Message) -> None:
    Stamp(f'User {message.from_user.id} uploading history', 'i')
    HandleMedia(message, 'photo_hist_link', f'{message.from_user.id}_history.jpg', False, 'buyouts')
    BOT.send_message(message.from_user.id, 'Отправьте фото photo_good_link???')
    BOT.register_next_step_handler(message, AcceptGood)


def AcceptGood(message: Message) -> None:
    Stamp(f'User {message.from_user.id} uploading good', 'i')
    HandleMedia(message, 'photo_good_link', f'{message.from_user.id}_good.jpg', False, 'buyouts')
    ShowButtons(BOT, message.from_user.id, MENU_BTNS, '🔄 Спасибо, выкуп отправлен на проверку!')


def ShowMyBuyouts(message: Message) -> None:
    if message.text == STATUS_BTNS[0]:
        with GetConCur(POOL) as (con, cur):
            cur.execute("SELECT pick_point_id, plan_time, delivery_time,"
                        "feedback, price, good_link, request"
                        "FROM buyouts JOIN plans on buyouts.plan_id = plans.id"
                        "WHERE user_id = %s AND fact_time IS NULL", (message.from_user.id,))
    elif message.text == STATUS_BTNS[1]:
        with GetConCur(POOL) as (con, cur):
            cur.execute("SELECT pick_point_id, plan_time, delivery_time,"
                        "feedback, price, good_link, request"
                        "FROM buyouts JOIN plans on buyouts.plan_id = plans.id"
                        "WHERE user_id = %s AND fact_time IS NOT NULL"
                        "AND delivery_time IS NULL", (message.from_user.id,))
    elif message.text == STATUS_BTNS[2]:
        with GetConCur(POOL) as (con, cur):
            cur.execute("SELECT pick_point_id, plan_time, delivery_time,"
                        "feedback, price, good_link, request"
                        "FROM buyouts JOIN plans on buyouts.plan_id = plans.id"
                        "WHERE user_id = %s AND delivery_time IS NOT NULL", (message.from_user.id,))
    else:
        BOT.send_message(message.from_user.id, '❌ Неизвестная команда...')
        ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')
        return
    buyouts = cur.fetchall()
    if not buyouts:
        BOT.send_message(message.from_user.id, '❌ Нет выкупов!')
        ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')
        return
    for buyout in buyouts:
        text = ''
        if buyout[0]:
            text += f'📍 ID ПВЗ (скоро адрес): {buyout[0]}\n'
        if buyout[1]:
            text += f'🕘 Планируемое время выкупа: {FormatTime(buyout[1])}\n'
        if buyout[2]:
            text += f'🕘 Планируемое время доставки: {FormatTime(buyout[2])}\n'
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
