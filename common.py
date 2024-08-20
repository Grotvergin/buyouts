from googleapiclient.discovery import Resource, build
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from colorama import Fore, Style
from telebot import TeleBot
from telebot.types import (Message, ReplyKeyboardMarkup,
                           KeyboardButton, InlineKeyboardMarkup,
                           InlineKeyboardButton)
from random import randint
from time import sleep
from requests import get, ConnectionError
from headers_agents import HEADERS, PARAMS
from source import (LONG_SLEEP, URL, TIME_FORMAT, DRIVE_PATTERN,
                    WB_WALLET_RATIO, BOT, POOL, ADM_ID,
                    DIR_MEDIA, ADM, VALIDATE_BTNS, VALIDATE_CLBK)
from googleapiclient.errors import HttpError
from ssl import SSLEOFError
from socket import gaierror
from httplib2.error import ServerNotFoundError
from googleapiclient.http import MediaFileUpload
from connect import GetConCur
from os.path import join


def BuildService() -> Resource:
    Stamp(f'Trying to build service', 'i')
    try:
        service = build('drive',
                        'v3',
                        credentials=Credentials.from_service_account_file('keys.json',
                                                                          scopes=['https://www.googleapis.com/auth/drive.file']))
    except (TimeoutError, ServerNotFoundError, gaierror, HttpError, SSLEOFError) as err:
        Stamp(f'Status = {err} on building service', 'e')
        Sleep(LONG_SLEEP)
        BuildService()
    else:
        Stamp('Built service successfully', 's')
        return service


def Stamp(message: str, level: str) -> None:
    time_stamp = datetime.now().strftime('[%m-%d|%H:%M:%S]')
    match level:
        case 'i':
            print(Fore.LIGHTBLUE_EX + time_stamp + '[INF] ' + message + '.' + Style.RESET_ALL)
        case 'w':
            print(Fore.LIGHTMAGENTA_EX + time_stamp + '[WAR] ' + message + '!' + Style.RESET_ALL)
        case 's':
            print(Fore.LIGHTGREEN_EX + time_stamp + '[SUC] ' + message + '.' + Style.RESET_ALL)
        case 'e':
            print(Fore.RED + time_stamp + '[ERR] ' + message + '!!!' + Style.RESET_ALL)
        case 'l':
            print(Fore.WHITE + time_stamp + '[SLE] ' + message + '...' + Style.RESET_ALL)
        case 'b':
            print(Fore.LIGHTYELLOW_EX + time_stamp + '[BOR] ' + message + '.' + Style.RESET_ALL)
        case _:
            print(Fore.WHITE + time_stamp + '[UNK] ' + message + '?' + Style.RESET_ALL)


def ShowButtons(bot: TeleBot, user_id: int, buttons: tuple, answer: str) -> None:
    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    if len(buttons) % 3 == 0:
        row_size = 3
    elif len(buttons) % 2 == 0:
        row_size = 2
    else:
        row_size = 1
    for i in range(0, len(buttons), row_size):
        row_buttons = buttons[i:i + row_size]
        markup.row(*[KeyboardButton(btn) for btn in row_buttons])
    bot.send_message(user_id, answer, reply_markup=markup, parse_mode='Markdown')


def InlineButtons(bot: TeleBot, user_id: int, buttons: tuple, answer: str, clbk_data: tuple) -> None:
    markup = InlineKeyboardMarkup()
    if len(buttons) % 3 == 0:
        row_size = 3
    elif len(buttons) % 2 == 0:
        row_size = 2
    else:
        row_size = 1
    for i in range(0, len(buttons), row_size):
        row_buttons = [InlineKeyboardButton(btn, callback_data=clbk_data[j]) for j, btn in enumerate(buttons[i:i + row_size], start=i)]
        markup.row(*row_buttons)
    bot.send_message(user_id, answer, reply_markup=markup)


def Sleep(timer: int, ratio: float = 0.0) -> None:
    rand_time = randint(int((1 - ratio) * timer), int((1 + ratio) * timer))
    Stamp(f'Sleeping {rand_time} seconds', 'l')
    sleep(rand_time)


def GetPriceGood(barcode: int) -> int:
    Stamp(f'Trying to get price for barcode: {barcode}', 'i')
    raw = GetDataWhileNotCorrect(barcode, 3)
    if raw:
        price = raw['data']['products'][0]['sizes'][0]['price']['total']
        price = round((float(price) / 100 * WB_WALLET_RATIO))
        Stamp(f'Got price for barcode: {barcode} costs {price}', 's')
        return price
    else:
        Stamp(f'Failed to get price for barcode: {barcode}', 'e')
        return 0


def GetDataWhileNotCorrect(barcode: int, max_attempts: int) -> dict | None:
    attempts = 0
    while attempts < max_attempts:
        raw_data = GetData(barcode)
        if BarcodeIsValid(raw_data):
            return raw_data
        attempts += 1
        Stamp(f'Attempt {attempts} failed, retrying', 'w')
    Stamp(f'Exceeded maximum attempts ({max_attempts}) for barcode: {barcode}', 'e')
    return


def BarcodeIsValid(raw: dict) -> bool:
    if 'data' in raw and 'products' in raw['data'] and raw['data']['products']:
        if 'sizes' in raw['data']['products'][0] and raw['data']['products'][0]['sizes']:
            if raw['data']['products'][0]['sizes'][0] and 'price' in raw['data']['products'][0]['sizes'][0]:
                if raw['data']['products'][0]['sizes'][0]['price'] and 'total' in raw['data']['products'][0]['sizes'][0]['price']:
                    if raw['data']['products'][0]['sizes'][0]['price']['total']:
                        return True
    return False


def GetData(barcode: int) -> dict:
    Stamp(f'Trying to connect {URL}', 'i')
    HEADERS['Referer'] = f'https://www.wildberries.ru/catalog/{barcode}/detail.aspx'
    PARAMS['nm'] = barcode
    try:
        response = get(URL, params=PARAMS, headers=HEADERS)
    except ConnectionError:
        Stamp(f'Connection on {URL}', 'e')
        Sleep(LONG_SLEEP)
        raw = GetData(barcode)
    else:
        if str(response.status_code)[0] == '2':
            Stamp(f'Status = {response.status_code} on {URL}', 's')
            if response.content:
                raw = response.json()
            else:
                Stamp('Response is empty', 'w')
                raw = {}
        else:
            Stamp(f'Status = {response.status_code} on {URL}', 'e')
            Sleep(LONG_SLEEP)
            raw = GetData(barcode)
    return raw


def FormatTime(time: str) -> str:
    try:
        clean_time = str(time)[:-6]
        date = datetime.strptime(clean_time, "%Y-%m-%d %H:%M:%S.%f")
        date += timedelta(hours=6)
        return date.strftime(TIME_FORMAT)
    except (ValueError, TypeError):
        return 'N/A'


def FormatCallback(clbk_data: tuple, formatting_data: tuple | str) -> tuple:
    new_clbk_data = []
    for one in clbk_data:
        new_clbk_data.append(one.format(*formatting_data))
    return tuple(new_clbk_data)


def UploadMedia(message: Message, file_info: dict, path: str, mimetype: str) -> str:
    file = BOT.download_file(file_info.file_path)
    with open(path, 'wb') as new_file:
        new_file.write(file)
    file_id = UploadToDrive(message, path, mimetype)
    return file_id


def UploadToDrive(message: Message, path: str, mimetype: str) -> str:
    try:
        srv = BuildService()
        media = MediaFileUpload(path, mimetype=mimetype)
        file = srv.files().create(body={'name': path}, media_body=media, fields='id').execute()
        srv.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
        return file.get('id')
    except Exception as e:
        BOT.send_message(message.from_user.id, f'❌ Произошла ошибка во время загрузки файла!')
        Stamp(f'Error while uploading a file: {str(e)}', 'e')


def ExtractPhotoFromMessage(message: Message) -> dict | None:
    media_file_info = None
    if message.photo:
        media_file_info = BOT.get_file(message.photo[-1].file_id)
    elif message.document and message.document.mime_type.startswith('image/'):
        media_file_info = BOT.get_file(message.document.file_id)
    if not media_file_info:
        BOT.send_message(message.from_user.id, '❌ Пожалуйста, отправьте фото:')
        return
    BOT.send_message(message.from_user.id, '🔄 Спасибо, ваше фото в обработке...')
    return media_file_info


def SendValidationRequest(media_link: str, table: str, field: str, entity_id: int, user_id: int) -> None:
    InlineButtons(ADM, ADM_ID, VALIDATE_BTNS, 'Ознакомьтесь с медиа ❓\n'
                                              f'🙆 Пользователь: {user_id}\n'
                                              f'🔗 Ссылка: {DRIVE_PATTERN.format(media_link)}\n'
                                              f'🗓 Таблица: {table}\n'
                                              f'🏷 Поле: {field}',
                  FormatCallback(VALIDATE_CLBK, (table, field, entity_id, user_id)))


def ExtractVideoFromMessage(message: Message) -> dict | None:
    media_file_info = None
    if message.video:
        media_file_info = BOT.get_file(message.video.file_id)
    elif message.document and message.document.mime_type.startswith('video/'):
        media_file_info = BOT.get_file(message.document.file_id)
    if not media_file_info:
        BOT.send_message(message.from_user.id, '❌ Пожалуйста, отправьте видео:')
        return
    BOT.send_message(message.from_user.id, '🔄 Спасибо, ваше видео в обработке...')
    return media_file_info


def HandlePhoto(message: Message, table: str, field: str, suffix: str, entity_id: int) -> bool:
    media_file_info = ExtractPhotoFromMessage(message)
    if not media_file_info:
        BOT.register_next_step_handler(message, HandlePhoto, table, field, suffix, entity_id)
        return False
    file_id = UploadMedia(message, media_file_info, join(DIR_MEDIA, f'{message.from_user.id}_{suffix}.jpg'), 'image/jpeg')
    SendValidationRequest(file_id, table, field, message.from_user.id, message.from_user.id)
    with GetConCur(POOL) as (con, cur):
        cur.execute(f"UPDATE {table} SET {field} = %s WHERE id = %s", (file_id, entity_id))
        con.commit()
    return True


def HandleVideo(message: Message, table: str, field: str, suffix: str, entity_id: int) -> bool:
    media_file_info = ExtractVideoFromMessage(message)
    if not media_file_info:
        BOT.send_message(message.from_user.id, '❌ Видео не распознано. Пожалуйста, попробуйте снова.')
        return False
    file_id = UploadMedia(message, media_file_info, join(DIR_MEDIA, f'{message.from_user.id}_{suffix}.jpg'), 'video/mp4')
    SendValidationRequest(file_id, table, field, message.from_user.id, message.from_user.id)
    with GetConCur(POOL) as (con, cur):
        cur.execute(f"UPDATE {table} SET {field} = %s WHERE id = %s", (file_id, entity_id))
        con.commit()
    return True
