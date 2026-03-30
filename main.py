import asyncio
import os
import re
import time
from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types, F
from uvicorn import Config, Server

TOKEN = os.getenv("BOT_TOKEN2")
TARGET_USER_ID = int(os.getenv("TARGET_USER_ID", 0))
BAN_LIST = {"badword1", "badword2", "spam", "scam"}

if not TOKEN or not TARGET_USER_ID:
    raise ValueError("Missing BOT_TOKEN2 or TARGET_USER_ID in ENV")

app = FastAPI()
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(F.new_chat_members)
async def welcome_new_members(message: types.Message):
    for member in message.new_chat_members:
        if member.id == (await bot.get_me()).id:
            await message.answer(
                "🦆 Антисашороботобот!\n"
                "Я тут шоб знищувати робочий спам.\n"
                "Я тут закон. КРЯ!"
            )
        else:
            await message.answer(f"Вітаю з відпустки, {member.full_name}! 🦆")

@dp.message(F.from_user.id == TARGET_USER_ID)
async def monitor_user(message: types.Message):
    if not message.text: return
    text_words = set(re.findall(r'\w+', message.text.lower()))
    if not BAN_LIST.isdisjoint(text_words):
        try:
            await message.delete()
        except Exception as e:
            print(f"Delete failed: {e}")

@app.get("/ping")
async def ping():
    return {"status": "online", "timestamp": time.time()}

@app.get("/")
async def root():
    return {"message": "Качка копаюча готова!"}

async def main():
    config = Config(app=app, host="0.0.0.0", port=8000, loop="asyncio")
    server = Server(config)
    
    await asyncio.gather(
        dp.start_polling(bot),
        server.serve()
    )

if __name__ == "__main__":
    asyncio.run(main())