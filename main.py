from source import *


def AuthorizeDatabase():
    conn = connect(
        dbname="buyouts",
        user="test",
        password=PASSWORD,
        host="185.219.82.218",
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


def ShowBuyouts(user_id: int = None) -> str | None:
    query = """
    SELECT 
        b.id,
        b.date_plan,
        b.date_fact,
        b.date_pick_up,
        b.date_shipment,
        b.photo_hist_link,
        b.photo_good_link,
        b.date_delivery,
        b.feedback,
        b.price
    FROM 
        buyouts AS b
    """

    if user_id:
        query += "WHERE b.user_id = %s"
        CUR.execute(query, (user_id,))
    else:
        query += "WHERE b.user_id IS NULL"
        CUR.execute(query)

    buyouts = CUR.fetchall()

    if not buyouts:
        return "Нет данных о выкупах."

    info = []
    for buyout in buyouts:
        info.append(
            f"🎁 Выкуп #{buyout[0]}\n"
            f"📅 Планируемая дата: {buyout[1]}\n"
            f"📅 Фактическая дата: {buyout[2]}\n"
            f"📅 Дата получения: {buyout[3]}\n"
            f"📅 Дата отгрузки: {buyout[4]}\n"
            f"🖼️ Фото истории: {buyout[5]}\n"
            f"🖼️ Фото товара: {buyout[6]}\n"
            f"📅 Дата доставки: {buyout[7]}\n"
            f"💬 Отзыв: {buyout[8]}\n"
            f"💵 Цена: {buyout[9]} рублей\n"
            "---------------------------------\n"
        )

    return ''.join(info)


@BOT.message_handler(content_types=['text'])
def Start(message: Message) -> None:
    Stamp(f'User {message.from_user.id} requested {message.text}', 'i')
    if message.text == MENU_BTNS[0]:
        Stamp(f'User {message.from_user.id} started registration', 'i')
        USER_STATES[message.from_user.id] = STATES[0]
        ShowButtons(message, SEX_BTNS, f'👋 Привет, {message.from_user.first_name}! '
                                   f'\nПожалуйста, укажите ваш пол:')
    elif message.text == MENU_BTNS[1]:
        buyouts = ShowBuyouts()
        if not buyouts:
            BOT.send_message(message.from_user.id, '❌ На данный момент нет доступных выкупов!')
        else:
            BOT.send_message(message.from_user.id, buyouts)
        ShowButtons(message, MENU_BTNS, '📚 Выберите действие:')
    elif message.text == MENU_BTNS[2]:
        buyouts = ShowBuyouts(message.from_user.id)
        if not buyouts:
            BOT.send_message(message.from_user.id, '❌ Вы еще не участвовали в выкупах!')
        else:
            BOT.send_message(message.from_user.id, buyouts)
        ShowButtons(message, MENU_BTNS, '📚 Выберите действие:')
    elif message.text == MENU_BTNS[3]:
        BOT.send_message(message.from_user.id, '📚 Помощь по боту:\n'
                                               '1. Для начала регистрации нажмите "Регистрация 📝"\n'
                                               '2. Для просмотра доступных выкупов нажмите "Доступные выкупы 🎁"\n'
                                               '3. Для просмотра ваших выкупов нажмите "Мои выкупы 🎁"')
    else:
        BOT.send_message(message.from_user.id, '❌ Неизвестная команда!')
        ShowButtons(message, MENU_BTNS, '📚 Выберите действие:')


if __name__ == '__main__':
    SERVICE = BuildService()
    CUR, CON = AuthorizeDatabase()
    Main()
