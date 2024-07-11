from source import *


def AuthorizeDatabase():
    conn = connect(
        dbname="buyouts",
        user="test",
        password=PASSWORD,
        host=HOST,
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
    CUR.execute("INSERT INTO users (id, sex) VALUES (%s, %s)", (message.from_user.id, sex))
    CON.commit()
    USER_STATES[message.from_user.id] = STATES[1]
    BOT.send_message(message.from_user.id, '❔ Введите ваше имя:')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == STATES[1])
def AcceptName(message: Message) -> None:
    Stamp(f'User {message.from_user.id} entering name', 'i')
    name = message.text.strip()
    if not match(r'^[A-Za-zА-Яа-яЁё-]+$', name) or len(name) > MAX_LEN_NAME:
        BOT.send_message(message.from_user.id, '❌ Пожалуйста, введите корректное имя:')
        return
    CUR.execute("UPDATE users SET name = %s WHERE id = %s", (name, message.from_user.id))
    CON.commit()
    USER_STATES[message.from_user.id] = STATES[2]
    BOT.send_message(message.from_user.id, '❔ Введите последние 4 цифры номера телефона без других знаков:')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == STATES[2])
def AcceptNumDigits(message: Message) -> None:
    Stamp(f'User {message.from_user.id} entering number digits', 'i')
    if len(message.text.strip()) != 4 or not message.text.strip().isdigit():
        BOT.send_message(message.from_user.id, '❌ Пожалуйста, введите корректные последние 4 цифры номера телефона:')
        return
    CUR.execute("UPDATE users SET num_digits = %s WHERE id = %s", (message.text.strip(), message.from_user.id))
    CON.commit()
    CUR.execute("SELECT * FROM cities")
    cities = [row[0] for row in CUR.fetchall()]
    USER_STATES[message.from_user.id] = STATES[3]
    InlineButtons(message, tuple(cities), '❔ Выберите ваш город:', 'city_')


@BOT.callback_query_handler(func=lambda call: call.data.startswith('city_'))
def HandleCityCallback(call: CallbackQuery) -> None:
    Stamp(f'User {call.from_user.id} choosing city', 'i')
    city = call.data.split('_')[1]
    CUR.execute("UPDATE users SET city = %s WHERE id = %s", (city, call.from_user.id))
    CON.commit()
    USER_STATES[call.from_user.id] = STATES[4]
    BOT.send_message(call.from_user.id, '❔ Отправьте видео истории покупок:')


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
    ShowButtons(message, MENU_BTNS, '📚 Выберите действие:')


def PrepareAvailableBuyouts() -> dict | None:
    CUR.execute('SELECT * FROM upcoming_buyouts')
    buyouts = CUR.fetchall()
    if not buyouts:
        return
    info = {}
    for buyout in buyouts:
        if buyout[3] == 'return':
            typage = 'с возвратом'
        else:
            typage = 'оставить себе'
        if buyout[1] is None:
            reward = AWARD_BUYOUT
        else:
            reward = AWARD_FEEDBACK + AWARD_BUYOUT
        info[buyout[5]] = f'🕘 Планируемое время: {buyout[0]}\n' \
                          f'📃 Текст отзыва: {buyout[1]}\n' \
                          f'🔗 Ссылка на товар: {buyout[2]}\n' \
                          f'❗️ Тип: {typage}\n' \
                          f'💰 Вознаграждение: {reward} руб.\n' \
                          f'📄 Запрос: {buyout[4]}\n'
    return info


def ShowMyBuyouts(user_id: int) -> None:
    CUR.execute("""SELECT b.date_plan,
                                    b.feedback,
                                     p.good_link,
                                     p.type,
                                     p.request,
                                     b.id
                              FROM buyouts AS b
                              JOIN plans AS p ON p.id = b.plan
                              WHERE b.user_id = %s""", (user_id,))
    buyouts = CUR.fetchall()
    if not buyouts:
        BOT.send_message(user_id, '❌ Вы еще не участвовали в выкупах!')
        return
    for buyout in buyouts:
        if buyout[3] == 'return':
            typage = 'с возвратом'
        else:
            typage = 'оставить себе'
        if buyout[1] is None:
            reward = AWARD_BUYOUT
        else:
            reward = AWARD_FEEDBACK + AWARD_BUYOUT
        BOT.send_message(user_id, f'🕘 Планируемое время: {buyout[0]}\n'
                                  f'📃 Текст отзыва: {buyout[1]}\n'
                                  f'🔗 Ссылка на товар: {buyout[2]}\n'
                                  f'❗️ Тип: {typage}\n'
                                  f'💰 Вознаграждение: {reward} руб.\n'
                                  f'📄 Запрос: {buyout[4]}\n\n')


def SendAvailableBuyouts(user_id: int) -> None:
    buyouts = PrepareAvailableBuyouts()
    if not buyouts:
        BOT.send_message(user_id, '❌ На данный момент нет доступных выкупов!')
    else:
        for one in buyouts.keys():
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Беру!", callback_data=f"take_{one}")]])
            BOT.send_message(user_id, buyouts[one], reply_markup=keyboard)


@BOT.callback_query_handler(func=lambda call: call.data.startswith('take_'))
def HandleTakeCallback(call: CallbackQuery) -> None:
    buyout_id = call.data.split('_')[1]
    try:
        CUR.execute("UPDATE buyouts SET user_id = %s WHERE id = %s", (call.from_user.id, buyout_id))
        CON.commit()
        BOT.send_message(call.from_user.id, '✅ Вы успешно записаны на выкуп!')
    except Exception as e:
        BOT.send_message(call.from_user.id, '❌ Произошла ошибка при записи на выкуп!')
        Stamp(f'Error while handling take callback: {str(e)}', 'e')


@BOT.message_handler(content_types=['text'])
def Start(message: Message) -> None:
    Stamp(f'User {message.from_user.id} requested {message.text}', 'i')
    if message.text == '/start':
        USER_STATES[message.from_user.id] = STATES[0]
        ShowButtons(message, SEX_BTNS, f'👋 Привет, {message.from_user.first_name}! '
                                       f'\nПожалуйста, укажите ваш пол:')
    elif message.text == MENU_BTNS[0]:
        SendAvailableBuyouts(message.from_user.id)
        ShowButtons(message, MENU_BTNS, '📚 Выберите действие:')
    elif message.text == MENU_BTNS[1]:
        ShowMyBuyouts(message.from_user.id)
        ShowButtons(message, MENU_BTNS, '📚 Выберите действие:')
    else:
        BOT.send_message(message.from_user.id, '❌ Неизвестная команда!')
        ShowButtons(message, MENU_BTNS, '📚 Выберите действие:')


if __name__ == '__main__':
    SERVICE = BuildService()
    CUR, CON = AuthorizeDatabase()
    Main()
