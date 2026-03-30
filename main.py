import asyncio
import os
import re
import time
import unicodedata
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
ADMIN_ID = 807986999

# ===== STRICTNESS LEVELS =====
# 1 - Mild:     obvious company names + grades only
# 2 - Normal:   + roles + basic processes
# 3 - Strict:   + technologies + tools
# 4 - Harsh:    + DevOps + cloud + architecture
# 5 - Nuclear:  everything, including slang

BAN_LEVELS = {
    1: [
        # Компанії
        "софт", "софти", "софтах", "softserve", "софтсерв", "циско", "cisco", "епам", "epam",
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
        "перф", "перформанс", "performance review", "перфревю", "перф ревю",
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
    ],
}

BAD_WORDS = [
    # мат українською
    "бля", "блять", "бляд", "блядь", "сука", "суки", "суку",
    "їбать", "їбаний", "єбать", "єбаний", "йобаний", "йобані",
    "пізда", "пізді", "піздець", "піздюк", "піздити",
    "хуй", "хуя", "хуйня", "хуйло", "нахуй", "похуй",
    "залупа", "залупу", "мудак", "мудаки", "мудила",
    "їбало", "довбойоб", "довбойобе",
    "шльоха", "шльохи", "шалава", "курва", "курви",
    "ублюдок", "ублюдки", "падло", "падлюка",
    "гандон", "гандони", "підарас", "підараси",
    "чмо", "чмошник", "чмошники", "сволота", "мерзота",
    "підар", "підари", "підарок", "підарки",
    # english
    "fuck", "fucker", "fucking", "fucked",
    "shit", "shithead", "bullshit",
    "bitch", "bastard", "asshole", "dickhead",
    "cunt", "prick", "twat", "slut", "whore", "nigger",
    "fag", "faggot", "cock", "douchebag", "motherfucker"
]

LEVEL_LABELS = {
    1: "🟢 чіл — компанії та посади",
    2: "🟡 стривожена капібара — ролі",
    3: "🟠 бомбастік сайдай — мови та інструменти",
    4: "🔴 залізна занавіса — девопс і хмари і вся байда",
    5: "☢️ чіхуахуа — анігіляція",
}

# ===== STATE =====
current_level = 5
karma = 0
last_insult_time = 0.0
INSULT_COOLDOWN = 5 * 60

KARMA_INSULTS = {
    -1:  "🦆 КРЯ!",
    -3:  "🦆 КРЯ! Вже {n} рази, Саша...",
    -5:  "🦆 КРЯ! П'ять! Йди програмуй десь інде!",
    -10: "🦆 КРЯ! Десять повідомлень про роботу. ДЕСЯТЬ. Качка розчарована.",
    -15: "🦆 КРЯ! Саша, ти хворий. Це вже {n} повідомлень. Звони лікарю.",
    -20: "🦆 КРЯ! {n} ПОВІДОМЛЕНЬ! КАЧКА ОГОЛОШУЄ НАДЗВИЧАЙНИЙ СТАН!",
    -30: "☢️ {n} ПОВІДОМЛЕНЬ. КАЧКА БІЛЬШЕ НЕ МОЖЕ. САША ТИ РОБОТ.",
    -50: "💀 {n}. П'ЯТДЕСЯТ. КАЧКА ПІШЛА З ЖИТТЯ. САША УБИВ КАЧКУ.",
}
KARMA_THRESHOLDS = sorted(KARMA_INSULTS.keys())

app = FastAPI()
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== HELPERS =====

def get_ban_list(level: int) -> list[str]:
    words = []
    for lvl in range(1, level + 1):
        words.extend(BAN_LEVELS[lvl])
    return words

def normalize(text: str) -> str:
    """Strip symbols/spaces between letters so д ж у н → джун"""
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[^\w]', '', text, flags=re.UNICODE)
    return text.lower()

def get_insult(k: int) -> str:
    applicable = [t for t in KARMA_THRESHOLDS if k <= t]
    key = applicable[-1] if applicable else KARMA_THRESHOLDS[0]
    return KARMA_INSULTS[key].format(n=abs(k))

# ===== CORE FILTER =====

async def check_and_delete(message: types.Message):
    global karma, last_insult_time

    if not message.text:
        return

    original_lower = message.text.lower()
    normalized = normalize(message.text)
    ban_list = get_ban_list(current_level)

    original_words = re.findall(r'\w+', original_lower)
    normalized_words = re.findall(r'\w+', normalized)
    all_words = list(dict.fromkeys(original_words + normalized_words))

    should_delete = False
    delete_reason = None
    matched_word = None

    # 1. bad words
    for word in all_words:
        match = process.extractOne(word, BAD_WORDS, scorer=fuzz.WRatio)
        if match:
            threshold = 92 if len(word) <= 3 else 85
            if match[1] > threshold:
                should_delete = True
                delete_reason = "badword"
                matched_word = word
                print(f"🤬 Swear: '{word}' matched '{match[0]}' ({match[1]:.1f}%)")
                break

    if not should_delete:
        for word in all_words:
            match = process.extractOne(word, ban_list, scorer=fuzz.WRatio)
            if match:
                threshold = 92 if len(word) <= 3 else 85
                if match[1] > threshold:
                    should_delete = True
                    delete_reason = "itword"
                    matched_word = word
                    print(f"🔥 IT word: '{word}' matched '{match[0]}' ({match[1]:.1f}%)")
                    break

    if not should_delete:
        multi_word_terms = [t for t in ban_list if ' ' in t]
        for term in multi_word_terms:
            if term in original_lower or term in normalized:
                should_delete = True
                delete_reason = "itword"
                matched_word = term
                print(f"🔥 Multi-word: '{term}' (exact)")
                break
            if fuzz.partial_ratio(term, original_lower) > 90:
                should_delete = True
                delete_reason = "itword"
                matched_word = term
                print(f"🔥 Multi-word: '{term}' (fuzzy)")
                break

    if not should_delete:
        return

    try:
        await message.delete()

        if delete_reason == "badword":
            await message.answer(f"🦆 НЕ МАТЮКАЙСЯ {matched_word.upper()}. КРЯ!")
        else:
            karma -= 1
            print(f"💀 Karma: {karma}")
            now = time.time()
            if now - last_insult_time >= INSULT_COOLDOWN:
                last_insult_time = now
                await message.answer(get_insult(karma))

    except Exception as e:
        print(f"Delete failed: {e}")

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
    await check_and_delete(message)


@dp.edited_message(lambda message: message.from_user.id in TARGET_IDS)
async def monitor_edited(message: types.Message):
    await check_and_delete(message)


@dp.message(F.text.startswith("/level"))
async def set_level(message: types.Message):
    global current_level
    if message.from_user.id != ADMIN_ID:
        await message.answer("🦆 Ти не качка. КРЯ!")
        return
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


@dp.message(F.text == "/karma")
async def show_karma(message: types.Message):
    if karma == 0:
        await message.answer("🦆 Карма чиста. Поки що.")
    elif karma >= -5:
        await message.answer(f"🦆 Карма Саші: {karma}. Качка стежить.")
    elif karma >= -15:
        await message.answer(f"🟡 Карма Саші: {karma}. Качка незадоволена.")
    elif karma >= -30:
        await message.answer(f"🔴 Карма Саші: {karma}. Качка в люті.")
    else:
        await message.answer(f"☢️ Карма Саші: {karma}. Качка мертва всередині.")


@dp.message(F.text == "/forgive")
async def forgive(message: types.Message):
    global karma
    if message.from_user.id != ADMIN_ID:
        await message.answer("🦆 Тільки головна качка може пробачати. КРЯ!")
        return
    old = karma
    karma = 0
    await message.answer(f"✅ Карму скинуто. Було: {old}. Саша отримав другий