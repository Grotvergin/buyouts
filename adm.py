from telebot.types import Message
from common import ShowButtons
from source import BOT, ADM, ADM_ID, CANCEL_BTN, MENU_BTNS


def SendQuestion(message: Message) -> None:
    if message.text == CANCEL_BTN[0]:
        ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')
        return
    ADM.send_message(ADM_ID, f'📢 Вопрос от пользователя {message.from_user.id} – @{message.from_user.username}:\n{message.text}')
    BOT.send_message(message.from_user.id, '✅ Ваш вопрос отправлен администратору!')
    ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')
