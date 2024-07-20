from source import *


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == REG_STATES[0])
def AcceptSex(message: Message) -> None:
    Stamp(f'User {message.from_user.id} choosing sex', 'i')
    if message.text not in SEX_BTNS:
        ShowButtons(message, SEX_BTNS, '❌ Пожалуйста, введите один из предложенных вариантов:')
        return
    sex = 'M' if message.text == SEX_BTNS[0] else 'F'
    CUR.execute("UPDATE users SET sex = %s WHERE id = %s", (sex, message.from_user.id))
    CON.commit()
    USER_STATES[message.from_user.id] = REG_STATES[1]
    BOT.send_message(message.from_user.id, '❔ Введите ваше имя:')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == REG_STATES[1])
def AcceptName(message: Message) -> None:
    Stamp(f'User {message.from_user.id} entering name', 'i')
    name = message.text.strip()
    if not match(r'^[А-Яа-яЁё-]+$', name) or len(name) > MAX_LEN_NAME:
        BOT.send_message(message.from_user.id, '❌ Пожалуйста, введите корректное имя:')
        return
    CUR.execute("UPDATE users SET name = %s WHERE id = %s", (name, message.from_user.id))
    CON.commit()
    USER_STATES[message.from_user.id] = REG_STATES[2]
    BOT.send_message(message.from_user.id, '❔ Введите вашу фамилию:')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == REG_STATES[2])
def AcceptSurname(message: Message) -> None:
    Stamp(f'User {message.from_user.id} entering surname', 'i')
    surname = message.text.strip()
    if not match(r'^[А-Яа-яЁё-]+$', surname) or len(surname) > MAX_LEN_SURNAME:
        BOT.send_message(message.from_user.id, '❌ Пожалуйста, введите корректную фамилию:')
        return
    CUR.execute("UPDATE users SET surname = %s WHERE id = %s", (surname, message.from_user.id))
    CON.commit()
    USER_STATES[message.from_user.id] = REG_STATES[3]
    BOT.send_message(message.from_user.id, '❔ Введите 11 цифр номера телефона без других знаков, например, 89151234567:')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == REG_STATES[3])
def AcceptNumDigits(message: Message) -> None:
    Stamp(f'User {message.from_user.id} entering phone', 'i')
    if len(message.text.strip()) != 11 or not message.text.strip().isdigit():
        BOT.send_message(message.from_user.id, '❌ Пожалуйста, введите номер телефона в корректном формате, например, 89151234567:')
        return
    CUR.execute("UPDATE users SET phone = %s WHERE id = %s", (message.text.strip(), message.from_user.id))
    CON.commit()
    CUR.execute("SELECT * FROM cities")
    cities = [row[0] for row in CUR.fetchall()]
    USER_STATES[message.from_user.id] = REG_STATES[4]
    InlineButtons(message.from_user.id, cities, '❔ Выберите ваш город:', [f'city_{city}' for city in cities])


@BOT.callback_query_handler(func=lambda call: call.data.startswith('city_'))
def HandleCityCallback(call: CallbackQuery) -> None:
    Stamp(f'User {call.from_user.id} choosing city', 'i')
    city = call.data.split('_')[1]
    CUR.execute("UPDATE users SET city = %s WHERE id = %s", (city, call.from_user.id))
    CON.commit()
    USER_STATES[call.from_user.id] = REG_STATES[5]
    BOT.send_message(call.from_user.id, '❔ Отправьте видео истории покупок:')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == REG_STATES[5], content_types=['video', 'document', 'text'])
def HandleVideoLink(message: Message) -> None:
    Stamp(f'User {message.from_user.id} uploading video', 'i')
    video_file_info = None
    if message.video:
        video_file_info = BOT.get_file(message.video.file_id)
    elif message.document and message.document.mime_type.startswith('video/'):
        video_file_info = BOT.get_file(message.document.file_id)
    if not video_file_info:
        BOT.send_message(message.from_user.id, '❌ Пожалуйста, отправьте видео:')
        return
    BOT.send_message(message.from_user.id, '🔄 Ваше видео загружается, пожалуйста, подождите...')
    try:
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
        remove(path)
    except Exception as e:
        BOT.send_message(message.from_user.id, f'❌ Произошла ошибка во время загрузки файла!')
        Stamp(f'Error while uploading a file: {str(e)}', 'e')
    USER_STATES[message.from_user.id] = REG_STATES[6]
    ShowButtons(message, WALLET_BTNS, '❔ У вас есть кошелек WB с привязанным номером?')


@BOT.message_handler(func=lambda message: USER_STATES.get(message.from_user.id) == REG_STATES[6])
def VerifyWallet(message: Message) -> None:
    Stamp(f'User {message.from_user.id} verifying wallet', 'i')
    if message.text not in WALLET_BTNS:
        ShowButtons(message, WALLET_BTNS, '❌ Пожалуйста, введите один из предложенных вариантов:')
    elif message.text == WALLET_BTNS[0]:
        del USER_STATES[message.from_user.id]
        BOT.send_message(message.from_user.id, '✔️ Спасибо, ваши данные отправлены на проверку!')
        ShowButtons(message, MENU_BTNS, '❔ Выберите действие:')
    elif message.text == WALLET_BTNS[1]:
        ShowButtons(message, WALLET_BTNS, '☢️ Привяжите кошелек!')


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
                InlineButtons(user_id, [btn_text], buyouts[one], [f'{clbk_data}{one}'])
    if not sent_at_least_one:
        if all_statuses:
            BOT.send_message(user_id, f'❌ Нет никаких выкупов!')
        else:
            BOT.send_message(user_id, f'❌ Нет выкупов со статусом {status}!')


def ShowUserInfo(user_id: int) -> str | None:
    CUR.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = CUR.fetchone()
    if not user:
        BOT.send_message(user_id, '❌ Вы не зарегистрированы в системе!')
        return
    text = f'🆔 ID: {user[0]}\n' \
           f'🚹 Пол: {user[1]}\n' \
           f'👤 Имя: {user[2]}\n' \
           f'👥 Фамилия: {user[3]}\n' \
           f'📞 Телефон: {user[4]}\n' \
           f'🏙 Город: {user[5]}\n' \
           f'📅 Дата подтверждения: {user[6]}\n' \
           f'📹 Видео: {user[7]}\n' \
           f'🆕 Дата обновления QR-кода: {user[7]}\n' \
           f'🔳 QR-код: {user[8]}\n'
    return text


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
        CUR.execute("SELECT good_link FROM plans AS p JOIN buyouts AS b ON p.id = b.plan_id WHERE b.id = %s", (buyout_id,))
        good_link = CUR.fetchone()[0]
        CUR.execute("UPDATE buyouts SET fact_time = NOW(), price = %s WHERE id = %s", (GetPriceGood(good_link), buyout_id))
        CON.commit()
        BOT.send_message(call.from_user.id, '✅ Четко, вижу заказал!')
    except Exception as e:
        BOT.send_message(call.from_user.id, '❌ Произошла ошибка при обновлении статуса!')
        Stamp(f'Error while handling ordered callback: {str(e)}', 'e')


@BOT.callback_query_handler(func=lambda call: call.data.startswith(CALLBACKS[2]))
def HandleArrivedCallback(call: CallbackQuery) -> None:
    buyout_id = call.data.split('_')[1]
    try:
        CUR.execute("UPDATE buyouts SET delivery_time = NOW() WHERE id = %s", (buyout_id,))
        CON.commit()
        BOT.send_message(call.from_user.id, '✅ Четко, вижу приехал!')
    except Exception as e:
        BOT.send_message(call.from_user.id, '❌ Произошла ошибка при обновлении статуса!')
        Stamp(f'Error while handling arrived callback: {str(e)}', 'e')


@BOT.callback_query_handler(func=lambda call: call.data.startswith(CALLBACKS[3]))
def HandlePickedUpCallback(call: CallbackQuery) -> None:
    buyout_id = call.data.split('_')[1]
    try:
        CUR.execute("UPDATE buyouts SET pick_up_time = NOW() WHERE id = %s", (buyout_id,))
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


def AcceptNewUser(message: Message) -> None:
    Stamp(f'User {message.from_user.id} registering at first', 'i')
    CUR.execute("SELECT id FROM users WHERE id = %s", (message.from_user.id,))
    if CUR.fetchone():
        BOT.send_message(message.from_user.id, '⚠️ Вы уже зарегистрированы!')
    else:
        CUR.execute("INSERT INTO users (id) VALUES (%s)", (message.from_user.id,))
        CON.commit()
        USER_STATES[message.from_user.id] = REG_STATES[0]
        BOT.send_message(message.from_user.id, '❔ Укажите ваш пол:')


def ShowUnconfirmedUsers() -> None:
    CUR.execute('SELECT id FROM users WHERE conf_time IS NULL')
    users = CUR.fetchall()
    if not users:
        BOT.send_message(ADM_ID, '⚠️ Нет неподтвержденных пользователей!')
        return
    for user in users:
        InlineButtons(ADM_ID,['✅ Принять', '❌ Отклонить'], ShowUserInfo(user[0]),
                      [f'accept_{user[0]}', f'reject_{user[0]}'])


@BOT.callback_query_handler(func=lambda call: call.data.startswith('accept_'))
def HandleAcceptUser(call: CallbackQuery) -> None:
    user_id = call.data.split('_')[1]
    try:
        CUR.execute("UPDATE users SET conf_time = NOW() WHERE id = %s", (user_id,))
        CON.commit()
        Stamp(f'User {user_id} accepted', 'i')
        BOT.send_message(user_id, '✅ Ваши данные подтверждены!')
        ADM.send_message(call.message.chat.id, f'✅ Пользователь {user_id} успешно принят!')
    except Exception as e:
        ADM.send_message(call.message.chat.id, '⚠️ Произошла ошибка при подтверждении пользователя!')
        Stamp(f'Error while handling accept callback: {str(e)}', 'e')


@BOT.callback_query_handler(func=lambda call: call.data.startswith('reject_'))
def HandleRejectUser(call: CallbackQuery) -> None:
    user_id = call.data.split('_')[1]
    try:
        Stamp(f'User {user_id} rejected', 'i')
        BOT.send_message(user_id, '❌ Ваши данные отклонены!')
        ADM.send_message(call.message.chat.id, f'❌ Пользователь {user_id} отклонен!')
    except Exception as e:
        ADM.send_message(call.message.chat.id, '⚠️ Произошла ошибка при отклонении пользователя!')
        Stamp(f'Error while handling reject callback: {str(e)}', 'e')


@BOT.message_handler(content_types=['text'])
def Start(message: Message) -> None:
    Stamp(f'User {message.from_user.id} requested {message.text}', 'i')
    if message.text == '/start':
        AcceptNewUser(message)
    elif message.text == MENU_BTNS[0]:
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
        BOT.send_message(message.from_user.id, ShowUserInfo(message.from_user.id))
    else:
        BOT.send_message(message.from_user.id, '❌ Неизвестная команда!')
    ShowButtons(message, MENU_BTNS, '❔ Выберите действие:')


@ADM.message_handler(content_types=['text'])
def Start(message: Message) -> None:
    Stamp(f'Admin {message.from_user.id} requested {message.text}', 'i')
    if message.text == '/start':
        ADM.send_message(message.from_user.id, f'🥹 Здравствуйте, администратор {message.from_user.username}!'
                                               'Сюда будут приходить уведомления о новых пользователях')
        ShowButtons(message, ADM_BTNS, '❔ Выберите действие:')
    elif message.text == ADM_BTNS[0]:
        SendBuyouts(message.from_user.id)
    else:
        ShowButtons(message, ADM_BTNS, '❌ Неизвестная команда!')


if __name__ == '__main__':
    SERVICE = BuildService()
    CUR, CON = AuthorizeDatabase()
    Main()
