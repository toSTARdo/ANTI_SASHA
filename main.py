import asyncio
import os
import re
import time
import random
import unicodedata
from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, KICKED, LEFT
from aiogram.types import ChatMemberUpdated
from uvicorn import Config, Server
from rapidfuzz import process, fuzz

# ===== CONFIG =====
TOKEN = os.getenv("BOT_TOKEN2")
TARGET_IDS = {
    int(os.getenv("TARGET_USER_ID", 0)),
    807986999
}
ADMIN_ID = 807986999

# ===== BAN LEVELS =====
BAN_LEVELS = {
    1: [
        "софт", "софти", "софтах", "softserve", "софтсерв", "циско", "cisco", "епам", "epam",
        "globallogic", "глобал", "люксофт", "luxoft", "ciklum", "сіклум",
        "grammarly", "грамарлі", "playtika", "wargaming", "intellias",
        "джун", "джуни", "джунів", "джуніор", "junior",
        "мідл", "мідли", "мідлів", "middle",
        "сеньйор", "сеньйори", "сеньйорів", "senior",
        "400", "300", "500",
    ],
    2: [
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
        "джава", "java", "котлін", "kotlin",
        "пайтон", "python", "джанго", "django", "flask", "fastapi",
        "джаваскрипт", "javascript", "typescript",
        "реакт", "react", "ангулар", "angular", "vue",
        "ноджс", "nodejs", "node",
        "го", "golang", "раст", "rust",
        "сі шарп", "c#", "dotnet", ".net",
        "php", "ruby", "rails", "swift",
        "html", "css", "sass", "tailwind",
        "postgres", "mysql", "mongo", "mongodb", "redis",
        "elasticsearch", "cassandra", "oracle", "sql", "nosql",
        "гіт", "git", "github", "gitlab", "bitbucket",
        "слак", "slack", "джира", "jira", "конфлюенс", "confluence",
        "постман", "postman", "swagger", "figma", "фігма",
        "vs code", "intellij", "pycharm",
        "сентрі", "sentry", "datadog",
    ],
    4: [
        "докер", "docker", "контейнер", "container",
        "кубер", "kubernetes", "k8s", "helm",
        "terraform", "ansible",
        "aws", "amazon", "azure", "gcp", "google cloud",
        "ec2", "s3", "lambda", "serverless",
        "jenkins", "github actions", "gitlab ci",
        "prometheus", "grafana", "nginx",
        "мікросервіс", "microservice", "монолит", "monolith",
        "апі", "api", "рест", "rest", "graphql", "grpc",
        "кафка", "kafka", "rabbitmq", "websocket",
        "кеш", "cache", "cdn", "балансер", "load balancer",
        "oauth", "jwt", "токен", "auth",
        "шардинг", "sharding", "реплікація", "replication",
        "machine learning", "ml", "ai", "нейромережа", "neural network",
        "chatgpt", "gpt", "llm", "pytorch", "tensorflow",
        "датасет", "dataset", "embedding", "ембединг",
        "agile", "scrum", "kanban", "okr", "kpi", "roadmap", "роадмап",
        "рефакторинг", "refactor", "технічний борг", "tech debt", "легасі", "legacy",
        "пайплайн", "pipeline", "cicd", "ci/cd",
        "стейджинг", "staging", "прод", "production",
        "постмортем", "postmortem", "ретро", "retrospective",
        "моніторинг", "monitoring", "алерт", "alert", "інцидент", "incident",
    ],
    5: [
        "офер", "оффер", "offer", "онбординг", "onboarding",
        "перф", "перформанс", "performance review",
        "бенефіти", "benefits", "страховка",
        "акції", "equity", "rsu", "бонус", "bonus", "рейз", "raise",
        "корпоратив", "team building", "тімбілдінг",
        "аутсорс", "outsource", "аутстаф", "remote", "ремоут", "гібрид",
        "релокейт", "relocation", "хакатон", "hackathon", "конференція",
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
    "бля", "блять", "бляд", "блядь", "сука", "суки", "суку", "сучий", "сучара", "сучці", "сучку",
    "їбать", "їбаний", "єбать", "єбаний", "йобаний", "йобані",
    "відхуярити", "захуячити", "нахуярити", "похуярити",
    "пізда", "пізді", "піздець", "піздюк", "піздити", "піздатий",
    "хуй", "хуя", "хуйня", "хуйло", "нахуй", "похуй", "захуяти",
    "залупа", "залупу", "мудак", "мудаки", "мудила", "мудацький",
    "їбало", "довбойоб", "довбойобе", "довбань",
    "шльоха", "шльохи", "шалава", "курва", "курви", "курвин",
    "ублюдок", "ублюдки", "падло", "падлюка", "падлюко",
    "гандон", "гандони", "підарас", "підараси", "підарасина",
    "блядь", "пизда", "хуйло", "мудак",
    "ёбаный", "ебаный", "ёбать", "ебать", "ёбнутый", "ебнутый",
    "пиздец", "нихуя", "похуй", "залупа", "шлюха",
    "fuck", "fucker", "fucking", "fucked", "fucks", "motherfucker",
    "shit", "shithead", "bullshit", "shitty",
    "bitch", "bastard", "asshole", "dickhead", "dipshit",
    "cunt", "prick", "twat", "wanker",
]

DUCK_REPLACEMENTS = ["КРЯ", "КРЯК", "КРЯ-КРЯ", "КРЯЯЯ", "КРЯК-КРЯК", "КВАК", "🦆"]

LEVEL_LABELS = {
    1: "🟢 чіл — компанії та посади",
    2: "🟡 стривожена капібара — ролі",
    3: "🟠 бомбастік сайдай — мови та інструменти",
    4: "🔴 залізна занавіса — девопс і хмари і вся байда",
    5: "☢️ чіхуахуа — анігіляція",
}

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

# ===== STATE =====
current_level = 5
karma = 0
last_insult_time = 0.0
INSULT_COOLDOWN = 5 * 60
bot_id: int = 0
cached_ban_list: list[str] = []

# ===== DUPLICATE GUARD =====
seen_message_ids: set[str] = set()
seen_lock = asyncio.Lock()

app = FastAPI()
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== HELPERS =====

def get_ban_list(level: int) -> list[str]:
    words = []
    for lvl in range(1, level + 1):
        words.extend(BAN_LEVELS[lvl])
    return words

def rebuild_ban_cache():
    global cached_ban_list
    cached_ban_list = get_ban_list(current_level)

def normalize(text: str) -> str:
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[^\w]', '', text, flags=re.UNICODE)
    return text.lower()

def get_insult(k: int) -> str:
    applicable = [t for t in KARMA_THRESHOLDS if k <= t]
    key = applicable[-1] if applicable else KARMA_THRESHOLDS[0]
    return KARMA_INSULTS[key].format(n=abs(k))

def duck_censor(text: str) -> str:
    """Replace ALL bad words in text with random duck sounds."""
    result = text
    for bad in BAD_WORDS:
        pattern = re.compile(re.escape(bad), re.IGNORECASE)
        result = pattern.sub(lambda _: random.choice(DUCK_REPLACEMENTS), result)
    return result

async def is_duplicate(message_id: int, text: str) -> bool:
    key = f"{message_id}:{text}"
    async with seen_lock:
        if key in seen_message_ids:
            return True
        seen_message_ids.add(key)
        return False

async def cleanup_seen(message_id: int, text: str, delay: int = 10):
    await asyncio.sleep(delay)
    async with seen_lock:
        seen_message_ids.discard(f"{message_id}:{text}")

# ===== CORE FILTER =====

async def check_and_delete(message: types.Message):
    global karma, last_insult_time

    if not message.text:
        return

    # ignore bot's own messages
    if message.from_user.id == bot_id:
        return

    # skip commands
    if message.text.startswith("/"):
        return

    # deduplicate
    if await is_duplicate(message.message_id, message.text):
        print(f"⚠️ Duplicate skip: {message.message_id}")
        return
    asyncio.create_task(cleanup_seen(message.message_id, message.text))

    original_lower = message.text.lower()
    normalized = normalize(message.text)
    original_words = re.findall(r'\w+', original_lower)
    normalized_words = re.findall(r'\w+', normalized)
    all_words = list(dict.fromkeys(original_words + normalized_words))

    should_delete = False
    delete_reason = None
    matched_word = None

    # 1. fast full-text substring check for bad words
    for bad in BAD_WORDS:
        if bad in original_lower or bad in normalized:
            should_delete = True
            delete_reason = "badword"
            matched_word = bad
            print(f"🤬 Swear fulltext: '{bad}'")
            break

    # 2. fuzzy bad word check
    if not should_delete:
        for word in all_words:
            match = process.extractOne(word, BAD_WORDS, scorer=fuzz.ratio)
            if match:
                threshold = 92 if len(word) <= 3 else 85
                if match[1] > threshold:
                    should_delete = True
                    delete_reason = "badword"
                    matched_word = word
                    print(f"🤬 Swear fuzzy: '{word}' → '{match[0]}' ({match[1]:.1f}%)")
                    break

    # 3. IT single words
    if not should_delete:
        for word in all_words:
            match = process.extractOne(word, BAD_WORDS, scorer=fuzz.ratio)
            if match:
                threshold = 92 if len(word) <= 3 else 85
                if match[1] > threshold:
                    should_delete = True
                    delete_reason = "itword"
                    matched_word = word
                    print(f"🔥 IT word: '{word}' → '{match[0]}' ({match[1]:.1f}%)")
                    break

    # 4. IT multi-word terms
    if not should_delete:
        multi_word_terms = [t for t in cached_ban_list if ' ' in t]
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
            censored = duck_censor(message.text)
            await message.answer(
                f"🦆 НЕ МАТЮКАЙСЯ {matched_word.upper()}. КРЯ!\n\n"
                f"А тепер те що хотів сказати користувач:\n"
                f"_{censored}_",
                parse_mode="Markdown"
            )
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
        if member.id == bot_id:
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


@dp.message(lambda m: m.from_user.id in TARGET_IDS and not (m.text or "").startswith("/"))
async def monitor_users(message: types.Message):
    await check_and_delete(message)


@dp.edited_message(lambda m: m.from_user.id in TARGET_IDS and not (m.text or "").startswith("/"))
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
    rebuild_ban_cache()
    await message.answer(f"✅ Рівень строгості змінено: {LEVEL_LABELS[current_level]}")


@dp.message(F.text == "/status")
async def status(message: types.Message):
    await message.answer(
        f"🦆 Статус качки:\n"
        f"Рівень: {LEVEL_LABELS[current_level]}\n"
        f"Слів у бан-листі: {len(cached_ban_list)}\n\n"
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
        await message.answer(f"☢️ Карма Саші: {karma}. Качка дедінсайд.")


@dp.message(F.text == "/forgive")
async def forgive(message: types.Message):
    global karma
    if message.from_user.id != ADMIN_ID:
        await message.answer("🦆 Тільки головна качка може пробачати. КРЯ!")
        return
    old = karma
    karma = 0
    await message.answer(f"✅ Карму скинуто. Було: {old}. Саша отримав другий шанс. 🕊️")


@dp.message(F.text == "/help")
async def help_cmd(message: types.Message):
    await message.answer(
        "🦆 Команди качки:\n\n"
        "/level 1-5 — змінити рівень строгості (admin)\n"
        "/status — поточний стан бота\n"
        "/karma — карма Саші\n"
        "/forgive — скинути карму (admin)\n"
        "/help — ця довідка"
    )


# ===== API =====

@app.get("/")
async def root():
    return {"message": "Качка копаюча готова!"}


@app.get("/ping")
async def ping():
    return {
        "status": "online",
        "timestamp": time.time(),
        "level": current_level,
        "karma": karma,
        "ban_list_size": len(cached_ban_list),
    }


# ===== MAIN =====

async def main():
    global bot_id
    bot_info = await bot.get_me()
    bot_id = bot_info.id
    rebuild_ban_cache()
    print(f"🦆 Bot ID: {bot_id}")
    print(f"🎯 Monitoring: {TARGET_IDS}")
    print(f"📋 Ban list size: {len(cached_ban_list)}")

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
