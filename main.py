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
TARGET_IDS = {
    int(os.getenv("TARGET_USER_ID", 0)),
    807986999
}

# ===== STRICTNESS LEVELS =====
# 1 - Mild:     obvious company names + grades only
# 2 - Normal:   + roles + basic processes
# 3 - Strict:   + technologies + tools
# 4 - Harsh:    + DevOps + cloud + architecture
# 5 - Nuclear:  everything, including slang

BAN_LEVELS = {
    1: [
        # Компанії
        "софти", "софтах", "softserve", "циско", "cisco", "епам", "epam",
        "globallogic", "глобал", "люксофт", "luxoft", "ciklum", "сіклум",
        "grammarly", "грамарлі", "playtika", "wargaming", "intellias",
        # Грейди
        "джун", "джуни", "джунів", "джуніор", "junior",
        "мідл", "мідли", "мідлів", "middle",
        "сеньйор", "сеньйори", "сеньйорів", "senior",
        "400", "300", "500",
    ],
    2: [
        # Ролі
        "девелопер", "developer", "розробник", "розробники", "розробників",
        "програміст", "програмісти", "програмістів", "програмую", "програмував",
        "інженер", "інженери", "інженерів", "engineer",
        "архітектор", "архітектори", "архітекторів", "architect",
        "спеціаліст", "спеціалісти", "спеціалістів",
        "аналітик", "аналітики", "analyst",
        "лід", "тімлід", "teamlead", "techlead", "техлід",
        "менеджер", "manager", "пм", "pm", "продакт", "product owner",
        "скрам-мастер", "scrummaster", "qa", "тестувальник", "tester",
        "девопс", "devops", "sre", "fullstack", "backend", "frontend",
        # Базові процеси
        "фіча", "фічу", "фіч", "feature",
        "тест", "тестування", "тестувати", "testing",
        "ревю", "review", "code review",
        "спринт", "sprint", "таск", "task", "тікет", "ticket",
        "баг", "бага", "багів", "debug", "фікс", "fix",
        "деплой", "deploy", "реліз", "release",
        "стендап", "standup", "daily", "мітинг", "meeting",
        "таска", "taska", "таски", "tasks", "point", "поінт", "story point",
        "перф", "перформанс", "performance review", "перфревю", "перф ревю"
    ],
    3: [
        # Мови програмування
        "джава", "java", "котлін", "kotlin",
        "пайтон", "python", "джанго", "django", "flask", "fastapi",
        "джаваскрипт", "javascript", "typescript",
        "реакт", "react", "ангулар", "angular", "vue",
        "ноджс", "nodejs", "node",
        "го", "golang", "раст", "rust",
        "сі шарп", "c#", "dotnet", ".net",
        "php", "ruby", "rails", "swift",
        "html", "css", "sass", "tailwind",
        # Бази даних
        "postgres", "mysql", "mongo", "mongodb", "redis",
        "elasticsearch", "cassandra", "oracle", "sql", "nosql",
        # Інструменти
        "гіт", "git", "github", "gitlab", "bitbucket",
        "слак", "slack", "джира", "jira", "конфлюенс", "confluence",
        "постман", "postman", "swagger", "figma", "фігма",
        "vs code", "intellij", "pycharm",
        "сентрі", "sentry", "datadog",
    ],
    4: [
        # DevOps / Cloud
        "докер", "docker", "контейнер", "container",
        "кубер", "kubernetes", "k8s", "helm",
        "terraform", "ansible",
        "aws", "amazon", "azure", "gcp", "google cloud",
        "ec2", "s3", "lambda", "serverless",
        "jenkins", "github actions", "gitlab ci",
        "prometheus", "grafana", "nginx",
        # Архітектура
        "мікросервіс", "microservice", "монолит", "monolith",
        "апі", "api", "рест", "rest", "graphql", "grpc",
        "кафка", "kafka", "rabbitmq", "websocket",
        "кеш", "cache", "cdn", "балансер", "load balancer",
        "oauth", "jwt", "токен", "auth",
        "шардинг", "sharding", "реплікація", "replication",
        # ML / AI
        "machine learning", "ml", "ai", "нейромережа", "neural network",
        "chatgpt", "gpt", "llm", "pytorch", "tensorflow",
        "датасет", "dataset", "embedding", "ембединг",
        # Методології
        "agile", "scrum", "kanban", "okr", "kpi", "roadmap", "роадмап",
        "рефакторинг", "refactor", "технічний борг", "tech debt", "легасі", "legacy",
        "пайплайн", "pipeline", "cicd", "ci/cd",
        "стейджинг", "staging", "прод", "production",
        "постмортем", "postmortem", "ретро", "retrospective",
        "моніторинг", "monitoring", "алерт", "alert", "інцидент", "incident",
    ],
    5: [
        # HR / офіс
        "офер", "оффер", "offer", "онбординг", "onboarding",
        "перф", "перформанс", "performance review",
        "бенефіти", "benefits", "страховка",
        "акції", "equity", "rsu", "бонус", "bonus", "рейз", "raise",
        "корпоратив", "team building", "тімбілдінг",
        "аутсорс", "outsource", "аутстаф", "remote", "ремоут", "гібрид",
        "релокейт", "relocation", "хакатон", "hackathon", "конференція",
        # Сленг / решта
        "імплементувати", "імплементація", "implementation",
        "інтегрувати", "інтеграція", "integration",
        "оптимізувати", "оптимізація", "optimization",
        "скейлити", "скейл", "scale",
        "дедлайн", "deadline", "овертайм", "overtime",
        "легасі", "legacy", "скоуп", "scope",
        "воркфлоу", "workflow", "юзкейс", "use case",
        "метрика", "metrics", "аналітика", "analytics",
        "логи", "logs", "трейс", "trace",
        "прототип", "prototype", "mvp", "пілот",
        "шипати", "шипнути", "шипнув", "шипінг",
        "бізнес логіка", "business logic",
        "фічафлаг", "feature flag", "a/b тест", "a/b testing",
        "естімейт", "estimate", "поінти", "story point",
        "епік", "epic", "юзер сторі", "user story",
        "груммінг", "grooming", "рефайнмент", "refinement",
        "колл", "call", "синк", "sync", "one-on-one",
        "юзер", "user", "клієнт", "client", "кастомер", "customer",
        "вимоги", "requirements", "специфікація", "spec",
    ]
}

def get_ban_list(level: int) -> list[str]:
    """Returns cumulative ban list up to the given level (1–5)."""
    words = []
    for lvl in range(1, level + 1):
        words.extend(BAN_LEVELS[lvl])
    return words

# ===== STATE =====
current_level = 3  # default level
app = FastAPI()
bot = Bot(token=TOKEN)
dp = Dispatcher()

LEVEL_LABELS = {
    1: "🟢 чіл — компанії та посади",
    2: "🟡 стривожена капібара — ролі",
    3: "🟠 бомбастік сайдай — мови та інструменти",
    4: "🔴 залізна занавіса — девопс і хмари і вся байда",
    5: "☢️ чіхуахуа — анігіляція",
}

# ===== HANDLERS =====

@dp.message(F.new_chat_members)
async def welcome_new_members(message: types.Message):
    for member in message.new_chat_members:
        bot_info = await bot.get_me()
        if member.id == bot_info.id:
            await message.answer(
                f"🦆 Антисашороботобот!\n"
                f"Я тут шоб знищувати робочий спам.\n"
                f"Я тут закон. КРЯ!\n\n"
                f"Поточний рівень: {LEVEL_LABELS[current_level]}\n"
                f"Змінити: /level 1-5"
            )
        else:
            await message.answer(f"Вітаю з відпустки, {member.full_name}! 🦆")


@dp.chat_member(ChatMemberUpdatedFilter(member_status_changed=(KICKED | LEFT)))
async def on_user_left(event: ChatMemberUpdated):
    if event.new_chat_member.user.id in TARGET_IDS:
        print(f"👋 TARGET GONE: {event.new_chat_member.user.full_name}")
        await bot.send_message(event.chat.id, "🦆 Відбулося правосуддя. КРЯ!")


@dp.message(lambda message: message.from_user.id in TARGET_IDS)
async def monitor_users(message: types.Message):
    if not message.text:
        return

    ban_list = get_ban_list(current_level)
    text_words = re.findall(r'\w+', message.text.lower())
    should_delete = False

    for word in text_words:
        match = process.extractOne(word, ban_list, scorer=fuzz.WRatio)
        if match and match[1] > 85:
            should_delete = True
            print(f"🔥 [{current_level}] Deleted: '{word}' matched '{match[0]}' ({match[1]:.1f}%)")
            break

    if should_delete:
        try:
            await message.delete()
            await message.answer("🦆 КРЯ!")
        except Exception as e:
            print(f"Delete failed: {e}")


@dp.message(F.text.startswith("/level"))
async def set_level(message: types.Message):
    global current_level
    parts = message.text.strip().split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Usage: /level 1-5")
        return
    lvl = int(parts[1])
    if lvl not in range(1, 6):
        await message.answer("⚠️ Level must be between 1 and 5.")
        return
    current_level = lvl
    await message.answer(f"✅ Рівень строгості змінено: {LEVEL_LABELS[current_level]}")


@dp.message(F.text == "/status")
async def status(message: types.Message):
    ban_list = get_ban_list(current_level)
    await message.answer(
        f"🦆 Статус качки:\n"
        f"Рівень: {LEVEL_LABELS[current_level]}\n"
        f"Слів у бан-листі: {len(ban_list)}\n\n"
        f"Змінити рівень: /level 1-5"
    )


@app.get("/")
async def root():
    return {"message": "Качка копаюча готова!"}


@app.get("/ping")
async def ping():
    return {"status": "online", "timestamp": time.time(), "level": current_level}


async def main():
    config = Config(app=app, host="0.0.0.0", port=8000, loop="asyncio")
    server = Server(config)
    await asyncio.gather(
        dp.start_polling(bot),
        server.serve()
    )

if __name__ == "__main__":
    if not TOKEN:
        print("❌ Error: BOT_TOKEN2 is missing!")
    else:
        asyncio.run(main())