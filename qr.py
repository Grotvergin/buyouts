from telebot.types import Message
from source import BOT, CANCEL_BTN, MENU_BTNS, POOL, DIR_MEDIA
from common import (ShowButtons, Stamp, SendValidationRequest,
                    FormatTime, ExtractPhotoFromMessage,
                    UploadToDrive)
from connect import GetConCur
from os.path import join
from cv2 import imread, imwrite
from pyzbar.pyzbar import decode


def RefreshQR(message: Message) -> None:
    Stamp(f'User {message.from_user.id} is refreshing QR-code', 'i')
    if message.text == CANCEL_BTN[0]:
        ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')
        return
    media_file_info = ExtractPhotoFromMessage(message)
    path = ExtractQRCode(message, media_file_info)
    if not path:
        Stamp(f'No valid qr code in photo found for user {message.from_user.id}', 'w')
        ShowButtons(BOT, message.from_user.id, CANCEL_BTN, '‼️ На фото не было найдено QR-кода. Пожалуйста, проверьте'
                                               'фото и попробуйте снова')
        BOT.register_next_step_handler(message, RefreshQR)
        return
    file_id = UploadToDrive(message, path, 'image/jpeg')
    with GetConCur(POOL) as (con, cur):
        cur.execute('UPDATE users SET qr_link = %s WHERE id = %s', (file_id, message.from_user.id))
        con.commit()
    SendValidationRequest(file_id, 'users', 'qr_link', message.from_user.id, message.from_user.id)
    Stamp(f'User {message.from_user.id} has uploaded a new QR-code', 'i')
    ShowButtons(BOT, message.from_user.id, MENU_BTNS, '❔ Выберите действие:')


def ExtractQRCode(message: Message, media_file_info: dict) -> None | str:
    file = BOT.download_file(media_file_info.file_path)
    path = join(DIR_MEDIA, f'{message.from_user.id}_qr.jpg')
    with open(path, 'wb') as f:
        f.write(file)
    orig_img = imread(path)
    decoded = decode(orig_img)
    if not decoded:
        return
    qr = decoded[0]
    x, y, w, h = qr.rect.left, qr.rect.top, qr.rect.width, qr.rect.height
    new_img = orig_img[y:y+h, x:x+w].copy()
    imwrite(path, new_img)
    return path


def FindOutDateQR(user_id: int) -> str:
    with GetConCur(POOL) as (con, cur):
        cur.execute("SELECT qr_time FROM users WHERE id = %s", (user_id,))
        qr_date = cur.fetchone()[0]
        return FormatTime(qr_date)
