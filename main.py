import asyncio
import os
import re
import time
from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, KICKED, LEFT
from aiogram.types import ChatMemberUpdated
from uvicorn import Config, Server
from rapidfuzz import process, fuzz

TOKEN = os.getenv("BOT_TOKEN2")
TARGET_USER_ID = int(os.getenv("TARGET_USER_ID", 0))

BAN_LIST = [
    "софти", "софтах", "400", "джун", "джуни", "джунів", "мідл", "мідли", "мідлів", 
    "сеньйор", "сеньйори", "сеньйорів", "циско", "softserve", "cisco", "фіча", 
    "тест", "тестування", "тестувати", "фічу", "фіч", "ревю", "девелопер", 
    "розробник", "розробники", "розробників", "програміст", "програмісти", 
    "програмістів", "інженер", "інженери", "інженерів", "архітектор", 
    "архітектори", "архітекторів", "спеціаліст", "спеціалісти", "спеціалістів", 
    "аналітик", "аналітики", "лід", "тімлід"
]

if not TOKEN or not TARGET_USER_ID:
    raise ValueError("Missing BOT_TOKEN2 or TARGET_USER_ID in ENV")

app = FastAPI()
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(F.new_chat_members)
async def welcome_new_members(message: types.Message):
    for member in message.new_chat_members:
        bot_info = await bot.get_me()
        if member.id == bot_info.id:
            await message.answer("🦆 Антисашороботобот!\nЯ тут шоб знищувати робочий спам.\nЯ тут закон. КРЯ!")
        else:
            await message.answer(f"Вітаю з відпустки, {member.full_name}! 🦆")

@dp.chat_member(ChatMemberUpdatedFilter(member_status_changed=(KICKED | LEFT)))
async def on_user_left(event: ChatMemberUpdated):
    if event.new_chat_member.user.id == TARGET_USER_ID:
        print(f"👋 TARGET GONE: {event.new_chat_member.user.full_name} has left or was kicked from the chat.")
        
        await bot.send_message(event.chat.id, "🦆 Відбулося правосуддя. КРЯ!")

@dp.message(F.from_user.id == TARGET_USER_ID)
async def monitor_user(message: types.Message):
    if not message.text:
        return
    
    text_words = re.findall(r'\w+', message.text.lower())
    should_delete = False
    
    for word in text_words:
        match = process.extractOne(word, BAN_LIST, scorer=fuzz.WRatio)
        if match and match[1] > 85:
            should_delete = True
            print(f"🔥 Deleted: '{word}' matched '{match[0]}' with {match[1]:.1f}% confidence.")
            break

    if should_delete:
        try:
            await message.delete()
            await message.answer("🦆 КРЯ!")
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