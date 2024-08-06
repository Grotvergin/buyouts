from source import (BOT, ADM, ADM_ID, USER_STATES,
                    REG_STATES, WALLET_BTNS,
                    MAX_LEN_NAME, MAX_LEN_SURNAME,
                    MENU_BTNS, SEX_BTNS, POOL)
from common import (ShowButtons, Stamp, InlineButtons,
                    FormatTime, HandleMedia)
from connect import GetConCur
from telebot.types import Message
from re import match
from source import DRIVE_PATTERN


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == REG_STATES[0])
def AcceptSex(message: Message) -> None:
    Stamp(f'User {message.from_user.id} choosing sex', 'i')
    if message.text not in SEX_BTNS:
        ShowButtons(BOT, message.from_user.id, SEX_BTNS, '❌ Пожалуйста, введите один из предложенных вариантов:')
        return
    with GetConCur(POOL) as (con, cur):
        sex = 'M' if message.text == SEX_BTNS[0] else 'F'
        cur.execute("UPDATE users SET sex = %s WHERE id = %s", (sex, message.from_user.id))
        con.commit()
    USER_STATES[message.from_user.id] = REG_STATES[1]
    BOT.send_message(message.from_user.id, '❔ Введите ваше имя:')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == REG_STATES[1])
def AcceptName(message: Message) -> None:
    Stamp(f'User {message.from_user.id} entering name', 'i')
    name = message.text.strip()
    if not match(r'^[А-Яа-яЁё-]+$', name) or len(name) > MAX_LEN_NAME or len(name) < 2:
        BOT.send_message(message.from_user.id, '❌ Пожалуйста, введите корректное имя:')
        return
    with GetConCur(POOL) as (con, cur):
        cur.execute("UPDATE users SET name = %s WHERE id = %s", (name, message.from_user.id))
        con.commit()
    USER_STATES[message.from_user.id] = REG_STATES[2]
    BOT.send_message(message.from_user.id, '❔ Введите вашу фамилию:')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == REG_STATES[2])
def AcceptSurname(message: Message) -> None:
    Stamp(f'User {message.from_user.id} entering surname', 'i')
    surname = message.text.strip()
    if not match(r'^[А-Яа-яЁё-]+$', surname) or len(surname) > MAX_LEN_SURNAME or len(surname) < 2:
        BOT.send_message(message.from_user.id, '❌ Пожалуйста, введите корректную фамилию:')
        return
    with GetConCur(POOL) as (con, cur):
        cur.execute("UPDATE users SET surname = %s WHERE id = %s", (surname, message.from_user.id))
        con.commit()
    USER_STATES[message.from_user.id] = REG_STATES[3]
    BOT.send_message(message.from_user.id, '❔ Введите 11 цифр номера телефона без других знаков, например, 89151234567:')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == REG_STATES[3])
def AcceptNumDigits(message: Message) -> None:
    Stamp(f'User {message.from_user.id} entering phone', 'i')
    if len(message.text.strip()) != 11 or not message.text.strip().isdigit():
        BOT.send_message(message.from_user.id, '❌ Пожалуйста, введите номер телефона в корректном формате, например, 89151234567:')
        return
    with GetConCur(POOL) as (con, cur):
        cur.execute("UPDATE users SET phone = %s WHERE id = %s", (message.text.strip(), message.from_user.id))
        con.commit()
    USER_STATES[message.from_user.id] = REG_STATES[4]
    BOT.send_message(message.from_user.id, '❔ Отправьте видео истории покупок:')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == REG_STATES[4], content_types=['video', 'document', 'text'])
def HandleVideoLink(message: Message) -> None:
    Stamp(f'User {message.from_user.id} uploading video', 'i')
    HandleMedia(message, 'video_link', f'{message.from_user.id}_wlc.mp4')
    USER_STATES[message.from_user.id] = REG_STATES[5]
    ShowButtons(BOT, message.from_user.id, WALLET_BTNS, '❔ У вас есть кошелек WB с привязанным номером?')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == REG_STATES[5])
def VerifyWallet(message: Message) -> None:
    Stamp(f'User {message.from_user.id} verifying wallet', 'i')
    if message.text not in WALLET_BTNS:
        ShowButtons(BOT, message.from_user.id, WALLET_BTNS, '❌ Пожалуйста, введите один из предложенных вариантов:')
    elif message.text == WALLET_BTNS[0]:
        del USER_STATES[message.from_user.id]
        BOT.send_message(message.from_user.id, '✔️ Спасибо, ваши данные отправлены на проверку!')
        InlineButtons(ADM, ADM_ID, ['✅ Принять', '❌ Отклонить'], ShowUserInfo(message.from_user.id),
                      [f'accept_{message.from_user.id}', f'reject_{message.from_user.id}'])
        ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')
    elif message.text == WALLET_BTNS[1]:
        ShowButtons(BOT, message.from_user.id, WALLET_BTNS, '☢️ Привяжите кошелек!')


def ShowUserInfo(user_id: int) -> str | None:
    with GetConCur(POOL) as (con, cur):
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
    if not user:
        BOT.send_message(user_id, '❌ Вы не зарегистрированы в системе!')
        return
    text = f'🆔 ID: {user[0]}\n' \
           f'🚹 Пол: {user[1]}\n' \
           f'👤 Имя: {user[2]}\n' \
           f'👥 Фамилия: {user[3]}\n' \
           f'📞 Телефон: {user[4]}\n' \
           f'📅 Профиль подтверждён: {FormatTime(user[5])}\n' \
           f'📹 Видео: {DRIVE_PATTERN.format(user[6])}\n' \
           f'🆕 Дата обновления QR-кода: {FormatTime(user[7])}\n'
    if user[8]:
        text += f'🔳 QR-код: {DRIVE_PATTERN.format(user[8])}\n'
    return text


def AcceptNewUser(message: Message) -> None:
    with GetConCur(POOL) as (con, cur):
        Stamp(f'User {message.from_user.id} registering at first', 'i')
        cur.execute("SELECT COUNT(*) FROM users WHERE id = %s", (message.from_user.id,))
        user_count = cur.fetchone()[0]
        if user_count == 1:
            BOT.send_message(message.from_user.id, '⚠️ Вы уже зарегистрированы!')
        elif user_count == 0:
            cur.execute("INSERT INTO users (id) VALUES (%s)", (message.from_user.id,))
            con.commit()
            USER_STATES[message.from_user.id] = REG_STATES[0]
            ShowButtons(BOT, message.from_user.id, SEX_BTNS, '❔ Укажите ваш пол:')
        else:
            Stamp(f'User {message.from_user.id} registered multiple times', 'w')
            ADM.send_message(ADM_ID, f'⚠️ Пользователь {message.from_user.id} зарегистрирован несколько раз!')
