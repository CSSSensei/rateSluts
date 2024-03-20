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
import io
import json
import os
import time
import shutil

import aiogram.utils.chat_action
import yadisk

import requests
import random
from typing import List, Dict, Union
from pathlib import Path

import tzlocal
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter, BaseFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile, InputMediaPhoto, InputMediaDocument, InputMediaVideo
from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ContentType,
                           MessageReactionUpdated)
from aiogram.utils.chat_action import ChatActionSender
from aiogram.types.reaction_type_emoji import ReactionTypeEmoji
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv, find_dotenv
from aiogram.client.session.aiohttp import AiohttpSession
from sql_db import check_id, reduce_attempts, set_verified, add_girlphoto, get_users, get_last_commit, \
    add_current_state, get_current_state, add_to_queue, delete_from_queue, get_queue, get_usersinfo_db, \
    get_username_by_id, insert_last_rate, get_last_rate, get_ban, delete_row, get_id_by_username, check_user, \
    get_not_incel, check_new_user
from sql_photos import *
from graphics import *
from weekly_rates import add_to_weekly, clear_db, get_weekly_db, get_weekly, weekly_cancel, weekly_resume, \
    get_weekly_db_info
from tier_list import draw_tier_list
from statham import get_randQuote, insert_quote, get_statham_db, del_quote
from administrators import *
from parser import *

load_dotenv(find_dotenv())

API_TOKEN: str = os.getenv('TOKEN')
channel_id = os.getenv('CHANNEL_ID')
channel_id_public = os.getenv('CHANNEL_ID_public')
ya_token = os.getenv('YAtoken')
storage: MemoryStorage = MemoryStorage()

bot: Bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp: Dispatcher = Dispatcher(storage=storage)
current_dm_id = {}
states_users = {}
caption_global = {}
legendary_quote = 'Назвался груздем — пошёл на хуй\nНе сделал дело — пошёл на хуй\nИ баба с возу пошла на хуй\nИ волки на хуй, и овцы на хуй\n\nХотел как лучше, а пошёл на хуй\nДают — бери, а бьют — иди на хуй\nДружба дружбой, а на хуй иди\nЧья бы корова мычала, а твоя пошла на хуй\n\nУченье свет, а ты пошёл на хуй\nСемь раз отмерь и иди на хуй\nСкажи мне кто твой друг, и оба на хуй\nЧем бы дитя не тешилось, а шло бы на хуй\n\nПришла беда — пошла на хуй!\nГотовь сани летом, а зимой на хyй иди!\nСо своим уставом иди на хуй!\nИди на хуй не отходя от кассы!'
hz_answers = ['Я тебя не понимаю...', 'Я не понимаю, о чем ты', 'Что ты имеешь в виду? 🧐', 'Я в замешательстве 🤨',
              'Не улавливаю смысла 🙃', 'Что ты пытаешься сказать❓', 'Не понимаю твоего сообщения 😕',
              '🤷‍♂️ Не понимаю 🤷‍♀️']
emoji_lol = '🍏🍎🍐🍊🍋🍌🍉🍇🍓🫐🍈🍒🍑🥭🍍🥥🥝🍅🍆🥑🫛🥦🥬🥒🌶🫑🌽🥕🫒🧄🧅🥔🍠🫚🥐🥯🍞🥖🥨🧀🥚🍳🧈🥞🧇🌭🍔🍟🍕🥪🥙🧆🌮🌯🫔🥗🥘🫕🥫🍝🍜🍲🍛🍣🍱🥟🦪🍤🍙🍚🍘🍥🥠🥮🍡🍧🍨🍦🥧🧁🍰🎂🍮🍭🍬🍫🍿🍩🍪🌰🍯🥛🫗🍼🫖☕️🍵🧃🥤🧋🍶🍾🧊⚽️🏀🏈⚾️🥎🎾🏐🏉🥏🎱🪀🏓🏸🎧🎫🎟🎲♟🎯🎳🎮🎰🧩🗾🎑🏞🌅🌄🌠🎇🎆🌇🌆🏙🌃🌌🌉🌁💣🧨💊🎁🎈🛍🪩📖📚📙📘📗📕📒📔📓📰🗞🧵👚👕👖👔💼👜🎩🧢👒🎓🧳👓🕶🥽🌂💍🐶🐭🐹🐰🦊🐻🐼🐻‍❄️🐨🐯🦁🐸🐵🙈🙉🙊🐒🐱🐔🐧🐦🐤🐣🐥🪿🦆🐦‍⬛️🦅🦉🦇🐺🐴🦄🐝🦋🦖🦕🐙🦑🪼🦐🐬🐋🐳🦈🦭🪽🕊🪶🐉🐲🦔🐁🌵🎄🌲🌳🌴🪵🌱🌿☘️🍀🎍🪴🎋🍃🍂🍁🪺🐚🪸🪨🌾💐🌷🌹🥀🪻🪷🌺🌸🌼🌻🌎🌍🌏🪐💫⭐️✨💥🔥🌪🌈☀️🌤⛅️🌥☁️☃️⛄️💨☂️🌊🌫'
emoji_banned = '⛔❗🤯😳❌⭕🛑📛🚫💢🚷📵🔴🟥💣🗿🐓🙊🙉🙈🐷🫵🥲🙁😕😟😔😞😧😦😯🙄😵💀🚨😐'
dice_points = {'🎲': 6, '🎯': 6, '🎳': 6, '🏀': 4, '⚽': 3, '🎰': 64}
replicas = {}
with open('replicas.txt', 'r', encoding='utf-8') as file:
    replicas = json.load(file)
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
incels = get_users()

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
basic_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[statistics_button, quote_button], [edit_rate]], resize_keyboard=True)
admin_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[statistics_button, quote_button], [edit_rate, settings_button]], resize_keyboard=True)
not_incel_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[statistics_button]], resize_keyboard=True)

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


class clear_states_username(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text[1:4] == 'cs_'


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


def get_keyboard(user_id: int):
    if user_id in get_admins():
        return admin_keyboard
    elif user_id in get_users():
        return basic_keyboard
    if len(get_avgs_not_incel(user_id)) > 5:
        return not_incel_keyboard
    return None


@dp.message(F.text, ban_username())
async def ban_username(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй', reply_markup=get_keyboard(message.from_user.id))
        return
    s = message.text[5:]
    result = get_ban(get_id_by_username(s))
    if result == 0:
        await message.answer(text=f'Строка с username=<i>"{s}"</i> не найдена в таблице')
    else:
        await message.answer(text=f'Пользователь <i>@{s}</i> был успешно забанен!')


@dp.message(F.text, clear_states_username())
async def ban_username(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй', reply_markup=get_keyboard(message.from_user.id))
        return
    s = message.text[4:]
    try:
        add_current_state(id=get_id_by_username(s), num=0)
        await message.answer(text=f'Состояние {s} очищено 🫡')
    except Exception as e:
        await message.answer(text=f'Произошла ошибка! Код 11\n{e}')


@dp.message(F.text, change_average_filter())
async def ban_username(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй', reply_markup=get_keyboard(message.from_user.id))
        return
    pattern = r'/(\w+)_([\w\d]+)_([\d]+)_([\d]+)'
    match = re.match(pattern, message.text)

    if match:
        try:
            username = match.group(2)
            sum_value = int(match.group(3))
            amount = int(match.group(4))
            user_id = get_id_by_username(username)
            if user_id is None or sum_value <= 0 or amount <= 0:
                await message.answer(text=f'Произошла ошибка! Ты еблан')
                return
            change_avg_rate(user_id, sum_value, amount)
            await message.answer(f'Значения для {username} были изменены на {sum_value}, {amount}')
        except Exception as e:
            await message.answer(text=f'Произошла ошибка! Ты еблан\n{e}')
    else:
        await message.answer(text=f'Произошла ошибка! Неправильный паттерн')


@dp.message(Command(commands='new_quote'), F.from_user.id.in_(incels))
async def send_quote_dada(message: Message, state: FSMContext):
    incels = get_users()
    await message.answer(text='Пришли цитату в формате фото или текста')
    await state.set_state(FSMFillForm.sendQuote)


@dp.message(Command(commands='test'), F.from_user.id.in_(incels))
async def test_something(message: Message):
    await message.answer(text='Эта команда для тестирования новых функций')


@dp.message(Command(commands='send_tier_list'), F.from_user.id.in_(incels))
async def send_tier_and_delete(message: Message, state: FSMContext):
    incels = get_users()
    await message.answer(text='Тир лист начал генерироваться')
    await weekly_tierlist(message.from_user.id)


@dp.message(Command(commands='stat'))
async def send_tier_and_delete(message: Message, state: FSMContext):
    await stat_photo(message, state)


@dp.message(Command(commands='delete_tier_list'))
async def send_tier_and_delete(message: Message, state: FSMContext):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй')
    else:
        array = [[InlineKeyboardButton(text='Удалить! Я КОНЧ! 😈',callback_data='ya_gay_delete_tier_db'),
                  InlineKeyboardButton(text='Не удалять ❌',callback_data='not_delete')]]
        await message.answer(
            text='<b>ВСЯ БД БУДЕТ СТЕРТА! Ты уверен???</b>\n<span class="tg-spoiler">Админ может дать пизды</span>',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=array))


@dp.message(Command(commands='upd_file'))
async def send_tier_and_delete(message: Message, state: FSMContext):
    global replicas
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй')
    else:
        if message.document and message.document.mime_type == 'text/plain':
            f = await bot.get_file(message.document.file_id)
            f_path = f.file_path
            await bot.download_file(file_path=f_path, destination='replicas2.txt')
            try:
                with open('replicas2.txt', 'r', encoding='utf-8') as file:
                    replicas = json.load(file)
                shutil.copyfile('replicas2.txt', 'replicas.txt')
                os.remove('replicas2.txt')
                await message.answer('Новый файл сохранен')
            except Exception as e:
                await bot.send_message(chat_id=972753303,
                                       text=f'Произошла ошибка при открытии файла "replicas.txt"\n{e}')
        else:
            await message.answer('❗️Ты забыл прикрепить файл или прикрепил файл не того типа')


@dp.callback_query(F.data.in_(['ya_gay_delete_tier_db',
                               'not_delete']))
async def process_buttons_press(callback: CallbackQuery):
    if callback.data == 'ya_gay_delete_tier_db':
        await callback.message.answer(text='<b>База данных с фотками тир листа удалена!</b>\n\nАдмин даст тебе пизды 💀')
        clear_db()
    else:
        await callback.message.answer(text='Правильный выбор! База данных осталась невредима 👍')
    await callback.message.edit_reply_markup(reply_markup=None)


@dp.message(F.text, send_DM(), F.from_user.id.in_(incels))
async def send_dm(message: Message, state: FSMContext):
    s = message.text[6:]
    if s == "all":
        await message.answer(text=f'Введите сообщение для отправки всем бомжам')
        current_dm_id[message.from_user.id] = -1
        await state.set_state(FSMFillForm.sendDM)
        return
    if s == "incels":
        await message.answer(text=f'Введите сообщение для отправки всем инцелам')
        current_dm_id[message.from_user.id] = -2
        await state.set_state(FSMFillForm.sendDM)
        return
    if s == "topincels":
        await message.answer(text=f'Введите сообщение для отправки топ инцелам')
        current_dm_id[message.from_user.id] = -3
        await state.set_state(FSMFillForm.sendDM)
        return
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
        await message.answer(text='иди нахуй')
        return
    s = message.text[5:]
    result = delete_row(s)
    if result == 0:
        await message.answer(text=f'Строка с username=<i>"{s}"</i> не найдена в таблице')
    else:
        await message.answer(text=f'Строка с username=<i>"{s}"</i> была успешно удалена')


def get_rates_keyboard(num: int, mailing: int = 1, ids='0', back=False, message_to_delete=0, back_ids=0):
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
        add_note(num, '')
        array_buttons.append([
            InlineKeyboardButton(text='🔙', callback_data=ManageSettings(action=8, photo_id=ids, message_to_delete=message_to_delete,
                                                                        back_ids=back_ids).pack())])
    markup = InlineKeyboardMarkup(inline_keyboard=array_buttons)
    return markup


async def send_results(num: int, rate: str):
    origin = get_origin(num)
    origin_id = check_user(origin)
    if origin_id not in get_users():
        add_not_incel_photo(num, get_photo_id_by_id(num), origin_id, float(rate))
        if origin_id is not None:
            if float(rate) <= 5:
                emoji_loc = '📉'
            else:
                emoji_loc = '📈'
            caption = f'{emoji_loc} Твое фото оценено на <b>{rate}</b> из <b>10</b>\n\n❤️ <i>Это не моё мнение и не мнение команды RatePhotosBot. Не судите строго за ошибки — я только учусь.</i>'
            try:
                await bot.send_photo(chat_id=origin_id, photo=get_photo_id_by_id(num), caption=caption, reply_markup=get_keyboard(origin_id))
                if len(get_avgs_not_incel(origin_id)) == 6:
                    await bot.send_message('🙀 Теперь тебе доступна статистика!\nНажимай скорее <i>/stat</i>', reply_markup=not_incel_keyboard)
            except Exception as e:
                await bot.send_message(chat_id=972753303, text=f'Произошла ошибка!\n{str(e)}')


async def send_group_photo(user_id: int, num: str):
    if '-' not in num:
        async with ChatActionSender(bot=bot, chat_id=user_id, action='upload_photo'):
            photo = send_photos_by_id(int(num))
            caption = f'👥 <b><a href="vk.com/{photo[1]}">{get_group_name(photo[1][:photo[1].find("?")])}</a></b>'
            msg = await bot.send_photo(chat_id=user_id, photo=photo[3], caption=photo[2] + ("\n\n" if len(photo[2]) > 0 else "") + caption,
                                       reply_markup=get_manage_photo(ids=int(num)))
            set_message_to_delete(user_id, f'{msg.message_id}')

        return
    num = list(map(int, num.split('-')))
    nums = [i for i in range(num[0], num[1] + 1)]
    photo = send_photos_by_id(nums[0])
    caption = f'👥 <b><a href="vk.com/{photo[1]}">{get_group_name(photo[1][:photo[1].find("?")])}</a></b>'
    media = []
    for num in nums:
        loc_photo = send_photos_by_id(num)
        media.append(InputMediaPhoto(media=loc_photo[3]))
    try:
        async with ChatActionSender(bot=bot, chat_id=user_id, action='upload_photo'):
            msg: List[Message] = await bot.send_media_group(user_id, media=media)
            await bot.send_message(chat_id=user_id, text=photo[2] + ("\n\n" if len(photo[2]) > 0 else "") + caption,
                                   reply_markup=get_manage_photo(ids=nums, message_to_delete=f'{msg[0].message_id}, {msg[-1].message_id}'),
                                   disable_web_page_preview=True)
            set_message_to_delete(user_id, f'{msg[0].message_id}-{msg[-1].message_id}')
    except Exception as e:
        await bot.send_message(chat_id=user_id, text=f'Произошла ошибка! Код 1\n{e}')


async def notify_admin(user_id: int, message_id=0):
    sets = get_settings(user_id)
    if sets[6] is not None:
        groups_set = set(map(int, sets[6].split(',')))
        if message_id != 0:
            async with ChatActionSender(bot=bot, chat_id=user_id):
                await bot.edit_message_caption(chat_id=user_id, message_id=message_id,
                                               caption=f'Начал поиск фото по группам\n<code>{"0".rjust(len(str(len(groups_set))))} из {len(groups_set)}</code>  | <code>{("{:2.2f}".format(00.00) + "%").rjust(6)}</code>')
        cnt_group = 0
        cnt = 0
        for group in groups_set:
            group_sets = get_group_sets(group)
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
                result = get_posts(parameters)
            except Exception as e:
                await bot.send_message(chat_id=user_id, text=f'Произошла ошибка! Код 2\n{e}')
            for link, post in result.items():
                async with ChatActionSender(bot=bot, chat_id=user_id,
                                            action='upload_photo'):  # Установка action "Отправка фотографии...
                    cnt += 1
                    caption = f'👥 <b><a href="vk.com/{group_sets[1]}?w=wall{link}">{group_sets[7]}</a></b>, 👍 {post[2]}'
                    if len(post[0]) == 1:
                        num = last_group_photo_id() + 1
                        if sets[7] != 2:
                            add_group_photo(num, f"{group_sets[1]}?w=wall{link}",
                                            format_text(post[1], group_sets[1], link), post[0][0])
                            if cnt == 1:
                                await send_group_photo(user_id, str(num))
                            else:
                                add_to_queue_group_photo(user_id, str(num))
                        else:
                            await bot.send_photo(chat_id=user_id, photo=post[0][0],
                                                 caption=format_text(post[1], group_sets[1], link) + (
                                                     "\n\n" if len(post[1]) > 0 else "") + caption,
                                                 reply_markup=get_manage_photo(ids=num, mode=sets[7]))
                    else:
                        photo_ids = []
                        media = []
                        first = True
                        num = last_group_photo_id()
                        for url in post[0]:
                            num += 1
                            if sets[7] != 2:
                                add_group_photo(num, f"{group_sets[1]}?w=wall{link}",
                                                format_text(post[1], group_sets[1], link), url)
                            photo_ids.append(num)
                            if first and sets[7] == 2:
                                media.append(
                                    InputMediaPhoto(media=url, caption=format_text(post[1], group_sets[1], link) + (
                                        "\n\n" if len(post[1]) > 1 else "") + caption))
                                first = False
                            else:
                                media.append(InputMediaPhoto(media=url))
                        try:
                            if sets[7] == 1:
                                if cnt == 1:
                                    await send_group_photo(user_id, f'{photo_ids[0]}-{photo_ids[-1]}')
                                else:
                                    add_to_queue_group_photo(user_id, f'{photo_ids[0]}-{photo_ids[-1]}')
                            else:
                                async with ChatActionSender(bot=bot, chat_id=user_id, action='upload_photo'):
                                    await bot.send_media_group(user_id, media=media)
                        except Exception as e:
                            await bot.send_message(chat_id=user_id, text=f'Произошла ошибка! Код 3\n{e}')
            update_time(group)
        if cnt == 0:
            if len(get_admins_queue(user_id)) == 0:
                await bot.send_message(chat_id=user_id, text=f'Фото с текущими фильтрами не нашлось 😨')
            else:
                await send_next_photo(user_id)
        if message_id != 0:
            async with ChatActionSender(bot=bot, chat_id=user_id):
                await bot.edit_message_media(chat_id=user_id, message_id=message_id,
                                             media=InputMediaPhoto(
                                                 media='https://sun1-86.userapi.com/s/v1/if1/hNz4gzygw7cug2Vg2fnASFV8jj5B8xeo4MdVvujz767OUMdDE5TJnxR07wNSeCwszzDwI-5r.jpg?size=200x200&quality=96&crop=0,0,300,300&ava=1',
                                                 caption=f'КОНЧИЛ поиск фото по группам\n<code>{len(groups_set)} из {len(groups_set)}</code> | <code>100.00%</code>'))
                await asyncio.sleep(5)
                await bot.delete_message(chat_id=user_id, message_id=message_id)


def get_text_of_settings(user_id: int) -> str:
    sets = get_settings(user_id)
    extra_emoji = '🧊' if sets[7] == 2 else ''
    text = f'<b>⚙️{extra_emoji} Твои текущие настройки</b>\n<blockquote>'
    groups_str = ''
    if sets[6] is not None:
        text += '<b>Группы:\n</b>🔄    🔢    📅     <i>название\n'
        groups_set = set(map(int, sets[6].split(',')))
        for group in groups_set:
            settings = get_group_sets(group)
            if not settings[2]:
                continue
            text += ['🆕      ', '👍      '][settings[3]] + str(settings[4]).ljust(9) + str(settings[5]).ljust(8) + f'<a href = "https://vk.com/{get_group_domain(group)}">{get_group_name(group)}</a>\n'
        text += '</i>'
    else:
        groups_str = '<i>У тебя пока нет групп</i>\n'
    week_array = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    weekday_str = ''
    if sets[3] is not None:
        for weekday in map(int, sets[3].split(',')):
            weekday_str += f'{week_array[weekday - 1]}, '
        weekday_str = weekday_str[:-2]
    else:
        weekday_str = 'ни один день недели не выбран, фото не будут присылаться'
    extra = f'\n<b>Дни недели:</b>\n<i>{weekday_str}</i>\n<b>Время:</b>\n<i>{sets[4]}:{sets[5]}</i></blockquote>'
    return text + groups_str + extra


def get_text_of_group_sets(group_id: int, include_name: bool = True):
    settings = get_group_sets(group_id)
    name = settings[7]
    domain = settings[1]
    text = f'👥 <b><a href="vk.com/{domain}">{name}</a></b>\n\n'
    active = '• <b><i>Активна 🟢</i></b>' if settings[2] else '• <b><i>Отключена ❌</i></b>'
    top_likes = f'• Сортировка по: <b>{"лайкам 👍" if settings[3] else "актуальности 🆕"}</b>'
    photo_amount = f'• Количество фото, за одно обращение к стене: <b>{settings[4]}</b>'
    time_delta = f'• Посты не раньше, чем <b>{settings[5]}</b> дней(-я) назад'
    last_update = f'• Последнее обновление <b>{datetime.datetime.fromtimestamp(settings[6]).strftime("%H:%M %d.%m.%y")}</b>' if settings[6] != 0 else ''
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


def get_admin_keyboard(user_id: int, cancel_url_sending: bool = False, superuser: bool = False):
    if cancel_url_sending:
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔙', callback_data=AdminCallBack(action=1).pack())]])
    array_buttons: list[list[InlineKeyboardButton]] = []
    if superuser:
        incels = list(get_users())
        admins = get_admins()
        for i in range((len(incels) + 2) // 3):
            loc_array = []
            for j in range(min(3, len(incels) - i * 3)):
                username = get_username_by_id(incels[i * 3 + j])
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
        row1 = [InlineKeyboardButton(text='✅', callback_data=ManageSettings(action=1, photo_id=ids, back_ids=back_ids, message_to_delete=message_to_delete).pack()),
                InlineKeyboardButton(text='📝🚫', callback_data=ManageSettings(action=2, photo_id=ids,back_ids=back_ids, message_to_delete=message_to_delete).pack()),
                InlineKeyboardButton(text='✏️', callback_data=ManageSettings(action=3, photo_id=ids, back_ids=back_ids, message_to_delete=message_to_delete).pack())]
        array_buttons: list[list[InlineKeyboardButton]] = [row1, [InlineKeyboardButton(text='🔙',
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
        rows.append([InlineKeyboardButton(text='🗑',
                                          callback_data=ManageSettings(action=6, photo_id=f'{min(ids)}, {max(ids)}',
                                                                       message_to_delete=message_to_delete).pack())])
        markup = InlineKeyboardMarkup(inline_keyboard=rows)
        return markup
    else:
        row1 = [InlineKeyboardButton(text='✅', callback_data=ManageSettings(action=1, photo_id=ids).pack()),
                InlineKeyboardButton(text='📝🚫', callback_data=ManageSettings(action=2, photo_id=ids).pack()),
                InlineKeyboardButton(text='✏️', callback_data=ManageSettings(action=3, photo_id=ids).pack()),
                InlineKeyboardButton(text='🗑', callback_data=ManageSettings(action=4, photo_id=ids).pack())]
        array_buttons: list[list[InlineKeyboardButton]] = [row1]
        markup = InlineKeyboardMarkup(inline_keyboard=array_buttons)
        return markup


def get_group_keyboard(groups_id: Union[List[int], None], go_back_to_menu: bool = False):
    back = InlineKeyboardButton(text='🔙', callback_data=AdminCallBack(action=-2).pack())
    add = InlineKeyboardButton(text='Добавить группу', callback_data=AdminCallBack(action=4).pack())
    array_buttons: list[list[InlineKeyboardButton]] = []
    if groups_id is None:
        array_buttons = [[add],[back]]
        return InlineKeyboardMarkup(inline_keyboard=array_buttons)
    active_groups = get_active_groups()
    for i in range((len(groups_id) + 2) // 3):
        loc_array = []
        for j in range(min(3, len(groups_id) - i * 3)):
            domain = get_group_name(groups_id[i * 3 + j])
            emoji_loc = '🟢' if groups_id[i * 3 + j] in active_groups else '❌'
            button = InlineKeyboardButton(text=emoji_loc + ' ' + domain,
                                          callback_data=GroupCallBack(group_id=groups_id[i * 3 + j]).pack())
            loc_array.append(button)
        array_buttons.append(loc_array)
    array_buttons.append([back, add])
    markup = InlineKeyboardMarkup(inline_keyboard=array_buttons)
    return markup


def get_notify_keyboard(user_id: int, hour: bool = False, minute: bool = False, week: bool = False):
    week_array = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    settings = get_settings(user_id)
    if week:
        weekdays = get_weekdays(user_id)
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
        hour = get_hour(user_id)
        start = 0
        if hour == 7 or hour == 19:
            start = 1
            array_buttons[0].append(InlineKeyboardButton(text='00 ❌', callback_data=NotifySettings(action=8, minute=0).pack()))
        for i in range(start, 6):
            array_buttons[0].append(InlineKeyboardButton(text=str(i)+'0' + (' ✅'if (str(i)+'0') == settings[5] else ''), callback_data=NotifySettings(action=5, minute=i).pack()))
        custom = InlineKeyboardButton(text='Свой вариант', callback_data=NotifySettings(action=6).pack())
        array_buttons.append([back, custom])
        return InlineKeyboardMarkup(inline_keyboard=array_buttons)
    settings = get_settings(user_id)
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
        await callback.message.edit_text(text=get_text_of_settings(callback.from_user.id), disable_web_page_preview=True,
                                         reply_markup=get_admin_keyboard(callback.from_user.id))
    elif action == 0:
        set_inactive(callback.from_user.id)
        await callback.message.delete()
        await callback.message.answer(text='Ты исключен из админов', reply_markup=basic_keyboard)
    elif action == 1:
        await state.clear()
        groups_str = get_settings(callback.from_user.id)[6]
        if groups_str is None:
            await callback.message.edit_text(text='👥 У тебя еще нет групп. Самое время добавить! Жми 👇🏿',reply_markup=get_group_keyboard(groups_id=None))
            return
        text = '<b>👥 Нажми на группу для регулировки или добавь новую:</b>'
        await callback.message.edit_text(text=text, reply_markup=get_group_keyboard(sorted(list(map(int, groups_str.split(','))))))
    elif action == 2:
        text = '<b>🔊 Нажми на кнопку для настройки периодичности рассылки:</b>'
        await callback.message.edit_text(text=text, reply_markup=get_notify_keyboard(callback.from_user.id))
    elif action == 3:
        sets = get_settings(callback.from_user.id)
        if not sets[1]:
            await callback.message.edit_text('Ты больше не админ!')
            return
        if sets[6] is None:
            await callback.message.edit_text('👥 Ты еще не добавил ни одной группы!',
                                             reply_markup=get_group_keyboard(groups_id=None))
        else:
            mes_id = await bot.send_photo(chat_id=callback.from_user.id, photo='https://i.postimg.cc/TYv4PFJP/drawing-kitten-animals-9-Favim-1.jpg', caption=f'Начал поиск фото по группам')
            await notify_admin(callback.from_user.id, message_id=mes_id.message_id)
            await callback.answer()

    elif action == 4:
        await callback.message.edit_text(text='Скинь ссылку на стену группы вк, из которой ты хочешь получать фото', reply_markup=get_admin_keyboard(callback.from_user.id, cancel_url_sending=True))
        await state.set_state(FSMFillForm.inserting_url)
    elif action == -1:
        await callback.message.edit_text(text='<b>👤 Все инцелы</b>: вот они слева направо', reply_markup=get_admin_keyboard(callback.from_user.id, superuser=True))
    elif action == 5:
        user_id = callback_data.user_id
        if user_id in get_admins():
            set_inactive(user_id)
            await bot.send_message(chat_id=user_id, text='Ты больше не админ', reply_markup=basic_keyboard)
        else:
            set_admin(user_id)
            await bot.send_message(chat_id=user_id, text='Тебя назначили админом 👑', reply_markup=admin_keyboard)
        await callback.message.edit_text(text='<b>👤 Все инцелы</b>: вот они слева направо',
                                         reply_markup=get_admin_keyboard(callback.from_user.id, superuser=True))


async def send_next_photo(user_id: int):
    queue = get_admins_queue(user_id)
    if len(queue) == 0:
        return
    i = min(queue)
    remove_from_admins_queue(user_id, i)
    extra = '' if len(queue) == 1 else f' | {len(queue) - 1} в очереди'
    if '-' not in i:
        async with ChatActionSender(bot=bot, chat_id=user_id, action='upload_photo'):
            photo = send_photos_by_id(int(i))
            caption = f'👥 <b><a href="vk.com/{photo[1]}">{get_group_name(photo[1][:photo[1].find("?")])}</a></b>' + extra
            msg = await bot.send_photo(chat_id=user_id, photo=photo[3],
                                       caption=photo[2] + ("\n\n" if len(photo[2]) > 0 else "") + caption,
                                       reply_markup=get_manage_photo(ids=int(i)))
            set_message_to_delete(user_id, str(msg.message_id))
        return
    else:
        num = list(map(int, i.split('-')))
        nums = [i for i in range(num[0], num[1] + 1)]
        photo = send_photos_by_id(nums[0])
        caption = f'👥 <b><a href="vk.com/{photo[1]}">{get_group_name(photo[1][:photo[1].find("?")])}</a></b>' + extra
        media = []
        for num in nums:
            loc_photo = send_photos_by_id(num)
            media.append(InputMediaPhoto(media=loc_photo[3]))
        try:
            async with ChatActionSender(bot=bot, chat_id=user_id, action='upload_photo'):
                msg: List[Message] = await bot.send_media_group(user_id, media=media)
                await bot.send_message(chat_id=user_id,
                                       text=photo[2] + ("\n\n" if len(photo[2]) > 0 else "") + caption,
                                       reply_markup=get_manage_photo(ids=nums,
                                                                     message_to_delete=f'{msg[0].message_id}, {msg[-1].message_id}'),
                                       disable_web_page_preview=True)
                set_message_to_delete(user_id, f'{msg[0].message_id}-{msg[-1].message_id}')
        except Exception as e:
            await bot.send_message(chat_id=user_id, text=f'Произошла ошибка! Код 4\n{e}')


@dp.callback_query(ManageSettings.filter())
async def moderate_manage_settings(callback: CallbackQuery, callback_data: ManageSettings, state: FSMContext):
    action = callback_data.action
    photo_id = callback_data.photo_id
    if action == 2:
        await callback.answer('Фото будет выложено без подписи')
    if action == 1 or action == 2:
        information = get_group_photo_info(photo_id)
        last_num = get_last()
        add_photo_id(last_num + 1, information[3], f'👥 {information[1]}')
        if information[2] != '' and action == 1:
            add_note(last_num + 1, information[2])
        try:
            await callback.message.edit_caption(
                caption=f'Оцени фото из группы 👥 <b><a href="vk.com/{information[1]}">{get_group_name(information[1][:information[1].find("?"):])}</a></b>',
                reply_markup=get_rates_keyboard(last_num + 1, 3, ids=photo_id, back_ids=callback_data.back_ids,
                                                message_to_delete=callback_data.message_to_delete))
        except Exception:
            await callback.message.edit_text(
                text=f'Оцени фото из группы 👥 <b><a href="vk.com/{information[1]}">{get_group_name(information[1][:information[1].find("?"):])}</a></b>',
                reply_markup=get_rates_keyboard(last_num + 1, 3, ids=photo_id, back_ids=callback_data.back_ids,
                                                message_to_delete=callback_data.message_to_delete),
                disable_web_page_preview=True)
    elif action == 3:
        if callback.message.photo:
            await callback.message.edit_caption(caption='Введи следующим сообщением подпись к этой пикче',
                                                reply_markup=get_rates_keyboard(0, 3, photo_id, True))
        else:
            await callback.message.edit_text('Введи следующим сообщением подпись к этой пикче',
                                             reply_markup=get_rates_keyboard(0, 3, photo_id,
                                                                             back_ids=callback_data.back_ids,
                                                                             message_to_delete=callback_data.message_to_delete,
                                                                             back=True))
        information = get_group_photo_info(photo_id)
        last_num = get_last()
        add_photo_id(last_num + 1, information[3], f'👥 {information[1]}')
        set_message_to_delete(callback.from_user.id, str(callback.message.message_id))
        caption_global[callback.from_user.id] = (last_num + 1, photo_id)
        await state.set_state(FSMFillForm.inserting_caption)
    elif action == 4:
        try:
            del_group_photo(photo_id)
            await callback.message.delete()
            await send_next_photo(callback.from_user.id)
        except Exception as e:
            await bot.send_message(chat_id=972753303, text=f'Ошибка код 5\n{e}')
    elif action == 5:
        await callback.message.edit_text(text=f'Выбери действие для выбранного фото', reply_markup=get_manage_photo(photo_id, mode=3, back_ids=callback_data.back_ids, message_to_delete=callback_data.message_to_delete))
    elif action == 6:
        try:
            start = int(photo_id.split(',')[0])
            end = int(photo_id.split(',')[1])
            for photo_id in range(start, end + 1):
                del_group_photo(photo_id)
            await callback.message.delete()
            msgs = list(map(int, callback_data.message_to_delete.split(',')))
            msgs_list = [i for i in range(msgs[0], msgs[-1] + 1)]
            await bot.delete_messages(chat_id=callback.from_user.id, message_ids=msgs_list)
            await send_next_photo(callback.from_user.id)
        except Exception as e:
            await bot.send_message(chat_id=972753303, text=f'Ошибка код 6\n{e}')
    elif action == 7:
        ids_str = callback_data.back_ids
        first = int(ids_str.split(',')[0])
        last = int(ids_str.split(',')[1])
        ids_list = [i for i in range(first, last + 1)]
        info = get_group_photo_info(first)
        queue = get_admins_queue(callback.from_user.id)
        extra = f' | {len(queue)} в очереди'
        txt = '' if info[2] is None else info[2]
        caption = f'{txt}\n\n👥 <b><a href="vk.com/{info[1]}">{get_group_name(info[1][:info[1].find("?")])}</a></b>' + extra
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
        queue = get_admins_queue(callback.from_user.id)
        extra = f' | {len(queue)} в очереди'
        photo = send_photos_by_id(int(photo_id))
        txt = '' if photo[2] is None else photo[2]
        caption = f'{txt}\n\n👥 <b><a href="vk.com/{photo[1]}">{get_group_name(photo[1][:photo[1].find("?")])}</a></b>' + extra
        if callback.message.photo:
            await callback.message.edit_caption(caption=caption, reply_markup=get_manage_photo(ids=id))
        else:
            await callback.message.edit_text(text=caption, reply_markup=get_manage_photo(ids=id, message_to_delete=callback_data.message_to_delete, back_ids=back_ids), disable_web_page_preview=True)
        await state.clear()


@dp.callback_query(GroupCallBack.filter())
async def moderate_group_settings(callback: CallbackQuery, callback_data: AdminCallBack):
    settings = get_group_sets(callback_data.group_id)
    await callback.message.edit_text(text=get_text_of_group_sets(callback_data.group_id, 1),
                                     disable_web_page_preview=True,
                                     reply_markup=group_settings_keyboard(settings))


@dp.callback_query(NotifySettings.filter())
async def moderate_notify_settings(callback: CallbackQuery, callback_data: NotifySettings, state: FSMContext):
    action = callback_data.action
    if action == 0:
        txt = 'Выбери <b>дни недели</b>, в которые ты хочешь получать фото:'
        await callback.message.edit_text(text=txt, reply_markup=get_notify_keyboard(callback.from_user.id, week=True))
    elif action == 1:
        txt = 'Выбери час или введи значение сам:'
        await callback.message.edit_text(text=txt, reply_markup=get_notify_keyboard(callback.from_user.id, hour=True))
    elif action == 2:
        txt = 'Выбери минуту или введи значение сам:'
        await callback.message.edit_text(text=txt, reply_markup=get_notify_keyboard(callback.from_user.id, minute=True))
    elif action == 3:
        hour = callback_data.hour
        change_hour(callback.from_user.id, hour)
        await callback.answer(text=f'{hour} 🕑')
        text = '<b>🔊 Нажми на кнопку для настройки периодичности рассылки:</b>'
        await callback.message.edit_text(text=text, reply_markup=get_notify_keyboard(callback.from_user.id))
    elif action == 4:
        await callback.message.edit_text(text='Введи свое значение часа, в который ты хочешь получать фото из выбанных групп. <u>Учти</u>, что сервер перезагружается в 7:00 и 19:00, поэтому это время лучше не выбирать')
        await state.set_state(FSMFillForm.inserting_hour)
    elif action == 5:
        minute = callback_data.minute
        minute = str(minute) + '0'
        change_minute(callback.from_user.id, minute)
        await callback.answer(text=minute+ ' 🕑')
        text = '<b>🔊 Нажми на кнопку для настройки периодичности рассылки:</b>'
        await callback.message.edit_text(text=text, reply_markup=get_notify_keyboard(callback.from_user.id))
    elif action == 6:
        await callback.message.edit_text(text='Введи свое значение минут, в которые ты хочешь получать фото из выбанных групп. <u>Учти</u>, что сервер перезагружается в 7:00 и 19:00, поэтому это время лучше не выбирать')
        await state.set_state(FSMFillForm.inserting_minute)
    elif action == 7:
        day = callback_data.week
        change_weekdays(callback.from_user.id, day)
        txt = 'Выбери <b>дни недели</b>, в которые ты хочешь получать фото:'
        await callback.message.edit_text(text=txt, reply_markup=get_notify_keyboard(callback.from_user.id, week=True))
    elif action == 8:
        await callback.answer('Данное значение выбрать нельзя')

@dp.callback_query(GroupSettings.filter())
async def moderate_group_deep_settings(callback: CallbackQuery, callback_data: GroupSettings):
    action = callback_data.action
    group_id = callback_data.group_id
    if action == 1 or action == 2:
        if action == 1:
            switch_active(group_id)
        else:
            switch_top_likes(group_id)

        await callback.message.edit_text(text=get_text_of_group_sets(group_id),
                                         disable_web_page_preview=True, reply_markup=group_settings_keyboard(get_group_sets(group_id)))
    elif action == 3:
        await callback.message.edit_text(text='Нажми на количество постов, которое ты хочешь получать единоразово при одном обращении к группе', reply_markup=group_settings_keyboard(settings=get_group_sets(group_id), get_amount=True))
    elif action == 4:
        await callback.message.edit_text(text='Нажми на количество дней, сколько пост должен находиться в группе',
                                         reply_markup=group_settings_keyboard(settings=get_group_sets(group_id), get_date=True))
    elif action == 5:
        name = get_group_name(group_id)
        try:
            delete_group(group_id, user_id=callback.from_user.id)
            await callback.answer(f'Группа {name} удалена 🗑')
        except Exception as e:
            await callback.message.edit_text(f'Произошла ошибка! Код 7\n{e}')
        groups_str = get_settings(callback.from_user.id)[6]
        if groups_str is None:
            await callback.message.edit_text(text='У тебя еще нет групп',
                                             reply_markup=get_group_keyboard(groups_id=None))
            return
        text = '<b>👥 Нажми на группу для регулировки или добавь новую:</b>'
        await callback.message.edit_text(text=text,
                                         reply_markup=get_group_keyboard(sorted(list(map(int, groups_str.split(','))))))
    elif action == 6:
        await callback.message.edit_text(text='ℹ️ информация по настройке рассылки группы:\n1) Переключи режим активности, чтобы <b>не получать фото</b> / <b>получать фото</b> этой группы\n2) Нажми на кнопку сортировки постов для переключения режимов:\n   <b>по лайкам:</b> в указанном диапазоне будут выбраны <i>n</i> постов с наибольшим количеством лайков\n   <b>по актуальности:</b> будет выбрано <i>n</i> последних постов в указанном диапазоне\n3) <b>Количество фото:</b> выбери, сколько фото ты хочешь получить при одном обращении к группе\n4) <b>Дата поста:</b> здесь тебе нужно выбрать, сколько дней назад должны быть выложены посты. Совет: чем дольше посты лежат на стене, тем больше просмотров и лайков они собирают, поэтому сортировка по лайкам будет работать лучше всего, это также помогает избежать ошибок.\n5) <b>Удалить:</b> полностью удаляет группу из твоего списка',
                                         reply_markup=group_settings_keyboard(get_group_sets(group_id), True))
    elif action == 7:
        await callback.message.edit_text(text=get_text_of_group_sets(group_id, 1),
                                         disable_web_page_preview=True,
                                         reply_markup=group_settings_keyboard(get_group_sets(group_id)))
    elif action == 8:
        amount = callback_data.amount
        change_amount(group_id, amount)
        await callback.answer(text=str(amount))
        await callback.message.edit_text(text=get_text_of_group_sets(group_id),
                                         disable_web_page_preview=True, reply_markup=group_settings_keyboard(get_group_sets(group_id)))
    elif action == 9:
        date = callback_data.date
        change_date(group_id, date)
        update_time(group_id, 0)
        await callback.answer(text=str(date))
        await callback.message.edit_text(text=get_text_of_group_sets(group_id),
                                         disable_web_page_preview=True, reply_markup=group_settings_keyboard(get_group_sets(group_id)))


@dp.message(StateFilter(FSMFillForm.inserting_url))
async def get_url_vk(message: Message, state: FSMContext):
    if message.text:
        valid = check_valid_url(message.text)
        if not valid[0]:
            await message.answer('Ссылка недействительна. Отправь ссылку на группу <b><u>vk.com</u></b>')
        else:
            group_id = add_group(message.from_user.id, valid[1])
            if group_id[0] == -1:
                await message.answer(f'Такая группа уже есть в твоём списке\n\n{get_text_of_group_sets(group_id[1], 1)}', disable_web_page_preview=True, reply_markup=group_settings_keyboard(get_group_sets(group_id[1])))
                await state.clear()
                return
            group_id = group_id[0]
            group_sets = get_group_sets(group_id)
            name = get_group_name(valid[1])
            await message.answer(
                f'Ты добавил группу <b>{name}</b>\n\nНастройки по умолчанию:\n{get_text_of_group_sets(group_id, 0)}',
                disable_web_page_preview=True, reply_markup=group_settings_keyboard(group_sets))
            await state.clear()
    else:
        await message.answer('Это не похоже на ссылку')

@dp.message(StateFilter(FSMFillForm.inserting_caption))
async def get_caption_group(message: Message, state: FSMContext):
    if not message.text:
        await message.answer('Это не похоже на текст для подписи к пикче')
        return
    num, photo_id = caption_global[message.from_user.id]
    if num == 0:
        await message.answer('Произошла ошибка')
        return
    caption_global[message.from_user.id] = (0, 0)
    add_note(num, message.text)
    caption_global[message.from_user.id]
    async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action='upload_photo'):
        await bot.send_photo(chat_id=message.from_user.id, photo=get_photo_id_by_id(num),
                             caption=f'Охуенная заметка: <b><i>{message.text}</i></b>. А теперь оцени фото',
                             reply_markup=get_rates_keyboard(num, mailing=3, ids=photo_id))
    previous = get_message_to_delete(message.from_user.id)
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
            await message.answer('Ты ввел неверное значение часа')
        else:
            hour = int(message.text)
            minute = get_minute(message.from_user.id)
            minute_str = str(minute)
            if minute == 0:
                minute_str = '00'
            elif minute < 10:
                minute_str = '0' + minute_str
            if (hour == 6 or hour == 18) and (minute >= 55):
                await message.answer(text=f'<b>Текущее значение минут: {minute_str}</b>. Сервер перезагружается в <u>{hour + 1}:00</u>, тебе лучше выбрать время чуть попозже')
                return
            if (hour == 7 or hour == 19) and (minute <= 9):
                await message.answer(text=f'<b>Текущее значение минут: {minute_str}</b>. Сервер перезагружается в <u>{hour}:00</u>, тебе лучше выбрать время чуть попозже')
                return
            if (hour == 9) and (minute <= 16 and minute >= 5):
                await message.answer(text=f'<b>Текущее значение минут: {minute_str}</b>. Сервер перезагружается в <u>9:10</u>, тебе лучше выбрать время чуть попозже')
                return
            set_hour(message.from_user.id, str(hour))
            await message.answer(f'Отлично! Теперь фото будут присылаться в <b>{hour}:{minute_str}</b>. <i>Изменения, будут применены при следующей перезагрузке сервера</i>', reply_markup=get_notify_keyboard(message.from_user.id))
            await state.clear()
    else:
        await message.answer('Это не похоже на часовой формат 🤨')


@dp.message(StateFilter(FSMFillForm.inserting_minute))
async def get_minute_vk(message: Message, state: FSMContext):
    if message.text:
        valid = check_minutes(message.text)
        if not valid:
            await message.answer('Ты ввел неверное значение минут')
        else:
            minute = int(message.text)
            hour = get_hour(message.from_user.id)
            if (hour == 6 or hour == 18) and (minute >=55):
                await message.answer(text=f'<b>Текущее значение часа: {hour}</b>. Сервер перезагружается в <u>{hour + 1}:00</u>, тебе лучше выбрать время чуть пораньше')
                return
            if (hour == 7 or hour == 19) and (minute <= 9):
                await message.answer(text=f'<b>Текущее значение часа: {hour}</b>. Сервер перезагружается в <u>{hour}:00</u>, тебе лучше выбрать время чуть попозже')
                return
            if (hour == 9) and (minute <= 16 and minute >= 5):
                await message.answer(text=f'<b>Текущее значение минут: {minute_str}</b>. Сервер перезагружается в <u>9:10</u>, тебе лучше выбрать время чуть попозже')
                return
            minute_str= str(minute)
            if minute == 0:
                minute_str = '00'
            elif minute < 10:
                minute_str = '0' + minute_str
            set_minute(message.from_user.id, minute_str)
            await message.answer(
                f'Отлично! Теперь фото будут присылаться в <b>{hour}:{minute_str}</b>. <i>Изменения, будут применены при следующей перезагрузке сервера</i>',
                reply_markup=get_notify_keyboard(message.from_user.id))
            await state.clear()
    else:
        await message.answer('Это не похоже на минутный формат 🤨')


@dp.callback_query(RateCallBack.filter())
async def filter_rates(callback: CallbackQuery,
                       callback_data: RateCallBack, state: FSMContext):
    num = callback_data.photo_id
    await callback.answer(text=rate[callback_data.r])
    mailing = callback_data.mailing
    votes = get_votes(num)
    photo_is_not_posted = True
    insert_last_rate(callback.from_user.id, num)
    if mailing == 1 and len(votes.keys()) >= len(get_users()):
        photo_is_not_posted = False  # индикатор, который отвечает за публикацию поста в канал (для того чтобы после изменения оценки пост не выложился еще раз)
    add_rate(num, callback.from_user.username, callback_data.r)
    delete_from_queue(callback.from_user.id, num)
    if mailing == 1:
        try:
            await callback.message.delete()
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
                                chat_id=get_id_by_username(last_username))
                            states_users[last_username] = datetime.datetime.now()

            if len(votes.keys()) >= len(get_users()) and photo_is_not_posted:
                avg = sum(votes.values()) / len(votes.keys())
                add_to_weekly(get_photo_id_by_id(num), avg)
                avg_str = '{:.2f}'.format(avg)
                avg_public = min(avg + 2, 10)
                avg_str_public = '{:.2f}'.format(avg_public)
                await send_results(num, avg_str_public)
                extra = ''
                spoiler = False
                if avg == 0:
                    spoiler = True
                    extra = '<b>🚨Осторожно!🚨\nУберите от экранов детей и людей с тонкой душевной организацией. Данное фото может Вас шокировать\n\n</b>'
                if avg == 11:
                    spoiler = True
                    extra = '<b>😍 Все участники банды инцелов оценили фото на 11 😍</b>\n\n'

                user_rates = ''
                sorted_rates = sorted(votes.items(), key=lambda x: x[1], reverse=True)
                for key, value in sorted_rates:
                    user_id = get_id_by_username(key)
                    if user_id is not None:
                        add_rate_to_avg(user_id, value)
                    user_rates += f'@{key}: <i>{value}</i>\n'
                rounded = round(avg)
                rounded_public = round(avg_public)
                note_str_origin = get_note_sql(num)
                note_str = f': <blockquote>{note_str_origin.replace("/anon", "").strip()}</blockquote>\n' if note_str_origin is not None else '\n\n'
                name = get_origin(num)
                name = '@' + name if name[0] != '👥' else f'👥 <a href="vk.com/{name[2:]}">{get_group_name(name[:name.find("?")][2:])}</a>'
                txt = extra + f'Автор пикчи <b>{name}</b>' + note_str + "Оценки инцелов:\n" + user_rates + '\n' f'Общая оценка: <b>{avg_str}</b>' + f'\n<i>#{rate2[rounded].replace(" ", "_")}</i>'
                await bot.send_photo(chat_id=channel_id, photo=get_photo_id_by_id(num), caption=txt,
                                     has_spoiler=spoiler)
                if note_str_origin is None or '/anon' not in note_str_origin:

                    txt2 = note_str[2:] + f'Оценено на <b>{avg_public}</b> из <b>10</b>' + f'\n<i>#{rate2[rounded_public].replace(" ", "_")}</i>'
                    await bot.send_photo(chat_id=channel_id_public, photo=get_photo_id_by_id(num), caption=txt2)
        except Exception as e:
            await bot.send_message(chat_id=972753303, text=f'Произошла ошибка после оценки фото № {num} пользователем {callback.from_user.username} \n{e}')
        try:
            q = get_queue(callback.from_user.id)
            if len(q) == 0:
                add_current_state(callback.from_user.id, 0, callback.from_user.username)
                return
            i = min(q)
            async with ChatActionSender(bot=bot, chat_id=callback.from_user.id, action='upload_photo'):
                await bot.send_photo(callback.from_user.id, get_photo_id_by_id(i),
                                     reply_markup=get_rates_keyboard(num=i, mailing=1))
            add_current_state(callback.from_user.id, i, callback.from_user.username)
        except Exception as e:
            await bot.send_message(chat_id=972753303,
                                   text=f'Произошла ошибка! Пользователь {callback.from_user.username} не получил фото из очереди\n{e}')
        return
    elif mailing == 2:
        await callback.message.delete()
        return
    elif mailing == 3:
        await callback.message.delete()
        await send_photo_to_users(callback.from_user.id, num)
        previous = get_message_to_delete(callback.from_user.id)
        if '-' in previous:
            previous = list(map(int, previous.split('-')))
            msgs_list = [i for i in range(previous[0], previous[-1] + 1)]
            await bot.delete_messages(chat_id=callback.from_user.id, message_ids=msgs_list)
        await send_next_photo(callback.from_user.id)
        return
    elif mailing == 4:
        rate_loc = get_not_incel_rate(num)
        if rate_loc == -1:
            rate_loc = callback_data.r + round(random.uniform(-1, 1), 2)
            if rate_loc <= 0:
                rate_loc = round(random.uniform(0, 1), 2)
            if rate_loc >= 10:
                rate_loc = round(random.uniform(9, 10), 2)
            add_rate_not_incel(num, rate_loc)
            await send_results(num, rate_loc)

    await callback.message.edit_text(f'Ты поставил оценку {callback_data.r} {emoji[callback_data.r]}')
    if mailing != 4:
        add_current_state(callback.from_user.id, 0, callback.from_user.username)
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
        note = get_note_sql(photo_id)
        note = '' if note is None else f'"{note}"'
        await bot.send_photo(972753303, photo=get_photo_id_by_id(photo_id),
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
        creator_id = get_id_by_username(creator)
        if creator_id is not None:
            try:
                add_rate_not_incel(photo_id, -2)
                await bot.send_photo(chat_id=creator_id, photo=get_photo_id_by_id(photo_id),
                                     caption=replicas['reject'],
                                     reply_markup=get_keyboard(creator_id))
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
                                      reply_markup=get_rates_keyboard(photo_id, 4))
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
            await bot.send_message(chat_id=creator_id, text='🔫 C этого момента ты в бане')
    elif action == 4:
        rate_loc = get_not_incel_rate(photo_id)
        if rate_loc == -1:
            rate_loc = round(random.uniform(3, 7), 2)
            add_rate_not_incel(photo_id, rate_loc)
            await send_results(photo_id, str(rate_loc))
    else:
        await callback.message.edit_text(text=f'Пощадим его', reply_markup=None)


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    result = check_id(user_id, username)
    if result[0]:
        await message.answer('Нахуя ты старт нажал', reply_markup=get_keyboard(message.from_user.id))
        async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action='upload_video'):
            await message.answer_video(video=FSInputFile(path='guide.mp4'))
        await state.set_state(FSMFillForm.verified)
    else:
        if result[1] <= 0   :
            await message.answer(random.choice(emoji_banned) + ' ' + random.choice(replicas['banned']).replace('$', '"'),
                                 reply_markup=ReplyKeyboardRemove())
            await state.set_state(FSMFillForm.banned)
            return

        await message.answer(replicas['hi'].replace('$', '"'), disable_web_page_preview=True, reply_markup=get_keyboard(user_id))

        #await message.answer_sticker(sticker='CAACAgIAAxkBAAELD9NljoEHEI6ehudWG_Cql5PXBwMw-AACSCYAAu2TuUvJCvMfrF9irTQE', reply_markup=not_incel_keyboard)


@dp.message_reaction()
async def message_reaction_handler(message_reaction: MessageReactionUpdated):
    if len(message_reaction.new_reaction)!=0:
        await bot.set_message_reaction(chat_id=message_reaction.chat.id, message_id=message_reaction.message_id,
                                   reaction=[ReactionTypeEmoji(emoji=message_reaction.new_reaction[0].emoji)])


@dp.message(Command(commands='password_yaincel'))
async def settings(message: Message, state: FSMContext):
    set_verified(message.from_user.id)
    await message.answer(text='Поздравляю, ты теперь в нашей банде инцелов', reply_markup=get_keyboard(message.from_user.id))
    await state.set_state(FSMFillForm.verified)


@dp.message(Command(commands='anon'), ~F.photo)
async def anon(message: Message, state: FSMContext):
    await message.answer(text='А фоточка? 🥺', reply_markup=get_keyboard(message.from_user.id))


@dp.message(Command(commands='clear_admin_queues'))
async def settings(message: Message, state: FSMContext):
    try:
        for user in get_admins():
            remove_from_admins_queue(user, 0)
    except Exception as e:
        await message.answer(text=f'Ошибка код 400\n{e}')
    await message.answer('очереди были очищены')


@dp.message(Command(commands='help'))
async def help(message: Message, state: FSMContext):
    result = check_id(message.from_user.id, message.from_user.username)
    if not result[0]:
        await message.answer(replicas['help'].replace('$', '"'), disable_web_page_preview=True, reply_markup=get_keyboard(message.from_user.id))
        async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action='upload_video'):
            await message.answer_video(video=FSInputFile(path='guide.mp4'))
        return
    await message.answer(
        text='Просто скинь мне любое фото, и оно будет отправлено всем участникам <a href="https://t.me/+D_c0v8cHybY2ODQy">банды инцелов</a>.\nКнопка "Статистика 📊" покажет тебе график всех средних значений оценок твоих фото.\n' + \
             'Отправил оценку ошибочно? Тогда нажми кнопку "Изменить последнюю оценку ✏️".\nЕсли ты хочешь добавить заметку к фото, сделай подпись к ней и отправь мне, она будет показана в канале по окончании голосования\n\n<span class="tg-spoiler">/quote — случайная цитата</span>',
        disable_web_page_preview=True, reply_markup=get_keyboard(message.from_user.id))
    async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action='upload_video'):
        await message.answer_video(video=FSInputFile(path='guide.mp4'))


@dp.message(Command(commands='info'))
async def info(message: Message, state: FSMContext):
    result = check_id(message.from_user.id, message.from_user.username)
    await message.answer(replicas['info'].replace('$', ''), disable_web_page_preview=True, reply_markup=get_keyboard(message.from_user.id))


@dp.message(Command(commands='about'))
async def about(message: Message, state: FSMContext):
    result = check_id(message.from_user.id, message.from_user.username)
    await message.answer(replicas['about'].replace('$', ''), disable_web_page_preview=True, reply_markup=get_keyboard(message.from_user.id))


@dp.message(Command(commands='quote'))
async def quote(message: Message):
    url = "http://api.forismatic.com/api/1.0/"
    params = {
        "method": "getQuote",
        "format": "json",
        "lang": "ru"
    }
    try:
        rand_int = random.random()
        keyboard: list[list[InlineKeyboardButton]] = [
            [InlineKeyboardButton(text='Еще цитата 📖', callback_data='more')]]
        markup_local = InlineKeyboardMarkup(inline_keyboard=keyboard)
        if rand_int <= 0.01:  # Шанс 1%
            quote = legendary_quote
        elif rand_int <= 0.4:
            try:
                result = get_randQuote()
            except Exception as e:
                await bot.send_message(chat_id=972753303, text=f'Произошла ошибка!\n{e}')
                return
            if result is None:
                return
            if result[0] is not None:
                if result[1] is not None:
                    if result[1].lower().count('(с)') + result[1].lower().count('(c)') + result[1].count('©') == 0:
                        caption = f'<blockquote>{result[1]}</blockquote>'
                    else:
                        caption = '<blockquote>' + result[1][:result[1].find('(') - 1] + '</blockquote>' + result[1][result[1].find('('):]
                await message.answer_photo(photo=result[0], caption=caption, reply_markup=markup_local)
            else:
                if result[1].lower().count('(с)') + result[1].lower().count('(c)') + result[1].count('©') == 0:
                    caption = f'<blockquote>{result[1]}</blockquote>'
                else:
                    caption = '<blockquote>' + result[1][:result[1].find('(') - 1] + '</blockquote>' + result[1][result[1].find('('):]
                await message.answer(text=caption, reply_markup=markup_local)
            return
        else:
            response = requests.get(url, params=params)
            quote = response.json()["quoteText"]

        await message.answer(text=f'<blockquote>{quote}</blockquote>', reply_markup=markup_local)
    except requests.RequestException as e:
        await message.answer(text=f'<i>{legendary_quote}</i>')


@dp.callback_query(F.data == 'more')
async def process_more_press(callback: CallbackQuery):
    url = "http://api.forismatic.com/api/1.0/"
    params = {
        "method": "getQuote",
        "format": "json",
        "lang": "ru"
    }
    try:
        await callback.answer()
        rand_int = random.random()
        keyboard: list[list[InlineKeyboardButton]] = [
            [InlineKeyboardButton(text='Еще цитата 📖', callback_data='more')]]
        markup_local = InlineKeyboardMarkup(inline_keyboard=keyboard)
        if rand_int <= 0.01:  # Шанс 1%
            quote = legendary_quote
        elif rand_int <= 0.25:
            try:
                result = get_randQuote()
            except Exception as e:
                await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! Код 9\n{e}')
                return
            if result is None:
                return
            if result[0] is not None:
                if result[1] is not None:
                    if result[1].lower().count('(с)') + result[1].lower().count('(c)') + result[1].count('©') == 0:
                        caption = f'<blockquote>{result[1]}</blockquote>'
                    else:
                        caption = '<blockquote>' + result[1][:result[1].find('(')-1] + '</blockquote>'+ result[1][result[1].find('('):]
                await callback.message.answer_photo(photo=result[0], caption=caption, reply_markup=markup_local)
            else:
                if result[1].lower().count('(с)') + result[1].lower().count('(c)') + result[1].count('©') == 0:
                    caption = f'<blockquote>{result[1]}</blockquote>'
                else:
                    caption = '<blockquote>' + result[1][:result[1].find('(') - 1] + '</blockquote>' + result[1][result[1].find('('):]
                await callback.message.answer(text=caption, reply_markup=markup_local)
            return
        else:
            response = requests.get(url, params=params)
            quote = response.json()["quoteText"]

        await callback.message.answer(text=f'<blockquote>{quote}</blockquote>', reply_markup=markup_local)
    except requests.RequestException as e:
        await callback.message.answer(text=f'<i>{legendary_quote}</i>')


@dp.message(Command(commands='get_users'), F.from_user.id.in_(incels))
async def send_clear_users_db(message: Message):
    incels = get_users()
    db = get_usersinfo_db()
    if db is None:
        await message.answer(text='БД пустая')
        return

    txt = f'Всего пользователей: <b>{len(db)}</b>\n\n<b>Инцелы:</b>\n'
    db_incel = [i for i in db if i[3]]
    db_not_incel = [i for i in db if i[3] == 0]
    db_not_incel = sorted(db_not_incel, key=lambda x: (
        -int(x[5].split(',')[-1]) if x[5] is not None else float('inf'), x[1] if x[1] is not None else ''))
    for user in db_incel:
        username = f'@{user[1]}' if user[1] is not None else 'N/A'
        queue_str = f'<i>Очередь:</i> {user[-2]}' if (user[3] and user[-2] is not None) else '<i>Очередь пуста ✅</i>'
        line = f'<b>{username}</b> | {queue_str}\n'
        if len(line) + len(txt) < 4096:
            txt += line
        else:
            await message.answer(text=txt)
            txt = line
    txt += '\n<b>Попуски:</b>\n'
    for user in db_not_incel:
        username = f'@{user[1]}' if user[1] is not None else 'N/A'
        banned = '| забанен 💀' if user[2] else ''
        a = ","
        photos = '' if user[5] is None else f"| <i>Фотки:</i> {', '.join(user[5].split(a))}"
        line = f'<b>{username}</b> {banned} {photos}\n'
        if line == '<b>N/A</b>  \n':
            continue
        if len(line) + len(txt) < 4096:
            txt += line
        else:
            try:
                await message.answer(text=txt)
            except Exception as e:
                await message.answer(text=f'Ошибка! {e}')
            txt = line
    try:
        await message.answer(text=txt)
    except Exception as e:
        await message.answer(text=f'Ошибка! {e}')


@dp.message(Command(commands='clear_queue'), F.from_user.id.in_(get_users()))
async def clear_queue(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй')
    else:
        try:
            for user in get_users():
                delete_from_queue(id=user)
                add_current_state(id=user, num=0)
            await message.answer(text='Очереди очищены 🫡')
        except Exception as e:
            await message.answer(text=f'Произошла ошибка! Код 10\n{e}')


@dp.message(Command(commands='upd_groupnames'), F.from_user.id.in_(get_users()))
async def upd_groupnames(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй')
    else:
        update_groupnames()
        await message.answer('Названия групп обновлены')



@dp.message(Command(commands='clear_states'), F.from_user.id.in_(get_users()))
async def clear_state(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй')
    else:
        try:
            for user in get_users():
                add_current_state(id=user, num=0)
            await message.answer(text='Состояния очищены 🫡')
        except Exception as e:
            await message.answer(text=f'Произошла ошибка! Код 11\n{e}')


@dp.message(Command(commands='backup'), F.from_user.id.in_(get_users()))
async def backup_files(message: Message):
    try:
        async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action='upload_document'):
            doc = InputMediaDocument(media=FSInputFile("slutsDB.db"))
            doc2 = InputMediaDocument(media=FSInputFile("usersDB.db"))
            doc3 = InputMediaDocument(media=FSInputFile("weekly.db"))
            doc4 = InputMediaDocument(media=FSInputFile("weekly_info.db"))
            doc5 = InputMediaDocument(media=FSInputFile("admins.db"))
            doc6 = InputMediaDocument(media=FSInputFile("statham.db"),
                                      caption=f'Бэкап <i>{datetime.datetime.now().date()}</i>')
            await bot.send_media_group(media=[doc, doc2, doc3, doc4, doc5, doc6], chat_id=message.chat.id)
    except Exception as e:
        await bot.send_message(chat_id=972753303, text=f'Произошла ошибка при отправке файлов для бэкапа\n{e}')


@dp.message(Command(commands='god_mode'), F.from_user.id.in_(get_users()))
async def god_mode(message: Message):
    if message.from_user.id == 972753303:
        set_admin(972753303)
        await message.answer(text='С возвращением!', reply_markup=admin_keyboard)


@dp.message(Command(commands='chill_mode'), F.from_user.id.in_(get_users()))
async def chill_mode_lol(message: Message):
    if message.from_user.id == 972753303:
        chill_mode(972753303)
        await message.answer(text='Почилль, дружище', reply_markup=admin_keyboard)


@dp.message(Command(commands='default_mode'), F.from_user.id.in_(get_users()))
async def default_mode_lol(message: Message):
    if message.from_user.id == 972753303:
        default_mode(972753303)
        await message.answer(text='Включен режим модерации', reply_markup=admin_keyboard)



@dp.message(Command(commands='get_users_info_db'), F.from_user.id.in_(get_users()))
async def send_users_db(message: Message):
    db = get_usersinfo_db()
    if db is None:
        await message.answer(text='БД пустая')
        return
    txt = map(str, db)
    txt = '\n'.join(txt)
    for i in range((len(txt) + 4096) // 4096):
        await message.answer(text=txt[i * 4096:(i + 1) * 4096])


@dp.message(Command(commands='avgs'), F.from_user.id.in_(get_users()))
async def send_avgs(message: Message):
    txt = '<b>Средние значения</b>\n'
    mx_len_username = 0
    averages = {}
    for user in incels:
        username = get_username_by_id(user)
        if len(username) > mx_len_username:
            mx_len_username = len(username)
        average_tuple = get_avg_rate(user)
        if average_tuple is None:
            averages[username] = 0
        else:
            averages[username] = average_tuple[0] / average_tuple[1]
    averages = sorted(averages.items(), key=lambda x: x[1], reverse=True)
    for username, avg in averages:
        if avg is None:
            avg = 0
        txt += f'<code>@{username.ljust(mx_len_username)}</code> | <b>{"{:.5f}".format(avg)}</b>\n'
    await message.answer(txt)


@dp.message(Command(commands='queue'), F.from_user.id.in_(get_users()))
async def get_queue_rates(message: Message):
    db = get_usersinfo_db()
    if db is None:
        await message.answer(text='БД пустая', reply_markup=get_keyboard(message.from_user.id))
        return
    db_incel = [i for i in db if i[3]]
    txt = ''
    mx_len_username = 0
    for incel_loc in db_incel:
        if len(incel_loc[1]) > mx_len_username:
            mx_len_username = len(incel_loc[1])
    cnt = 0
    for incel_loc in db_incel:
        if incel_loc[-2] is None:
            queue = '✅'
        else:
            queue = f"В очереди <b>{len(incel_loc[-2].split(','))}</b>"
            cnt += 1
        line = f'<code>@{incel_loc[1].ljust(mx_len_username)}</code> | {queue}\n'
        txt += line
    txt += f'<blockquote>Итого ублюдков: <b>{cnt}</b></blockquote>'
    await message.answer(text=txt, reply_markup=get_keyboard(message.from_user.id))


@dp.message(Command(commands='remove_quote'), F.from_user.id.in_(get_users()))
async def remove_quote(message: Message):
    if len(message.text) <= len('remove_quote') + 2:
        await message.answer(text='Произошла ошибка')
        return
    num = int(message.text[len('remove_quote') + 2:])
    res = del_quote(num)
    if res:
        await message.answer(text=f'Цитата №{num} удалена')
    else:
        await message.answer(text='Произошла ошибка')


@dp.message(Command(commands='get_statham_db'), F.from_user.id.in_(get_users()))
async def send_statham_db(message: Message):
    db = get_statham_db()
    if db is None or len(db) == 0:
        await message.answer(text='БД пустая')
        return
    txt = map(str, db)
    txt = '\n'.join(txt)
    for i in range((len(txt) + 4096) // 4096):
        await message.answer(text=txt[i * 4096:(i + 1) * 4096])


@dp.message(Command(commands='getcoms'), F.from_user.id.in_(get_users()))
async def get_all_commands(message: Message):
    txt = '/start\n/help\n/stat\n/anon\n/info\n/quote\n/del_...\n/ban_...\n/send_..\n/send_all\n/send_incels\n/send_topincels\n/cs_...\n/cavg_...\n/new_quote\n/remove_quote ...\n/queue\n/backup\n/get_statham_db\n/send_tier_list\n/upd_groupnames\n/avgs\n/upd_file\n/delete_tier_list\n/get_users\n/get_users_info_db\n/get_weekly_db\n/get_latest_sluts\n/get_sluts_db\n/weekly_off\n/weekly_on\n/clear_queue\n/clear_states\n/clear_admin_queues\n/get_ban\n/password_yaincel\n/getcoms\n/about'
    await message.answer(text=txt, reply_markup=get_keyboard(message.from_user.id))


@dp.message(Command(commands='get_weekly_db'))
async def send_weekly_db(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй')
    else:
        db = get_weekly_db_info()
        if db is None:
            await message.answer(text='БД пустая')
            return
        txt = str(db)
        for i in range((len(txt) + 4096) // 4096):
            await message.answer(text=txt[i * 4096:(i + 1) * 4096])


@dp.message(Command(commands='weekly_off'))
async def weekly_cancel_func(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй')
    else:
        weekly_cancel(message.from_user.id)
        await message.answer(text='Еженедельная рассылка тир листа отключена')


@dp.message(Command(commands='weekly_on'))
async def send_users_db_func(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй')
    else:
        weekly_resume(message.from_user.id)
        await message.answer(text='Еженедельная рассылка тир листа возобновлена')


@dp.message(Command(commands='get_ban'))
async def ban_user(message: Message, state: FSMContext):
    get_ban(message.from_user.id)
    await message.answer(text='Ты исключен из банды инцелов', reply_markup=ReplyKeyboardRemove())
    await state.set_state(FSMFillForm.banned)


@dp.message(Command(commands='get_sluts_db'))
async def send_sluts_db(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй')
    else:
        if get_sluts_db() is None:
            await message.answer(text='БД пустая')
            return
        txt = map(str, get_sluts_db())
        txt = '\n'.join(txt)
        for i in range((len(txt) + 4096) // 4096):
            await message.answer(text=txt[i * 4096:(i + 1) * 4096])


@dp.message(Command(commands='get_latest_sluts'))
async def send_latest_sluts_db(message: Message):
    if message.from_user.id != 972753303:
        await message.answer(text='иди нахуй')
    else:
        sluts_list = get_sluts_db()
        if sluts_list is None:
            await message.answer(text='БД пустая')
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
            if i[1] is None:
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
    set_verified(id=message.from_user.id)
    await message.answer(
        text='<b>Привет, уёбище!</b>\nТеперь ты в нашей банде. Просто пришли мне фото, и его смогут оценить все участники. Если ты хочешь добавить заметку, сделай подпись к фото и отправь мне, она будет показана в <b><a href="https://t.me/+D_c0v8cHybY2ODQy">канале</a></b> по окончании голосования. Также тебе будут присылаться фото от других пользователей для оценки. Не забудь добавить <b>/anon</b>, если не хочешь, чтобы фото попало в <b><a href="https://t.me/rateimage">публичный канал</a></b>',
        disable_web_page_preview=True, reply_markup=get_keyboard(message.from_user.id))
    await state.set_state(FSMFillForm.verified)


@dp.message(F.photo, StateFilter(FSMFillForm.sending_photo))
async def get_photo_by_button(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    last_num = get_last()
    add_photo_id(last_num + 1, file_id, message.from_user.username)
    add_girlphoto(message.from_user.id, last_num + 1)
    await message.answer(text='Оцени фото, которое ты скинул',
                         reply_markup=get_rates_keyboard(last_num + 1, 0))
    add_current_state(message.from_user.id, -1, message.from_user.username)
    await state.clear()


@dp.message(F.text == 'Не отправлять фото', StateFilter(FSMFillForm.sending_photo))
async def cancel_sending(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text='Ты вышел из меню отправки фото')
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
    result = check_id(message.from_user.id, message.from_user.username)
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
    add_current_state(message.from_user.id, -1, message.from_user.username)


@dp.message(StateFilter(FSMFillForm.rating))
async def remember_to_rate(message: Message, state: FSMContext):
    await message.answer(text='Поставь оценку, сука!')


@dp.message(F.photo, ~StateFilter(FSMFillForm.sendDM))
async def default_photo(message: Message, state: FSMContext):
    result = check_id(message.from_user.id, message.from_user.username)
    file_id = message.photo[-1].file_id
    last_num = get_last()
    add_photo_id(last_num + 1, file_id, message.from_user.username)
    add_girlphoto(message.from_user.id, last_num + 1)
    if not result[0]:
        if result[1] == -1:
            await message.answer(random.choice(emoji_banned) + ' ' + random.choice(replicas['banned']).replace('$', '"'),
                                 reply_markup=ReplyKeyboardRemove())
            await state.set_state(FSMFillForm.banned)
            return
        caption = '' if message.caption is None else message.caption
        if caption != '':
            add_note(last_num + 1, message.caption)

        try:
            if check_new_user(message.from_user.id):
                await message.answer(replicas['warning'])
            note = '' if (message.caption is None or message.caption.replace('/anon', '').strip() == '') else f'\nПодпись: <i>"{message.caption.replace("/anon", "")}"</i>'
            if message.caption is None or '/anon' not in message.caption:
                text = '🙋🏼‍♀️ Выкладываем в канал'
            else:
                text = '🙅🏼‍♀️ Не выкладываем в канал'
            await message.answer(text=f'{random.choice(emoji_lol)} Давай проверим!{note}\n<b>{text}</b>\n\nПравильно?', reply_markup=confirm_keyboard(last_num + 1))
        except Exception as e:
            await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! Код 12\n{str(e)}')
        return


    if message.caption is not None:
        await message.answer(
            text=f'Ты прислал фото с заметкой: <i>{message.caption.replace("/anon", "").strip()}</i>. Оцени фото, которое ты скинул',
            reply_markup=get_rates_keyboard(last_num + 1, 0))
        add_note(last_num + 1, message.caption)
    else:
        await message.answer(
            text='Оцени фото, которое ты скинул',
            reply_markup=get_rates_keyboard(last_num + 1, 0))
    await state.set_state(FSMFillForm.rating)
    add_current_state(message.from_user.id, -1, message.from_user.username)


@dp.message(F.text == 'Статистика 📊', ~StateFilter(FSMFillForm.rating))
async def stat_photo(message: Message, state: FSMContext):
    result = check_id(message.from_user.id, message.from_user.username)
    if not result[0]:
        if result[1] == -1:
            await message.answer(random.choice(emoji_banned) + ' ' + random.choice(replicas['banned']).replace('$', '"'),
                                 reply_markup=ReplyKeyboardRemove())
            await state.set_state(FSMFillForm.banned)
            return
        not_incel_rates = get_avgs_not_incel(message.from_user.id)
        if len(not_incel_rates) > 5:
            async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action='upload_photo'):
                user_id = message.from_user.id
                get_statistics_not_incel(user_id)
                photo = InputMediaPhoto(media=FSInputFile(f'myplot_{user_id}2.png'), caption='График')
                photo2 = InputMediaPhoto(media=FSInputFile(f'myplot_{user_id}.png'), caption='Гистограмма')
                media = [photo, photo2]
                await bot.send_media_group(media=media, chat_id=message.from_user.id)
                os.remove(f'myplot_{user_id}.png')
                os.remove(f'myplot_{user_id}2.png')
        else:
            await message.answer(text=f'📶 Пришли <b>более 5 фото</b>, чтобы получить статистику\nТебе осталось прислать {6 - len(not_incel_rates)}', reply_markup=get_keyboard(message.from_user.id))
        return
    if len_photos_by_username(message.from_user.username) > 0:
        async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action='upload_photo'):
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
        average = get_avg_rate(message.from_user.id)
        avg = ''
        if average is not None:
            avg_float = average[0] / average[1]
            avg = f'\nCредняя оценка: <b>{"{:.2f}".format(avg_float)}</b> ' + emoji[round(avg_float)]
        await message.answer(text=f'Твое последнее фото оценили {votes}/{users} человек ' + avg)
    else:
        await message.answer(text='Ты еще не присылал никаких фото')


@dp.message(F.text == 'Изменить последнюю оценку ✏️', ~StateFilter(FSMFillForm.rating))
async def change_last_rate(message: Message, state: FSMContext):
    result = check_id(message.from_user.id, message.from_user.username)
    if not result[0]:
        if result[1] == -1:
            await message.answer(random.choice(emoji_banned) + ' ' + random.choice(replicas['banned']).replace('$', '"'),
                                 reply_markup=ReplyKeyboardRemove())
            await state.set_state(FSMFillForm.banned)
        await message.answer('Бля, иди нахуй реально!', reply_markup=get_keyboard(message.from_user.id))
        return
    last_rate = get_last_rate(message.from_user.id)
    if last_rate == 0 or last_rate == 5:
        await message.answer(text='Ты не оценивал чужих фото')
        return
    async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action='upload_photo'):
        await bot.send_photo(chat_id=message.from_user.id, photo=get_photo_id_by_id(last_rate),
                             reply_markup=get_rates_keyboard(last_rate, 2), caption='Ну давай, переобуйся, тварь')


@dp.message(F.text == 'Настройки ⚙️', F.from_user.id.in_(get_users()))
async def settings_button(message: Message):
    user_id = message.from_user.id
    if user_id not in get_admins():
        await message.answer(text='Извини, ты больше не админ', reply_markup=basic_keyboard)
        return
    await message.answer(text=get_text_of_settings(message.from_user.id), disable_web_page_preview=True,
                         reply_markup=get_admin_keyboard(user_id))

@dp.message(StateFilter(FSMFillForm.sendDM))
async def send_dm_func(message: Message, state: FSMContext):
    if current_dm_id.get(message.from_user.id, 0) == 0:
        await message.answer(text='Произошла ошибка', reply_markup=get_keyboard(message.from_user.id))
        await state.clear()
        return
    if current_dm_id.get(message.from_user.id, 0) == -1:
        current_dm_id[message.from_user.id] = 0
        await state.clear()
        not_incel_ids: set = get_not_incel()
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
        incels: set = get_users()
        successfully_sent = 0
        for id_local in incels:
            try:
                await bot.copy_message(chat_id=id_local, message_id=message.message_id,
                                       from_chat_id=message.chat.id)
                successfully_sent += 1
            except Exception as e:
                pass
        await message.answer(text=f'Сообщение отправлено {successfully_sent} инцелам')
        return
    if current_dm_id.get(message.from_user.id, 0) == -3:
        current_dm_id[message.from_user.id] = 0
        await state.clear()
        incels: set = get_users()
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
        await message.answer(text=f'Сообщение отправлено {successfully_sent} инцелам')
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
    await message.answer('я знаю', reply_to_message_id=message.message_id)


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
    result = check_id(message.from_user.id, message.from_user.username)
    if not result[0] and result[1] != -1:
        if message.text:
            await bot.send_message(chat_id=972753303, text=f'<i>@{message.from_user.username}:</i>\n"{message.text}"', disable_notification=True)
        else:
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
        await message.answer(text=random.choice(replicas.get('unknown', hz_answers)).replace('$', '"'),
                             reply_markup=get_keyboard(message.from_user.id), disable_web_page_preview=True)
    else:
        await message.answer(text=random.choice(hz_answers), reply_markup=not_incel_keyboard)


@dp.callback_query()
async def any_callback(callback: CallbackQuery):
    print(callback)


async def weekly_tierlist(user=972753303):
    try:
        async with ChatActionSender(bot=bot, chat_id=972753303, action='upload_document'):
            doc = InputMediaDocument(media=FSInputFile("slutsDB.db"))
            doc2 = InputMediaDocument(media=FSInputFile("usersDB.db"))
            doc3 = InputMediaDocument(media=FSInputFile("weekly.db"))
            doc4 = InputMediaDocument(media=FSInputFile("weekly_info.db"))
            doc5 = InputMediaDocument(media=FSInputFile("admins.db"))
            doc6 = InputMediaDocument(media=FSInputFile("statham.db"),
                                      caption=f'Бэкап <i>{datetime.datetime.now().date()}</i>')
            await bot.send_media_group(media=[doc, doc2, doc3, doc4, doc5, doc6], chat_id=972753303)
    except Exception as e:
        await bot.send_message(chat_id=972753303, text=f'Произошла ошибка при отправке файлов для бэкапа\n{e}')
    async with ChatActionSender(bot=bot, chat_id=972753303):
        d = get_weekly_db()
        new_d = {}
        cnt = 1
        for key, values in d.items():
            for value in values:
                if value[:4]=='http':
                    try:
                        response = requests.get(value)
                        if response.status_code == 200:
                            with open(f"test_{cnt}.jpg", "wb") as file:
                                file.write(response.content)
                    except Exception as e:
                        await bot.send_message(chat_id=972753303, text=f'Произошла ошибка! Код 13\n{e}')
                else:
                    f = await bot.get_file(value)
                    f_path = f.file_path
                    await bot.download_file(f_path, f"test_{cnt}.jpg")
                new_d[key] = [f"test_{cnt}.jpg"] + new_d.get(key, [])
                cnt += 1
        image_path = Path(f"test_{cnt}.jpg").resolve()
        try:
            res = draw_tier_list(new_d)
        except Exception as e:
            await bot.send_message(chat_id=972753303, text=f'Ошибка при создании тир листа\n{e}')
        for i in range(1, cnt):
            try:
                os.remove(f"test_{i}.jpg")
            except Exception as e:
                image_path = Path(f"test_{i}.jpg").resolve()
                await bot.send_message(chat_id=972753303, text=f'{e}\nПапка, где должны удалиться файлы: {image_path}')
        if get_weekly(972753303):
            try:
                media = []
                for path in res[1]:
                    capt = '<b>тир лист ❤️</b>'
                    media.append(InputMediaPhoto(media=path, caption=capt))
                await bot.send_media_group(chat_id=channel_id, media=media)
            except:
                await bot.send_message(chat_id=972753303, text=f'{e}\nПапка, где должен быть тирлист: {image_path}')
        else:
            await bot.send_message(chat_id=user, text='Тир лист отключен')
        try:
            client = yadisk.Client(token=ya_token)
            with client:
                cnt = 0
                for path in res[1]:
                    client.upload(path.replace('_compressed', ''), f"/incel/tier-list_{datetime.datetime.now().date()}-{cnt}.png", overwrite=True)
                    cnt+=1
            await bot.send_message(chat_id=user, text=f'Залил тир лист в ебейшем качестве <b><a href="https://disk.yandex.ru/d/0fhOxQsjp4yqSQ">сюда</a></b>\n\nБыло использовано <b>{res[0]}</b> фоток', disable_web_page_preview=True)
        except Exception as e:
            image_path = Path("tier_list.png").resolve()
            await bot.send_message(chat_id=972753303, text=f'{e}\nПапка, где должен быть тирлист: {image_path}')
        for path in res[1]:
            os.remove(path.replace('_compressed', ''))
            os.remove(path)


async def notify():
    for user in get_users():
        q = get_queue(user)
        if get_current_state(user) == -1:
            await bot.send_message(text='Заверши отправку фото, сука 🤬. Ты можешь оценить своё же фото, долбоеб?')
            continue
        if len(q) == 0:
            continue
        if states_users.get(user, None) is None or states_users[user] + datetime.timedelta(
                hours=1) < datetime.datetime.now():
            await bot.send_message(chat_id=user, text='Напоминание:\n\n<b>оцени фото, тварь 🤬</b>',
                                   reply_markup=get_keyboard(user))
            states_users[user] = datetime.datetime.now()


async def main():
    scheduler: AsyncIOScheduler = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))
    scheduler.add_job(notify, trigger='cron', hour='9-22/6', minute=0)
    scheduler.add_job(weekly_tierlist, trigger=CronTrigger(day_of_week='sun', hour=20, minute=0))

    day_of_week_list = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    for admin in get_admins():
        sets = get_settings(admin)
        days = get_weekdays(admin)
        for i in days:
            trigger = CronTrigger(day_of_week=day_of_week_list[i - 1], hour=int(sets[4]), minute=int(sets[5]))
            scheduler.add_job(notify_admin, trigger=trigger, args=(admin,))

    scheduler.start()
    await dp.start_polling(bot)


if __name__ == '__main__':
    print('Бот запущен')
    asyncio.run(main())
