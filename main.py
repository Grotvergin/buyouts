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
    ShowButtons(message, MENU_BTNS, '❔ Выберите действие:')


def PrepareBuyouts(user_id: int = None) -> dict | None:
    if user_id:
        CUR.execute('SELECT * FROM fetch_buyouts_for_user(%s)', (user_id,))
    else:
        CUR.execute('SELECT * FROM upcoming_buyouts')
    buyouts = CUR.fetchall()
    if not buyouts:
        return
    info = {}
    for buyout in buyouts:
        text = ''
        status = STATUSES[0]
        reward = AWARD_BUYOUT
        if buyout[0]:
            text += f'📍 ID ПВЗ (в будущем – адрес): {buyout[0]}\n'
        if buyout[1]:
            status = STATUSES[1]
        if buyout[2]:
            text += f'🕘 Планируемое время выкупа: {buyout[2]}\n'
        if buyout[3]:
            text += f'🏁 Фактическое время выкупа: {buyout[3]}\n'
            status = STATUSES[2]
        if buyout[4]:
            text += f'🚛 Доставлен на ПВЗ: {buyout[4]}\n'
            status = STATUSES[3]
        if buyout[5]:
            text += f'📤 Забран из ПВЗ: {buyout[5]}\n'
            status = STATUSES[4]
        if buyout[6]:
            text += f'📝 Отзыв: {buyout[6]}\n'
            reward += AWARD_FEEDBACK
        if buyout[7]:
            text += f'🔗 Ссылка: {buyout[7]}\n'
        if buyout[8]:
            text += f'🔸 Тип: {TYPAGES[buyout[8]]}\n'
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
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(btn_text, callback_data=f"{clbk_data}{one}")]])
                BOT.send_message(user_id, buyouts[one], reply_markup=keyboard)

    if not sent_at_least_one:
        if all_statuses:
            BOT.send_message(user_id, f'❌ Нет никаких выкупов!')
        else:
            BOT.send_message(user_id, f'❌ Нет выкупов со статусом {status}!')


def ShowUserInfo(user_id: int) -> None:
    CUR.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = CUR.fetchone()
    if not user:
        BOT.send_message(user_id, '❌ Вы не зарегистрированы в системе!')
        return
    text = f'👤 Имя: {user[2]}\n' \
           f'🚹 Пол: {"Мужской" if user[1] == "M" else "Женский"}\n' \
           f'📞 Последние 4 цифры номера: {user[3]}\n' \
           f'🏙 Город: {user[4]}\n' \
           f'📹 Видео: {user[6]}\n' \
           f'🆔 ID: {user[0]}\n' \
           f'📅 Дата регистрации: {user[5]}\n' \
           f'🆕 Дата обновления QR-кода: {user[7]}\n' \
           f'🔳 QR-код: {user[8]}\n'
    BOT.send_message(user_id, text)


@BOT.callback_query_handler(func=lambda call: call.data.startswith(CALLBACKS[0]))
def HandleChooseCallback(call: CallbackQuery) -> None:
    buyout_id = call.data.split('_')[1]
    try:
        CUR.execute("UPDATE buyouts SET user_id = %s WHERE id = %s", (call.from_user.id, buyout_id))
        CON.commit()
        BOT.send_message(call.from_user.id, '✅ Вы успешно записаны на выкуп!')
    except Exception as e:
        BOT.send_message(call.from_user.id, '❌ Произошла ошибка при записи на выкуп!')
        Stamp(f'Error while handling take callback: {str(e)}', 'e')


@BOT.callback_query_handler(func=lambda call: call.data.startswith(CALLBACKS[1]))
def HandleOrderedCallback(call: CallbackQuery) -> None:
    buyout_id = call.data.split('_')[1]
    try:
        CUR.execute("UPDATE buyouts SET date_fact = CURRENT_TIMESTAMP AT TIME ZONE 'MSK' WHERE id = %s", (buyout_id,))
        CON.commit()
        BOT.send_message(call.from_user.id, '✅ Четко, вижу заказал!')
    except Exception as e:
        BOT.send_message(call.from_user.id, '❌ Произошла ошибка при обновлении статуса!')
        Stamp(f'Error while handling ordered callback: {str(e)}', 'e')


@BOT.callback_query_handler(func=lambda call: call.data.startswith(CALLBACKS[2]))
def HandleArrivedCallback(call: CallbackQuery) -> None:
    buyout_id = call.data.split('_')[1]
    try:
        CUR.execute("UPDATE buyouts SET date_delivery = CURRENT_TIMESTAMP AT TIME ZONE 'MSK' WHERE id = %s", (buyout_id,))
        CON.commit()
        BOT.send_message(call.from_user.id, '✅ Четко, вижу приехал!')
    except Exception as e:
        BOT.send_message(call.from_user.id, '❌ Произошла ошибка при обновлении статуса!')
        Stamp(f'Error while handling arrived callback: {str(e)}', 'e')


@BOT.callback_query_handler(func=lambda call: call.data.startswith(CALLBACKS[3]))
def HandlePickedUpCallback(call: CallbackQuery) -> None:
    buyout_id = call.data.split('_')[1]
    try:
        CUR.execute("UPDATE buyouts SET date_pick_up = CURRENT_TIMESTAMP AT TIME ZONE 'MSK' WHERE id = %s", (buyout_id,))
        CON.commit()
        BOT.send_message(call.from_user.id, '✅ Четко, вижу забрал!')
    except Exception as e:
        BOT.send_message(call.from_user.id, '❌ Произошла ошибка при обновлении статуса!')
        Stamp(f'Error while handling picked up callback: {str(e)}', 'e')


@BOT.callback_query_handler(func=lambda call: call.data.startswith(CALLBACKS[4]))
def HandleFeedbackCallback(call: CallbackQuery) -> None:
    buyout_id = call.data.split('_')[1]
    try:
        CON.commit()
        BOT.send_message(call.from_user.id, '✅ Четко, вижу оценил!')
    except Exception as e:
        BOT.send_message(call.from_user.id, '❌ Произошла ошибка при обновлении статуса!')
        Stamp(f'Error while handling feedback callback: {str(e)}', 'e')


@BOT.message_handler(content_types=['text'])
def Start(message: Message) -> None:
    Stamp(f'User {message.from_user.id} requested {message.text}', 'i')
    if message.text == '/start':
        USER_STATES[message.from_user.id] = STATES[0]
        ShowButtons(message, SEX_BTNS, f'👋 Привет, {message.from_user.first_name}! '
                                       f'\nПожалуйста, укажите ваш пол:')
    else:
        if message.text == MENU_BTNS[0]:
            SendBuyouts(message.from_user.id, STATUSES[0])
        elif message.text == MENU_BTNS[1]:
            SendBuyouts(message.from_user.id, STATUSES[1])
        elif message.text == MENU_BTNS[2]:
            SendBuyouts(message.from_user.id, STATUSES[2])
        elif message.text == MENU_BTNS[3]:
            SendBuyouts(message.from_user.id, STATUSES[3])
        elif message.text == MENU_BTNS[4]:
            SendBuyouts(message.from_user.id, STATUSES[4])
        elif message.text == MENU_BTNS[5]:
            SendBuyouts(message.from_user.id, all_statuses=True)
        elif message.text == MENU_BTNS[6]:
            ShowUserInfo(message.from_user.id)
        else:
            BOT.send_message(message.from_user.id, '❌ Неизвестная команда!')
        ShowButtons(message, MENU_BTNS, '❔ Выберите действие:')


if __name__ == '__main__':
    SERVICE = BuildService()
    CUR, CON = AuthorizeDatabase()
    Main()
