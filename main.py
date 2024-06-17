import psycopg2

from source import *


def AuthorizeDatabase():
    conn = psycopg2.connect(
        dbname="buyouts",
        user="postgres",
        password=PASSWORD,
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    return cursor, conn


def Main():
    while True:
        try:
            BOT.polling(none_stop=True, interval=1)
        except Exception as e:
            Stamp(f'{e}', 'e')
            Stamp(format_exc(), 'e')


@BOT.message_handler(commands=['start'])
def Start(message: Message) -> None:
    USER_STATES[message.from_user.id] = STATE_WAITING_FOR_SEX
    ShowButtons(message, SEX_BTNS, f'👋 Привет, {message.from_user.first_name}! '
                                   f'<Текст от Паши>. \n Пожалуйста, укажите ваш пол:')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == STATE_WAITING_FOR_SEX)
def AcceptSex(message: Message) -> None:
    if message.text not in SEX_BTNS:
        ShowButtons(message, SEX_BTNS, '❌ Пожалуйста, введите один из предложенных вариантов:')
        return
    sex = 'M' if message.text == SEX_BTNS[0] else 'F'
    USER_STATES[message.from_user.id] = STATE_WAITING_FOR_NAME
    CUR.execute("INSERT INTO users (id, sex, reg_date) VALUES (%s, %s, %s)", (message.from_user.id, sex, datetime.now().date()))
    CON.commit()
    USER_STATES[message.from_user.id] = {'state': STATE_WAITING_FOR_NAME, 'user_id': message.from_user.id}
    BOT.send_message(message.from_user.id, '❔ Пожалуйста, введите ваше имя:')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id, {}).get('state') == STATE_WAITING_FOR_NAME)
def AcceptName(message: Message) -> None:
    name = message.text.strip()
    if not match(r'^[A-Za-zА-Яа-яЁё-]+$', name) or len(message.text) > 15:
        BOT.send_message('❌ Пожалуйста, введите корректное имя:')
        return
    CUR.execute("UPDATE users SET name = %s WHERE id = %s", (name, message.from_user.id))
    CON.commit()
    USER_STATES[message.from_user.id]['state'] = STATE_WAITING_FOR_NUM_DIGITS
    BOT.send_message(message.from_user.id, '❔ Пожалуйста, введите последние 4 цифры номера телефона без других знаков:')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id, {}).get('state') == STATE_WAITING_FOR_NUM_DIGITS)
def handle_num_digits(message: Message) -> None:
    try:
        num_digits = int(message.text.strip())
        if len(str(num_digits)) != 4:
            raise ValueError
    except ValueError:
        BOT.send_message(message.from_user.id, '❌ Пожалуйста, введите корректные последние 4 цифры номера телефона:')
        return
    CUR.execute("UPDATE users SET num_digits = %s WHERE id = %s", (num_digits, message.from_user.id))
    CON.commit()
    USER_STATES[message.from_user.id]['state'] = STATE_WAITING_FOR_CITY
    CUR.execute("SELECT name FROM cities")
    cities = [row[0] for row in CUR.fetchall()]
    InlineButtons(message, tuple(cities), '❔ Пожалуйста, выберите ваш город:', 'city_')


@BOT.callback_query_handler(func=lambda call: call.data.startswith('city_'))
def handle_city_callback(call: CallbackQuery) -> None:
    city = call.data.split('_')[1]
    CUR.execute("UPDATE users SET city = %s WHERE id = %s", (city, call.from_user.id))
    CON.commit()
    USER_STATES[call.from_user.id]['state'] = STATE_WAITING_FOR_VIDEO
    BOT.send_message(call.from_user.id, '❔ Пожалуйста, отправьте видео??? Надо объяснить челу че отправить:')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id, {}).get('state') == STATE_WAITING_FOR_VIDEO)
def handle_video_link(message: Message) -> None:
    Stamp(f'User {message.from_user.id} uploading video', 'i')
    if not message.video:
        BOT.send_message(message.from_user.id, '❌ Пожалуйста, отправьте видео:')
        return
    video_file_info = BOT.get_file(message.video.file_id)
    video_file = BOT.download_file(video_file_info.file_path)
    path = f"{message.video.file_id}.mp4"
    with open(path, 'wb') as new_file:
        new_file.write(video_file)
    file_metadata = {
        'name': path,
        'mimeType': 'video/mp4'
    }

    media = MediaFileUpload(f"{message.video.file_id}.mp4", mimetype='video/mp4', resumable=True)
    file = SERVICE.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    video_link = f"https://drive.google.com/file/d/{file.get('id')}/view?usp=sharing"
    CUR.execute("UPDATE users SET video_link = %s WHERE id = %s", (video_link, message.from_user.id))
    CON.commit()
    remove(path)
    del USER_STATES[message.from_user.id]
    BOT.send_message(message.from_user.id, '✅ Спасибо, регистрация завершена!')


if __name__ == '__main__':
    SERVICE = BuildService()
    CUR, CON = AuthorizeDatabase()
    Main()