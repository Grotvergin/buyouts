from time import strftime, strptime
from telebot.types import CallbackQuery
from common import InlineButtons, Stamp, GetPriceGood
from connect import GetConCur
from source import (BOT, AWARD_BUYOUT,
                    WB_PATTERN, CALLBACKS, STATUSES,
                    STATUSES_AND_BTNS,
                    AWARD_FEEDBACK, POOL)


def PrepareBuyouts(user_id: int = None) -> dict | None:
    with GetConCur(POOL) as (con, cur):
        if user_id:
            cur.execute('SELECT * FROM fetch_buyouts_for_user(%s)', (user_id,))
        else:
            cur.execute('SELECT * FROM upcoming_buyouts')
        buyouts = cur.fetchall()
    if not buyouts:
        return
    info = {}
    for buyout in buyouts:
        text = ''
        status = STATUSES[0]
        reward = AWARD_BUYOUT
        if buyout[0]:
            text += f'📍 ID ПВЗ: {buyout[0]}\n'
        if buyout[1]:
            status = STATUSES[1]
        if buyout[2]:
            text += f'🕘 Планируемое время выкупа: {FormatTime(buyout[2])}\n'
        if buyout[3]:
            text += f'🏁 Фактическое время выкупа: {FormatTime(buyout[3])}\n'
            status = STATUSES[2]
        if buyout[4]:
            text += f'🚛 Доставлен на ПВЗ: {FormatTime(buyout[4])}\n'
            status = STATUSES[3]
        if buyout[5]:
            text += f'📤 Забран из ПВЗ: {FormatTime(buyout[5])}\n'
            status = STATUSES[4]
        if buyout[6]:
            text += f'📝 Отзыв: {buyout[6]}\n'
            reward += AWARD_FEEDBACK
        if buyout[7]:
            text += f'🔗 Ссылка: {WB_PATTERN.format(buyout[7])}\n'
        if buyout[9]:
            text += f'📄 Запрос: {buyout[9]}\n'
        text += f'💰 Вознаграждение: {reward} ₽\n'
        text += f'⚠️ Статус: {status}\n'
        info[buyout[10]] = (text, status)
    return info


def SendBuyouts(user_id: int, status: str = None, all_statuses: bool = False) -> None:
    sent_at_least_one = False
    if status == STATUSES[0]:
        buyouts = PrepareBuyouts()
    else:
        buyouts = PrepareBuyouts(user_id)
    if buyouts:
        for one in buyouts.keys():
            if buyouts[one][1] == status or all_statuses:
                sent_at_least_one = True
                btn_text, clbk_data = STATUSES_AND_BTNS[buyouts[one][1]]
                InlineButtons(BOT, user_id, [btn_text], buyouts[one], [f'{clbk_data}{one}'])
    if not sent_at_least_one:
        if all_statuses:
            BOT.send_message(user_id, f'❌ Нет никаких выкупов!')
        else:
            BOT.send_message(user_id, f'❌ Нет выкупов со статусом {status}!')


def FormatTime(time: str) -> str:
    try:
        date = strptime(time, "%Y-%m-%d %H:%M:%S.%f")
    except (ValueError, TypeError):
        return 'N/A'
    return strftime("%d.%m.%Y %H:%M", date)


@BOT.callback_query_handler(func=lambda call: call.data.startswith(CALLBACKS[0]))
def HandleChooseCallback(call: CallbackQuery) -> None:
    buyout_id = call.data.split('_')[1]
    try:
        with GetConCur(POOL) as (con, cur):
            cur.execute("UPDATE buyouts SET user_id = %s WHERE id = %s", (call.from_user.id, buyout_id))
            con.commit()
        BOT.send_message(call.from_user.id, '✅ Вы успешно записаны на выкуп!')
    except Exception as e:
        BOT.send_message(call.from_user.id, '❌ Произошла ошибка при записи на выкуп!')
        Stamp(f'Error while handling take callback: {str(e)}', 'e')


@BOT.callback_query_handler(func=lambda call: call.data.startswith(CALLBACKS[1]))
def HandleOrderedCallback(call: CallbackQuery) -> None:
    buyout_id = call.data.split('_')[1]
    try:
        with GetConCur(POOL) as (con, cur):
            cur.execute("SELECT good_link FROM plans AS p JOIN buyouts AS b ON p.id = b.plan_id WHERE b.id = %s", (buyout_id,))
            good_link = cur.fetchone()[0]
            cur.execute("UPDATE buyouts SET fact_time = NOW(), price = %s WHERE id = %s", (GetPriceGood(good_link), buyout_id))
            con.commit()
        BOT.send_message(call.from_user.id, '✅ Четко, вижу заказал!')
    except Exception as e:
        BOT.send_message(call.from_user.id, '❌ Произошла ошибка при обновлении статуса!')
        Stamp(f'Error while handling ordered callback: {str(e)}', 'e')


@BOT.callback_query_handler(func=lambda call: call.data.startswith(CALLBACKS[2]))
def HandleArrivedCallback(call: CallbackQuery) -> None:
    buyout_id = call.data.split('_')[1]
    try:
        with GetConCur(POOL) as (con, cur):
            cur.execute("UPDATE buyouts SET delivery_time = NOW() WHERE id = %s", (buyout_id,))
            con.commit()
        BOT.send_message(call.from_user.id, '✅ Четко, вижу приехал!')
    except Exception as e:
        BOT.send_message(call.from_user.id, '❌ Произошла ошибка при обновлении статуса!')
        Stamp(f'Error while handling arrived callback: {str(e)}', 'e')


@BOT.callback_query_handler(func=lambda call: call.data.startswith(CALLBACKS[3]))
def HandlePickedUpCallback(call: CallbackQuery) -> None:
    buyout_id = call.data.split('_')[1]
    try:
        with GetConCur(POOL) as (con, cur):
            cur.execute("UPDATE buyouts SET pick_up_time = NOW() WHERE id = %s", (buyout_id,))
            con.commit()
        BOT.send_message(call.from_user.id, '✅ Четко, вижу забрал!')
    except Exception as e:
        BOT.send_message(call.from_user.id, '❌ Произошла ошибка при обновлении статуса!')
        Stamp(f'Error while handling picked up callback: {str(e)}', 'e')


@BOT.callback_query_handler(func=lambda call: call.data.startswith(CALLBACKS[4]))
def HandleFeedbackCallback(call: CallbackQuery) -> None:
    buyout_id = call.data.split('_')[1]
    try:
        with GetConCur(POOL) as (con, cur):
            con.commit()
        BOT.send_message(call.from_user.id, '✅ Четко, вижу оценил!')
    except Exception as e:
        BOT.send_message(call.from_user.id, '❌ Произошла ошибка при обновлении статуса!')
        Stamp(f'Error while handling feedback callback: {str(e)}', 'e')
