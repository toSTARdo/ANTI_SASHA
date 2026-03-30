import asyncio
import os
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from fastapi import FastAPI
import time

app = FastAPI()

@app.get("/ping")
async def ping():
    return {
        "status": "online",
        "timestamp": time.time(),
        "message": "pong"
    }
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables!")
TARGET_USER_ID = int(os.getenv("TARGET_USER_ID"))
if not TARGET_USER_ID:
    raise ValueError("No TARGET_USER_ID found in environment variables!")

BAN_LIST = {"badword1", "badword2", "spam", "scam"}

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(F.from_user.id == TARGET_USER_ID)
async def monitor_user(message: types.Message):
    text_words = set(re.findall(r'\w+', message.text.lower())) if message.text else set()
    
    if not BAN_LIST.isdisjoint(text_words):
        try:
            await message.delete()
            print(f"Deleted message from {TARGET_USER_ID} containing banned words.")
        except Exception as e:
            print(f"Failed to delete message: {e}")

async def main():
    print("Bot is polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import re
    asyncio.run(main())