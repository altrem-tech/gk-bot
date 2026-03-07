import asyncio
from datetime import timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv
import os

from aiogram.filters import Command

from database import *

load_dotenv()
TOKEN = os.environ.get("BOT_TOKEN")

bot = Bot(TOKEN)
dp = Dispatcher()

RANKS = [
    ("Рядовой 2 класса", "нитохэй", 0),
    ("Рядовой 1 класса", "иттохэй", 200),
    ("Старший рядовой", "дзётохэй", 450),
    ("Ефрейтор", "хэйтё", 800),
    ("Сержант", "гунсо", 1200),
    ("Старшина", "сотё", 2000),
    ("Младший лейтенант", "дзюнъи", 3000),
    ("Лейтенант", "шёи", 4000),
    ("Старший лейтенант", "чуи", 6000),
    ("Капитан", "тайи", 8000),
    ("Майор", "сёса", 12000),
    ("Подполковник", "тюса", 20000),
    ("Полковник", "тайса", 40000)
]

def get_rank(messages):
    current_rank = RANKS[0]

    for rank in RANKS:
        if messages >= rank[2]:
            current_rank = rank
        else:
            break

    return current_rank


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📄 Рапорт", callback_data="menu_profile")],
            [InlineKeyboardButton(text="🪖 Сменить специальность", callback_data="menu_speciality")],
            [InlineKeyboardButton(text="✏️ Сменить имя", callback_data="menu_newname")],
            [InlineKeyboardButton(text="♻️ Сбросить имя", callback_data="menu_resetname")]
        ]
    )

@dp.message(Command("menu"))
async def open_menu(message: Message):
    await message.answer(
        "🏯 Меню 7-й дивизии",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "menu_profile")
async def menu_profile(callback: CallbackQuery):

    user = await get_user(callback.from_user.id, callback.message.chat.id)

    if not user:
        await add_user(callback.from_user.id, callback.message.chat.id, callback.from_user.username)
        user = await get_user(callback.from_user.id, callback.message.chat.id)

    name = user[3] if user[3] else callback.from_user.full_name
    messages_count = user[4]
    rank_rus = user[5]
    rank_jap = user[6]
    rep = user[7]
    enlist_date = user[8]
    speciality = user[9]

    progress = get_progress(messages_count)

    await callback.message.answer(
        profile_output(name, rank_rus, rank_jap, messages_count, rep, progress, enlist_date, speciality)
    )

    await callback.answer()

@dp.callback_query(F.data == "menu_speciality")
async def menu_speciality(callback: CallbackQuery):

    user = await get_user(callback.from_user.id, callback.message.chat.id)

    if not user:
        await add_user(callback.from_user.id, callback.message.chat.id, callback.from_user.username)
        user = await get_user(callback.from_user.id, callback.message.chat.id)

    last_change = user[10]

    if last_change:
        from datetime import datetime

        last_change_date = datetime.strptime(last_change, "%Y-%m-%d")
        now = datetime.now()

        if now - last_change_date < timedelta(days=7):

            remaining = 7 - (now - last_change_date).days

            await callback.message.answer(
                f"⚠️ Сменить специальность можно раз в 7 дней.\n"
                f"Осталось ждать: {remaining} дн."
            )

            await callback.answer()
            return

    await callback.message.answer(
        "🪖 Выберите новую специальность:",
        reply_markup=speciality_keyboard()
    )

    await callback.answer()

@dp.callback_query(F.data == "menu_newname")
async def menu_newname(callback: CallbackQuery):

    await callback.message.answer(
        "✏️ Напишите команду:\n\n"
        "/newname ваше_имя"
    )

    await callback.answer()

@dp.callback_query(F.data == "menu_resetname")
async def menu_resetname(callback: CallbackQuery):

    await update_name(callback.from_user.id, callback.message.chat.id, None)

    await callback.message.answer("♻️ Имя сброшено до стандартного.")

    await callback.answer()

@dp.message(Command("newname"))
async def set_name(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Формат записи:\n/newname новое_имя")
        return

    new_name = args[1]
    if len(new_name) > 20:
        await message.answer("Имя превышает допустимую длину.")
        return

    await update_name(message.from_user.id, message.chat.id, new_name)
    await message.answer(f"Имя успешно изменено. Текущее имя: {new_name}")


@dp.message(Command("resetname"))
async def reset_name(message: Message):
    await update_name(message.from_user.id, message.chat.id, None)
    await message.answer(f"Имя сброшено до стандартного.")

def speciality_keyboard():
    buttons = []

    for spec in SPECIALITIES:
        buttons.append(
            [InlineKeyboardButton(text=spec, callback_data=f"spec_{spec}")]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("speciality"))
async def choose_speciality(message: Message):
    user = await get_user(message.from_user.id, message.chat.id)

    if not user:
        await add_user(message.from_user.id, message.chat.id, message.from_user.username)
        user = await get_user(message.from_user.id, message.chat.id)

    last_change = user[10]

    if last_change:
        from datetime import datetime, timedelta

        last_change_date = datetime.strptime(last_change, "%Y-%m-%d")
        now = datetime.now()

        if now - last_change_date < timedelta(days=7):

            remaining = 7 - (now - last_change_date).days

            await message.answer(
                f"⚠️ Сменить специальность можно раз в 7 дней.\n"
                f"Осталось ждать: {remaining} дн."
            )
            return

    await message.answer(
        "🪖 Выберите новую специальность:",
        reply_markup=speciality_keyboard()
    )

@dp.callback_query(F.data.startswith("spec_"))
async def set_speciality(callback: CallbackQuery):

    speciality = callback.data.replace("spec_", "")

    await update_speciality(
        callback.from_user.id,
        callback.message.chat.id,
        speciality
    )

    await callback.message.edit_text(
        f"🪖 Специальность изменена:\n{speciality}"
    )

    await callback.answer()


@dp.message(F.reply_to_message)
async def reputation_system(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    user = await get_user(user_id, chat_id)
    if not user:
        await add_user(user_id, chat_id, message.from_user.username)
        user = await get_user(user_id, chat_id)

    text = message.text.lower()
    if text not in ["жиза", "+", "респект"]:
        return

    rep = user[7]

    if rep >= 15:
        return

    old_stars = rep // 3
    rep += 1
    new_stars = rep // 3

    target_id = message.reply_to_message.from_user.id

    await update_tsurumi_rep(target_id, chat_id, rep)

    if new_stars > old_stars:
        await message.answer(
            f"⭐ Солдат получил звезду доверия Цуруми!\n"
            f"Теперь: {reputation_stars(rep)}"
        )


@dp.message(F.text.startswith("рапорт"))
async def profile(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    user = await get_user(user_id, chat_id)
    if not user:
        await add_user(user_id, chat_id, message.from_user.username)
        user = await get_user(user_id, chat_id)

    name = user[3] if user[3] else message.from_user.full_name
    messages_count = user[4]
    rank_rus = user[5]
    rank_jap = user[6]
    rep = user[7]
    enlist_date = user[8]
    speciality = user[9]

    progress = get_progress(messages_count)

    await message.answer(
        profile_output(name, rank_rus, rank_jap, messages_count, rep, progress, enlist_date, speciality)
    )

def profile_output(name, rank, jap_rank, messages, tsurumi_reputation, progress_to_next_rank, enlist_date, speciality):
    indent = " "
    return f"""
    {indent}軍務報告 ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖
    7-я дивизия Имперской Армии
    ───────────
    🎖️ Имя бойца: {name} {jap_rank} доно\n
    Звание: {rank}
    Специальность: {speciality}
    Дата призыва: {enlist_date}\n
    
    Личный счётчик сообщений: {messages}
    Репутация у Цуруми: 
    {reputation_stars(tsurumi_reputation)}\n

    Приказы выполнять без вопросов.
    🏯 Прогресс к следующему званию: 
    {progress_bar(progress_to_next_rank)} {progress_to_next_rank}%
    ───────────
    Служба во славу дивизии.
    
    """

def reputation_stars(rep, max_stars=5):

    stars = rep // 3

    if stars > max_stars:
        stars = max_stars

    filled = "★" * stars
    empty = "☆" * (max_stars - stars)

    return filled + empty


def progress_bar(percent, length=10):
    filled_length = int(length * percent // 100)
    bar = "█" * filled_length + "-" * (length - filled_length)
    return bar

def get_progress(messages):
    for i in range(len(RANKS) - 1):
        current = RANKS[i]
        next_rank = RANKS[i + 1]

        if current[2] <= messages < next_rank[2]:
            span = next_rank[2] - current[2]
            progress = messages - current[2]

            percent = int(progress / span * 100)
            return percent

    return 100


@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    user = await get_user(user_id, chat_id)
    if not user:
        await add_user(user_id, chat_id, message.from_user.username)
        user = await get_user(user_id, chat_id)

    messages = user[4] + 1
    old_rank = user[5]

    rank_data = get_rank(messages)
    new_rank, new_jap_rank, _ = rank_data

    await update_messages(user_id, chat_id, messages, new_rank, new_jap_rank)

    name = user[3] if user[3] else message.from_user.full_name

    if new_rank != old_rank:
        await message.answer(
            f"🏅 {name} повышен!\n"
            f"Новое звание: {new_rank} ({new_jap_rank})"
        )

async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())