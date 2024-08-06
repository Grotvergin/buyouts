from telebot.types import Message
from source import BOT, CANCEL_BTN, MENU_BTNS, POOL
from common import ShowButtons, Stamp, HandleMedia, FormatTime
from connect import GetConCur


def RefreshQR(message: Message) -> None:
    Stamp(f'User {message.from_user.id} is refreshing QR-code', 'i')
    if message.text == CANCEL_BTN[0]:
        ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')
        return
    HandleMedia(message, 'qr_link', f'qr_{message.from_user.id}.jpg', False)
    Stamp(f'User {message.from_user.id} has uploaded a new QR-code', 'i')
    with GetConCur(POOL) as (con, cur):
        cur.execute("UPDATE users SET qr_time = NOW() WHERE id = %s", (message.from_user.id,))
        con.commit()
    ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')


def FindOutDateQR(user_id: int) -> str:
    with GetConCur(POOL) as (con, cur):
        cur.execute("SELECT qr_time FROM users WHERE id = %s", (user_id,))
        qr_date = cur.fetchone()[0]
        return FormatTime(qr_date)
