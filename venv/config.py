import asyncio
import calendar
import datetime
import io
import json
import os
import time
import shutil
import threading
import concurrent.futures
import aiohttp
import aiofiles

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
    get_not_incel, check_new_user, change_queue, get_unban, add_new_birthday, get_birthday, get_top_incels, sync_get_users
from sql_photos import *
from graphics import *
from weekly_rates import *
from tier_list import draw_tier_list
from statham import get_randQuote, insert_quote, get_statham_db, del_quote
from administrators import *
from parser import *
from cv_color import *
from watermark import *
from vova_function import *

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
emoji_lol = ['🍏', '🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🫐', '🍈', '🍒', '🍑', '🥭', '🍍', '🥥', '🥝', '🍅', '🍆', '🥑', '🫛', '🥦', '🥬', '🥒', '🌶', '🫑',
             '🌽', '🥕', '🫒', '🧄', '🧅', '🥔', '🍠', '🫚', '🥐', '🥯', '🍞', '🥖', '🥨', '🧀', '🥚', '🍳', '🧈', '🥞', '🧇', '🌭', '🍔', '🍟', '🍕', '🥪', '🥙', '🧆',
             '🌮', '🌯', '🫔', '🥗', '🥘', '🫕', '🥫', '🍝', '🍜', '🍲', '🍛', '🍣', '🍱', '🥟', '🦪', '🍤', '🍙', '🍚', '🍘', '🍥', '🥠', '🥮', '🍡', '🍧', '🍨', '🍦',
             '🥧', '🧁', '🍰', '🎂', '🍮', '🍭', '🍬', '🍫', '🍿', '🍩', '🍪', '🌰', '🍯', '🥛', '🫗', '🍼', '🫖', '☕️', '🍵', '🧃', '🥤', '🧋', '🍶', '🍾', '🧊', '⚽️',
             '🏀', '🏈', '⚾️', '🥎', '🎾', '🏐', '🏉', '🥏', '🎱', '🪀', '🏓', '🏸', '🎧', '🎫', '🎟', '🎲', '♟', '🎯', '🎳', '🎮', '🎰', '🧩', '🗾', '🎑', '🏞', '🌅',
             '🌄', '🌠', '🎇', '🎆', '🌇', '🌆', '🏙', '🌃', '🌌', '🌉', '🌁', '💣', '🧨', '💊', '🎁', '🎈', '🛍', '🪩', '📖', '📚', '📙', '📘', '📗', '📕', '📒', '📔',
             '📓', '📰', '🗞', '🧵', '👚', '👕', '👖', '👔', '💼', '👜', '🎩', '🧢', '👒', '🎓', '🧳', '👓', '🕶', '🥽', '🌂', '💍', '🐶', '🐭', '🐹', '🐰', '🦊', '🐻',
             '🐼', '🐻‍❄️', '🐨', '🐯', '🦁', '🐸', '🐵', '🙈', '🙉', '🙊', '🐒', '🐱', '🐔', '🐧', '🐦', '🐤', '🐣', '🐥', '🪿', '🦆', '🐦‍⬛️', '🦅', '🦉', '🦇', '🐺',
             '🐴', '🦄', '🐝', '🦋', '🦖', '🦕', '🐙', '🦑', '🪼', '🦐', '🐬', '🐋', '🐳', '🦈', '🦭', '🪽', '🕊', '🪶', '🐉', '🐲', '🦔', '🐁', '🌵', '🎄', '🌲', '🌳',
             '🌴', '🪵', '🌱', '🌿', '☘️', '🍀', '🎍', '🪴', '🎋', '🍃', '🍂', '🍁', '🪺', '🐚', '🪸', '🪨', '🌾', '💐', '🌷', '🌹', '🥀', '🪻', '🪷', '🌺', '🌸', '🌼',
             '🌻', '🌎', '🌍', '🌏', '🪐', '💫', '⭐️', '✨', '💥', '🔥', '🌪', '🌈', '☀️', '🌤', '⛅️', '🌥', '☁️', '☃️', '⛄️', '💨', '☂️', '🌊', '🌫']
emoji_banned = '⛔❗🤯😳❌⭕🛑📛🚫💢🚷📵🔴🟥💣🗿🐓🙊🙉🙈🐷🫵🥲🙁😕😟😔😞😧😦😯🙄😵💀🚨😐'
dice_points = {'🎲': 6, '🎯': 6, '🎳': 6, '🏀': 4, '⚽': 3, '🎰': 64}
replicas = {}
with open(f'{os.path.dirname(__file__)}/DB/replicas.txt', 'r', encoding='utf-8') as file:
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

rate3 = {
    10: '#Богиня',
    9: '#Шоколадная',
    8: '#Вашей_маме_зять_не_нужен<a href="https://t.me/RatePhotosBot">?</a>',
    7: '#Прелесть',
    6: '#Найс',
    5: '#Мило',
    4: '#На_любителя',
    3: '#Сомнительно',
    2: '#Cтрашное',
    1: '#Фу',
    0: '#Кандидат_от_оппозиции'
}


def encrypt(num: float):
    num = round((num), 2)
    whole_part = int(num)
    decimal_part = round((num - whole_part), 2)
    decimal_part = '{:.2f}'.format(decimal_part)
    return f"r{whole_part}p{decimal_part[2:]}"
