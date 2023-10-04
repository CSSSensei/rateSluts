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
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv, find_dotenv
from aiogram.client.session.aiohttp import AiohttpSession
from sql_db import check_id, reduce_attempts, set_verified, add_girlphoto, get_users, get_last_commit, \
    add_current_state, get_current_state, add_to_queue, delete_from_queue, get_queue, get_usersinfo_db
from sql_photos import get_last, add_photo_id, add_rate, add_note, get_photo_id_by_id, get_note_sql, get_votes, \
    get_origin, max_photo_id_among_all, len_photos_by_username, max_photo_id_by_username, get_sluts_db
from graphics import get_statistics

load_dotenv(find_dotenv())

API_TOKEN: str = os.getenv('TOKEN')
channel_id = os.getenv('CHANNEL_ID')
storage: MemoryStorage = MemoryStorage()
# Создаем объекты бота и диспетчера
bot: Bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp: Dispatcher = Dispatcher(storage=storage)

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
    inserting_password = State()
    verified = State()
    banned = State()
    sending_photo = State()
    inserting_comment = State()
    rating = State()


class RateCallBack(CallbackData, prefix="rating"):
    r: int
    photo_id: int
    mailing: int


send_slut_button: KeyboardButton = KeyboardButton(
    text='Разослать фото')
statistics_button: KeyboardButton = KeyboardButton(
    text='Статистика по отправленным фото')
basic_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[statistics_button]], resize_keyboard=True,
    one_time_keyboard=True)
no_comments_button: KeyboardButton = KeyboardButton(
    text='Оставить без комментариев')
keyboard2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[no_comments_button]], resize_keyboard=True,
    one_time_keyboard=True)

cancel_photo: KeyboardButton = KeyboardButton(
    text='Не отправлять фото')
keyboard3: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[cancel_photo]], resize_keyboard=True,
    one_time_keyboard=True)


def get_rates_keyboard(num, mailing):
    array_buttons: list[list[InlineKeyboardButton]] = [[], []]
    for i in range(12):
        array_buttons[i // 6].append(InlineKeyboardButton(
            text=str(i) + f' {emoji[i]}',
            callback_data=RateCallBack(r=i, photo_id=num, mailing=mailing).pack()))
    markup = InlineKeyboardMarkup(
        inline_keyboard=array_buttons)
    return markup


@dp.callback_query(RateCallBack.filter())
async def filter_rates(callback: CallbackQuery,
                       callback_data: RateCallBack, state: FSMContext):
    num = callback_data.photo_id
    await callback.answer(text=rate[callback_data.r])
    mailing = callback_data.mailing
    votes = get_votes(num)
    flag = True
    if mailing and len(votes.keys()) == len(get_users()):
        flag = False  # FLag - индикатор, который отвечает за публикацию поста в канал
    add_rate(num, callback.from_user.username, callback_data.r)
    delete_from_queue(callback.from_user.id, num)

    if mailing:
        await callback.message.delete()
        add_current_state(callback.from_user.id, 0, callback.from_user.username)
        votes = get_votes(num)
        if len(votes.keys()) == len(get_users()) and flag:
            avg = sum(votes.values()) / len(votes.keys())
            avg_str = '{:.2f}'.format(avg)
            user_rates = ''
            for key, value in votes.items():
                user_rates += f'@{key}: <i>{value}</i>\n'
            rounded = round(avg)
            note_str = get_note_sql(num)
            note_str = f': <b><i>{get_note_sql(num)}</i></b>\n\n' if note_str is not None else '\n\n'
            txt = f'Автор пикчи <b>@{get_origin(num)}</b>' + note_str + "Оценки инцелов:\n" + user_rates + '\n' f'Общая оценка: <b>{avg_str}</b>' + f'\n<i>#{rate2[rounded].replace(" ", "_")}</i>'
            await bot.send_photo(chat_id=channel_id, photo=get_photo_id_by_id(num), caption=txt)
        q = get_queue(callback.from_user.id)
        if len(q) == 0:
            return
        i = next(iter(q))
        await bot.send_photo(callback.from_user.id, get_photo_id_by_id(i),
                             reply_markup=get_rates_keyboard(num=i, mailing=1))
        add_current_state(callback.from_user.id, i, callback.from_user.username)
        add_to_queue(callback.from_user.id, i)
        return

    await callback.message.edit_text(f'Ты поставил оценку {callback_data.r} {emoji[callback_data.r]}')
    await bot.send_message(chat_id=callback.from_user.id,
                           text='Введи заметку, которая будет видна по окончании голосования, либо нажми "Оставить без комментариев"',
                           reply_markup=keyboard2)
    await state.set_state(FSMFillForm.inserting_comment)


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
        await message.answer('Привет, лошара. Введи пароль, чтобы попасть в нашу тусовку')
        await state.set_state(FSMFillForm.inserting_password)


@dp.message(Command(commands='password_yaincel'))
async def settings(message: Message, state: FSMContext):
    set_verified(message.from_user.id)
    await message.answer(text='Поздравляю, ты теперь в нашей банде инцелов', reply_markup=basic_keyboard)
    await state.set_state(FSMFillForm.verified)


@dp.message(Command(commands='get_users_info_db'))
async def settings(message: Message, state: FSMContext):
    txt = map(str, get_usersinfo_db())
    txt = '\n'.join(txt)
    await message.answer(text=txt, reply_markup=basic_keyboard)


@dp.message(Command(commands='get_sluts_db'))
async def settings(message: Message, state: FSMContext):
    txt = map(str, get_sluts_db())
    txt = '\n'.join(txt)
    for i in range((len(txt) + 4096) // 4096):
        await message.answer(text=txt[i * 4096:(i + 1) * 4096], reply_markup=basic_keyboard)


@dp.message(F.text == 'яинцел', StateFilter(FSMFillForm.inserting_password))
async def get_password(message: Message, state: FSMContext):
    set_verified(id=message.from_user.id)
    await message.answer(
        text='Легенда! Теперь ты в нашей банде. Тебе доступны команды отправки фото. Также тебе будут присылаться фото от других пользователей для оценки',
        reply_markup=basic_keyboard)
    await state.set_state(FSMFillForm.verified)


@dp.message(F.text != 'яинцел', StateFilter(FSMFillForm.inserting_password))
async def wrong_password(message: Message, state: FSMContext):
    attempts = reduce_attempts(message.from_user.id)
    if attempts > 0:
        await message.answer(text=f'Неверный пароль. Осталось попыток: {attempts}')
    else:
        await message.answer(text='Ты ввел неверный пароль 5 раз. Иди на хуй, дружок')
        await state.set_state(FSMFillForm.banned)


@dp.message(F.photo, StateFilter(FSMFillForm.sending_photo))
async def get_photo(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    last_num = get_last()
    add_photo_id(last_num + 1, file_id, message.from_user.username)  # этот идентификатор нужно где-то сохранить
    add_girlphoto(message.from_user.id, last_num + 1)
    # await bot.send_photo(message.chat.id, file_id)
    await message.answer(text='Оцени фото, которое ты скинул',
                         reply_markup=get_rates_keyboard(last_num + 1, 0))
    await state.clear()


@dp.message(F.text == 'Не отправлять фото', StateFilter(FSMFillForm.sending_photo))
async def send_photo(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text='Ты вышел из меню отправки фото', reply_markup=basic_keyboard)
    add_current_state(message.from_user.id, 0, message.from_user.username)


@dp.message(~F.photo, StateFilter(FSMFillForm.sending_photo))
async def get_photo(message: Message, state: FSMContext):
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


@dp.message(F.text == 'Оставить без комментариев', StateFilter(FSMFillForm.inserting_comment))
async def get_no_notes(message: Message, state: FSMContext):
    await message.answer(text='Заебись',
                         reply_markup=basic_keyboard)
    await send_photo_to_users(message.from_user.id, get_last_commit(message.from_user.id))
    await state.clear()
    add_current_state(message.from_user.id, 0, message.from_user.username)


@dp.message(~F.text, StateFilter(FSMFillForm.inserting_comment))
async def get_no_notes(message: Message, state: FSMContext):
    await message.answer(text='Это похоже на текст для заметки, долбоёб?',
                         reply_markup=keyboard2)


@dp.message(F.text, StateFilter(FSMFillForm.inserting_comment))
async def get_note_main(message: Message, state: FSMContext):
    add_note(get_last_commit(message.from_user.id), message.text)
    await message.answer(
        text=f'Охуенная заметка: <b><i>{message.text}</i></b>. Сообщение отправлено всем участникам <a href="https://t.me/+D_c0v8cHybY2ODQy">банды инцелов</a>',
        disable_web_page_preview=True, reply_markup=basic_keyboard)
    await send_photo_to_users(message.from_user.id, get_last_commit(message.from_user.id))
    await state.clear()
    add_current_state(message.from_user.id, 0, message.from_user.username)


@dp.message(StateFilter(FSMFillForm.banned))
async def urbanned(message: Message, state: FSMContext):
    await message.answer(text='Ты заблокирован, долбоёб')


@dp.message(F.text == 'Разослать фото')
async def send_photo(message: Message, state: FSMContext):
    result = check_id(message.from_user.id, message.from_user.username)
    if not result[0]:
        await message.answer('Введи пароль', reply_markup=ReplyKeyboardRemove())
        await state.set_state(FSMFillForm.inserting_password)
        return
    await message.answer(text='Пришли фото', reply_markup=keyboard3)
    await state.set_state(FSMFillForm.sending_photo)
    add_current_state(message.from_user.id, -1, message.from_user.username)


@dp.message(StateFilter(FSMFillForm.rating))
async def default_photo(message: Message, state: FSMContext):
    await message.answer(text='Поставь оценку, сука!')


@dp.message(F.photo)
async def default_photo(message: Message, state: FSMContext):
    result = check_id(message.from_user.id, message.from_user.username)
    if not result[0]:
        await message.answer('Введи пароль', reply_markup=ReplyKeyboardRemove())
        await state.set_state(FSMFillForm.inserting_password)
        return
    file_id = message.photo[-1].file_id
    last_num = get_last()
    add_photo_id(last_num + 1, file_id, message.from_user.username)  # этот идентификатор нужно где-то сохранить
    add_girlphoto(message.from_user.id, last_num + 1)
    await message.answer(text='Оцени фото, которое ты скинул',
                         reply_markup=get_rates_keyboard(last_num + 1, 0))
    await state.set_state(FSMFillForm.rating)
    add_current_state(message.from_user.id, -1, message.from_user.username)


@dp.message(F.text == 'Статистика по отправленным фото', ~StateFilter(FSMFillForm.rating))
async def stat_photo(message: Message, state: FSMContext):
    result = check_id(message.from_user.id, message.from_user.username)
    if not result[0]:
        await message.answer('Введи пароль', reply_markup=ReplyKeyboardRemove())
        await state.set_state(FSMFillForm.inserting_password)
        return
    if len_photos_by_username(message.from_user.username) > 0:
        username = message.from_user.username
        get_statistics(username)
        photo = FSInputFile(f'myplot_{username}.jpg')
        await bot.send_photo(photo=photo, chat_id=message.from_user.id)
        os.remove(f'myplot_{username}.jpg')
        await message.answer(
            text=f'Ваше последнее фото оценили {len(get_votes(max_photo_id_by_username(username)).keys())}/{len(get_users())} человек')
    else:
        await message.answer(text='Ты еще не присылал никаких фото', reply_markup=basic_keyboard)


@dp.message(
    lambda message: message.text is not None and (
            message.text.lower() == 'спасибо' or message.text.lower() == 'от души' or message.text.lower() == 'благодарю'))
async def u_r_wellcome(message):
    await bot.send_sticker(chat_id=message.chat.id,
                           sticker='CAACAgEAAxkBAAEKShplAfTsN4pzL4pB_yuGKGksXz2oywACZQEAAnY3dj9hlcwZRAnaOjAE')


@dp.message(
    lambda message: message.text is not None and (
            message.text.lower() == 'иди нахуй' or message.text.lower() == 'пошел нахуй' or message.text.lower() == 'иди на хуй'))
async def u_r_wellcome(message):
    await bot.send_sticker(chat_id=message.chat.id,
                           sticker='CAACAgEAAxkBAAEKSrVlAiPwEKrocvOADTQWgKGACLGGlwAChAEAAnY3dj_hnFOGe-uonzAE')


@dp.message(lambda message: message.text is not None and message.text.lower() == 'я гей')
async def u_r_wellcome(message):
    await message.answer('я знаю')


@dp.message()
async def process_name_command(message: Message):
    result = check_id(message.from_user.id, message.from_user.username)
    if not result[0]:
        await message.answer('Введи пароль', reply_markup=ReplyKeyboardRemove())
        await state.set_state(FSMFillForm.inserting_password)
        return
    await message.answer(text='я не понимаю о чем ты', reply_markup=basic_keyboard)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    print('Бот запущен')
    asyncio.run(main())
