import datetime
import random

import aiosqlite

DB_NAME = "/home/ubuntu/gk-bot/database.db"

SPECIALITIES = [
    "Стрелок",
    "Пулемётчик",
    "Разведчик",
    "Связист",
    "Санитар",
    "Сапёр",
    "Кавалерист",
    "Артиллерист"
]

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # Добавляем chat_id и делаем связку (user_id, chat_id) уникальной
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER,
            chat_id INTEGER,
            username TEXT,
            name TEXT,
            messages INTEGER DEFAULT 0,
            rank TEXT DEFAULT 'Рядовой 2 класса',
            jap_rank TEXT DEFAULT 'нитохэй',
            tsurumi_rep INTEGER DEFAULT 0,
            enlist_date TEXT,
            speciality TEXT,
            last_speciality_change TEXT,
            PRIMARY KEY (user_id, chat_id)
        )
        """)
        await db.commit()

async def get_user(user_id, chat_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ? AND chat_id = ?",
            (user_id, chat_id)
        )
        return await cursor.fetchone()

from datetime import datetime

async def add_user(user_id, chat_id, username):
    enlist_date = datetime.now().strftime("%d.%m.%Y")
    speciality = random.choice(SPECIALITIES)

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """INSERT OR IGNORE INTO users 
            (user_id, chat_id, username, enlist_date, speciality) 
            VALUES (?, ?, ?, ?, ?)""",
            (user_id, chat_id, username, enlist_date, speciality)
        )
        await db.commit()

async def update_messages(user_id, chat_id, messages, rank, jap_rank):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET messages = ?, rank = ?, jap_rank = ? WHERE user_id = ? AND chat_id = ?",
            (messages, rank, jap_rank, user_id, chat_id)
        )
        await db.commit()

async def update_name(user_id, chat_id, name):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET name = ? WHERE user_id = ? AND chat_id = ?",
            (name, user_id, chat_id)
        )
        await db.commit()

async def update_tsurumi_rep(user_id, chat_id, tsurumi_rep):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
             "UPDATE users SET tsurumi_rep = ? WHERE user_id = ? AND chat_id = ?",
            (tsurumi_rep, user_id, chat_id)
        )
        await db.commit()

async def update_speciality(user_id, chat_id, speciality):
    last_change = datetime.now().strftime("%Y-%m-%d")

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """UPDATE users 
            SET speciality = ?, last_speciality_change = ?
            WHERE user_id = ? AND chat_id = ?""",
            (speciality, last_change, user_id, chat_id)
        )
        await db.commit()