#
#                      \`*-.
#                       )  _`-.
#                      .  : `. .
#                      : _   '  \
#                      ; *` _.   `*-._
#                      `-.-'          `-.
#                        ;       `       `.
#                        :.       .        \
#                        . \  .   :   .-'   .
#                        '  `+.;  ;  '      :
#                        :  '  |    ;       ;-.
#                        ; '   : :`-:     _.`* ;
#                    .*' /  .*' ; .*`- +'  `*'
#                     `*-*   `*-*  `*-*'
#
#        _   _  _  _            _               _
#       | \ | |(_)| |          | |             | |
#       |  \| | _ | | __  ___  | |  ___  _ __  | | __  ___
#       | . ` || || |/ / / _ \ | | / _ \| '_ \ | |/ / / _ \
#       | |\  || ||   < | (_) || ||  __/| | | ||   < | (_) |
#       \_| \_/|_||_|\_\ \___/ |_| \___||_| |_||_|\_\ \___/
#                                _      _     _        _
#                               | |    (_)   (_)      (_)
#        _ __ ___    ___  _ __  | |__   _     _   ___  _  ___
#       | '_ ` _ \  / _ \| '_ \ | '_ \ | |   | | / __|| |/ __|
#       | | | | | ||  __/| |_) || | | || |   | || (__ | |\__ \
#       |_| |_| |_| \___|| .__/ |_| |_||_|   |_| \___||_||___/
#                        | |
#                        |_|

from config import *

incels = sync_get_users()

class FSMFillForm(StatesGroup):
    verified = State()
    banned = State()
    sending_photo = State()
    rating = State()
    sendDM = State()
    sendQuote = State()
    inserting_url = State()
    inserting_caption = State()
    inserting_hour = State()
    inserting_minute = State()


class RateCallBack(CallbackData, prefix="rating"):
    r: int
    photo_id: int
    mailing: int

class ModerateCallBack(CallbackData, prefix="moderate"):
    action: int
    photo_id: int
    creator: str


class GroupCallBack(CallbackData, prefix="group"):
    group_id: int


class GroupSettings(CallbackData, prefix="public_settings"):
    action: int
    group_id: int
    amount: int = 0
    date: int = 0


class NotifySettings(CallbackData, prefix="notify"):
    action: int
    week: int = 0
    hour: int = 0
    minute: int = 0


class AdminCallBack(CallbackData, prefix="admin"):
    action: int
    user_id: int = 0


class ConfirmCallBack(CallbackData, prefix="confirm"):
    action: int
    photo_id: int = 0


class ManageSettings(CallbackData, prefix="manage"):
    action: int
    photo_id: Union[int, str] = 0
    back_ids: Union[int, str] = 0
    message_to_delete: Union[int, str] = 0


send_slut_button: KeyboardButton = KeyboardButton(
    text='Разослать фото')
statistics_button: KeyboardButton = KeyboardButton(
    text='Статистика 📊')
edit_rate: KeyboardButton = KeyboardButton(
    text='Изменить последнюю оценку ✏️')
quote_button: KeyboardButton = KeyboardButton(
    text='Цитата 💬')
settings_button: KeyboardButton = KeyboardButton(
    text='Настройки ⚙️')
resend: KeyboardButton = KeyboardButton(
    text='Фото из очереди 🌆')
basic_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[statistics_button, quote_button], [edit_rate, resend]], resize_keyboard=True)
admin_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[statistics_button, quote_button], [edit_rate, resend], [settings_button]], resize_keyboard=True)
not_incel_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[statistics_button]], resize_keyboard=True, input_field_placeholder='Жду фоточку 🥰')

cancel_photo: KeyboardButton = KeyboardButton(
    text='Не отправлять фото')
keyboard3: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[cancel_photo]], resize_keyboard=True,
    one_time_keyboard=True)


class check_username(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text[1:5] == 'del_'


class ban_username(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text[1:5] == 'ban_'


class unban_username(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text[1:7] == 'unban_'


class add_birthday_command(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text[1:13] == 'add_birthday'


class clear_states_username(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text[1:4] == 'cs_'


class change_queue_username(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text[1:4] == 'cq_'


class change_average_filter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text[1:6] == 'cavg_'



class send_DM(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text[1:6] == 'send_'


@dp.message(StateFilter(FSMFillForm.banned))
async def urbanned(message: Message, state: FSMContext):
    await message.answer(random.choice(emoji_banned) + ' ' + random.choice(replicas['banned']).replace('$', '"'),
                         reply_markup=ReplyKeyboardRemove())


async def get_keyboard(user_id: int):
    if user_id in await get_users():
        queue_len = len(await get_queue(user_id))
        input_field = 'Сейчас новых фоточек нет, но ты можешь кинуть свою 🥰'
        if queue_len != 0:
            input_field = f'В очереди {queue_len} 🚨 Оцени фотки! 😡'
    if user_id in await get_admins():
        admin_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
            keyboard=[[statistics_button, quote_button], [edit_rate, resend], [settings_button]], resize_keyboard=True,
            input_field_placeholder=input_field)
        return admin_keyboard
    elif user_id in await get_users():
        basic_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
            keyboard=[[statistics_button, quote_button], [edit_rate, resend]], resize_keyboard=True, input_field_placeholder=input_field)
        return basic_keyboard
    if len(await get_avgs_not_incel(user_id)) > 5:
        return not_incel_keyboard
    return None


@dp.message(F.text, ban_username())
async def ban_username_command(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='Иди нахуй!', reply_markup=await get_keyboard(message.from_user.id))
        return
    s = message.text[5:]
    await delete_row_in_average(await get_id_by_username(s))
    result = await get_ban(await get_id_by_username(s))
    if result == 0:
        await message.answer(text=f'Строка с username: <i>"{s}"</i> не найдена в таблице')
    else:
        await message.answer(text=f'Пользователь <i>@{s}</i> был успешно забанен! Нахуй его!')


@dp.message(F.text, unban_username())
async def unban_username_command(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='Иди нахуй!', reply_markup=await get_keyboard(message.from_user.id))
        return
    s = message.text[7:]
    result = await get_unban(await get_id_by_username(s))
    if result == 0:
        await message.answer(text=f'Строка с username=<i>"{s}"</i> не найдена в таблице')
    else:
        await message.answer(text=f'Пользователь <i>@{s}</i> был успешно разбанен! Зря...')


@dp.message(F.text, add_birthday_command(), F.from_user.id.in_(incels))
async def add_birthday_func(message: Message):
    pattern = r"/add_birthday_(\w+)_(\d{4}-\d{2}-\d{2})"
    match = re.match(pattern, message.text)
    if match:
        username = match.group(1)
        date = match.group(2)
        try:
            await add_new_birthday(await get_id_by_username(username), int(datetime.datetime.strptime(date, '%Y-%m-%d').timestamp()))
            await message.answer(f'Ты добавил ДР <i>{date}</i> для пользователя <b>@{username}</b>')
        except Exception as e:
            await message.answer(f'Произошла ошибка!\n{e}')
    else:
        await message.answer("Не удалось извлечь имя пользователя и дату из сообщения.")


@dp.message(F.text, clear_states_username())
async def clear_state_username(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='Иди нахуй!', reply_markup=await get_keyboard(message.from_user.id))
        return
    s = message.text[4:]
    try:
        await add_current_state(id=await get_id_by_username(s), num=0)
        await message.answer(text=f'Состояние {s} очищено 🫡')
    except Exception as e:
        await message.answer(text=f'Произошла ошибка! Код 11\n{e}')


@dp.message(F.text, change_queue_username())
async def change_queue_command(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='Иди нахуй!', reply_markup=await get_keyboard(message.from_user.id))
        return
    s = message.text[4:]
    try:
        username = s[:s.find('\n')]
        new_queue = s[s.find('\n') + 1:]
        await change_queue(await get_id_by_username(username), new_queue)
        await message.answer(f'Очередь для {username} изменена на {new_queue}')

    except Exception as e:
        await message.answer(text=f'Произошла ошибка! Код 11\n{e}')


@dp.message(F.text, change_average_filter())
async def change_average_command(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='Иди нахуй!', reply_markup=await get_keyboard(message.from_user.id))
        return
    pattern = r'/(\w+)_([\w\d]+)_([\d]+)_([\d]+)'
    match = re.match(pattern, message.text)

    if match:
        try:
            username = match.group(2)
            sum_value = int(match.group(3))
            amount = int(match.group(4))
            user_id = await get_id_by_username(username)
            if user_id is None or sum_value <= 0 or amount <= 0:
                await message.answer(text=f'Произошла ошибка! Ты еблан')
                return
            await change_avg_rate(user_id, sum_value, amount)
            await message.answer(f'Значения для {username} были изменены на {sum_value}, {amount}')
        except Exception as e:
            await message.answer(text=f'Произошла ошибка! Ты еблан\n{e}')
    else:
        await message.answer(text=f'Произошла ошибка! Неправильный паттерн')


@dp.message(Command(commands='new_quote'), F.from_user.id.in_(incels))
async def send_quote_dada(message: Message, state: FSMContext):
    incels = await get_users()
    await message.answer(text='Пришли цитату в формате фото или текста')
    await state.set_state(FSMFillForm.sendQuote)

cnt = 1

@dp.message(Command(commands='test'), F.from_user.id.in_(incels))
async def test_something(message: Message):
    #await message.answer(text='Эта команда для тестирования новых функций')
    await message.answer_photo(photo=await get_photo_id_by_id(random.randint(1,1970)), reply_markup=
            InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Еще', callback_data='more1')]]))
    global cnt
    cnt += 1


@dp.message(Command(commands='amogus'))
async def amogus_command(message: Message):
    await message.answer(text=random.choice(replicas['amogus']), reply_markup=await get_keyboard(message.from_user.id))


@dp.message(Command(commands='pepe'))
async def pepe_command(message: Message):
    await message.answer(text=random.choice(replicas['pepe']), reply_markup=await get_keyboard(message.from_user.id))


@dp.message(Command(commands='phasalov'))
async def phasalov_command(message: Message):
    n = random.randint(1, 100)
    txt = (f"```C\nfor (int i = 0; i < k; i++) {'{'}\n"
           f"    if (n == {n}) {'{'}\n"
           f"        n = {n};\n"
           f"    {'}'}\n"
           f"{'}'}```")
    await message.answer(text=txt, reply_markup=await get_keyboard(message.from_user.id), parse_mode="MarkdownV2")


@dp.callback_query(F.data == 'more1')
async def more1(callback: CallbackQuery):
    global cnt
    await callback.message.edit_media(media=InputMediaPhoto(media=await get_photo_id_by_id(random.randint(1, 1970))), reply_markup=
            InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Еще', callback_data='more1')]]))
    cnt+=1


@dp.message(Command(commands='send_tier_list'), F.from_user.id.in_(incels))
async def send_tier_and_delete(message: Message, state: FSMContext):
    incels = await get_users()
    await message.answer(text='Тир лист начал генерироваться...')
    await weekly_tierlist(message.from_user.id)


@dp.message(Command(commands='stat'))
async def send_tier_and_delete(message: Message, state: FSMContext):
    await stat_photo(message, state)


# @dp.message(Command(commands='sex'))
# async def send_tier_and_delete(message: Message, state: FSMContext):
#     pass


@dp.message(Command(commands='delete_tier_list'))
async def send_tier_and_delete(message: Message, state: FSMContext):
    if message.from_user.id != 972753303:
        await message.answer(text='Иди нахуй!')
    else:
        array = [[InlineKeyboardButton(text='Удалить! Я КОНЧ! 😈',callback_data='ya_gay_delete_tier_db'),
                  InlineKeyboardButton(text='Не удалять ❌',callback_data='not_delete')]]
        await message.answer(
            text='<b>ВСЯ БД БУДЕТ СТЕРТА! Ты уверен?</b>\n<span class="tg-spoiler">Админ может дать пизды!</span>',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=array))


@dp.message(Command(commands='upd_file'))
async def update_replicas_file(message: Message, state: FSMContext):
    global replicas
    if message.from_user.id != 972753303:
        await message.answer(text='Иди нахуй!')
    else:
        if message.document and message.document.mime_type == 'text/plain':
            f = await bot.get_file(message.document.file_id)
            f_path = f.file_path
            await bot.download_file(file_path=f_path, destination=f'{os.path.dirname(__file__)}/DB/replicas2.txt')
            try:
                with open(f'{os.path.dirname(__file__)}/DB/replicas2.txt', 'r', encoding='utf-8') as file:
                    replicas = json.load(file)
                shutil.copyfile(f'{os.path.dirname(__file__)}/DB/replicas2.txt', f'{os.path.dirname(__file__)}/DB/replicas.txt')
                os.remove(f'{os.path.dirname(__file__)}/DB/replicas2.txt')
                await message.answer('Новый файл сохранен')
            except Exception as e:
                await bot.send_message(chat_id=972753303,
                                       text=f'Произошла ошибка при открытии файла <i>"replicas.txt"</i>\n{e}')
        else:
            await message.answer('❗️Ты забыл прикрепить файл или прикрепил файл не того типа')


@dp.callback_query(F.data.in_(['ya_gay_delete_tier_db',
                               'not_delete']))
async def permanently_delete_db(callback: CallbackQuery):
    if callback.data == 'ya_gay_delete_tier_db':
        await callback.message.answer(text='<b>💀 База данных с фотками тир листа удалена!</b>\n\nАдмин даст тебе пизды!')
        await clear_db()
    else:
        await callback.message.answer(text='Правильный выбор! База данных осталась невредима 👍')
    await callback.message.edit_reply_markup(reply_markup=None)


@dp.message(F.text, send_DM(), F.from_user.id.in_(incels))
async def send_dm(message: Message, state: FSMContext):
    s = message.text[6:]
    if s == "all":
        await message.answer(text=f'Введите сообщение для отправки <b>всем бомжам</b>')
        current_dm_id[message.from_user.id] = -1
        await state.set_state(FSMFillForm.sendDM)
        return
    if s == "incels":
        await message.answer(text=f'Введите сообщение для отправки <b>всем инцелам</b>')
        current_dm_id[message.from_user.id] = -2
        await state.set_state(FSMFillForm.sendDM)
        return
    if s == "topincels":
        await message.answer(text=f'Введите сообщение для отправки <b>топ инцелам</b>')
        current_dm_id[message.from_user.id] = -3
        await state.set_state(FSMFillForm.sendDM)
        return
    if len(s) <= 2:
        await message.answer(text=f'Пользователь с username: <i>"{s}"</i> не найден в таблице')
        return
    result = await check_user(s)
    if result is None:
        await message.answer(text=f'Пользователь с username: <i>"{s}"</i> не найден в таблице')
    else:
        await message.answer(text=f'Введите сообщение для отправки <i>@{s}</i>')
        current_dm_id[message.from_user.id] = result
        await state.set_state(FSMFillForm.sendDM)


@dp.message(F.text, check_username())
async def del_username(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='Иди нахуй!')
        return
    s = message.text[5:]
    result = await delete_row(s)
    if result == 0:
        await message.answer(text=f'Строка с username: <i>"{s}"</i> не найдена в таблице')
    else:
        await message.answer(text=f'Строка с username: <i>"{s}"</i> была успешно удалена')


async def get_rates_keyboard(num: int, mailing: int = 1, ids='0', back=False, message_to_delete=0, back_ids=0, delete=True):
    array_buttons: list[list[InlineKeyboardButton]] = [[], []]
    if back:
        array_buttons = [[InlineKeyboardButton(text='🔙',
                                               callback_data=ManageSettings(action=8, photo_id=ids, message_to_delete=message_to_delete,
                                                                            back_ids=back_ids).pack())]]
        return InlineKeyboardMarkup(inline_keyboard=array_buttons)
    for i in range(12):
        array_buttons[i // 6].append(InlineKeyboardButton(
            text=str(i) + f' {emoji[i]}',
            callback_data=RateCallBack(r=i, photo_id=num, mailing=mailing).pack()))

    if mailing == 3:
        if delete:
            await add_note(num, '')
        array_buttons.append([
            InlineKeyboardButton(text='🔙', callback_data=ManageSettings(action=8, photo_id=ids, message_to_delete=message_to_delete,
                                                                        back_ids=back_ids).pack())])
    markup = InlineKeyboardMarkup(inline_keyboard=array_buttons)
    return markup


async def send_results(num: int, rate: str):
    origin = await get_origin(num)
    origin_id = await check_user(origin)
    if origin_id and origin_id not in await get_users():
        await add_not_incel_photo(num, await get_photo_id_by_id(num), origin_id, float(rate))
        if origin_id is not None:
            if float(rate) <= 5:
                emoji_loc = '📉'
            else:
                emoji_loc = '📈'
            caption = f'{emoji_loc} Твое фото оценено на <b>{rate}</b> из <b>10</b>\n\n❤️ <i>Это не моё мнение и не мнение команды RatePhotosBot. Не судите строго за ошибки — я только учусь</i>'
            try:
                await bot.send_photo(chat_id=origin_id, photo=await get_photo_id_by_id(num), caption=caption, reply_markup=await get_keyboard(origin_id))
                if len(await get_avgs_not_incel(origin_id)) == 6:
                    await bot.send_message(chat_id=origin_id, text='🙀 Теперь тебе доступна статистика!\nНажимай скорее <i>/stat</i>', reply_markup=not_incel_keyboard)
            except Exception as e:
                await bot.send_message(chat_id=972753303, text=f'Произошла ошибка!\n{str(e)}')


async def send_group_photo(user_id: int, num: str):
    if '-' not in num:
        async with ChatActionSender(bot=bot, chat_id=user_id, action='upload_photo'):
            photo = await send_photos_by_id(int(num))
            caption = f'👥 <b><a href="vk.com/{photo[1]}">{await get_group_name(photo[1][:photo[1].find("?")])}</a></b>'
            msg = await bot.send_photo(chat_id=user_id, photo=photo[3], caption=photo[2] + ("\n\n" if len(photo[2]) > 0 else "") + caption,
                                       reply_markup=get_manage_photo(ids=int(num)))
            await set_message_to_delete(user_id, f'{msg.message_id}')

        return
    num = list(map(int, num.split('-')))
    nums = [i for i in range(num[0], num[1] + 1)]
    photo = await send_photos_by_id(nums[0])
    caption = f'👥 <b><a href="vk.com/{photo[1]}">{await get_group_name(photo[1][:photo[1].find("?")])}</a></b>'
    media = []
    for num in nums:
        loc_photo = await send_photos_by_id(num)
        media.append(InputMediaPhoto(media=loc_photo[3]))
    try:
        async with ChatActionSender(bot=bot, chat_id=user_id, action='upload_photo'):
            msg: List[Message] = await bot.send_media_group(user_id, media=media)
            await bot.send_message(chat_id=user_id, text=photo[2] + ("\n\n" if len(photo[2]) > 0 else "") + caption,
                                   reply_markup=get_manage_photo(ids=nums, message_to_delete=f'{msg[0].message_id}, {msg[-1].message_id}'),
                                   disable_web_page_preview=True)
            await set_message_to_delete(user_id, f'{msg[0].message_id}-{msg[-1].message_id}')
    except Exception as e:
        await bot.send_message(chat_id=user_id, text=f'Произошла ошибка! Код 1\n{e}')


async def already_in_db(path):
    try:
        current_loop = asyncio.get_running_loop()
        executor = concurrent.futures.ThreadPoolExecutor()

        rand_int = random.randint(1, 10 ** 8)
        saved_path = f"{os.path.dirname(__file__)}/pictures/public_photo{rand_int}.jpg"
        if path[:4] == 'http':
            async with aiohttp.ClientSession() as session:
                async with session.get(path) as response:
                    if response.status == 200:
                        async with aiofiles.open(saved_path, "wb") as file:
                            content = await response.read()
                            await file.write(content)
        else:
            f = await bot.get_file(path)
            f_path = f.file_path
            await bot.download_file(f_path, saved_path)
        hash = await current_loop.run_in_executor(executor, get_hash, saved_path)
        os.remove(saved_path)
        if await get_similarities(hash):
            return True
        return False
    except Exception as e:
        await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! Код 9945\n{e}')
        return False


async def notify_admin(user_id: int, message_id=0):
    sets = await get_settings(user_id)
    if sets[6] is not None:
        groups_set = set(map(int, sets[6].split(',')))
        if message_id != 0:
            async with ChatActionSender(bot=bot, chat_id=user_id):
                await bot.edit_message_caption(chat_id=user_id, message_id=message_id,
                                               caption=f'Начал поиск фото по группам\n<code>{"0".rjust(len(str(len(groups_set))))} из {len(groups_set)}</code>  | <code>{("{:2.2f}".format(00.00) + "%").rjust(6)}</code>')
        cnt_group = 0
        cnt = 0
        skipped = 0
        for group in groups_set:
            group_sets = await get_group_sets(group)
            if message_id != 0:
                progress = cnt_group / len(groups_set)
                async with ChatActionSender(bot=bot, chat_id=user_id):
                    await bot.edit_message_media(chat_id=user_id, message_id=message_id,
                                                 media=InputMediaPhoto(media=group_sets[8],
                                                                       caption=f'Начал поиск фото по группам\n<code>{str(cnt_group).rjust(len(str(len(groups_set))))} из {len(groups_set)}</code>  | <code>{("{:.2f}".format(progress * 100) + "%").rjust(6)}</code>\n<i>{group_sets[7]}</i>'))
            cnt_group += 1
            if not group_sets[2]:
                continue
            parameters = {'domain': group_sets[1], 'top_likes': group_sets[3], 'photo_amount': group_sets[4],
                          'time_delta': group_sets[5], 'last_update': group_sets[6] if group_sets[6] is not None else 0}
            try:
                result = await get_posts(parameters)
            except Exception as e:
                await bot.send_message(chat_id=user_id, text=f'Произошла ошибка! Код 2\n{e}')
            for link, post in result.items():
                async with ChatActionSender(bot=bot, chat_id=user_id,
                                            action='upload_photo'):  # Установка action "Отправка фотографии...
                    cnt += 1
                    caption = f'👥 <b><a href="vk.com/{group_sets[1]}?w=wall{link}">{group_sets[7]}</a></b>, 👍 {post[2]}'
                    if len(post[0]) == 1:
                        num = await last_group_photo_id() + 1
                        if sets[7] == 1:
                            if await already_in_db(post[0][0]):
                                skipped += 1
                                continue
                            await download_hash(link=post[0][0])
                            await add_group_photo(num, f"{group_sets[1]}?w=wall{link}",
                                                  format_text(post[1], group_sets[1], link), post[0][0])
                            if cnt - 1 == skipped:
                                await send_group_photo(user_id, str(num))
                            else:
                                await add_to_queue_group_photo(user_id, str(num))
                        else:
                            extra2 = ''
                            await bot.send_photo(chat_id=user_id, photo=post[0][0],
                                                 caption=extra2 + '\n' + format_text(post[1], group_sets[1], link) + (
                                                     "\n\n" if len(post[1]) > 0 else "") + caption,
                                                 reply_markup=get_manage_photo(ids=num, mode=sets[7]))
                    else:
                        photo_ids = []
                        media = []
                        first = True
                        num = await last_group_photo_id()
                        for url in post[0]:
                            if sets[7] == 1:
                                if await already_in_db(url):
                                    continue
                                await download_hash(link=url)
                            num += 1
                            if sets[7] == 1:
                                await add_group_photo(num, f"{group_sets[1]}?w=wall{link}",
                                                      format_text(post[1], group_sets[1], link), url)
                            photo_ids.append(num)
                            if first and sets[7] == 2:
                                media.append(InputMediaPhoto(media=url, caption=format_text(post[1], group_sets[1], link) + (
                                    "\n\n" if len(post[1]) > 1 else "") + caption))
                                first = False
                            else:
                                media.append(InputMediaPhoto(media=url))
                        try:
                            if len(media) == 0:
                                skipped += 1
                                continue
                            if sets[7] == 1:
                                if cnt - 1 == skipped:
                                    await send_group_photo(user_id, f'{photo_ids[0]}-{photo_ids[-1]}')
                                else:
                                    await add_to_queue_group_photo(user_id, f'{photo_ids[0]}-{photo_ids[-1]}')
                            else:
                                async with ChatActionSender(bot=bot, chat_id=user_id, action='upload_photo'):
                                    await bot.send_media_group(user_id, media=media)
                        except Exception as e:
                            await bot.send_message(chat_id=user_id, text=f'Произошла ошибка! Код 3\n{e}')
            await update_time(group)
        if cnt == skipped:
            if len(await get_admins_queue(user_id)) == 0:
                await bot.send_message(chat_id=user_id, text=f'Фото с текущими фильтрами не нашлось 😨')
            else:
                await send_next_photo(user_id)
        if message_id != 0:
            async with ChatActionSender(bot=bot, chat_id=user_id):
                await bot.edit_message_media(chat_id=user_id, message_id=message_id,
                                             media=InputMediaPhoto(
                                                 media='https://sun1-86.userapi.com/s/v1/if1/hNz4gzygw7cug2Vg2fnASFV8jj5B8xeo4MdVvujz767OUMdDE5TJnxR07wNSeCwszzDwI-5r.jpg?size=200x200&quality=96&crop=0,0,300,300&ava=1',
                                                 caption=f'Кончил поиск фото по группам\n<code>{len(groups_set)} из {len(groups_set)}</code> | <code>100.00%</code>'))
                await asyncio.sleep(5)
                await bot.delete_message(chat_id=user_id, message_id=message_id)


async def get_text_of_settings(user_id: int) -> str:
    sets = await get_settings(user_id)
    extra_emoji = '🧊' if sets[7] == 2 else ''
    text = f'<b>⚙️{extra_emoji} Твои текущие настройки</b>\n<blockquote>'
    groups_str = ''
    if sets[6] is not None:
        text += '<b>Группы:\n</b>🔄    🔢    📅     <i>название\n'
        groups_set = set(map(int, sets[6].split(',')))
        for group in groups_set:
            settings = await get_group_sets(group)
            if not settings[2]:
                continue
            text += ['🆕      ', '👍      '][settings[3]] + str(settings[4]).ljust(9) + str(settings[5]).ljust(8) + f'<a href = "https://vk.com/{await get_group_domain(group)}">{await get_group_name(group)}</a>\n'
        text += '</i>'
    else:
        groups_str = '<i>У тебя пока нет групп!</i>\n'
    week_array = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    weekday_str = ''
    if sets[3] is not None:
        for weekday in map(int, sets[3].split(',')):
            weekday_str += f'{week_array[weekday - 1]}, '
        weekday_str = weekday_str[:-2]
    else:
        weekday_str = 'Ни один день недели не выбран, фото не будут присылаться'
    extra = f'\n<b>Дни недели:</b>\n<i>{weekday_str}</i>\n<b>Время:</b>\n<i>{sets[4]}:{sets[5]}</i></blockquote>'
    return text + groups_str + extra


async def get_text_of_group_sets(group_id: int, include_name: bool = True):
    settings = await get_group_sets(group_id)
    name = settings[7]
    domain = settings[1]
    text = f'👥 <b><a href="vk.com/{domain}">{name}</a></b>\n\n'
    active = '• <b><i>Активна 🟢</i></b>' if settings[2] else '• <b><i>Отключена ❌</i></b>'
    top_likes = f'• Сортировка по: <b>{"лайкам 👍" if settings[3] else "актуальности 🆕"}</b>'
    photo_amount = f'• Количество фото, за одно обращение к стене: <b>{settings[4]}</b>'
    time_delta = f'• Посты не раньше, чем <b>{settings[5]}</b> дней(-я) назад'
    last_update = f'• Последнее обращение <b>{datetime.datetime.fromtimestamp(settings[6]).strftime("%H:%M %d.%m.%y")}</b>' if settings[6] != 0 else ''
    if include_name:
        return f'{text}{active}\n{top_likes}\n{photo_amount}\n{time_delta}\n{last_update}'
    else:
        return f'{active}\n{top_likes}\n{photo_amount}\n{time_delta}\n{last_update}'


def moderate_keyboard(file_id: int, creator: str):
    if file_id == -1:
        array = [[InlineKeyboardButton(text='✅', callback_data=ModerateCallBack(action=3, photo_id=file_id,
                                                                                creator=creator).pack()),
                  InlineKeyboardButton(text='❌', callback_data=ModerateCallBack(action=2, photo_id=file_id,
                                                                                creator=creator).pack())]]
        return InlineKeyboardMarkup(inline_keyboard=array)
    array = [[InlineKeyboardButton(text='✅', callback_data=ModerateCallBack(action=1, photo_id=file_id, creator=creator).pack()),
              InlineKeyboardButton(text='❌', callback_data=ModerateCallBack(action=0, photo_id=file_id, creator=creator).pack()),
              InlineKeyboardButton(text='🔕', callback_data=ModerateCallBack(action=4, photo_id=file_id, creator=creator).pack())]]
    return InlineKeyboardMarkup(
        inline_keyboard=array)


def confirm_keyboard(file_id: int):
    array = [[InlineKeyboardButton(text='✅', callback_data=ConfirmCallBack(action=1, photo_id=file_id).pack()),
              InlineKeyboardButton(text='❌', callback_data=ConfirmCallBack(action=0, photo_id=file_id).pack())]]
    return InlineKeyboardMarkup(inline_keyboard=array)


async def get_admin_keyboard(user_id: int, cancel_url_sending: bool = False, superuser: bool = False):
    if cancel_url_sending:
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔙', callback_data=AdminCallBack(action=1).pack())]])
    array_buttons: list[list[InlineKeyboardButton]] = []
    if superuser:
        incels = list(await get_users())
        admins = await get_admins()
        for i in range((len(incels) + 2) // 3):
            loc_array = []
            for j in range(min(3, len(incels) - i * 3)):
                username = await get_username_by_id(incels[i * 3 + j])
                emoji_loc = ' 💎' if incels[i * 3 + j] in admins else ''
                button = InlineKeyboardButton(text=username + emoji_loc,
                                              callback_data=AdminCallBack(action=5, user_id=incels[i * 3 + j]).pack())
                loc_array.append(button)
            array_buttons.append(loc_array)
        array_buttons.append([InlineKeyboardButton(text='🔙', callback_data=AdminCallBack(action=-2).pack())])
        return InlineKeyboardMarkup(inline_keyboard=array_buttons)
    row1 = [InlineKeyboardButton(text='Группы 👥', callback_data=AdminCallBack(action=1).pack()),
            InlineKeyboardButton(text='Оповещения 🔊', callback_data=AdminCallBack(action=2).pack())]
    row2 = [InlineKeyboardButton(text='Получить фото ➡️', callback_data=AdminCallBack(action=3).pack()),
            InlineKeyboardButton(text='Уволиться 🚫', callback_data=AdminCallBack(action=0).pack())]
    array_buttons = [row1, row2]
    if user_id == 972753303:
        array_buttons.append(
            [InlineKeyboardButton(text='Настоящие админы 👑', callback_data=AdminCallBack(action=-1).pack())])
    markup = InlineKeyboardMarkup(inline_keyboard=array_buttons)
    return markup


def get_manage_photo(ids: Union[int, List], mode=1, back_ids=0, message_to_delete=0):
    if mode == 2:
        return None
    elif mode == 3:
        row1 = [InlineKeyboardButton(text='📝🚫', callback_data=ManageSettings(action=2, photo_id=ids,back_ids=back_ids, message_to_delete=message_to_delete).pack()),
                InlineKeyboardButton(text='🥷', callback_data=ManageSettings(action=9, photo_id=ids, back_ids=back_ids, message_to_delete=message_to_delete).pack())]
        row2 = [InlineKeyboardButton(text='✅', callback_data=ManageSettings(action=1, photo_id=ids, back_ids=back_ids, message_to_delete=message_to_delete).pack()),
                InlineKeyboardButton(text='✏️', callback_data=ManageSettings(action=3, photo_id=ids, back_ids=back_ids, message_to_delete=message_to_delete).pack())]
        array_buttons: list[list[InlineKeyboardButton]] = [row1, row2, [InlineKeyboardButton(text='🔙',
                                                                                       callback_data=ManageSettings(
                                                                                           action=7, photo_id=ids,
                                                                                           back_ids=back_ids,
                                                                                           message_to_delete=message_to_delete).pack())]]
        markup = InlineKeyboardMarkup(inline_keyboard=array_buttons)
        return markup
    if isinstance(ids, list):
        rows = []
        cnt = 1
        for i in range((len(ids) + 4) // 5):
            loc_array = []
            for j in range(min(5, len(ids) - i * 5)):
                button = InlineKeyboardButton(text=str(cnt),
                                              callback_data=ManageSettings(action=5, photo_id=ids[i * 5 + j],
                                                                           back_ids=f'{min(ids)}, {max(ids)}',
                                                                           message_to_delete=message_to_delete).pack())
                loc_array.append(button)
                cnt += 1
            rows.append(loc_array)
        if len(rows) >= 2:
            if len(rows[-1]) <= 2:
                rows[-1] = rows[-2][-2:] + rows[-1]
                rows[-2] = rows[-2][:-2]
            elif len(rows[-1]) == 3:
                rows[-1] = rows[-2][-1:] + rows[-1]
                rows[-2] = rows[-2][:-1]
        rows.append([InlineKeyboardButton(text='Расхуярить!',
                                          callback_data=ManageSettings(action=10, photo_id=f'{min(ids)}, {max(ids)}',
                                                                       message_to_delete=message_to_delete).pack()),
                     InlineKeyboardButton(text='🗑',
                                          callback_data=ManageSettings(action=6, photo_id=f'{min(ids)}, {max(ids)}',
                                                                       message_to_delete=message_to_delete).pack())])
        markup = InlineKeyboardMarkup(inline_keyboard=rows)
        return markup
    else:
        row1 = [InlineKeyboardButton(text='📝🚫', callback_data=ManageSettings(action=2, photo_id=ids).pack()),
                InlineKeyboardButton(text='🥷', callback_data=ManageSettings(action=9, photo_id=ids).pack())]
        row2 = [InlineKeyboardButton(text='✅', callback_data=ManageSettings(action=1, photo_id=ids).pack()),
                InlineKeyboardButton(text='✏️', callback_data=ManageSettings(action=3, photo_id=ids).pack()),
                InlineKeyboardButton(text='🗑', callback_data=ManageSettings(action=4, photo_id=ids).pack())]
        array_buttons: list[list[InlineKeyboardButton]] = [row1, row2]
        markup = InlineKeyboardMarkup(inline_keyboard=array_buttons)
        return markup


async def get_group_keyboard(groups_id: Union[List[int], None], go_back_to_menu: bool = False):
    back = InlineKeyboardButton(text='🔙', callback_data=AdminCallBack(action=-2).pack())
    add = InlineKeyboardButton(text='Добавить группу', callback_data=AdminCallBack(action=4).pack())
    array_buttons: list[list[InlineKeyboardButton]] = []
    if groups_id is None:
        array_buttons = [[add],[back]]
        return InlineKeyboardMarkup(inline_keyboard=array_buttons)
    active_groups = await get_active_groups()
    for i in range((len(groups_id) + 2) // 3):
        loc_array = []
        for j in range(min(3, len(groups_id) - i * 3)):
            domain = await get_group_name(groups_id[i * 3 + j])
            emoji_loc = '🟢' if groups_id[i * 3 + j] in active_groups else '❌'
            button = InlineKeyboardButton(text=emoji_loc + ' ' + domain,
                                          callback_data=GroupCallBack(group_id=groups_id[i * 3 + j]).pack())
            loc_array.append(button)
        array_buttons.append(loc_array)
    array_buttons.append([back, add])
    markup = InlineKeyboardMarkup(inline_keyboard=array_buttons)
    return markup


async def get_notify_keyboard(user_id: int, hour: bool = False, minute: bool = False, week: bool = False):
    week_array = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    settings = await get_settings(user_id)
    if week:
        weekdays = await get_weekdays(user_id)
        array_buttons = [[]]
        back = InlineKeyboardButton(text='🔙', callback_data=AdminCallBack(action=2).pack())
        for i in range(7):
            emoji_loc = ' ✅' if (i + 1) in weekdays else ' ❌'
            array_buttons[0].append(InlineKeyboardButton(text=week_array[i] + emoji_loc,
                                                         callback_data=NotifySettings(action=7, week=i + 1).pack()))
        array_buttons.append([back])
        return InlineKeyboardMarkup(inline_keyboard=array_buttons)
    if hour:
        array_buttons = [[]]
        back = InlineKeyboardButton(text='🔙', callback_data=AdminCallBack(action=2).pack())
        for i in range(10, 23, 2):
            array_buttons[0].append(InlineKeyboardButton(text=str(i) + (' ✅'if str(i) == settings[4] else ''), callback_data=NotifySettings(action=3, hour=i).pack()))
        custom = InlineKeyboardButton(text='Свой вариант', callback_data=NotifySettings(action=4).pack())
        array_buttons.append([back, custom])
        return InlineKeyboardMarkup(inline_keyboard=array_buttons)
    if minute:
        array_buttons = [[]]
        back = InlineKeyboardButton(text='🔙', callback_data=AdminCallBack(action=2).pack())
        hour = await get_hour(user_id)
        start = 0
        if hour == 7 or hour == 19:
            start = 1
            array_buttons[0].append(InlineKeyboardButton(text='00 ❌', callback_data=NotifySettings(action=8, minute=0).pack()))
        for i in range(start, 6):
            array_buttons[0].append(InlineKeyboardButton(text=str(i)+'0' + (' ✅'if (str(i)+'0') == settings[5] else ''), callback_data=NotifySettings(action=5, minute=i).pack()))
        custom = InlineKeyboardButton(text='Свой вариант', callback_data=NotifySettings(action=6).pack())
        array_buttons.append([back, custom])
        return InlineKeyboardMarkup(inline_keyboard=array_buttons)
    settings = await get_settings(user_id)
    back = InlineKeyboardButton(text='🔙', callback_data=AdminCallBack(action=-2).pack())
    day_of_week = InlineKeyboardButton(text='Настроить дни недели 🗓', callback_data=NotifySettings(action=0).pack())
    hour = InlineKeyboardButton(text=f'В {settings[4]} ч.', callback_data=NotifySettings(action=1).pack())
    minute = InlineKeyboardButton(text=f'{settings[5]} мин.', callback_data=NotifySettings(action=2).pack())
    array_buttons: list[list[InlineKeyboardButton]] = [[day_of_week], [hour, minute], [back]]
    return InlineKeyboardMarkup(inline_keyboard=array_buttons)


def group_settings_keyboard(settings: tuple, go_back_to_public_settings: bool = False, get_date: bool = False, get_amount: bool = False):
    if go_back_to_public_settings:
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔙', callback_data=GroupSettings(action=7, group_id=settings[0]).pack())]])
    array_buttons: list[list[InlineKeyboardButton]] = []
    if get_date or get_amount:
        loc_array = []
        action = 8 if get_amount else 9
        delta = 1 if get_amount else 0
        value = settings[4] if get_amount else settings[5]
        for i in range(0 + delta, 8 + delta):
            loc_array.append(InlineKeyboardButton(text=str(i) + (' ✅' if i == int(value) else ''), callback_data=GroupSettings(action=action, group_id=settings[0], amount=i, date=i).pack()))
        array_buttons.append(loc_array)
        array_buttons.append([InlineKeyboardButton(text='🔙', callback_data=GroupSettings(action=7, group_id=settings[0]).pack())])
        return InlineKeyboardMarkup(inline_keyboard=array_buttons)
    back = InlineKeyboardButton(text='🔙', callback_data=AdminCallBack(action=1).pack())
    delete = InlineKeyboardButton(text='Удалить 🗑', callback_data=GroupSettings(action=5, group_id=settings[0]).pack())
    info = InlineKeyboardButton(text='ℹ️', callback_data=GroupSettings(action=6, group_id=settings[0]).pack())
    row1 = [InlineKeyboardButton(text='Отключить ❌' if settings[2] else 'Включить 🟢', callback_data=GroupSettings(action=1, group_id=settings[0]).pack()),
            InlineKeyboardButton(text='Сортировать по 🆕' if settings[3] else 'Сортировать по 👍', callback_data=GroupSettings(action=2, group_id=settings[0]).pack())]
    row2 = [InlineKeyboardButton(text='Количество фото', callback_data=GroupSettings(action=3, group_id=settings[0]).pack()),
            InlineKeyboardButton(text='Дата поста', callback_data=GroupSettings(action=4, group_id=settings[0]).pack())]
    markup = InlineKeyboardMarkup(inline_keyboard=[row1, row2, [back, delete, info]])
    return markup



@dp.callback_query(AdminCallBack.filter())
async def moderate_main_settings(callback: CallbackQuery, callback_data: AdminCallBack, state: FSMContext):
    action = callback_data.action
    if action == -2:
        await callback.message.edit_text(text=await get_text_of_settings(callback.from_user.id), disable_web_page_preview=True,
                                         reply_markup=await get_admin_keyboard(callback.from_user.id))
    elif action == 0:
        await set_inactive(callback.from_user.id)
        await callback.message.delete()
        await callback.message.answer(text='Ты исключен из админов! Лох, ну ты типа пидор', reply_markup=basic_keyboard)
    elif action == 1:
        await state.clear()
        groups_str = await get_settings(callback.from_user.id)
        groups_str = groups_str[6]
        if groups_str is None:
            await callback.message.edit_text(text='👥 У тебя еще нет групп. Самое время добавить! Жми 👇🏿',reply_markup=get_group_keyboard(groups_id=None))
            return
        text = '<b>👥 Нажми на группу для регулировки или добавь новую</b>'
        await callback.message.edit_text(text=text, reply_markup=await get_group_keyboard(sorted(list(map(int, groups_str.split(','))))))
    elif action == 2:
        text = '<b>🔊 Нажми на кнопку для настройки периодичности рассылки</b>'
        await callback.message.edit_text(text=text, reply_markup=await get_notify_keyboard(callback.from_user.id))
    elif action == 3:
        sets = await get_settings(callback.from_user.id)
        if not sets[1]:
            await callback.message.edit_text('Ты больше не админ! Лох, ну ты типа пидор')
            return
        if sets[6] is None:
            await callback.message.edit_text('👥 Ты еще не добавил ни одной группы! Самое время добавить! Жми 👇',
                                             reply_markup=await get_group_keyboard(groups_id=None))
        else:
            mes_id = await bot.send_photo(chat_id=callback.from_user.id, photo='https://i.postimg.cc/TYv4PFJP/drawing-kitten-animals-9-Favim-1.jpg', caption=f'Начал поиск фото по группам')
            await callback.answer()
            await notify_admin(callback.from_user.id, message_id=mes_id.message_id)


    elif action == 4:
        await callback.message.edit_text(text='Скинь ссылку на стену группы вк, из которой ты хочешь получать фото', reply_markup=await get_admin_keyboard(callback.from_user.id, cancel_url_sending=True))
        await state.set_state(FSMFillForm.inserting_url)
    elif action == -1:
        await callback.message.edit_text(text='<b>👤 Все инцелы</b>: вот они слева направо', reply_markup=await get_admin_keyboard(callback.from_user.id, superuser=True))
    elif action == 5:
        user_id = callback_data.user_id
        if user_id in await get_admins():
            await set_inactive(user_id)
            await bot.send_message(chat_id=user_id, text='Ты больше не админ! Лох, ну ты типа пидор', reply_markup=basic_keyboard)
        else:
            await set_admin(user_id)
            await bot.send_message(chat_id=user_id, text='Тебя назначили админом 👑\n<i>Напоминаю, что админы работаю бесплатно</i>', reply_markup=admin_keyboard)
        await callback.message.edit_text(text='<b>👤 Все инцелы</b>: вот они слева направо',
                                         reply_markup=await get_admin_keyboard(callback.from_user.id, superuser=True))


async def send_next_photo(user_id: int):
    queue = await get_admins_queue(user_id)
    if len(queue) == 0:
        return
    i = min(queue)
    await remove_from_admins_queue(user_id, i)
    try:
        extra = '' if len(queue) == 0 else f' | {len(queue)} в очереди'
        if '-' not in i:
            async with ChatActionSender(bot=bot, chat_id=user_id, action='upload_photo'):
                photo = await send_photos_by_id(int(i))
                caption = f'👥 <b><a href="vk.com/{photo[1]}">{await get_group_name(photo[1][:photo[1].find("?")])}</a></b>' + extra
                msg = await bot.send_photo(chat_id=user_id, photo=photo[3],
                                           caption=photo[2] + ("\n\n" if len(photo[2]) > 0 else "") + caption,
                                           reply_markup=get_manage_photo(ids=int(i)))
                await set_message_to_delete(user_id, str(msg.message_id))
            return
        else:
            num = list(map(int, i.split('-')))
            nums = [i for i in range(num[0], num[1] + 1)]
            photo = await send_photos_by_id(nums[0])
            caption = f'👥 <b><a href="vk.com/{photo[1]}">{await get_group_name(photo[1][:photo[1].find("?")])}</a></b>' + extra
            media = []
            for num in nums:
                loc_photo = await send_photos_by_id(num)
                media.append(InputMediaPhoto(media=loc_photo[3]))

            async with ChatActionSender(bot=bot, chat_id=user_id, action='upload_photo'):
                msg: List[Message] = await bot.send_media_group(user_id, media=media)
                await bot.send_message(chat_id=user_id,
                                       text=photo[2] + ("\n\n" if len(photo[2]) > 0 else "") + caption,
                                       reply_markup=get_manage_photo(ids=nums,
                                                                     message_to_delete=f'{msg[0].message_id}, {msg[-1].message_id}'),
                                       disable_web_page_preview=True)
                await set_message_to_delete(user_id, f'{msg[0].message_id}-{msg[-1].message_id}')
    except Exception as e:
        await bot.send_message(chat_id=user_id, text=f'Произошла ошибка! Код 4\n{e}')
        if user_id != 972753303:
            await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! Код 4\n{e}')
        await send_next_photo(user_id)



@dp.callback_query(ManageSettings.filter())
async def moderate_manage_settings(callback: CallbackQuery, callback_data: ManageSettings, state: FSMContext):
    action = callback_data.action
    photo_id = callback_data.photo_id
    if action == 2:
        await callback.answer('Фото будет выложено без подписи')
    if action == 1 or action == 2:
        information = await get_group_photo_info(photo_id)
        last_num = await get_last()
        await add_photo_id(last_num + 1, information[3], f'👥 {information[1]}')
        if information[2] != '' and action == 1:
            await add_note(last_num + 1, information[2])
        try:
            await callback.message.edit_caption(
                caption=f'Оцени фото из группы 👥 <b><a href="vk.com/{information[1]}">{await get_group_name(information[1][:information[1].find("?"):])}</a></b>',
                reply_markup=await get_rates_keyboard(last_num + 1, 3, ids=photo_id, back_ids=callback_data.back_ids,
                                                message_to_delete=callback_data.message_to_delete, delete=False))
        except Exception:
            await callback.message.edit_text(
                text=f'Оцени фото из группы 👥 <b><a href="vk.com/{information[1]}">{await get_group_name(information[1][:information[1].find("?"):])}</a></b>',
                reply_markup=await get_rates_keyboard(last_num + 1, 3, ids=photo_id, back_ids=callback_data.back_ids,
                                                message_to_delete=callback_data.message_to_delete, delete=False),
                disable_web_page_preview=True)
    elif action == 3:
        if callback.message.photo:
            await callback.message.edit_caption(caption='Введи следующим сообщением подпись к этой пикче...',
                                                reply_markup=await get_rates_keyboard(0, 3, photo_id, True))
        else:
            await callback.message.edit_text('Введи следующим сообщением подпись к этой пикче...',
                                             reply_markup=await get_rates_keyboard(0, 3, photo_id,
                                                                             back_ids=callback_data.back_ids,
                                                                             message_to_delete=callback_data.message_to_delete,
                                                                             back=True))
        information = await get_group_photo_info(photo_id)
        last_num = await get_last()
        await add_photo_id(last_num + 1, information[3], f'👥 {information[1]}')
        await set_message_to_delete(callback.from_user.id, str(callback.message.message_id))
        caption_global[callback.from_user.id] = (last_num + 1, photo_id)
        await state.set_state(FSMFillForm.inserting_caption)
    elif action == 4:
        try:
            await send_next_photo(callback.from_user.id)
            await del_group_photo(photo_id)
            await callback.message.delete()
        except Exception as e:
            await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! Код 5\n{e}')
    elif action == 5:
        await callback.message.edit_text(text=f'Выбери действие для выбранного фото',
                                         reply_markup=get_manage_photo(photo_id, mode=3, back_ids=callback_data.back_ids,
                                                                       message_to_delete=callback_data.message_to_delete))
    elif action == 6:
        try:
            await send_next_photo(callback.from_user.id)
            start = int(photo_id.split(',')[0])
            end = int(photo_id.split(',')[1])
            for photo_id in range(start, end + 1):
                await del_group_photo(photo_id)
            await callback.message.delete()
            msgs = list(map(int, callback_data.message_to_delete.split(',')))
            msgs_list = [i for i in range(msgs[0], msgs[-1] + 1)]
            await bot.delete_messages(chat_id=callback.from_user.id, message_ids=msgs_list)
        except Exception as e:
            await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! Код 6\n{e}')
    elif action == 7:
        ids_str = callback_data.back_ids
        first = int(ids_str.split(',')[0])
        last = int(ids_str.split(',')[1])
        ids_list = [i for i in range(first, last + 1)]
        info = await get_group_photo_info(first)
        queue = await get_admins_queue(callback.from_user.id)
        extra = f' | {len(queue) + 1} в очереди'
        txt = '' if info[2] is None else info[2]
        caption = f'{txt}\n\n👥 <b><a href="vk.com/{info[1]}">{await get_group_name(info[1][:info[1].find("?")])}</a></b>' + extra
        await callback.message.edit_text(text=caption,
                                      reply_markup=get_manage_photo(ids=ids_list, message_to_delete=callback_data.message_to_delete),
                                      disable_web_page_preview=True)
    elif action == 8:
        back_ids = callback_data.back_ids
        if ',' in back_ids:
            first = int(back_ids.split(',')[0])
            last = int(back_ids.split(',')[1])
            id = [i for i in range(first, last + 1)]
        else:
            id = photo_id
        queue = await get_admins_queue(callback.from_user.id)
        extra = f' | {len(queue) + 1} в очереди'
        photo = await send_photos_by_id(int(photo_id))
        txt = '' if photo[2] is None else photo[2]
        caption = f'{txt}\n\n👥 <b><a href="vk.com/{photo[1]}">{await get_group_name(photo[1][:photo[1].find("?")])}</a></b>' + extra
        if callback.message.photo:
            await callback.message.edit_caption(caption=caption, reply_markup=get_manage_photo(ids=id))
        else:
            await callback.message.edit_text(text=caption, reply_markup=get_manage_photo(ids=id, message_to_delete=callback_data.message_to_delete, back_ids=back_ids), disable_web_page_preview=True)
        await state.clear()
    elif action == 9:
        information = await get_group_photo_info(photo_id)
        last_num = await get_last()
        await add_photo_id(last_num + 1, information[3], f'👥 {information[1]}')
        await add_note(last_num + 1, '/anon')
        try:
            await callback.message.edit_caption(
                caption=f'Стыдно такое выкладывать, да, выблядок?\nОцени фото из группы 👥 <b><a href="vk.com/{information[1]}">{await get_group_name(information[1][:information[1].find("?"):])}</a></b>',
                reply_markup=await get_rates_keyboard(last_num + 1, 3, ids=photo_id, back_ids=callback_data.back_ids,
                                                message_to_delete=callback_data.message_to_delete, delete=False))
        except Exception:
            await callback.message.edit_text(
                text=f'Стыдно такое выкладывать, да, выблядок?\nОцени фото из группы 👥 <b><a href="vk.com/{information[1]}">{await get_group_name(information[1][:information[1].find("?"):])}</a></b>',
                reply_markup=await get_rates_keyboard(last_num + 1, 3, ids=photo_id, back_ids=callback_data.back_ids,
                                                message_to_delete=callback_data.message_to_delete, delete=False),
                disable_web_page_preview=True)
    elif action == 10:
        await callback.answer()
        local_keyboard = [[InlineKeyboardButton(text='Да ✅', callback_data=ManageSettings(action=11, photo_id=photo_id,
                                                                                          message_to_delete=callback_data.message_to_delete).pack()),
                           InlineKeyboardButton(text='Нет, я даун 👺', callback_data=ManageSettings(action=12, photo_id=photo_id,
                                                                                                   message_to_delete=callback_data.message_to_delete).pack())]]
        await callback.message.answer(text='Разделить фотки по отдельности❓', reply_markup=InlineKeyboardMarkup(inline_keyboard=local_keyboard))
        await set_message_to_delete(callback.from_user.id, callback.message.message_id)
    elif action == 11:
        await callback.answer('Фотки будут высланы по отдельности')
        messages_to_delete = await get_message_to_delete(callback.from_user.id)
        min_photo = int(photo_id.split(',')[0])
        max_photo = int(photo_id.split(',')[1])
        for i in range(min_photo, max_photo + 1):
            await add_to_queue_group_photo(callback.from_user.id, str(i))
        await send_next_photo(callback.from_user.id)
        await callback.message.delete()
        msgs = list(map(int, callback_data.message_to_delete.split(',')))
        msgs_list = [i for i in range(msgs[0], msgs[-1] + 1)]
        await bot.delete_messages(chat_id=callback.from_user.id, message_ids=msgs_list)
        await bot.delete_message(chat_id=callback.from_user.id, message_id=messages_to_delete)


    elif action == 12:
        await callback.answer('Пьяница, блядь, можешь по кнопкам попадать?')
        await callback.message.delete()


@dp.callback_query(GroupCallBack.filter())
async def moderate_group_settings(callback: CallbackQuery, callback_data: AdminCallBack):
    settings = await get_group_sets(callback_data.group_id)
    await callback.message.edit_text(text=await get_text_of_group_sets(callback_data.group_id, 1),
                                     disable_web_page_preview=True,
                                     reply_markup=group_settings_keyboard(settings))


@dp.callback_query(NotifySettings.filter())
async def moderate_notify_settings(callback: CallbackQuery, callback_data: NotifySettings, state: FSMContext):
    action = callback_data.action
    if action == 0:
        txt = 'Выбери <b>дни недели</b>, в которые ты хочешь получать фото'
        await callback.message.edit_text(text=txt, reply_markup=await get_notify_keyboard(callback.from_user.id, week=True))
    elif action == 1:
        txt = 'Выбери час или введи значение сам'
        await callback.message.edit_text(text=txt, reply_markup=await get_notify_keyboard(callback.from_user.id, hour=True))
    elif action == 2:
        txt = 'Выбери минуту или введи значение сам'
        await callback.message.edit_text(text=txt, reply_markup=await get_notify_keyboard(callback.from_user.id, minute=True))
    elif action == 3:
        hour = callback_data.hour
        await change_hour(callback.from_user.id, hour)
        await callback.answer(text=f'{hour} 🕑')
        text = '<b>🔊 Нажми на кнопку для настройки периодичности рассылки</b>'
        await callback.message.edit_text(text=text, reply_markup=await get_notify_keyboard(callback.from_user.id))
    elif action == 4:
        await callback.message.edit_text(text='Введи свое значение часа, в который ты хочешь получать фото из выбанных групп. <u>Учти</u>, что сервер перезагружается в 7:00 и 19:00, поэтому это время лучше не выбирать. Выбрал — еблан!')
        await state.set_state(FSMFillForm.inserting_hour)
    elif action == 5:
        minute = callback_data.minute
        minute = str(minute) + '0'
        await change_minute(callback.from_user.id, minute)
        await callback.answer(text=minute+ ' 🕑')
        text = '<b>🔊 Нажми на кнопку для настройки периодичности рассылки</b>'
        await callback.message.edit_text(text=text, reply_markup=await get_notify_keyboard(callback.from_user.id))
    elif action == 6:
        await callback.message.edit_text(text='Введи свое значение минут, в которые ты хочешь получать фото из выбанных групп. <u>Учти</u>, что сервер перезагружается в 7:00 и 19:00, поэтому это время лучше не выбирать. Выбрал — еблан!')
        await state.set_state(FSMFillForm.inserting_minute)
    elif action == 7:
        day = callback_data.week
        await change_weekdays(callback.from_user.id, day)
        txt = 'Выбери <b>дни недели</b>, в которые ты хочешь получать фото'
        await callback.message.edit_text(text=txt, reply_markup=await get_notify_keyboard(callback.from_user.id, week=True))
    elif action == 8:
        await callback.answer('Данное значение выбрать нельзя!')

@dp.callback_query(GroupSettings.filter())
async def moderate_group_deep_settings(callback: CallbackQuery, callback_data: GroupSettings):
    action = callback_data.action
    group_id = callback_data.group_id
    if action == 1 or action == 2:
        if action == 1:
            await switch_active(group_id)
        else:
            await switch_top_likes(group_id)

        await callback.message.edit_text(text=await get_text_of_group_sets(group_id),
                                         disable_web_page_preview=True, reply_markup=group_settings_keyboard(await get_group_sets(group_id)))
    elif action == 3:
        await callback.message.edit_text(text='Нажми на количество постов, которое ты хочешь получать единоразово при одном обращении к группе', reply_markup=group_settings_keyboard(settings=await get_group_sets(group_id), get_amount=True))
    elif action == 4:
        await callback.message.edit_text(text='Нажми на количество дней, сколько пост должен находиться в группе',
                                         reply_markup=group_settings_keyboard(settings=await get_group_sets(group_id), get_date=True))
    elif action == 5:
        name = await get_group_name(group_id)
        try:
            await delete_group(group_id, user_id=callback.from_user.id)
            await callback.answer(f'Группа {name} удалена 🗑')
        except Exception as e:
            await callback.message.edit_text(f'Произошла ошибка! Код 7\n{e}')
        groups_str = await get_settings(callback.from_user.id)
        groups_str = groups_str[6]
        if groups_str is None:
            await callback.message.edit_text(text='У тебя еще нет групп',
                                             reply_markup=await get_group_keyboard(groups_id=None))
            return
        text = '<b>👥 Нажми на группу для регулировки или добавь новую</b>'
        await callback.message.edit_text(text=text,
                                         reply_markup=await get_group_keyboard(sorted(list(map(int, groups_str.split(','))))))
    elif action == 6:
        await callback.message.edit_text(text='ℹ️ <b>Информация по настройке рассылки группы</b>\n1) Переключи режим активности, чтобы <b>не получать фото</b> / <b>получать фото</b> этой группы\n2) Нажми на кнопку сортировки постов для переключения режимов:\n   <b>по лайкам:</b> в указанном диапазоне будут выбраны <i>n</i> постов с наибольшим количеством лайков\n   <b>по актуальности:</b> будет выбрано <i>n</i> последних постов в указанном диапазоне\n3) <b>Количество фото:</b> выбери, сколько фото ты хочешь получить при одном обращении к группе\n4) <b>Дата поста:</b> здесь тебе нужно выбрать, сколько дней назад должны быть выложены посты. Совет: чем дольше посты лежат на стене, тем больше просмотров и лайков они собирают, поэтому сортировка по лайкам будет работать лучше всего, это также помогает избежать ошибок.\n5) <b>Удалить:</b> полностью удаляет группу из твоего списка',
                                         reply_markup=group_settings_keyboard(await get_group_sets(group_id), True))
    elif action == 7:
        await callback.message.edit_text(text=await get_text_of_group_sets(group_id, 1),
                                         disable_web_page_preview=True,
                                         reply_markup=group_settings_keyboard(await get_group_sets(group_id)))
    elif action == 8:
        amount = callback_data.amount
        await change_amount(group_id, amount)
        await callback.answer(text=str(amount))
        await callback.message.edit_text(text=await get_text_of_group_sets(group_id),
                                         disable_web_page_preview=True, reply_markup=group_settings_keyboard(await get_group_sets(group_id)))
    elif action == 9:
        date = callback_data.date
        await change_date(group_id, date)
        await update_time(group_id, 0)
        await callback.answer(text=str(date))
        await callback.message.edit_text(text=await get_text_of_group_sets(group_id),
                                         disable_web_page_preview=True, reply_markup=group_settings_keyboard(await get_group_sets(group_id)))


@dp.message(StateFilter(FSMFillForm.inserting_url))
async def get_url_vk(message: Message, state: FSMContext):
    if message.text:
        valid = check_valid_url(message.text)
        if not valid[0]:
            await message.answer('Ссылка недействительна. Отправь ссылку на группу <b><u>vk.com</u></b>')
        else:
            group_id = await add_group(message.from_user.id, valid[1])
            if group_id[0] == -1:
                await message.answer(f'Такая группа уже есть в твоём списке\n\n{await get_text_of_group_sets(group_id[1], 1)}', disable_web_page_preview=True, reply_markup=group_settings_keyboard(await get_group_sets(group_id[1])))
                await state.clear()
                return
            group_id = group_id[0]
            group_sets = await get_group_sets(group_id)
            name = await get_group_name(valid[1])
            await message.answer(
                f'Ты добавил группу <b>{name}</b>\n\nНастройки по умолчанию\n{await get_text_of_group_sets(group_id, 0)}',
                disable_web_page_preview=True, reply_markup=group_settings_keyboard(group_sets))
            await state.clear()
    else:
        await message.answer('Это не похоже на ссылку! Лох')

@dp.message(StateFilter(FSMFillForm.inserting_caption))
async def get_caption_group(message: Message, state: FSMContext):
    if not message.text:
        await message.answer('Это не похоже на текст для подписи к пикче, сука русский учи')
        return
    num, photo_id = caption_global.get(message.from_user.id, (0, 0))
    if num == 0:
        await message.answer('Произошла ошибка!')
        return
    caption_global[message.from_user.id] = (0, 0)
    await add_note(num, message.text)
    async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action='upload_photo'):
        await bot.send_photo(chat_id=message.from_user.id, photo=await get_photo_id_by_id(num),
                             caption=f'Охуенная заметка: <b><i>{message.text}</i></b>. А теперь оцени фото, мразь',
                             reply_markup=await get_rates_keyboard(num, mailing=3, ids=photo_id, delete=False))
    previous = await get_message_to_delete(message.from_user.id)
    if '-' in previous:
        previous = list(map(int, previous.split('-')))
        msgs_list = [i for i in range(previous[0], previous[-1] + 1)]
        await bot.delete_messages(chat_id=message.from_user.id, message_ids=msgs_list)
    else:
        await bot.delete_message(chat_id=message.from_user.id, message_id=int(previous))
    await state.clear()


@dp.message(StateFilter(FSMFillForm.inserting_hour))
async def get_hour_vk(message: Message, state: FSMContext):
    if message.text:
        valid = check_hours(message.text)
        if not valid:
            await message.answer('Ты ввел неверное значение часа. Ты не умеешь считать?')
        else:
            hour = int(message.text)
            minute = await get_minute(message.from_user.id)
            minute_str = str(minute)
            if minute == 0:
                minute_str = '00'
            elif minute < 10:
                minute_str = '0' + minute_str
            if (hour == 6 or hour == 18) and (minute >= 55):
                await message.answer(text=f'<b>Текущее значение минут: {minute_str}</b>. Сервер перезагружается в <u>{hour + 1}:00</u>, тебе лучше выбрать время чуть попозже!')
                return
            if (hour == 7 or hour == 19) and (minute <= 9):
                await message.answer(text=f'<b>Текущее значение минут: {minute_str}</b>. Сервер перезагружается в <u>{hour}:00</u>, тебе лучше выбрать время чуть попозже!')
                return
            if (hour == 9) and (minute <= 16 and minute >= 5):
                await message.answer(text=f'<b>Текущее значение минут: {minute_str}</b>. Сервер перезагружается в <u>9:10</u>, тебе лучше выбрать время чуть попозже!')
                return
            await set_hour(message.from_user.id, str(hour))
            await message.answer(f'Отлично! Теперь шлюхи будут присылаться в <b>{hour}:{minute_str}</b>. <i>Изменения, будут применены при следующей перезагрузке сервера...</i>', reply_markup=await get_notify_keyboard(message.from_user.id))
            await state.clear()
    else:
        await message.answer('Это не похоже на часовой формат 🤨\nТы не умеешь считать?')


@dp.message(StateFilter(FSMFillForm.inserting_minute))
async def get_minute_vk(message: Message, state: FSMContext):
    if message.text:
        valid = check_minutes(message.text)
        if not valid:
            await message.answer('Ты ввел неверное значение минут')
        else:
            minute = int(message.text)
            hour = await get_hour(message.from_user.id)
            if (hour == 6 or hour == 18) and (minute >=55):
                await message.answer(text=f'<b>Текущее значение часа: {hour}</b>. Сервер перезагружается в <u>{hour + 1}:00</u>, тебе лучше выбрать время чуть пораньше!')
                return
            if (hour == 7 or hour == 19) and (minute <= 9):
                await message.answer(text=f'<b>Текущее значение часа: {hour}</b>. Сервер перезагружается в <u>{hour}:00</u>, тебе лучше выбрать время чуть попозже!')
                return
            if (hour == 9) and (minute <= 16 and minute >= 5):
                await message.answer(text=f'<b>Текущее значение минут: {minute_str}</b>. Сервер перезагружается в <u>9:10</u>, тебе лучше выбрать время чуть попозже!')
                return
            minute_str= str(minute)
            if minute == 0:
                minute_str = '00'
            elif minute < 10:
                minute_str = '0' + minute_str
            await set_minute(message.from_user.id, minute_str)
            await message.answer(
                f'Отлично! Теперь шлюшандры будут присылаться в <b>{hour}:{minute_str}</b>. <i>Изменения, будут применены при следующей перезагрузке сервера...</i>',
                reply_markup=await get_notify_keyboard(message.from_user.id))
            await state.clear()
    else:
        await message.answer('Это не похоже на минутный формат 🤨\nЧё ебальник разинул?')


async def send_incel_photo(callback: Union[CallbackQuery, None] = None, user_id: Union[int, None] = None):
    if callback:
        user_id = callback.from_user.id
        username = callback.from_user.username
    else:
        username = 0
    try:
        q = await get_queue(user_id)
        if q is None or len(q) == 0:
            await add_current_state(user_id, 0, username)
            if callback:
                await callback.message.delete()
            else:
                await bot.send_message(chat_id=user_id, text='Очередь пуста 👌')
            return

        i = min(q)
        media = InputMediaPhoto(media=await get_photo_id_by_id(i))
        reply_markup = await get_rates_keyboard(num=i, mailing=1)

        if callback:
            async with ChatActionSender(bot=bot, chat_id=user_id, action='upload_photo'):
                await callback.message.edit_media(media=media, reply_markup=reply_markup)
        else:
            await bot.send_photo(user_id, await get_photo_id_by_id(i), reply_markup=reply_markup)

        await add_current_state(user_id, i, username)

    except Exception as e:
        error_text = f'Произошла ошибка! Пользователь {username if username != 0 else "id:"} ({user_id}) не получил фото из очереди.\n{e}'
        if not 'specified new message content and reply markup are exactly the same' in str(e):
            await bot.send_message(chat_id=972753303, text=error_text)
            if 'wrong type of the web page content' in str(e):
                num = min(await get_queue(user_id))
                await bot.send_message(chat_id=972753303, text=f'Фотка #{num} была удалена из очереди')
                await delete_from_queue(user_id, num)


async def download_hash(num=1, link=None):
    path = f"{os.path.dirname(__file__)}/pictures/image_{random.randint(1, 10 ** 8)}.jpg"
    if link:
        value = link
    else:
        value = await get_photo_id_by_id(num)
    if value[:4] == 'http':
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(value) as response:
                    if response.status == 200:
                        async with aiofiles.open(path, "wb") as file:
                            content = await response.read()
                            await file.write(content)
        except Exception as e:
            await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! Код 6666\n{e}')
    else:
        f = await bot.get_file(value)
        f_path = f.file_path
        await bot.download_file(f_path, path)
    try:
        hash = get_hash(path)
        await add_to_weekly(value, None, hash)
        os.remove(path)
    except Exception as e:
        await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! Код 7777\n{e}')


@dp.callback_query(RateCallBack.filter())
async def filter_rates(callback: CallbackQuery,
                       callback_data: RateCallBack, state: FSMContext):
    if not (await check_id(callback.from_user.id, callback.from_user.username))[0]:
        await state.set_state(FSMFillForm.banned)
        await callback.message.delete()
        await callback.answer('Ты заблокирован!')
        return
    num = callback_data.photo_id
    mailing = callback_data.mailing
    if mailing == 2:
        last_rate = await get_rate(num, callback.from_user.id)
    else:
        await callback.answer(text=rate[callback_data.r])
    votes = await get_votes(num)
    photo_is_not_posted = True
    await insert_last_rate(callback.from_user.id, num)
    global incels
    incels = await get_users()
    if mailing == 1 and {await get_id_by_username(i) for i in votes.keys() if await get_id_by_username(i) in incels} == incels:
        photo_is_not_posted = False  # индикатор, который отвечает за публикацию поста в канал (для того чтобы после изменения оценки пост не выложился еще раз)
    await add_rate(num, callback.from_user.username, callback_data.r)
    await delete_from_queue(callback.from_user.id, num)
    last_upd = await get_last_upd(callback.from_user.id)
    current_time = int(time.time())
    if current_time - last_upd <= 60:
        await increment_time(callback.from_user.id, current_time - last_upd, current_time)
    else:
        await increment_time(callback.from_user.id, 1, current_time)
    if mailing == 1:
        try:
            votes = await get_votes(num)
            if len(votes.keys()) + 1 == len(await get_users()):
                voted = set(votes.keys())
                users = set()
                for i in await get_users():
                    users.add(await get_username_by_id(i))
                last_username = next(iter((users - voted)))
                if last_username and isinstance(last_username, str) and len(last_username) > 0:
                    user_id = await get_id_by_username(last_username)
                    if user_id and (last_username not in states_users or states_users[last_username] + datetime.timedelta(
                            hours=1) < datetime.datetime.now()):
                        await add_afk(user_id)
                        await bot.send_message(
                            text=f'<b>{last_username}</b>, ебать твой рот, нажми на кнопку, ты последний такой хуесос 😡',
                            chat_id=user_id)
                        states_users[last_username] = datetime.datetime.now()

            if len(votes.keys()) >= len(await get_users()) and photo_is_not_posted:
                photo_id = await get_photo_id_by_id(num)
                note_str_origin = await get_note_sql(num)
                if note_str_origin is None or '/anon' not in note_str_origin:
                    await add_to_queue_public_info(num)
                avg = sum(votes.values()) / len(votes.keys())
                value = photo_id
                path_local = f"{os.path.dirname(__file__)}/pictures/image_{random.randint(1, 10 ** 8)}.jpg"
                if value[:4] == 'http':
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(value) as response:
                                if response.status == 200:
                                    async with aiofiles.open(path_local, "wb") as file:
                                        content = await response.read()
                                        await file.write(content)
                    except Exception as e:
                        await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! Код 1453\n{e}')
                else:
                    f = await bot.get_file(value)
                    f_path = f.file_path
                    await bot.download_file(f_path, path_local)
                try:
                    hash = get_hash(path_local)
                    await add_to_weekly(photo_id, avg, hash)
                    os.remove(path_local)
                except Exception:
                    await add_to_weekly(photo_id, avg)
                avg_str = '{:.2f}'.format(avg)
                extra = ''
                spoiler = False
                if avg == 0:
                    spoiler = True
                    extra = '<b>🚨Осторожно!🚨\nУберите от экранов детей и людей с тонкой душевной организацией. Данное фото может Вас, пидоров, шокировать\n\n</b>'
                if avg == 11:
                    spoiler = True
                    extra = '<b>😍 Все участники банды инцелов оценили фото на 11 😍</b>\n\n'

                user_rates = ''
                sorted_rates = sorted(votes.items(), key=lambda x: x[1], reverse=True)
                rounded = round(avg)
                for key, value in sorted_rates:
                    if value == rounded:
                        await add_hit(await get_id_by_username(key), 1)
                    else:
                        await add_hit(await get_id_by_username(key))
                    user_id = await get_id_by_username(key)
                    if user_id:
                        await add_rate_to_avg(user_id, value)
                    user_rates += f'@{key}: <i>{value}</i>\n'

                note_str = f': <blockquote>{note_str_origin.replace("/anon", "").strip()}</blockquote>\n' if note_str_origin else '\n\n'
                name = await get_origin(num)
                name = '@' + name if name[0] != '👥' else f'👥 <a href="vk.com/{name[2:]}">{await get_group_name(name[:name.find("?")][2:])}</a>'
                txt = extra + f'Автор пикчи <b>{name}</b>' + note_str + "Оценки инцелов:\n" + user_rates + '\n' f'Общая оценка: <b>{avg_str}</b>' + f'\n<i>#{rate2[rounded].replace(" ", "_")}</i>'
                await bot.send_photo(chat_id=channel_id, photo=photo_id, caption=txt,
                                     has_spoiler=spoiler)
        except Exception as e:
            await bot.send_message(chat_id=972753303, text=f'Произошла ошибка после оценки фото № {num} пользователем {callback.from_user.username}.\n{e}')
        await send_incel_photo(callback=callback)
        return
    elif mailing == 2:
        if last_rate != callback_data.r:
            await add_overshoot(callback.from_user.id)
            await callback.answer(text=rate[callback_data.r])
        else:
            await callback.answer('🤨 В сохраненки кинул, онанист чёртов???')
        await callback.message.delete()
        return
    elif mailing == 3:
        previous = await get_message_to_delete(callback.from_user.id)
        await send_next_photo(callback.from_user.id)
        await callback.message.delete()
        await send_photo_to_users(callback.from_user.id, num)
        if '-' in previous:
            previous = list(map(int, previous.split('-')))
            msgs_list = [i for i in range(previous[0], previous[-1] + 1)]
            await bot.delete_messages(chat_id=callback.from_user.id, message_ids=msgs_list)
        await download_hash(num)
        return
    elif mailing == 4:
        rate_loc = await get_not_incel_rate(num)
        if rate_loc == -1:
            rate_loc = callback_data.r + round(random.uniform(-1, 1), 2)
            rate_loc = max(0, min(10, rate_loc))
            await add_rate_not_incel(num, rate_loc)
            await send_results(num, rate_loc)

    await download_hash(num)
    await callback.message.edit_text(f'Ты поставил оценку {callback_data.r} {emoji[callback_data.r]}')
    await state.clear()
    await send_photo_to_users(callback.from_user.id, num)


@dp.callback_query(ConfirmCallBack.filter())
async def confirm_photo_filter(callback: CallbackQuery,
                               callback_data: ConfirmCallBack, state: FSMContext):
    action = callback_data.action
    photo_id = callback_data.photo_id
    await callback.answer(text=['❌', '✅'][action % 2])
    if action == 0:
        await callback.message.edit_text('⛔️ Поймали в последний момент.\nОтправка фото отменена')
    elif action == 1:
        note = await get_note_sql(photo_id)
        note = '' if note is None else f'"{note}"'
        await bot.send_photo(972753303, photo=await get_photo_id_by_id(photo_id),
                             caption=f'Фото от пользователя <i>@{callback.from_user.username}</i>\n<i>{note}</i>',
                             reply_markup=moderate_keyboard(photo_id, callback.from_user.username))
        await callback.message.edit_text("😎 Твоё фото добавлено в очередь")


@dp.callback_query(ModerateCallBack.filter())
async def moderate_photo(callback: CallbackQuery,
                         callback_data: ModerateCallBack, state: FSMContext):
    action = callback_data.action
    photo_id = callback_data.photo_id
    creator = callback_data.creator
    if action != 4:
        await callback.answer(text=['❌', '✅'][action % 2])
    else:
        await callback.answer(text='🔕')
    await callback.message.edit_reply_markup(reply_markup=None)
    if action == 0:
        creator_id = await get_id_by_username(creator)
        if creator_id:
            try:
                await add_rate_not_incel(photo_id, -2)
                await bot.send_photo(chat_id=creator_id, photo=await get_photo_id_by_id(photo_id),
                                     caption=replicas['reject'],
                                     reply_markup=await get_keyboard(creator_id))
            except Exception as e:
                await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! Код 8\n{str(e)}')
        await callback.message.answer(text=f'<b>Забанить долбоеба?</b>\n<i>@{creator}</i>',
                                      reply_markup=moderate_keyboard(-1, creator))
    elif action == 1:
        #creator_id = get_id_by_username(creator)
        # if creator_id is not None:
        #     try:
        #         await bot.send_photo(chat_id=creator_id, photo=get_photo_id_by_id(photo_id),
        #                      caption='Ваше фото ✅ <b>принято</b> ✅\n\nОжидайте, пока нейросеть оценит его. Напоминаем, что это может занять время ⏰ <span class="tg-spoiler">(Много времени ⌚️🕐⏲)</span>',
        #                      reply_markup=not_incel_keyboard)
        #     except Exception as e:
        #         await bot.send_message(chat_id=972753303, text=f'Произошла ошибка!\n{str(e)}')
        await callback.message.answer(text='Оцени это фото',
                                      reply_markup=await get_rates_keyboard(photo_id, 4))
    elif action == 3:
        creator_id = await get_id_by_username(creator)
        if creator_id is None:
            await callback.message.edit_text(text=f'Строка с username: <i>"{creator}"</i> не найдена в таблице')
            return
        result = await get_ban(creator_id)
        if result == 0:
            await callback.message.edit_text(text=f'Строка с username: <i>"{creator}"</i> не найдена в таблице')
        else:
            await callback.message.edit_text(text=f'Пользователь <i>@{creator}</i> был успешно забанен! Нахуй его',
                                             reply_markup=None)
            await bot.send_message(chat_id=creator_id, text='🔫 C этого момента ты в бане')
    elif action == 4:
        rate_loc = await get_not_incel_rate(photo_id)
        if rate_loc == -1:
            rate_loc = round(random.uniform(3, 7), 2)
            await add_rate_not_incel(photo_id, rate_loc)
            await send_results(photo_id, str(rate_loc))
    else:
        await callback.message.edit_text(text=f'Пощадим его', reply_markup=None)


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    result = await check_id(user_id, username)
    if result[0]:
        await message.answer('Нахуя ты старт нажал? Если для теста, извиняюсь, хотя похуй. Иди нахуй!', reply_markup=await get_keyboard(message.from_user.id))
        await state.set_state(FSMFillForm.verified)
    else:
        if result[1] <= 0   :
            await message.answer(random.choice(emoji_banned) + ' ' + random.choice(replicas['banned']).replace('$', '"'),
                                 reply_markup=ReplyKeyboardRemove())
            await state.set_state(FSMFillForm.banned)
            return

        await message.answer(replicas['hi'].replace('$', '"'), disable_web_page_preview=True, reply_markup=await get_keyboard(user_id))

        #await message.answer_sticker(sticker='CAACAgIAAxkBAAELD9NljoEHEI6ehudWG_Cql5PXBwMw-AACSCYAAu2TuUvJCvMfrF9irTQE', reply_markup=not_incel_keyboard)


@dp.message_reaction()
async def message_reaction_handler(message_reaction: MessageReactionUpdated):
    if len(message_reaction.new_reaction)!=0:
        await bot.set_message_reaction(chat_id=message_reaction.chat.id, message_id=message_reaction.message_id,
                                   reaction=[ReactionTypeEmoji(emoji=message_reaction.new_reaction[0].emoji)])


@dp.message(Command(commands='password_yaincel'))
async def password_yaincel(message: Message, state: FSMContext):
    await set_verified(message.from_user.id)
    await message.answer(text='Поздравляю, ты теперь в нашей банде инцелов!', reply_markup=await get_keyboard(message.from_user.id))
    await state.set_state(FSMFillForm.verified)


@dp.message(Command(commands='anon'), ~F.photo)
async def anon(message: Message, state: FSMContext):
    await message.answer(text='А фоточка? 🥺', reply_markup=await get_keyboard(message.from_user.id))


@dp.message(Command(commands='clear_admin_queues'))
async def clear_admin_queues_command(message: Message, state: FSMContext):
    try:
        for user in await get_admins():
            await remove_from_admins_queue(user, 0)
    except Exception as e:
        await message.answer(text=f'Произошла ошибка! Код 400\n{e}')
    await message.answer('Очереди были очищены')


@dp.message(Command(commands='help'))
async def help(message: Message, state: FSMContext):
    result = await check_id(message.from_user.id, message.from_user.username)
    if not result[0]:
        await message.answer(replicas['help'].replace('$', '"'), disable_web_page_preview=True, reply_markup=await get_keyboard(message.from_user.id))
        async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action='upload_video'):
            await message.answer_video(video=FSInputFile(path=f'{os.path.dirname(__file__)}/asset/guide.mp4'))
        return
    await message.answer(
        text='Просто скинь мне любое фото, и оно будет отправлено всем участникам <a href="https://t.me/+D_c0v8cHybY2ODQy">банды инцелов</a>.\nКнопка "Статистика 📊" покажет тебе график всех средних значений оценок твоих фото.\n' + \
             'Отправил оценку ошибочно? Тогда нажми кнопку "Изменить последнюю оценку ✏️".\nЕсли ты хочешь добавить заметку к фото, сделай подпись к ней и отправь мне, она будет показана в канале по окончании голосования\n\n<span class="tg-spoiler">/quote — случайная цитата</span>',
        disable_web_page_preview=True, reply_markup=await get_keyboard(message.from_user.id))
    async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action='upload_video'):
        await message.answer_video(video=FSInputFile(path=f'{os.path.dirname(__file__)}/asset/guide.mp4'))


@dp.message(Command(commands='info'))
async def info(message: Message, state: FSMContext):
    result = await check_id(message.from_user.id, message.from_user.username)
    await message.answer(replicas['info'].replace('$', ''), disable_web_page_preview=True, reply_markup=await get_keyboard(message.from_user.id))


@dp.message(Command(commands='about'))
async def about(message: Message, state: FSMContext):
    result = await check_id(message.from_user.id, message.from_user.username)
    await message.answer(replicas['about'].replace('$', ''), disable_web_page_preview=True, reply_markup=await get_keyboard(message.from_user.id))


def format_caption(text):
    if text is None:
        return ''
    if text.lower().count('(с)') + text.lower().count('(c)') + text.count('©') == 0:
        caption = f'<blockquote>{text}</blockquote>'
    else:
        if '©' in text:
            caption = '<blockquote>' + text[:text.find('©') - 1] + '</blockquote>' + text[text.find('©'):]
        else:
            caption = '<blockquote>' + text[:text.find('(') - 1] + '</blockquote>' + text[text.find('('):]
    return caption


async def send_quote(user_id):
    url = "http://api.forismatic.com/api/1.0/"
    params = {
        "method": "getQuote",
        "format": "json",
        "lang": "ru"
    }
    try:
        rand_int = random.random()
        keyboard = [[InlineKeyboardButton(text='Еще цитата 📖', callback_data='more')]]
        markup_local = InlineKeyboardMarkup(inline_keyboard=keyboard)

        if rand_int <= 0.01:
            quote = legendary_quote
        elif rand_int <= 0.4:
            try:
                result = get_randQuote()
            except Exception as e:
                await bot.send_message(chat_id=972753303, text=f'Произошла ошибка!\n{e}')
                return
            if result is None:
                return
            if result[0]:
                caption = format_caption(result[1])
                await bot.send_photo(chat_id=user_id, photo=result[0], caption=caption, reply_markup=markup_local)
            else:
                caption = format_caption(result[1])
                await bot.send_message(chat_id=user_id, text=caption, reply_markup=markup_local)
            return
        else:
            response = requests.get(url, params=params)
            quote = response.json().get("quoteText")

        await bot.send_message(chat_id=user_id, text=f'<blockquote>{quote}</blockquote>', reply_markup=markup_local)
    except requests.RequestException as e:
        await bot.send_message(chat_id=user_id, text=f'<i>{legendary_quote}</i>')


@dp.message(Command(commands='quote'))
async def quote(message: Message):
    await send_quote(message.from_user.id)


@dp.callback_query(F.data == 'more')
async def process_more_press(callback: CallbackQuery):
    await callback.answer()
    await send_quote(callback.from_user.id)


@dp.message(Command(commands='get_users'), F.from_user.id.in_(incels))
async def send_clear_users_db(message: Message):
    incels = await get_users()
    db = await get_usersinfo_db()
    if db is None:
        await message.answer(text='БД пуста!')
        return

    txt = f'Всего пользователей: <b>{len(db)}</b>\n\n<b>Инцелы:</b>\n'
    db_incel = [i for i in db if i[3]]
    db_not_incel = [i for i in db if i[3] == 0]
    db_not_incel = sorted(db_not_incel, key=lambda x: (
        -int(x[5].split(',')[-1]) if x[5] else float('inf'), x[1] if x[1] else ''))
    for user in db_incel:
        username = f'@{user[1]}' if user[1] else '⬜'
        queue_str = f'<i>Очередь:</i> {user[-2][:60]}' if (user[3] and user[-2]) else '<i>Очередь пуста ✅</i>'
        line = f'<b>{username}</b> | {queue_str}\n'
        if len(line) + len(txt) < 4096:
            txt += line
        else:
            try:
                await message.answer(text=txt)
            except Exception as e:
                await message.answer(text=f'Произошла ошибка!\n{e}')
            txt = line
    txt += '\n<b>Попуски:</b>\n'
    for user in db_not_incel:
        username = f'@{user[1]}' if user[1] else '⬜'
        banned = '| забанен 💀' if user[2] else ''
        a = ","
        photos = '' if user[5] is None else f"| <i>Фотки:</i> {', '.join(user[5].split(a))}"
        line = f'<b>{username}</b> {banned} {photos}\n'
        if line == '<b>⬜</b>  \n':
            continue
        if len(line) + len(txt) < 4096:
            txt += line
        else:
            try:
                await message.answer(text=txt)
            except Exception as e:
                await message.answer(text=f'Произошла ошибка!\n{e}')
            txt = line
    try:
        await message.answer(text=txt)
    except Exception as e:
        await message.answer(text=f'Произошла ошибка!\n{e}')


@dp.message(Command(commands='clear_queue'), F.from_user.id.in_(incels))
async def clear_queue(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='Иди нахуй!')
    else:
        try:
            for user in await get_users():
                await delete_from_queue(id=user)
                await add_current_state(id=user, num=0)
            await message.answer(text='Очереди очищены 🫡')
        except Exception as e:
            await message.answer(text=f'Произошла ошибка! Код 10\n{e}')


@dp.message(Command(commands='upd_groupnames'), F.from_user.id.in_(incels))
async def upd_groupnames(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='Иди нахуй!')
    else:
        await update_groupnames()
        await message.answer('Названия групп обновлены!')



@dp.message(Command(commands='clear_states'), F.from_user.id.in_(incels))
async def clear_state(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='Иди нахуй!')
    else:
        try:
            for user in await get_users():
                await add_current_state(id=user, num=0)
            await message.answer(text='Состояния очищены 🫡')
        except Exception as e:
            await message.answer(text=f'Произошла ошибка! Код 11\n{e}')


@dp.message(Command(commands='backup'), F.from_user.id.in_(incels))
async def backup_files(message: Message):
    try:
        async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action='upload_document'):
            doc = InputMediaDocument(media=FSInputFile(f"{os.path.dirname(__file__)}/DB/slutsDB.db"))
            doc2 = InputMediaDocument(media=FSInputFile(f"{os.path.dirname(__file__)}/DB/usersDB.db"))
            doc3 = InputMediaDocument(media=FSInputFile(f"{os.path.dirname(__file__)}/DB/weekly.db"))
            doc4 = InputMediaDocument(media=FSInputFile(f"{os.path.dirname(__file__)}/DB/weekly_info.db"))
            doc5 = InputMediaDocument(media=FSInputFile(f"{os.path.dirname(__file__)}/DB/admins.db"))
            doc6 = InputMediaDocument(media=FSInputFile(f"{os.path.dirname(__file__)}/DB/emoji.db"))
            doc7 = InputMediaDocument(media=FSInputFile(f"{os.path.dirname(__file__)}/DB/statham.db"),
                                      caption=f'Бэкап <i>{datetime.datetime.now().date()}</i>')
            await bot.send_media_group(media=[doc, doc2, doc3, doc4, doc5, doc6, doc7], chat_id=message.chat.id)
    except Exception as e:
        await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! При отправке файлов для бэкапа.\n{e}')


@dp.message(Command(commands='god_mode'), F.from_user.id.in_(incels))
async def god_mode(message: Message):
    if message.from_user.id == 972753303:
        await set_admin(972753303)
        await message.answer(text='С возвращением!', reply_markup=await get_keyboard(972753303))


@dp.message(Command(commands='chill_mode'), F.from_user.id.in_(incels))
async def chill_mode_lol(message: Message):
    if message.from_user.id == 972753303:
        await set_admin_mode(972753303, 2)
        await message.answer(text='Почилль, дружище!', reply_markup=await get_keyboard(972753303))


@dp.message(Command(commands='default_mode'), F.from_user.id.in_(incels))
async def default_mode_lol(message: Message):
    if message.from_user.id == 972753303:
        await set_admin_mode(972753303, 1)
        await message.answer(text='Включен режим модерации', reply_markup=await get_keyboard(972753303))



@dp.message(Command(commands='get_users_info_db'), F.from_user.id.in_(incels))
async def send_users_db(message: Message):
    db = await get_usersinfo_db()
    if db is None:
        await message.answer(text='БД пуста')
        return
    txt = map(str, db)
    txt = '\n'.join(txt)
    for i in range((len(txt) + 4096) // 4096):
        await message.answer(text=txt[i * 4096:(i + 1) * 4096])


@dp.message(Command(commands='avgs'), F.from_user.id.in_(incels))
async def send_avgs(message: Message):
    def center_string(s, total_length):
        s = str(s)
        remaining_length = total_length - len(s)
        if remaining_length <= 0:
            return "<code>" + s[:total_length] + "</code>"

        right_spaces = remaining_length // 2
        left_spaces = remaining_length - right_spaces

        return "<code>" + " " * left_spaces + s + " " * right_spaces + "</code>"

    txt = '<b>Характеристики</b>\n'
    mx_len_username = 0
    averages, overshoot, hit, afk = {}, {}, {}, {}
    for user in incels:
        username = await get_username_by_id(user)
        if len(username) > mx_len_username:
            mx_len_username = len(username)
        average_tuple = await get_avg_stats(user)
        if average_tuple is None:
            averages[username] = afk[username] = overshoot[username] = 0
            hit[username] = '0.00%'
        else:
            averages[username] = average_tuple[1] / average_tuple[2]
            overshoot[username] = average_tuple[3]
            hit[username] = f'{"{:.1f}".format(average_tuple[4] / average_tuple[5] * 100)}%'
            afk[username] = average_tuple[6]
    averages = sorted(averages.items(), key=lambda x: x[1], reverse=True)
    txt += f'<code>{"".ljust(mx_len_username)}  </code>   <b>AVG    👟➔👠<code>   🎯   ⠀</code>AFK</b>\n'
    hidden_space = '<code> </code>'
    for username, avg in averages:
        if avg is None:
            avg = 0
        if overshoot[username] >= 10 ** 4:
            overshoot[username] = f'{overshoot[username] // 1000}к'
        if afk[username] >= 10 ** 4:
            afk[username] = f'{afk[username] // 1000}к'
        txt += f'<code>@{username.ljust(mx_len_username)}</code>┃{"{:.4f}".format(avg)}│{center_string(overshoot[username], 5)}│{center_string(hit[username], 6)}│<code>{str(afk[username]).rjust(4)}</code>\n'
    await message.answer(txt, reply_markup=await get_keyboard(message.from_user.id))


@dp.message(Command(commands='queue'), F.from_user.id.in_(incels))
async def get_queue_rates(message: Message):
    db = await get_usersinfo_db()
    if db is None:
        await message.answer(text='<b>БД пуста</b>', reply_markup=await get_keyboard(message.from_user.id))
        return
    db_incel = [i for i in db if i[3]]
    txt = '<b>Фото в очереди</b>\n'
    mx_len_username = 0
    for incel_loc in db_incel:
        if len(incel_loc[1]) > mx_len_username:
            mx_len_username = len(incel_loc[1])
    cnt = 0
    db_incel = sorted(db_incel, key=lambda x: len(x[-2].split(',')) if x[-2] else 0, reverse=True)

    for incel_loc in db_incel:
        admin_str = ""
        if incel_loc[0] in await get_admins():
            admin_queue_len = len(await get_admins_queue(incel_loc[0]))
            admin_str = f'{"" if admin_queue_len == 0 else f"│{admin_queue_len}"}'
        if incel_loc[-2] is None:
            queue = '✅'
        else:
            queue = f"{len(incel_loc[-2].split(','))}"
            cnt += 1
        line = f'<code>@{incel_loc[1].ljust(mx_len_username)}</code>┃{queue}{admin_str}\n'
        txt += line
    txt += f'\n<i>Итого ублюдков: <b>{cnt}</b></i>'
    await message.answer(text=txt, reply_markup=await get_keyboard(message.from_user.id))


@dp.message(Command(commands='public_queue'), F.from_user.id.in_(incels))
async def get_queue_rates(message: Message):
    try:
        queue_length = await public_queue()
        await message.answer(text=f'<b>Очередь публикации</b>\n<code>@rateimage</code>┃{queue_length}', reply_markup=await get_keyboard(message.from_user.id))
    except Exception as e:
        await message.answer(text=f'Произошла ошибка!\n{e}', reply_markup=await get_keyboard(message.from_user.id))


@dp.message(Command(commands='wasted_time'), F.from_user.id.in_(incels))
async def get_queue_rates(message: Message):
    txt = '<b>Проёбано времени</b>\n'
    mx_len_username = 0
    wasted = {}
    for user in incels:
        username = await get_username_by_id(user)
        wasted[username] = (await get_avg_stats(user))[8]
        if len(username) > mx_len_username:
            mx_len_username = len(username)
    wasted = sorted(wasted.items(), key=lambda x: x[1], reverse=True)
    for user, w_time in wasted:
        txt += f'<code>@{user.ljust(mx_len_username)}</code>┃{convert_unix_time(w_time)}\n'
    await message.answer(txt, reply_markup=await get_keyboard(message.from_user.id))


@dp.message(Command(commands='remove_quote'), F.from_user.id.in_(incels))
async def remove_quote(message: Message):
    if len(message.text) <= len('remove_quote') + 2:
        await message.answer(text='Произошла ошибка!')
        return
    num = int(message.text[len('remove_quote') + 2:])
    res = del_quote(num)
    if res:
        await message.answer(text=f'Цитата №{num} удалена')
    else:
        await message.answer(text='Произошла ошибка!')


@dp.message(Command(commands='get_statham_db'), F.from_user.id.in_(incels))
async def send_statham_db(message: Message):
    db = get_statham_db()
    if db is None or len(db) == 0:
        await message.answer(text='БД пуста')
        return
    txt = map(str, db)
    txt = '\n'.join(txt)
    for i in range((len(txt) + 4096) // 4096):
        await message.answer(text=txt[i * 4096:(i + 1) * 4096])


@dp.message(Command(commands='getcoms'), F.from_user.id.in_(incels))
async def get_all_commands(message: Message):
    txt = '/start\n/help\n/stat\n/anon\n/info\n/quote\n/del_...\n/ban_...\n/send_..\n/send_all\n/send_incels\n/send_topsync_get_users()\n/cs_...\n/cavg_...\n/new_quote\n/remove_quote ...\n/queue\n/wasted_time\n/backup\n/get_statham_db\n/send_tier_list\n/upd_groupnames\n/avgs\n/upd_file\n/delete_tier_list\n/get_users\n/get_users_info_db\n/get_weekly_db\n/get_latest_sluts\n/get_sluts_db\n/weekly_off\n/weekly_on\n/clear_queue\n/clear_states\n/clear_admin_queues\n/get_ban\n/password_yaincel\n/public_queue\n/getcoms\n/amogus\n/pepe\n/about'
    await message.answer(text=txt, reply_markup=await get_keyboard(message.from_user.id))


@dp.message(Command(commands='get_weekly_db'))
async def send_weekly_db(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='Иди нахуй!')
    else:
        db = await get_weekly_db_info()
        if db is None:
            await message.answer(text='БД пуста')
            return
        txt = str(db)
        for i in range((len(txt) + 4096) // 4096):
            await message.answer(text=txt[i * 4096:(i + 1) * 4096])


@dp.message(Command(commands='weekly_off'))
async def weekly_cancel_func(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='Иди нахуй!')
    else:
        await weekly_cancel(message.from_user.id)
        await message.answer(text='Еженедельная рассылка тир листа отключена')


@dp.message(Command(commands='weekly_on'))
async def send_users_db_func(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй')
    else:
        await weekly_resume(message.from_user.id)
        await message.answer(text='Еженедельная рассылка тир листа возобновлена')


@dp.message(Command(commands='get_ban'))
async def ban_user(message: Message, state: FSMContext):
    await get_ban(message.from_user.id)
    await message.answer(text='Ты исключен из банды инцелов, насколько ты плох? Режим милой тяночки включён', reply_markup=ReplyKeyboardRemove())
    await state.set_state(FSMFillForm.banned)


@dp.message(Command(commands='get_sluts_db'))
async def send_sluts_db(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='Иди нахуй!')
    else:
        if await get_sluts_db() is None:
            await message.answer(text='БД пуста')
            return
        txt = map(str, await get_sluts_db())
        txt = '\n'.join(txt)
        for i in range((len(txt) + 4096) // 4096):
            await message.answer(text=txt[i * 4096:(i + 1) * 4096])


@dp.message(Command(commands='get_latest_sluts'))
async def send_latest_sluts_db(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='Иди нахуй!')
    else:
        sluts_list = await get_sluts_db()
        if sluts_list is None:
            await message.answer(text='БД пуста')
            return
        sluts_list = sluts_list[-5:]
        sluts_last3 = []
        txt = ''
        for i in iter(sluts_list):
            if i[2] is None:
                rates = 'Нет оценок'
            else:
                rates = '<b>Оценки:</b><blockquote>'
                for key, value in json.loads(i[2]).items():
                    rates += f'<i>{key}</i> – {value}, '
                rates = rates[:-2] + '</blockquote>'
            if i[1] is None or len(i[1]) == 0 :
                caption = ''
            else:
                caption = f'"<i>{i[1]}</i>" | '
            name = i[-1]
            name = '@' + name if name[0] != '👥' else f'👥 <a href="vk.com/{name[2:]}">{name[:name.find("?")][2:]}</a>'
            txt += f'№ {i[0]} Автор: {name} | {caption}{rates}\n'
        await message.answer(text=txt, disable_web_page_preview=True)


@dp.message(F.content_type.in_({ContentType.PHOTO, ContentType.TEXT}), StateFilter(FSMFillForm.sendQuote))
async def insert_new_quote(message: Message, state: FSMContext):
    await state.clear()
    if message.text:
        insert_quote(photo=None, caption=message.text)
    else:
        file_id = message.photo[-1].file_id
        insert_quote(photo=file_id, caption=message.caption)
    await message.answer(text='Цитата зафиксирована 👍')


@dp.message(F.text == 'яинцел')
async def get_verified(message: Message, state: FSMContext):
    await set_verified(id=message.from_user.id)
    await message.answer(
        text='<b>Привет, уёбище!</b>\nТеперь ты в нашей банде. Просто пришли мне фото, и его смогут оценить все участники. Если ты хочешь добавить заметку, сделай подпись к фото и отправь мне, она будет показана в <b><a href="https://t.me/+D_c0v8cHybY2ODQy">канале</a></b> по окончании голосования. Также тебе будут присылаться фото от других пользователей для оценки. Не забудь добавить <b>/anon</b>, если не хочешь, чтобы фото попало в <b><a href="https://t.me/rateimage">публичный канал</a></b>',
        disable_web_page_preview=True, reply_markup=await get_keyboard(message.from_user.id))
    await state.set_state(FSMFillForm.verified)


@dp.message(F.photo, StateFilter(FSMFillForm.sending_photo))
async def get_photo_by_button(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    last_num = await get_last()
    await add_photo_id(last_num + 1, file_id, message.from_user.username)
    await add_girlphoto(message.from_user.id, last_num + 1)
    await message.answer(text='Оцени фото, которое ты скинул!',
                         reply_markup=await get_rates_keyboard(last_num + 1, 0))
    await state.clear()


@dp.message(F.text == 'Не отправлять фото', StateFilter(FSMFillForm.sending_photo))
async def cancel_sending(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text='Ты вышел из меню отправки фото')
    await add_current_state(message.from_user.id, 0, message.from_user.username)


@dp.message(~F.photo, StateFilter(FSMFillForm.sending_photo))
async def invalid_type_photo(message: Message, state: FSMContext):
    await message.answer(text='Это похоже на фото, долбоёб?', reply_markup=keyboard3)


async def send_photo_to_users(origin_user, num: int):
    for user in await get_users():
        if user == origin_user:
            continue
        await add_to_queue(user, num)
        if await get_current_state(user) != 0:
            continue
        await add_current_state(user, num)
        await bot.send_photo(user, await get_photo_id_by_id(num), reply_markup=await get_rates_keyboard(num=num, mailing=1))
        states_users[user] = datetime.datetime.now()


# @dp.message(F.text, StateFilter(FSMFillForm.inserting_comment))
# async def get_note_main(message: Message, state: FSMContext):
#     add_note(get_last_commit(message.from_user.id), message.text)
#     await message.answer(
#         text=f'Охуенная заметка: <b><i>{message.text}</i></b>. Сообщение отправлено всем участникам <a href="https://t.me/+D_c0v8cHybY2ODQy">банды инцелов</a>',
#         disable_web_page_preview=True, reply_markup=basic_keyboard)
#     await send_photo_to_users(message.from_user.id, get_last_commit(message.from_user.id))
#     await state.clear()
#     add_current_state(message.from_user.id, 0, message.from_user.username)





@dp.message(F.text == 'Разослать фото')
async def send_photo(message: Message, state: FSMContext):
    result = await check_id(message.from_user.id, message.from_user.username)
    if not result[0]:
        if result[1] == -1:
            await message.answer(random.choice(emoji_banned) + ' ' + random.choice(replicas['banned']).replace('$', '"'),
                                 reply_markup=ReplyKeyboardRemove())
            await state.set_state(FSMFillForm.banned)
            return
        await message.answer('Ну так пришли его', reply_markup=ReplyKeyboardRemove())
        return
    await message.answer(text='Пришли фото', reply_markup=keyboard3)
    await state.set_state(FSMFillForm.sending_photo)


@dp.message(StateFilter(FSMFillForm.rating))
async def remember_to_rate(message: Message, state: FSMContext):
    await message.answer(text='Поставь оценку, сука!')


@dp.message(F.photo, ~StateFilter(FSMFillForm.sendDM))
async def default_photo(message: Message, state: FSMContext):
    result = await check_id(message.from_user.id, message.from_user.username)
    file_id = message.photo[-1].file_id
    if not result[0]:
        if result[1] == -1:
            await message.answer(random.choice(emoji_banned) + ' ' + random.choice(replicas['banned']).replace('$', '"'),
                                 reply_markup=ReplyKeyboardRemove())
            await state.set_state(FSMFillForm.banned)
            return
        min_num = await get_min()
        await add_photo_id(min_num - 1, file_id, message.from_user.username)
        await add_girlphoto(message.from_user.id, min_num - 1)
        caption = '' if message.caption is None else message.caption
        if caption != '':
            await add_note(min_num - 1, message.caption)

        try:
            if await check_new_user(message.from_user.id):
                await message.answer(replicas['warning'])
            note = '' if (message.caption is None or message.caption.replace('/anon', '').strip() == '') else f'\nПодпись: <i>"{message.caption.replace("/anon", "")}"</i>'
            if message.caption is None or '/anon' not in message.caption:
                text = '🙋🏼‍♀️ Выкладываем в канал'
            else:
                text = '🙅🏼‍♀️ Не выкладываем в канал'
            await message.answer(text=f'{random.choice(emoji_lol)} Давай проверим!{note}\n<b>{text}</b>\n\nПравильно?',
                                 reply_markup=confirm_keyboard(min_num - 1))
        except Exception as e:
            await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! Код 12\n{str(e)}')
        return
    if await already_in_db(file_id):
        txt = '⛔️ <b>Фото уже в БД</b> ⛔️️'
        caption_global[message.from_user.id] = (file_id, message.caption)
        await message.answer(text=txt, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Всё равно добавить!', callback_data='ignore_warning')]]))
        return
    last_num = await get_last()
    await add_photo_id(last_num + 1, file_id, message.from_user.username)
    await add_girlphoto(message.from_user.id, last_num + 1)
    if message.caption:
        await message.answer(text=f'Ты прислал фото с заметкой: <i>{message.caption}</i>. Оцени фото, которое ты скинул',
                             reply_markup=await get_rates_keyboard(last_num + 1, 0))
        await add_note(last_num + 1, message.caption)
    else:
        await message.answer(text='Оцени фото, которое ты скинул', reply_markup=await get_rates_keyboard(last_num + 1, 0))


@dp.callback_query(F.data == 'ignore_warning')
async def igmore_warning(callback: CallbackQuery):
    file_id, caption = caption_global.get(callback.from_user.id, (0, 0))
    caption_global[callback.from_user.id] = (0, 0)
    if file_id == 0:
        await callback.message.edit_text('Произошла ошибка')
        return
    last_num = await get_last()
    await add_photo_id(last_num + 1, file_id, callback.message.from_user.username)
    await add_girlphoto(callback.message.from_user.id, last_num + 1)
    if caption and caption != 0:
        await callback.message.edit_text(text=f'Ты прислал фото с заметкой: <i>{caption}</i>. Оцени фото, которое ты скинул',
                                         reply_markup=await get_rates_keyboard(last_num + 1, 0))
        await add_note(last_num + 1, caption)
    else:
        await callback.message.edit_text(text='Оцени фото, которое ты скинул', reply_markup=await get_rates_keyboard(last_num + 1, 0))


@dp.message(F.text == 'Фото из очереди 🌆')
async def resend_photo(message: Message):
    await send_incel_photo(user_id=message.from_user.id)


@dp.message(F.text == 'Статистика 📊', ~StateFilter(FSMFillForm.rating))
async def stat_photo(message: Message, state: FSMContext):
    result = await check_id(message.from_user.id, message.from_user.username)
    if not result[0]:
        if result[1] == -1:
            await message.answer(random.choice(emoji_banned) + ' ' + random.choice(replicas['banned']).replace('$', '"'),
                                 reply_markup=ReplyKeyboardRemove())
            await state.set_state(FSMFillForm.banned)
            return
        not_incel_rates = await get_avgs_not_incel(message.from_user.id)
        if len(not_incel_rates) > 5:
            async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action='upload_photo'):
                user_id = message.from_user.id
                await get_statistics_not_incel(user_id)
                await bot.send_photo(photo=FSInputFile(f'{os.path.dirname(__file__)}/pictures/myplot_{user_id}.png'), chat_id=message.from_user.id)
                os.remove(f'{os.path.dirname(__file__)}/pictures/myplot_{user_id}.png')
        else:
            await message.answer(text=f'📶 Пришли <b>не менее 6 фото</b>, чтобы получить статистику\nТебе осталось прислать {6 - len(not_incel_rates)}', reply_markup=await get_keyboard(message.from_user.id))
        return
    if await len_photos_by_username(message.from_user.username) > 0:
        async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action='upload_photo'):
            await get_statistics(message.from_user.username)
        votes = len((await get_votes(await max_photo_id_by_username(message.from_user.username))).keys())
        users = len(await get_users())
        if votes > users:
            users = votes
        stats = await get_avg_stats(message.from_user.id)
        avg = ''
        if stats:
            avg_float = stats[1] / stats[2] if stats[2] != 0 else 0
            avg = f'\nCредняя оценка: <b>{"{:.2f}".format(avg_float)}</b> ' + emoji[round(avg_float)]
            overshoot = stats[3]
            hit = stats[4]
            last_incel = stats[6]
            if overshoot in (11, 12, 13, 14):
                ending = 'раз'
            elif overshoot % 10 == 1:
                ending = 'раз'
            elif overshoot % 10 in (2, 3, 4):
                ending = 'раза'
            else:
                ending = 'раз'
            percentage = '0.00' if stats[5] == 0 else "{:.2f}".format(hit / stats[5] * 100)
            if float(percentage) > 30:
                emoji_local = '🤯'
            else:
                emoji_local = '🙂'
            if last_incel < await get_large_last_incel():
                emoji_local2 = '👍'
            else:
                emoji_local2 = '👎'
            if last_incel in (11, 12, 13, 14):
                ending3 = 'раз'
            elif last_incel % 10 == 1:
                ending3 = 'раз'
            elif last_incel % 10 in (2, 3, 4):
                ending3 = 'раза'
            else:
                ending3 = 'раз'
            extra = f'Переобулся: <b>{overshoot} {ending}</b> {["🤡", "👠"][overshoot < await get_large_overshoot()]}\nПроцент угаданной оценки: <b>{percentage}%</b> {emoji_local}\nОказался последним: <b>{last_incel} {ending3}</b> {emoji_local2}\nПроёбано: <b>{convert_unix_time(stats[8])}</b>'
        await message.answer_photo(photo=FSInputFile(f'{os.path.dirname(__file__)}/pictures/myplot_{message.from_user.username}.png'), caption=f'Твое последнее фото оценили {votes}/{users} человек' + avg + '\n' + extra)
        os.remove(f'{os.path.dirname(__file__)}/pictures/myplot_{message.from_user.username}.png')
    else:
        await message.answer(text='Ты еще не присылал никаких фото', reply_markup=await get_keyboard(message.from_user.id))


@dp.message(F.text == 'Изменить последнюю оценку ✏️', ~StateFilter(FSMFillForm.rating))
async def change_last_rate(message: Message, state: FSMContext):
    result = await check_id(message.from_user.id, message.from_user.username)
    if not result[0]:
        if result[1] == -1:
            await message.answer(random.choice(emoji_banned) + ' ' + random.choice(replicas['banned']).replace('$', '"'),
                                 reply_markup=ReplyKeyboardRemove())
            await state.set_state(FSMFillForm.banned)
        await message.answer('Бля, иди нахуй реально!', reply_markup=await get_keyboard(message.from_user.id))
        return
    last_rate = await get_last_rate(message.from_user.id)
    if last_rate == 0 or last_rate == 5:
        await message.answer(text='Ты не оценивал чужих фото!')
        return
    async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action='upload_photo'):
        await bot.send_photo(chat_id=message.from_user.id, photo=await get_photo_id_by_id(last_rate),
                             reply_markup=await get_rates_keyboard(last_rate, 2), caption='Ну давай, переобуйся, тварь!')


@dp.message(F.text == 'Настройки ⚙️', F.from_user.id.in_(sync_get_users()))
async def settings_button_func(message: Message):
    user_id = message.from_user.id
    if user_id not in await get_admins():
        await message.answer(text='Извини, ты больше не админ, лох!', reply_markup=basic_keyboard)
        return
    await message.answer(text=await get_text_of_settings(message.from_user.id), disable_web_page_preview=True,
                         reply_markup=await get_admin_keyboard(user_id))

@dp.message(StateFilter(FSMFillForm.sendDM))
async def send_dm_func(message: Message, state: FSMContext):
    if current_dm_id.get(message.from_user.id, 0) == 0:
        await message.answer(text='Произошла ошибка!', reply_markup=await get_keyboard(message.from_user.id))
        await state.clear()
        return
    if current_dm_id.get(message.from_user.id, 0) == -1:
        current_dm_id[message.from_user.id] = 0
        await state.clear()
        not_incel_ids: set = await get_not_incel()
        successfully_sent = 0
        for id_local in not_incel_ids:
            try:
                await bot.copy_message(chat_id=id_local, message_id=message.message_id,
                                       from_chat_id=message.chat.id)
                successfully_sent += 1
            except Exception as e:
                pass
        await message.answer(text=f'Сообщение отправлено {successfully_sent} пользователю(-ям)')
        return
    if current_dm_id.get(message.from_user.id, 0) == -2:
        current_dm_id[message.from_user.id] = 0
        await state.clear()
        incels: set = await get_users()
        successfully_sent = 0
        for id_local in incels:
            try:
                await bot.copy_message(chat_id=id_local, message_id=message.message_id,
                                       from_chat_id=message.chat.id)
                successfully_sent += 1
            except Exception as e:
                pass
        await message.answer(text=f'Сообщение отправлено {successfully_sent} инцелу(-ам)')
        return
    if current_dm_id.get(message.from_user.id, 0) == -3:
        current_dm_id[message.from_user.id] = 0
        await state.clear()
        incels: set = await get_users()
        successfully_sent = 0
        for id_local in incels:
            if id_local in (955289704):
                continue
            try:
                await bot.copy_message(chat_id=id_local, message_id=message.message_id,
                                       from_chat_id=message.chat.id)
                successfully_sent += 1
            except Exception as e:
                pass
        await message.answer(text=f'Сообщение отправлено {successfully_sent} инцелу(-ам)')
        return
    try:
        await bot.copy_message(chat_id=current_dm_id[message.from_user.id], message_id=message.message_id,
                               from_chat_id=message.chat.id)
        await message.answer(text='Сообщение отправлено!')
    except Exception as e:
        await message.answer(text=f'Произошла ошибка!\nПользователь заблокировал бота 😰')
    current_dm_id[message.from_user.id] = 0
    await state.clear()


@dp.message(
    lambda message: message.text is not None and (
            message.text.lower() == 'спасибо' or message.text.lower() == 'от души' or message.text.lower() == 'благодарю' or message.text.lower() == 'спс'))
async def u_r_wellcome(message: Message):
    await bot.set_message_reaction(chat_id=message.chat.id, message_id=message.message_id,
                                   reaction=[ReactionTypeEmoji(emoji='❤️')], is_big=True)
    await bot.send_sticker(chat_id=message.chat.id,
                           sticker='CAACAgEAAxkBAAEKShplAfTsN4pzL4pB_yuGKGksXz2oywACZQEAAnY3dj9hlcwZRAnaOjAE', reply_to_message_id=message.message_id)
    # for i in range(len(replicas['banned'])):
    #     await message.answer(random.choice(emoji_banned) + ' ' + replicas['banned'][i].replace('$', '"'),
    # #                          reply_markup=ReplyKeyboardRemove())
    # await message.answer(random.choice(emoji_banned) + ' ' + random.choice(replicas['banned']).replace('$', '"'),
    #                      reply_markup=ReplyKeyboardRemove())


@dp.message(
    lambda message: message.text is not None and (
            message.text.lower() == 'иди нахуй' or message.text.lower() == 'пошел нахуй' or message.text.lower() == 'иди на хуй' or message.text.lower() == 'сука'))
async def fuckoff(message):
    await bot.set_message_reaction(chat_id=message.chat.id, message_id=message.message_id,
                                   reaction=[ReactionTypeEmoji(emoji='🤡')], is_big=True)
    await bot.send_sticker(chat_id=message.chat.id,
                           sticker='CAACAgEAAxkBAAEKSrVlAiPwEKrocvOADTQWgKGACLGGlwAChAEAAnY3dj_hnFOGe-uonzAE')


@dp.message(lambda message: message.text is not None and message.text.lower() == 'я гей')
async def ik(message):
    await bot.set_message_reaction(chat_id=message.chat.id, message_id=message.message_id,
                                   reaction=[ReactionTypeEmoji(emoji='💅')], is_big=True)
    await message.answer('Я знаю', reply_to_message_id=message.message_id)


@dp.message(F.text == 'Цитата 💬')
async def incel_get_quote(message: Message):
    await quote(message)


@dp.message(F.dice)
async def dice_message(message: Message):
    emoji = message.dice.emoji
    score = message.dice.value
    await asyncio.sleep(3)
    if score >= dice_points[emoji]:
        await message.answer(text=random.choice(replicas['grats']))
        if emoji == '🎰':
            await bot.set_message_reaction(chat_id=message.chat.id, message_id=message.message_id,
                                           reaction=[ReactionTypeEmoji(emoji='🤯')], is_big=True)
            await bot.send_sticker(chat_id=message.chat.id,
                                   sticker='CAACAgIAAxkBAAELO0dlrmyiCn3T4rSpqM3zyjNv2ksI5AACowADDPlNDMG5-fZfTkbJNAQ')
    else:
        await message.answer(text=random.choice(replicas['regret']))


@dp.message()
async def any_message(message: Message, state: FSMContext):
    result = await check_id(message.from_user.id, message.from_user.username)
    if not result[0] and result[1] != -1:
        if message.text:
            pass
            #await bot.send_message(chat_id=972753303, text=f'<i>@{message.from_user.username}:</i>\n"{message.text}"', disable_notification=True)
        elif message.video or message.animation:
            caption = '' if message.caption is None else f':\n"{message.caption}"'
            await bot.copy_message(from_chat_id=message.chat.id, chat_id=972753303, message_id=message.message_id, disable_notification=True,
                               caption=f'<i>@{message.from_user.username}</i>{caption}')
    if not result[0] and result[1] == -1:
        await message.answer(random.choice(emoji_banned) + ' ' + random.choice(replicas['banned']).replace('$', '"'),
                             reply_markup=ReplyKeyboardRemove())
        await state.set_state(FSMFillForm.banned)
        return
    if message.sticker:
        if random.randint(1, 100) < 5:
            await message.answer('А как тебе мой стикер?')
            await bot.send_sticker(chat_id=message.chat.id, sticker='CAACAgIAAxkBAAELwF1l-pvCWkbiwxyH-htdYp3sFx9-BQACHgADUWPTK8qfqjqR5o-iNAQ')
            await message.answer('В фотографиях я лучше разбираюсь.')
        else:
            extra = [
                f"💬 Оценка стикера нейросетью: <b>{round(random.uniform(4, 9), 2)}</b> из <b>10</b>. Шучу, могу только фотографии оценивать.",
                f"Стикером не получится подписать фоточку, но можно этим эмодзи {message.sticker.emoji}",
                f"Можешь вместо стикера прислать фото с этим эмодзи {message.sticker.emoji}",
                f"Прости, я не вижу картинку, я вижу только эмодзи {message.sticker.emoji}. Так что присылай фото, чтобы я увидел.",
                f"Давай ты изобразишь эту эмоцию {message.sticker.emoji} на фоточке."]
            await message.answer(
                random.choice(replicas.get('sticker', ['Стикеры — это хорошо, но мне больше нравятся фоточки']) + extra).replace('$', '"'),
                disable_web_page_preview=True)
    elif message.video:
        extra = [f"😄 Оценка видео нейросетью: <b>{round(random.uniform(4, 9), 2)}</b> из <b>10</b>. Шучу, могу только фотографии оценивать."]
        await message.answer(random.choice(replicas.get('video', ['Видео — это хорошо, но мне больше нравятся фоточки']) + extra).replace('$', '"'),
                             disable_web_page_preview=True)
    elif message.video_note:
        extra = [f"😄 Оценка кружочка нейросетью: <b>{round(random.uniform(4, 9), 2)}</b> из <b>10</b>. Шучу, могу только фотографии оценивать."]
        await message.answer(random.choice(replicas.get('video_note', ['Кружочки — это хорошо, но мне больше нравятся фоточки']) + extra).replace('$', '"'),
                             disable_web_page_preview=True)
    elif message.voice:
        if random.randint(1, 100) < 5:
            duration = message.voice.duration
            if duration in (11, 12, 13, 14):
                ending = 'секунд'
            elif duration % 10 == 1:
                ending = 'секунда'
            elif duration % 10 in (2, 3, 4):
                ending = 'секунды'
            else:
                ending = 'секунд'
            extra = f'Почему только {duration} {ending}? 🥺 Я готов слушать твой голос вечно! Но только если скинешь фоточку'
            await message.answer(extra, disable_web_page_preview=True)
            return
        await message.answer(random.choice(replicas['voice']).replace('$', '"'), disable_web_page_preview=True)
    elif message.document:
        if 'image' in message.document.mime_type:
            await message.answer('Скинь эту же фоточку со сжатием 🥺')
            return
        extra = '🗾🎑🏞🌅🌄🌠🎇🎆🌇🌆🏙🌃🌌🌉🌁🩻'
        await message.answer(
            random.choice(extra) + ' ' + random.choice(replicas.get('doc', ['Файл — это хорошо, но мне больше нравятся фоточки'])).replace('$', '"'),
            disable_web_page_preview=True)
    elif message.text:
        disabled = ['🧑‍🦽', '👨‍🦽', '👨‍🦼', '🧑‍🦼', '👩‍🦽']
        for i in disabled:
            if i in message.text:
                anecdotes = [
                    'Идут три инвалида по пустыне.\nСлепой, безрукий и колясочник.\nИдут идут и видят оазис. Ну безрукий туда ныряет. Вылазит и видит, что у него руки выросли. Говорит остальным что он волшебный и сразу за ним туда нырнул слепой. Вылазит и говорит:\n— Братцы, я теперь вижу\nА за ним со всех сил ковыляет до оазиса колясочник. Ныряет.\nВылезает и говорит:\n— У меня, блять, теперь новые покрышки.',
                    'На съезд инвалидов-колясочников никто не пришёл.']
                await message.answer(text=random.choice(anecdotes),
                                     reply_markup=await get_keyboard(message.from_user.id))
                return
        await message.answer(text=random.choice(replicas.get('unknown', hz_answers)).replace('$', '"'),
                             reply_markup=await get_keyboard(message.from_user.id), disable_web_page_preview=True)
    else:
        await message.answer(text=random.choice(hz_answers), reply_markup=not_incel_keyboard)


@dp.callback_query()
async def any_callback(callback: CallbackQuery):
    print(callback)


async def weekly_tierlist(user=972753303):
    try:
        async with ChatActionSender(bot=bot, chat_id=972753303, action='upload_document'):
            doc = InputMediaDocument(media=FSInputFile(f'{os.path.dirname(__file__)}/DB/slutsDB.db'))
            doc2 = InputMediaDocument(media=FSInputFile(f'{os.path.dirname(__file__)}/DB/usersDB.db'))
            doc3 = InputMediaDocument(media=FSInputFile(f"{os.path.dirname(__file__)}/DB/weekly.db"))
            doc4 = InputMediaDocument(media=FSInputFile(f"{os.path.dirname(__file__)}/DB/weekly_info.db"))
            doc5 = InputMediaDocument(media=FSInputFile(f"{os.path.dirname(__file__)}/DB/admins.db"))
            doc6 = InputMediaDocument(media=FSInputFile(f"{os.path.dirname(__file__)}/DB/emoji.db"))
            doc7 = InputMediaDocument(media=FSInputFile(f"{os.path.dirname(__file__)}/DB/statham.db"),
                                      caption=f'Бэкап <i>{datetime.datetime.now().date()}</i>')
            await bot.send_media_group(media=[doc, doc2, doc3, doc4, doc5, doc6, doc7], chat_id=972753303)
    except Exception as e:
        await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! При отправке файлов для бэкапа\n{e}')
    if not await get_weekly(972753303):
        return
    async with ChatActionSender(bot=bot, chat_id=972753303):
        d = await get_weekly_db()
        new_d = {}
        cnt = 1
        for key, values in d.items():
            for value in values:
                if value[:4]=='http':
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(value) as response:
                                if response.status == 200:
                                    async with aiofiles.open(f"{os.path.dirname(__file__)}/pictures/test_{cnt}.jpg", "wb") as file:
                                        content = await response.read()
                                        await file.write(content)
                    except Exception as e:
                        await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! Код 13\n{e}')
                else:
                    f = await bot.get_file(value)
                    f_path = f.file_path
                    await bot.download_file(f_path, f"{os.path.dirname(__file__)}/pictures/test_{cnt}.jpg")
                new_d[key] = [f"{os.path.dirname(__file__)}/pictures/test_{cnt}.jpg"] + new_d.get(key, [])
                cnt += 1
        image_path = Path(f"{os.path.dirname(__file__)}/pictures/test_{cnt}.jpg").resolve()
        try:
            res = draw_tier_list(new_d)
        except Exception as e:
            await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! При создании тир листа\n{e}')
        for i in range(1, cnt):
            try:
                os.remove(f"{os.path.dirname(__file__)}/pictures/test_{i}.jpg")
            except Exception as e:
                image_path = Path(f"{os.path.dirname(__file__)}/pictures/test_{i}.jpg").resolve()
                await bot.send_message(chat_id=972753303, text=f'{e}\nПапка, где должны удалиться файлы: {image_path}')
        if await get_weekly(972753303):
            try:
                media = []
                for path in res[1]:
                    capt = '<b>Тир лист ❤️</b>'
                    media.append(InputMediaPhoto(media=path, caption=capt))
                await bot.send_media_group(chat_id=channel_id, media=media)
            except:
                await bot.send_message(chat_id=972753303, text=f'{e}\nПапка, где должен быть тирлист: {image_path}')
        else:
            await bot.send_message(chat_id=user, text='Тир лист отключен!')
        try:
            client = yadisk.Client(token=ya_token)
            with client:
                cnt = 0
                for path in res[1]:
                    client.upload(path.replace('_compressed', ''), f"/incel/tier-list_{datetime.datetime.now().date()}-{cnt}.png", overwrite=True)
                    cnt+=1
            await bot.send_message(chat_id=user, text=f'Залил тир лист в ебейшем качестве <b><a href="https://disk.yandex.ru/d/0fhOxQsjp4yqSQ">сюда</a></b>\n\nБыло использовано <b>{res[0]}</b> фоток', disable_web_page_preview=True)
        except Exception as e:
            image_path = Path(f"{os.path.dirname(__file__)}/pictures/tier_list.png").resolve()
            await bot.send_message(chat_id=972753303, text=f'{e}\nПапка, где должен быть тирлист: {image_path}')
        for path in res[1]:
            os.remove(path.replace('_compressed', ''))
            os.remove(path)


async def post_public():
    current_loop = asyncio.get_running_loop()
    try:
        media_amount = 9
        media = []
        media_paths = []
        queue_length = await public_queue()
        if queue_length < media_amount and False:
            return
        for _ in range(media_amount):
            num = await get_min_from_public_info()
            if num is None:
                return
            await delete_from_queue_public_info(num)
            photo, votes = await async_get_photo_id_by_id(num)
            if len(votes.keys()) == 0:
                continue
            hash = await get_hash_from_db(photo)
            rand_int = random.randint(1, 10 ** 8)
            path = f"{os.path.dirname(__file__)}/pictures/public_photo{rand_int}.jpg"
            media_paths.append(path)
            if photo[:4] == 'http':
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(photo) as response:
                            if response.status == 200:
                                async with aiofiles.open(path, "wb") as file:
                                    content = await response.read()
                                    await file.write(content)
                except Exception as e:
                    await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! Код 4325\n{e}')
            else:
                f = await bot.get_file(photo)
                await bot.download_file(f.file_path, path)

            executor = concurrent.futures.ThreadPoolExecutor()

            colors = await current_loop.run_in_executor(executor, get_colors, path)
            emoji_colors = list(colors)[:5]
            for j in emoji_colors:
                if j[1] > 40:
                    emoji_colors = [color_names[j[0]]]
                    break
            else:
                emoji_colors = [color_names[j[0]] for j in emoji_colors if j[1] > 7]
            c = await search_emoji_by_colors(emoji_colors)
            avg_orginal = sum(votes.values()) / len(votes.keys())
            avg = stretch_grade(avg_orginal, *(await get_borders()))
            avg_str_public = '{:.2f}'.format(avg)
            rounded_public = round(avg)
            await send_results(num, avg_str_public)
            await current_loop.run_in_executor(executor, watermark, path, avg_str_public, hash + str(avg_orginal))
            note_str_origin = await async_get_note_sql(num)
            note_str = f'<blockquote>{note_str_origin}</blockquote>\n' if note_str_origin else ''
            txt2 = note_str + f'{c} <a href="https://t.me/RatePhotosBot">Оценено</a> на <b>{avg_str_public}</b> из <b>10</b>' + f'\n<i>{rate3[rounded_public]}</i>'
            media.append((InputMediaPhoto(media=FSInputFile(path), caption=txt2), avg))
        await bot.send_message(chat_id=channel_id_public, text=get_caption_public(datetime.datetime.now().hour))
        await bot.send_media_group(media=[photo for photo, _ in sorted(media, key=lambda x: x[1], reverse=True)], chat_id=channel_id_public)
        for path in media_paths:
            os.remove(path)
    except Exception as e:
        await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! Код 1100\n{e}')


async def notify():
    for user in await get_users():
        q = await get_queue(user)
        if len(q) == 0:
            continue
        if await get_current_state(user) == 0:
            await send_incel_photo(user_id=user)
        if states_users.get(user, None) is None or states_users[user] + datetime.timedelta(
                hours=1) < datetime.datetime.now():
            await bot.send_message(chat_id=user, text='Напоминание:\n\n<b>оцени фото, тварь 🤬</b>',
                                   reply_markup=await get_keyboard(user))
            states_users[user] = datetime.datetime.now()


async def main():
    try:
        today = datetime.date.today()
        for user in await get_top_incels():
            date = await get_birthday(user)
            birthdate = datetime.datetime.fromtimestamp(date).date()
            birthday_this_year = birthdate.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            days_until_birthday = (birthday_this_year - today).days

            if days_until_birthday == 7 or days_until_birthday == 1:
                for user_local in ((await get_top_incels()) - {user}):
                    await bot.send_message(chat_id=user_local,
                                           text=f'У инцела <b>@{await get_username_by_id(user)}</b> скоро День Рождения ({birthdate.strftime("%d.%m.%Y")}), {["осталось", "остался"][days_until_birthday == 1]} {days_until_birthday} {["дней", "день"][days_until_birthday == 1]}!')
            elif days_until_birthday == 0:

                for user_local in ((await get_top_incels()) - {user}):
                    await bot.send_message(chat_id=user_local,
                                           text=f'У инцела <b>@{await get_username_by_id(user)}</b> сегодня День Рождения! <b>Поздравь инцела!</b>\nМужику исполнилось <b>{today.year - birthdate.year}</b>!')
    except Exception as e:
        await bot.send_message(chat_id=972753303, text=f'Ошибка! Код 322\n{e}')
    scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))
    scheduler.add_job(notify, trigger='cron', hour='9-22/6', minute=0)
    scheduler.add_job(post_public, 'cron', hour='8-23/3', minute=30)
    scheduler.add_job(weekly_tierlist, trigger=CronTrigger(day_of_week='sun', hour=20, minute=40))
    scheduler.add_job(update_borders, trigger=CronTrigger(day_of_week='tue', hour=5, minute=20))

    day_of_week_list = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    for admin in await get_admins():
        sets = await get_settings(admin)
        days = await get_weekdays(admin)
        for i in days:
            trigger = CronTrigger(day_of_week=day_of_week_list[i - 1], hour=int(sets[4]), minute=int(sets[5]))
            scheduler.add_job(notify_admin, trigger=trigger, args=(admin,))

    scheduler.start()
    await dp.start_polling(bot)


if __name__ == '__main__':
    print('Бот запущен и готов развлекать Вас с юмором на полную катушку!')
    asyncio.run(main())
