from source import *


def AuthorizeDatabase():
    conn = connect(
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
    Stamp(f'User {message.from_user.id} started bot', 'i')
    USER_STATES[message.from_user.id] = STATES[0]
    ShowButtons(message, SEX_BTNS, f'👋 Привет, {message.from_user.first_name}! '
                                   f'<Текст от Паши>.\nПожалуйста, укажите ваш пол:')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == STATES[0])
def AcceptSex(message: Message) -> None:
    Stamp(f'User {message.from_user.id} choosing sex', 'i')
    if message.text not in SEX_BTNS:
        ShowButtons(message, SEX_BTNS, '❌ Пожалуйста, введите один из предложенных вариантов:')
        return
    sex = 'M' if message.text == SEX_BTNS[0] else 'F'
    CUR.execute("INSERT INTO users (id, sex, reg_date) VALUES (%s, %s, %s)", (message.from_user.id, sex, datetime.now().date()))
    CON.commit()
    USER_STATES[message.from_user.id] = STATES[1]
    BOT.send_message(message.from_user.id, '❔ Пожалуйста, введите ваше имя:')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == STATES[1])
def AcceptName(message: Message) -> None:
    Stamp(f'User {message.from_user.id} entering name', 'i')
    name = message.text.strip()
    if not match(r'^[A-Za-zА-Яа-яЁё-]+$', name) or len(message.text) > 15:
        BOT.send_message(message.from_user.id, '❌ Пожалуйста, введите корректное имя:')
        return
    CUR.execute("UPDATE users SET name = %s WHERE id = %s", (name, message.from_user.id))
    CON.commit()
    USER_STATES[message.from_user.id] = STATES[2]
    BOT.send_message(message.from_user.id, '❔ Пожалуйста, введите последние 4 цифры номера телефона без других знаков:')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == STATES[2])
def AcceptNumDigits(message: Message) -> None:
    Stamp(f'User {message.from_user.id} entering num_digits', 'i')
    try:
        num_digits = int(message.text.strip())
        if len(str(num_digits)) != 4:
            raise ValueError
    except ValueError:
        BOT.send_message(message.from_user.id, '❌ Пожалуйста, введите корректные последние 4 цифры номера телефона:')
        return
    CUR.execute("UPDATE users SET num_digits = %s WHERE id = %s", (num_digits, message.from_user.id))
    CON.commit()
    CUR.execute("SELECT name FROM cities")
    cities = [row[0] for row in CUR.fetchall()]
    USER_STATES[message.from_user.id] = STATES[3]
    InlineButtons(message, tuple(cities), '❔ Пожалуйста, выберите ваш город:', 'city_')


@BOT.callback_query_handler(func=lambda call: call.data.startswith('city_'))
def HandleCityCallback(call: CallbackQuery) -> None:
    Stamp(f'User {call.from_user.id} choosing city', 'i')
    city = call.data.split('_')[1]
    CUR.execute("UPDATE users SET city = %s WHERE id = %s", (city, call.from_user.id))
    CON.commit()
    USER_STATES[call.from_user.id] = STATES[4]
    BOT.send_message(call.from_user.id, '❔ Пожалуйста, отправьте видео:')
    print(USER_STATES)


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == STATES[4], content_types=['video', 'text'])
def HandleVideoLink(message: Message) -> None:
    Stamp(f'User {message.from_user.id} uploading video', 'i')
    if not message.video:
        BOT.send_message(message.from_user.id, '❌ Пожалуйста, отправьте видео:')
        return
    try:
        video_file_info = BOT.get_file(message.video.file_id)
        video_file = BOT.download_file(video_file_info.file_path)
        path = f"{message.from_user.id}_welcome.mp4"
        with open(path, 'wb') as new_file:
            new_file.write(video_file)
        media = MediaFileUpload(path, mimetype='video/mp4')
        file = SERVICE.files().create(body={'name': path}, media_body=media, fields='id').execute()
        SERVICE.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
        video_link = f"https://drive.google.com/file/d/{file.get('id')}/view?usp=sharing"
        CUR.execute("UPDATE users SET video_link = %s WHERE id = %s", (video_link, message.from_user.id))
        CON.commit()
    except Exception as e:
        BOT.send_message(message.from_user.id, f'❌ Произошла ошибка во время загрузки файла!')
        Stamp(f'Error while uploading a file: {str(e)}', 'e')
    del USER_STATES[message.from_user.id]
    BOT.send_message(message.from_user.id, '✅ Спасибо, регистрация завершена!')


if __name__ == '__main__':
    SERVICE = BuildService()
    CUR, CON = AuthorizeDatabase()
    Main()
