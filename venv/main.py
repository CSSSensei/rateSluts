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

import asyncio
import calendar
import datetime
import os
from typing import List, Dict

import tzlocal
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter, BaseFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv, find_dotenv
from aiogram.client.session.aiohttp import AiohttpSession
from sql_db import check_id, reduce_attempts, set_verified, add_girlphoto, get_users, get_last_commit, \
    add_current_state, get_current_state, add_to_queue, delete_from_queue, get_queue, get_usersinfo_db, \
    get_username_by_id, insert_last_rate, get_last_rate, get_ban, delete_row, get_id_by_username, check_user
from sql_photos import get_last, add_photo_id, add_rate, add_note, get_photo_id_by_id, get_note_sql, get_votes, \
    get_origin, max_photo_id_among_all, len_photos_by_username, max_photo_id_by_username, get_sluts_db
from graphics import get_statistics
from weekly_rates import add_to_weekly, clear_db, get_weekly_db, get_weekly, weekly_cancel, weekly_resume, \
    get_weekly_db_info
from tier_list import draw_tier_list

load_dotenv(find_dotenv())

API_TOKEN: str = os.getenv('TOKEN')
channel_id = os.getenv('CHANNEL_ID')
storage: MemoryStorage = MemoryStorage()
# Создаем объекты бота и диспетчера
bot: Bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp: Dispatcher = Dispatcher(storage=storage)
current_dm_id={}
states_users = {}

emoji = {
    0: '🤢',
    1: '🤮',
    2: '😒',
    3: '😕',
    4: '😔',
    5: '😐',
    6: '🙂',
    7: '😊',
    8: '🥰',
    9: '😘',
    10: '😍',
    11: '💦'
}
rate = {
    11: '2D',
    10: 'Жена (Mommy)',
    9: 'Я бы ей дал',
    8: 'Ахуенная',
    7: 'Хорошенькая',
    6: 'Ничего такая',
    5: 'Под пиво пойдет',
    4: 'Под водочку сойдёт',
    3: 'Хуйня (я бы ей не дал)',
    2: 'Полная хуйня',
    1: 'Что ты такое...?',
    0: 'Ребят... вырвите мне глаза'
}
rate2 = {
    11: '2D',
    10: 'mommy',
    9: 'Я бы ей дал',
    8: 'Ахуенная',
    7: 'Хорошенькая',
    6: 'Ничего такая',
    5: 'Под пиво пойдет',
    4: 'Под водочку сойдёт',
    3: 'Хуйня',
    2: 'Полная хуйня',
    1: 'хуже чем полная хуйня',
    0: 'вырвите мне глаза'
}


class FSMFillForm(StatesGroup):
    verified = State()
    banned = State()
    sending_photo = State()
    rating = State()
    sendDM = State()


class RateCallBack(CallbackData, prefix="rating"):
    r: int
    photo_id: int
    mailing: int

class ModerateCallBack(CallbackData, prefix="moderate"):
    action: int
    photo_id: int
    creator: str


send_slut_button: KeyboardButton = KeyboardButton(
    text='Разослать фото')
statistics_button: KeyboardButton = KeyboardButton(
    text='Статистика по отправленным фото')
edit_rate: KeyboardButton = KeyboardButton(
    text='Изменить последнюю оценку')
basic_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[statistics_button], [edit_rate]], resize_keyboard=True,
    one_time_keyboard=True)
not_incel_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[statistics_button]], resize_keyboard=True,
    one_time_keyboard=True)

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


class send_DM(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text[1:6] == 'send_'


@dp.message(F.text, ban_username())
async def ban_username(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй', reply_markup=basic_keyboard)
        return
    s = message.text[5:]
    result = get_ban(get_id_by_username(s))
    if result == 0:
        await message.answer(text=f'Строка с username=<i>"{s}"</i> не найдена в таблице')
    else:
        await message.answer(text=f'Пользователь <i>@{s}</i> был успешно забанен!')


@dp.message(F.text, send_DM())
async def send_dm(message: Message, state: FSMContext):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй', reply_markup=basic_keyboard)
        return
    s = message.text[6:]
    if len(s) <= 2:
        await message.answer(text=f'Пользователь с username=<i>"{s}"</i> не найден в таблице')
        return
    result = check_user(s)
    if result is None:
        await message.answer(text=f'Пользователь с username=<i>"{s}"</i> не найден в таблице')
    else:
        await message.answer(text=f'Введите сообщение для отправки <i>@{s}</i>')
        current_dm_id[message.from_user.id] = result
        await state.set_state(FSMFillForm.sendDM)

@dp.message(F.text, check_username())
async def del_username(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй', reply_markup=basic_keyboard)
        return
    s = message.text[5:]
    result = delete_row(s)
    if result == 0:
        await message.answer(text=f'Строка с username=<i>"{s}"</i> не найдена в таблице')
    else:
        await message.answer(text=f'Строка с username=<i>"{s}"</i> была успешно удалена')


def get_rates_keyboard(num: int, mailing: int):
    array_buttons: list[list[InlineKeyboardButton]] = [[], []]
    for i in range(12):
        array_buttons[i // 6].append(InlineKeyboardButton(
            text=str(i) + f' {emoji[i]}',
            callback_data=RateCallBack(r=i, photo_id=num, mailing=mailing).pack()))
    markup = InlineKeyboardMarkup(
        inline_keyboard=array_buttons)
    return markup


async def send_results(num: int, rate: str):
    origin = get_origin(num)
    origin_id = check_user(origin)
    if origin_id is not None:
        caption = f'Привет, {origin}.\n Ваше фото оценено на <b>{rate}</b>'
        await bot.send_photo(chat_id=origin_id, photo=get_photo_id_by_id(num), caption=caption)


def moderate_keyboard(file_id: int, creator: str):
    if file_id == -1:
        array = [[InlineKeyboardButton(
            text='✅',
            callback_data=ModerateCallBack(action=3, photo_id=file_id, creator=creator).pack()),
            InlineKeyboardButton(
                text='❌',
                callback_data=ModerateCallBack(action=2, photo_id=file_id, creator=creator).pack())]]
        return InlineKeyboardMarkup(
            inline_keyboard=array)
    array = [[InlineKeyboardButton(
        text='✅',
        callback_data=ModerateCallBack(action=1, photo_id=file_id, creator=creator).pack()),
        InlineKeyboardButton(
            text='❌',
            callback_data=ModerateCallBack(action=0, photo_id=file_id, creator=creator).pack())]]
    return InlineKeyboardMarkup(
        inline_keyboard=array)

@dp.callback_query(RateCallBack.filter())
async def filter_rates(callback: CallbackQuery,
                       callback_data: RateCallBack, state: FSMContext):
    num = callback_data.photo_id
    await callback.answer(text=rate[callback_data.r])
    mailing = callback_data.mailing
    votes = get_votes(num)
    flag = True
    insert_last_rate(callback.from_user.id, num)
    if mailing and len(votes.keys()) >= len(get_users()):
        flag = False  # FLag - индикатор, который отвечает за публикацию поста в канал (для того чтобы после изменения оценки пост не выложился еще раз)
    add_rate(num, callback.from_user.username, callback_data.r)
    delete_from_queue(callback.from_user.id, num)

    if mailing:
        await callback.message.delete()
        add_current_state(callback.from_user.id, 0, callback.from_user.username)
        votes = get_votes(num)
        if len(votes.keys()) + 1 == len(get_users()):
            voted = set(votes.keys())
            users = set()
            for i in get_users():
                users.add(get_username_by_id(i))
            last_username = next(iter((users - voted)))
            if last_username is not None and type(last_username) == str and len(last_username) > 0:
                if get_id_by_username(last_username) is not None:
                    if states_users.get(last_username, None) is None or states_users[last_username] + datetime.timedelta(hours=1) < datetime.datetime.now():
                        await bot.send_message(
                            text=f'<b>{last_username}</b>, ебать твой рот, нажми на кнопку, ты последний такой хуесос 😡',
                            chat_id=get_id_by_username(last_username), reply_markup=basic_keyboard)
                        states_users[last_username] = datetime.datetime.now()

        if len(votes.keys()) >= len(get_users()) and flag:


            avg = sum(votes.values()) / len(votes.keys())
            avg_str = '{:.2f}'.format(avg)
            await send_results(num, avg_str)
            extra = ''
            spoiler = False
            if avg == 0:
                spoiler = True
                extra = '<b>🚨Осторожно!🚨\nУберите от экранов детей и людей с тонкой душевной организацией. Данное фото может вас шокировать\n\n</b>'
            if avg == 11:
                spoiler = True
                extra = '<b>😍 Все участники банды инцелов оценили фото на 11 😍</b>\n\n'

            user_rates = ''
            for key, value in votes.items():
                user_rates += f'@{key}: <i>{value}</i>\n'
            rounded = round(avg)
            note_str = get_note_sql(num)
            note_str = f': <b><i>{get_note_sql(num)}</i></b>\n\n' if note_str is not None else '\n\n'
            txt = extra + f'Автор пикчи <b>@{get_origin(num)}</b>' + note_str + "Оценки инцелов:\n" + user_rates + '\n' f'Общая оценка: <b>{avg_str}</b>' + f'\n<i>#{rate2[rounded].replace(" ", "_")}</i>'
            await bot.send_photo(chat_id=channel_id, photo=get_photo_id_by_id(num), caption=txt,
                                 has_spoiler=spoiler)
            add_to_weekly(get_photo_id_by_id(num), avg)
        q = get_queue(callback.from_user.id)
        if len(q) == 0:
            return
        i = next(iter(q))
        await bot.send_photo(callback.from_user.id, get_photo_id_by_id(i),
                             reply_markup=get_rates_keyboard(num=i, mailing=1))
        add_current_state(callback.from_user.id, i, callback.from_user.username)
        return

    await callback.message.edit_text(f'Ты поставил оценку {callback_data.r} {emoji[callback_data.r]}')
    add_current_state(callback.from_user.id, 0, callback.from_user.username)
    await state.clear()
    await send_photo_to_users(callback.from_user.id, num)


@dp.callback_query(ModerateCallBack.filter())
async def moderate_photo(callback: CallbackQuery,
                         callback_data: ModerateCallBack, state: FSMContext):
    action = callback_data.action
    photo_id = callback_data.photo_id
    creator = callback_data.creator
    await callback.answer(text=['❌', '✅'][action % 2])
    await callback.message.edit_reply_markup(reply_markup=None)
    if action == 0:
        await callback.message.answer(text=f'<b>Забанить долбоеба?</b>\n<i>@{creator}</i>',
                                      reply_markup=moderate_keyboard(-1, creator))
    elif action == 1:
        await callback.message.answer(text='Оцени это фото',
                                      reply_markup=get_rates_keyboard(photo_id, 0))
    elif action == 3:
        creator_id = get_id_by_username(creator)
        if creator_id is None:
            await callback.message.edit_text(text=f'Строка с username=<i>"{creator}"</i> не найдена в таблице')
            return
        result = get_ban(creator_id)
        if result == 0:
            await callback.message.edit_text(text=f'Строка с username=<i>"{creator}"</i> не найдена в таблице')
        else:
            await callback.message.edit_text(text=f'Пользователь <i>@{creator}</i> был успешно забанен!',
                                             reply_markup=None)
    else:
        await callback.message.edit_text(text=f'Пощадим его', reply_markup=None)


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    result = check_id(user_id, username)
    if result[0]:
        await message.answer('Нахуя ты старт нажал', reply_markup=basic_keyboard)
        await state.set_state(FSMFillForm.verified)
    else:
        if result[1] <= 0:
            await message.answer('Ты заблокирован', reply_markup=ReplyKeyboardRemove())
            await state.set_state(FSMFillForm.banned)
            return
        await message.answer('Просто пришли свое фото, и нейросеть оценит твою внешность\n/help', reply_markup=not_incel_keyboard)


@dp.message(Command(commands='password_yaincel'))
async def settings(message: Message, state: FSMContext):
    set_verified(message.from_user.id)
    await message.answer(text='Поздравляю, ты теперь в нашей банде инцелов', reply_markup=basic_keyboard)
    await state.set_state(FSMFillForm.verified)


@dp.message(Command(commands='help'))
async def help(message: Message, state: FSMContext):
    result = check_id(message.from_user.id, message.from_user.username)
    if not result[0]:
        await message.answer('Скинь мне любое фото, и нейросеть оценит его по всей своей ебанутой строгости. На это может понадобиться время. Если Вы добавите подпись к картинке, оценка будет точнее', reply_markup=not_incel_keyboard)
        return
    await message.answer(
        text='Просто скинь мне любое фото, и оно будет отправлено всем участникам <a href="https://t.me/+D_c0v8cHybY2ODQy">банды инцелов</a>. Либо просто напиши "Разослать фото".\nКнопка "Статистика по отправленным фото" покажет тебе график всех средних значений оценок твоих фото.\n' + \
             'Отправил оценку ошибочно? Тогда нажми кнопку "Изменить последнюю оценку".\nЕсли ты хочешь добавить заметку к фото, сделай подпись к ней и отправь мне, она будет показана в канале по окончании голосования',
        disable_web_page_preview=True, reply_markup=basic_keyboard)


@dp.message(Command(commands='get_users_info_db'))
async def send_users_db(message: Message, state: FSMContext):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй', reply_markup=basic_keyboard)
    else:
        db = get_usersinfo_db()
        if db is None:
            await message.answer(text='БД пустая', reply_markup=basic_keyboard)
            return
        txt = map(str, db)
        txt = '\n'.join(txt)
        for i in range((len(txt) + 4096) // 4096):
            await message.answer(text=txt[i * 4096:(i + 1) * 4096], reply_markup=basic_keyboard)


@dp.message(Command(commands='get_weekly_db'))
async def send_weekly_db(message: Message, state: FSMContext):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй', reply_markup=basic_keyboard)
    else:
        db = get_weekly_db_info()
        if db is None:
            await message.answer(text='БД пустая', reply_markup=basic_keyboard)
            return
        txt = map(str, db)
        txt = '\n'.join(txt)
        for i in range((len(txt) + 4096) // 4096):
            await message.answer(text=txt[i * 4096:(i + 1) * 4096], reply_markup=basic_keyboard)


@dp.message(Command(commands='weekly_off'))
async def weekly_cancel_func(message: Message, state: FSMContext):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй', reply_markup=basic_keyboard)
    else:
        weekly_cancel(message.from_user.id)
        await message.answer(text='Еженедельная рассылка тир листа отключена', reply_markup=basic_keyboard)


@dp.message(Command(commands='weekly_on'))
async def send_users_db_func(message: Message, state: FSMContext):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй', reply_markup=basic_keyboard)
    else:
        weekly_resume(message.from_user.id)
        await message.answer(text='Еженедельная рассылка тир листа возобновлена', reply_markup=basic_keyboard)


@dp.message(Command(commands='send_tier_list'))
async def send_tier_and_delete(message: Message, state: FSMContext):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй', reply_markup=basic_keyboard)
    else:
        await message.answer(text='Тир лист был отправлен, БД очищена', reply_markup=basic_keyboard)
        await weekly_tierlist(automatic=0)


@dp.message(Command(commands='send_tier_list_notdel'))
async def send_tier_list(message: Message, state: FSMContext):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй', reply_markup=basic_keyboard)
    else:
        await message.answer(text='Тир лист был отправлен, БД сохранена', reply_markup=basic_keyboard)
        await weekly_tierlist(delete=0, automatic=0)


@dp.message(Command(commands='get_ban'))
async def ban_user(message: Message, state: FSMContext):
    get_ban(message.from_user.id)
    await message.answer(text='Вы исключены из банды инцелов', reply_markup=ReplyKeyboardRemove())
    await state.set_state(FSMFillForm.banned)


@dp.message(Command(commands='get_sluts_db'))
async def send_sluts_db(message: Message, state: FSMContext):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй', reply_markup=basic_keyboard)
    else:
        if get_sluts_db() is None:
            await message.answer(text='БД пустая', reply_markup=basic_keyboard)
            return
        txt = map(str, get_sluts_db())
        txt = '\n'.join(txt)
        for i in range((len(txt) + 4096) // 4096):
            await message.answer(text=txt[i * 4096:(i + 1) * 4096], reply_markup=basic_keyboard)


@dp.message(F.text == 'яинцел')
async def get_verified(message: Message, state: FSMContext):
    set_verified(id=message.from_user.id)
    await message.answer(
        text='Легенда! Теперь ты в нашей банде. Просто пришли мне фото, и его смогут оценить все участники. Если ты хочешь добавить заметку, сделай подпись к ней и отправь мне, она будет показана в канале по окончании голосования. Также тебе будут присылаться фото от других пользователей для оценки',
        reply_markup=basic_keyboard)
    await state.set_state(FSMFillForm.verified)




@dp.message(F.photo, StateFilter(FSMFillForm.sending_photo))
async def get_photo_by_button(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    last_num = get_last()
    add_photo_id(last_num + 1, file_id, message.from_user.username)  # этот идентификатор нужно где-то сохранить
    add_girlphoto(message.from_user.id, last_num + 1)
    # await bot.send_photo(message.chat.id, file_id)
    await message.answer(text='Оцени фото, которое ты скинул',
                         reply_markup=get_rates_keyboard(last_num + 1, 0))
    add_current_state(message.from_user.id, -1, message.from_user.username)
    await state.clear()


@dp.message(F.text == 'Не отправлять фото', StateFilter(FSMFillForm.sending_photo))
async def cancel_sending(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text='Ты вышел из меню отправки фото', reply_markup=basic_keyboard)
    add_current_state(message.from_user.id, 0, message.from_user.username)


@dp.message(~F.photo, StateFilter(FSMFillForm.sending_photo))
async def invalid_type_photo(message: Message, state: FSMContext):
    await message.answer(text='Это похоже на фото, долбоёб?', reply_markup=keyboard3)


async def send_photo_to_users(origin_user, num: int):
    for user in get_users():
        if user == origin_user:
            continue
        add_to_queue(user, num)
        if get_current_state(user) != 0:
            continue
        add_current_state(user, num)
        await bot.send_photo(user, get_photo_id_by_id(num), reply_markup=get_rates_keyboard(num=num, mailing=1))


# @dp.message(F.text, StateFilter(FSMFillForm.inserting_comment))
# async def get_note_main(message: Message, state: FSMContext):
#     add_note(get_last_commit(message.from_user.id), message.text)
#     await message.answer(
#         text=f'Охуенная заметка: <b><i>{message.text}</i></b>. Сообщение отправлено всем участникам <a href="https://t.me/+D_c0v8cHybY2ODQy">банды инцелов</a>',
#         disable_web_page_preview=True, reply_markup=basic_keyboard)
#     await send_photo_to_users(message.from_user.id, get_last_commit(message.from_user.id))
#     await state.clear()
#     add_current_state(message.from_user.id, 0, message.from_user.username)


@dp.message(StateFilter(FSMFillForm.banned))
async def urbanned(message: Message, state: FSMContext):
    await message.answer(text='Ты заблокирован, долбоёб')


@dp.message(F.text == 'Разослать фото')
async def send_photo(message: Message, state: FSMContext):
    result = check_id(message.from_user.id, message.from_user.username)
    if not result[0]:
        if result[1] == -1:
            await message.answer('Ты заблокирован!', reply_markup=ReplyKeyboardRemove())
            await state.set_state(FSMFillForm.banned)
            return
        await message.answer('Ну так пришли его', reply_markup=ReplyKeyboardRemove())
        return
    await message.answer(text='Пришли фото', reply_markup=keyboard3)
    await state.set_state(FSMFillForm.sending_photo)
    add_current_state(message.from_user.id, -1, message.from_user.username)


@dp.message(StateFilter(FSMFillForm.rating))
async def remember_to_rate(message: Message, state: FSMContext):
    await message.answer(text='Поставь оценку, сука!')


@dp.message(F.photo)
async def default_photo(message: Message, state: FSMContext):
    result = check_id(message.from_user.id, message.from_user.username)
    file_id = message.photo[-1].file_id
    last_num = get_last()
    add_photo_id(last_num + 1, file_id, message.from_user.username)  # этот идентификатор нужно где-то сохранить
    add_girlphoto(message.from_user.id, last_num + 1)
    if not result[0]:
        if result[1] == -1:
            await message.answer('Ты заблокирован!', reply_markup=ReplyKeyboardRemove())
            await state.set_state(FSMFillForm.banned)
            return
        await message.answer('Фото пройдет модерацию и будет оценено нейросетью, ожидайте',
                             reply_markup=ReplyKeyboardRemove())
        caption = '' if message.caption is None else message.caption
        if caption != '':
            add_note(last_num + 1, message.caption)
            caption = f'\n"{caption}"'
        await bot.send_photo(972753303, photo=message.photo[-1].file_id,
                             caption=f'Фото от пользователя <i>@{message.from_user.username}</i><i>{caption}</i>',
                             reply_markup=moderate_keyboard(last_num + 1, message.from_user.username))
        return


    if message.caption is not None:
        await message.answer(
            text=f'Ты прислал фото с заметкой: <i>{message.caption}</i>. Оцени фото, которое ты скинул',
            reply_markup=get_rates_keyboard(last_num + 1, 0))
        add_note(last_num + 1, message.caption)
    else:
        await message.answer(
            text='Оцени фото, которое ты скинул',
            reply_markup=get_rates_keyboard(last_num + 1, 0))
    await state.set_state(FSMFillForm.rating)
    add_current_state(message.from_user.id, -1, message.from_user.username)


@dp.message(F.text == 'Статистика по отправленным фото', ~StateFilter(FSMFillForm.rating))
async def stat_photo(message: Message, state: FSMContext):
    result = check_id(message.from_user.id, message.from_user.username)
    if not result[0]:
        if result[1] == -1:
            await message.answer('Ты заблокирован!', reply_markup=ReplyKeyboardRemove())
            await state.set_state(FSMFillForm.banned)
            return
        if len_photos_by_username(message.from_user.username) > 0:
            username = message.from_user.username
            get_statistics(username)
            photo = InputMediaPhoto(media=FSInputFile(f'myplot_{username}2.png'), caption='График')
            photo2 = InputMediaPhoto(media=FSInputFile(f'myplot_{username}.png'), caption='Гистограмма')
            media = [photo, photo2]
            await bot.send_media_group(media=media, chat_id=message.from_user.id)
            os.remove(f'myplot_{username}.png')
            os.remove(f'myplot_{username}2.png')
            await message.answer(
                text=f'Ваше последнее фото на стадции оценки {len(get_votes(max_photo_id_by_username(username)).keys())/len(get_users())*100}%', reply_markup=not_incel_keyboard)
        else:
            await message.answer(text='Ты еще не присылал никаких фото', reply_markup=not_incel_keyboard)
        return
    if len_photos_by_username(message.from_user.username) > 0:
        username = message.from_user.username
        get_statistics(username)
        photo = InputMediaPhoto(media=FSInputFile(f'myplot_{username}2.png'), caption='График')
        photo2 = InputMediaPhoto(media=FSInputFile(f'myplot_{username}.png'), caption='Гистограмма')
        media = [photo, photo2]
        await bot.send_media_group(media=media, chat_id=message.from_user.id)
        os.remove(f'myplot_{username}.png')
        os.remove(f'myplot_{username}2.png')
        votes = len(get_votes(max_photo_id_by_username(username)).keys())
        users = len(get_users())
        if votes > users:
            users = votes
        await message.answer(
            text=f'Ваше последнее фото оценили {votes}/{users} человек')
    else:
        await message.answer(text='Ты еще не присылал никаких фото', reply_markup=basic_keyboard)


@dp.message(F.text == 'Изменить последнюю оценку', ~StateFilter(FSMFillForm.rating))
async def stat_photo(message: Message, state: FSMContext):
    result = check_id(message.from_user.id, message.from_user.username)
    if not result[0]:
        if result[1] == -1:
            await message.answer('Ты заблокирован!', reply_markup=ReplyKeyboardRemove())
            await state.set_state(FSMFillForm.banned)
        return
    last_rate = get_last_rate(message.from_user.id)
    if last_rate == 0 or last_rate == 5:
        await message.answer(text='Ты не оценивал чужих фото', reply_markup=basic_keyboard)
        return
    await bot.send_photo(chat_id=message.from_user.id, photo=get_photo_id_by_id(last_rate),
                         reply_markup=get_rates_keyboard(last_rate, 1), caption='Ну давай, переобуйся, тварь')


@dp.message(StateFilter(FSMFillForm.sendDM))
async def stat_photo(message: Message, state: FSMContext):
    result = check_id(message.from_user.id, message.from_user.username)
    if not result[0]:
        if result[1] == -1:
            await message.answer('Ты заблокирован!', reply_markup=ReplyKeyboardRemove())
            await state.set_state(FSMFillForm.banned)
        return
    if current_dm_id[message.from_user.id] == 0:
        await message.answer(text='Произошла ошибка', reply_markup=basic_keyboard)
        return
    await message.answer(text='Сообщение отправлено!', reply_markup=basic_keyboard)
    await bot.copy_message(chat_id=current_dm_id[message.from_user.id], message_id=message.message_id,
                           from_chat_id=message.chat.id)
    current_dm_id[message.from_user.id] = 0
    await state.clear()



@dp.message(
    lambda message: message.text is not None and (
            message.text.lower() == 'спасибо' or message.text.lower() == 'от души' or message.text.lower() == 'благодарю'))
async def u_r_wellcome(message):
    await bot.send_sticker(chat_id=message.chat.id,
                           sticker='CAACAgEAAxkBAAEKShplAfTsN4pzL4pB_yuGKGksXz2oywACZQEAAnY3dj9hlcwZRAnaOjAE')


@dp.message(
    lambda message: message.text is not None and (
            message.text.lower() == 'иди нахуй' or message.text.lower() == 'пошел нахуй' or message.text.lower() == 'иди на хуй'))
async def fuckoff(message):
    await bot.send_sticker(chat_id=message.chat.id,
                           sticker='CAACAgEAAxkBAAEKSrVlAiPwEKrocvOADTQWgKGACLGGlwAChAEAAnY3dj_hnFOGe-uonzAE')


@dp.message(lambda message: message.text is not None and message.text.lower() == 'я гей')
async def ik(message):
    await message.answer('я знаю')


@dp.message()
async def any_message(message: Message, state: FSMContext):
    result = check_id(message.from_user.id, message.from_user.username)
    if not result[0] and result[1] != -1:
        if message.text:
            await bot.send_message(chat_id=972753303, text=f'<i>@{message.from_user.username}:</i>\n"{message.text}"', disable_notification=True)
        else:
            caption = '' if message.caption is None else f':\n"{message.caption}"'
            await bot.copy_message(from_chat_id=message.chat.id,chat_id=972753303, message_id=message.message_id, disable_notification=True, caption=f'<i>@{message.from_user.username}</i>{caption}')
    if not result[0] and result[1] == -1:
        await message.answer('Ты заблокирован!', reply_markup=ReplyKeyboardRemove())
        await state.set_state(FSMFillForm.banned)
        return
    await message.answer(text='я не понимаю, о чем ты', reply_markup=basic_keyboard)


async def weekly_tierlist(delete=1, automatic=1):
    if get_weekly(972753303):
        d = get_weekly_db()
        new_d = {}
        cnt = 1
        for key, values in d.items():
            for value in values:
                f = await bot.get_file(value)
                f_path = f.file_path
                await bot.download_file(f_path, f"test_{cnt}.jpg")
                new_d[key] = [f"test_{cnt}.jpg"] + new_d.get(key, [])
                cnt += 1
        draw_tier_list(new_d)
        for i in range(1, cnt):
            os.remove(f"test_{i}.jpg")
        photo = FSInputFile("tier_list.png")
        if automatic:
            await bot.send_document(document=photo, chat_id=channel_id, caption='<b>Еженедельный тир лист ❤️</b>')
        else:
            await bot.send_document(document=photo, chat_id=channel_id, caption='<b>Текущий тир лист ❤️</b>')
        os.remove("tier_list.png")
        if delete:
            clear_db()
    else:
        await bot.send_message(chat_id=972753303, text='Тир лист отключен',reply_markup=basic_keyboard)

async def notify():
    for user in get_users():
        q = get_queue(user)
        if get_current_state(user) == -1:
            await bot.send_message(text='Заверши отправку фото, сука 🤬. Ты можешь оценить своё же фото, долбоеб?')
            continue
        if len(q) == 0:
            continue
        await bot.send_message(chat_id=user, text='Напоминание:\n\n<b>оцени фото, тварь 🤬</b>',
                               reply_markup=basic_keyboard)


async def main():
    scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))
    scheduler.add_job(notify, trigger='cron', hour='9-22/3', minute=0)
    scheduler.start()

    scheduler2: AsyncIOScheduler = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))
    trigger = CronTrigger(day_of_week='sun', hour=20, minute=0)
    scheduler2.add_job(weekly_tierlist, trigger=trigger)
    scheduler2.start()

    await dp.start_polling(bot)


if __name__ == '__main__':
    print('Бот запущен')
    asyncio.run(main())
