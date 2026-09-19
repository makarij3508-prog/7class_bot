import asyncio
import logging
import random
import os
import aiohttp
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.chat_action import ChatActionSender
from aiohttp import web

# ==========================================
# 🚨 КРИТИЧНА КОНФІГУРАЦІЯ СИСТЕМИ v2.4 (7-В)
# ==========================================

# 🔌 ТВОЙ НОВИЙ ЧИСТИЙ ТОКЕН БОТА (БЕЗ РЕКЛАМИ ЛЕВИХ КАНАЛІВ)
BOT_TOKEN = "8735817305:AAG-F0qhTrCmbase2GtQcDtkBZV2o1fTceg"

# 👑 TVІЙ ЖОРСТКИЙ ID СУПЕР-АДМІНА (МАКАР — ГОЛОВНИЙ РОЗРОБНИК РІВНЯ 5)
SUPER_ADMIN_IDS = [8791830931]

# 🪪 СИСТЕМА ДИНАМІЧНИХ ПРАВ ПО ЮЗЕРНЕЙМАХ (КЕРУЄТЬСЯ З АДМІНКИ)
ADMIN_L4_USERNAMES = ["@пример_админа_л4"]  # Рівень 4: Головні Адміністратори
MODERATOR_USERNAMES = []                     # Рівень 3: Модератори чату класу
STAROSTA_USERNAMES = []                      # Рівень 2: Старости (Звіти та відмітки)
ASSISTANT_USERNAMES = []                     # Рівень 1: Помічники по ДЗ
TESTER_USERNAMES = []                        # Тестувальники тех. режиму

# 👑 ОФІЦІЙНА РОЛЬ КЛАСНОГО КЕРІВНИКА (ІМУНІТЕТ ТА ЗВІТИ)
TEACHER_USERNAME = "@victoria197198"

# 📊 ВНУТРІШНІ ДИНАМІЧНІ СПИСКИ ТЕЛЕГРАМ ID (ЗАПОВНЮЮТЬСЯ АВТОМАТИЧНО)
ADMIN_L4_IDS = []
MODERATOR_IDS = []
HW_ASSISTANT_IDS = []
STAROSTA_IDS = []
TESTER_IDS = []
TEACHER_CHAT_ID = 0

# 🔗 СЛОВНИКИ ДЛЯ СИНХРОНІЗАЦІЇ ІМЕН ТА ID
USER_TELEGRAM_NAMES = {8791830931: "Макар"}
USER_USERNAMES = {}

# 💬 БАЗА ДАНИХ ШКІЛЬКОГО ЧАТУ, МУТІВ ТА БАНІВ
CHAT_REGISTERED_USERS = {}  # Хто зараз знаходиться всередині кімнати чату
BANNED_USERS = []           # Чорний список чату (ID забанених)
MUTED_USERS = {}            # Словник активних мутів: ID -> timestamp закінчення

# 🪙 ЕКОНОМІЧНА БАЗА ДАНИХ v2.4 (СІМКИ В 7-В)
USER_BALANCES = {}          # ID користувача -> кількість Сімок 🪙
USER_LAST_CASE = {}         # ID користувача -> timestamp останнього подарунка 🎁
USER_CUSTOM_TAGS = {}       # ID користувача -> придбаний тег у чаті (наприклад: "Дед інсайд")
USER_ITEMS = {}             # ID користувача -> список куплених речей (shpora, antimut)

# 🎭 СИСТЕМА ТАЄМНОГО ШПИГУНА 7-В
CURRENT_SECRET_AGENT_ID = 0   # Telegram ID обраного шпигуна на сьогодні
AGENT_HAS_SENT_SECRET = False  # Чи відправив вже шпигун свій секрет сьогодні

# 🛠️ СИСТЕМНІ СТАТУСИ ТА ДАНІ КОНТЕНТУ
IS_TESTING_MODE = False
IMPORTANT_ANNOUNCEMENT = "📌 **Важливі оголошення:**\n\nНаразі немає нових оголошень від адміністрації або Бакланової Вікторії Олександрівни."
BOOKS_DATA = "📚 **Електронні підручники для 7-В класу (НУШ):**\n\nСкористайтеся меню налаштувань або введіть запити в Гугл з командою site:pidruchnyk.com.ua"
ABSENT_TODAY_LIST = []
RANDOM_MODE = "dice"
HOMEWORK_DATA = {}          # Сюди на льоту підтягується вечне ДЗ з файлу

# ==========================================
# 👥 ПОВНА БАЗА ДАНИХ ТВОГО КЛАСУ (28 УЧНІВ)
# ==========================================
RANDOM_NAMES = [
    "Олександр", "Андрій", "Данило", "Колодинський Богдан", "Ковалевчук Богдан", 
    "Мирослава", "Матвій", "Софія", "Михайло", "Макар", "Ілона", "Марічка", 
    "Маргарита", "Ангеліна", "Нікіта", "Альберт", "Єва", "Роман", "Владислав", 
    "Назарій", "Едуард", "Станіслав", "Артем", "Емілія", "Вероніка", "Ілля", "Дмитро", "Макс"
]

# 🚨 ОНОВЛЕНО НА 7-В КЛАС: Лише одна чиста стартова медаль для всіх учнів!
USER_ACHIEVEMENTS = {name: ["🥈 Активний учень 7-В класу"] for name in RANDOM_NAMES}

# 🪪 БАЗА ПРИВ'ЯЗКИ СПРАВЖНІХ ІМЕН ДО ЮЗЕРНЕЙМІВ
USER_USERNAMES_TEXT = {
    "@llona_x": "Ілона", "@selarkin": "Роман", "@play.funtime.su": "Едуард",
    "@marri_chk": "Марічка", "@myveronichkam": "Вероніка", "@Red_tea21": "Назарій",
    "@Mi42a": "Мирослава", "@sanichka_gg": "Олександр", "@shadow123446": "Емілія",
    "@ezhik_lite": "Артем", "@Vladore1488": "Колодинський Богдан", "@Sharik_xd": "Ковальчук Богдан",
    "@victoria197198": "Бакланова Вікторія Олександрівна"  # Твоя вчителька
}

# 🎒 ПРЕДМЕТИ ТА ЦІНИ В МАГАЗИНІ СІМОК
SHOP_ITEMS = {
    "item_shpora": {"name": "🃏 Шпаргалка (+30% до дуелей)", "price": 50},
    "item_antimut": {"name": "🛡️ Анти-Мут (Одноразовий)", "price": 100},
    "item_buytag": {"name": "🏷️ Власний Тег у чаті", "price": 150}
}

# 🗓️ ШКІЛЬНИЙ РОЗКЛАД УРОКІВ 7-В
SCHEDULE_DATA = {
    "mon": "🗓️ **Понеділок:**\n1. ЗБД / Зар. літ.\n2. Фізика\n3. Фізкультура\n4. Укр. література\n5. Алгебра\n6. Англійська\n7. Географія",
    "tue": "🗓️ **Вівторок:**\n1. Історія\n2. Біологія\n3. Геометрія\n4. Укр. мова\n5. ЗБД\n6. Інформатика\n7. Технології",
    "wed": "🗓️ **Середа:**\n1. Укр. мова\n2. Хімія\n3. Зар. література\n4. Фізкультура\n5. Алгебра\n6. Англійська\n7. Географія",
    "thu": "🗓️ **Четвер:**\n1. Англ. / Біологія\n2. Фізика\n3. Мистецтво\n4. Укр. мова\n5. Геометрія\n6. Інформатика\n7. Історія",
    "fri": "🗓️ **P'ятниця:**\n1. Історія\n2. Мистецтво\n3. Англійська\n4. Укр. література\n5. Фізкультура\n6. Біологія\n7. Алгебра"
}

# 📚 НАЗВИ ПРЕДМЕТІВ ТА ДНІВ ТИЖНЯ ДЛЯ СИНХРОНІЗАЦІЇ КНОПОК
SUBJECT_NAMES = {
    "algebra": "📐 Алгебра", "geometry": "📐 Геометрія", "physics": "量 Фізика", "chemistry": "🧪 Хімія",
    "biology": "🧬 Біологія", "geography": "🌍 Географія", "hist_ua": "📜 Історія Укр.", "hist_world": "🏰 Всесвітня iст.",
    "lang_ua": "🇺🇦 Укр. мова", "lit_ua": "📚 Укр. літ.", "english": "🇬🇧 Англійська", "lit_world": "🗺️ Зарубіжна літ.",
    "inf": "💻 Інформатика", "tech": "🛠️ Технології", "art": "🎨 Мистецтво", "zbd": "🌱 ЗБД"
}
DAY_NAMES = {"mon": "Понеділок", "tue": "Вівторок", "wed": "Середа", "thu": "Четвер", "fri": "П'ятниця"}

# 🔮 БАЗА ПЕРЕДБАЧЕНЬ НА СЬОГОДНІ
PREDICTIONS = [
    "🌟 Сьогодні твій щасливий день! Все буде спокійно і без двійок.",
    "⚡ Обережно! На фізрі доведеться побігати на норматив.",
    "🧠 Ідеальний час, щоб підняти бал з алгебри або геометрії!",
    "🍕 У їдальні сьогодні неймовірно смачні булочки, встигни на перерві!",
    "🎒 Ти забудеш щось важливе вдома, перевір рюкзак просто зараз!",
    "🍀 На укр. мові тебе сьогодні омине виклик до дошки. Везунчик!"
]

# ==========================================
# ⚙️ МАШИНА СТАНІВ (FSM) ДЛЯ ІНТЕРАКТИВУ
# ==========================================

class BotStates(StatesGroup):
    waiting_for_question = State()          # Очікування запитання для ШІ
    waiting_for_grades = State()            # Очікування оцінок для середнього балу
    waiting_for_hw_text = State()           # Ввід тексту домашнього завдання адмінами
    waiting_for_important_text = State()    # Ввід важливого оголошення
    waiting_for_books_text = State()        # Оновлення списку підручників
    waiting_for_schedule_text = State()     # Ввід нового розкладу уроків
    waiting_for_absence_info = State()      # Ввід списку прогульників старостою
    admin_choosing_user_ach = State()       # Вибір учня для видачі медалі
    admin_input_achievement = State()       # Текст нового досягнення
    admin_input_username_for_level = State() # Ввід ніка для рівнів доступу
    admin_choosing_ach_to_delete = State()   # Стан для видалення конкретної медалі учня
    user_in_chat_window = State()           # Користувач знаходиться всередині чату
    waiting_for_secret_text = State()       # Ввід анонімного тексту Таємним Шпигуном
    waiting_for_custom_tag = State()        # Ввід власного тексту для купівлі тегу

# Ініціалізація основних об'єктів айограма
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Хендлер для проходження перевірки працездатності (Health Check) на Render
async def handle_render_hc(request):
    return web.Response(text="OK")

# ==========================================
# 🎹 ГЕНЕРАТОРИ ГОЛОВНИХ ТА АДМІН-МЕНЮ БОТА
# ==========================================

def get_main_menu(user_id: int) -> ReplyKeyboardMarkup:
    """Генерація головного меню з перевіркою прав та показом кнопки Шпигуна"""
    buttons = [
        [KeyboardButton(text="🗓️ Розклад"), KeyboardButton(text="📝 ДЗ")],
        [KeyboardButton(text="🤖 ШІ Допомога"), KeyboardButton(text="🔊 Чат класу")],
        [KeyboardButton(text="📚 Книги"), KeyboardButton(text="📌 Важливе")],
        [KeyboardButton(text="🎲 Рандом"), KeyboardButton(text="⚙️ Налаштування")]
    ]
    
    # 🎭 Якщо цей користувач сьогодні обраний Таємним Шпигуном — виводимо йому секретну кнопку!
    if user_id == CURRENT_SECRET_AGENT_ID and not AGENT_HAS_SENT_SECRET:
        buttons.insert(2, [KeyboardButton(text="🤫 Секретний Злив")])
        
    all_protected_ids = []
    for s in [ADMIN_L4_IDS, MODERATOR_IDS, HW_ASSISTANT_IDS, STAROSTA_IDS, TESTER_IDS]:
        if s: 
            all_protected_ids.extend(s)
            
    if (user_id == 8791830931 or user_id in all_protected_ids or user_id == TEACHER_CHAT_ID):
        buttons.append([KeyboardButton(text="🛠️ Admin Panel")])
        
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_ai_mode_menu() -> ReplyKeyboardMarkup:
    """Кнопка виходу з інтерактивного сеансу зі штучним інтелектом"""
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🛑 Вийти з режиму ШІ")]], resize_keyboard=True)

def get_chat_exit_menu() -> ReplyKeyboardMarkup:
    """Кнопка для безпечного виходу із закритої кімнати чату класу"""
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🚪 Вийти з чату")]], resize_keyboard=True)

def get_subjects_menu(prefix: str) -> InlineKeyboardMarkup:
    """Абсолютно чиста та вивірена інлайн-клавіатура предметів без конфліктів ключів"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📐 Алгебра", callback_data=f"{prefix}_algebra"), 
         InlineKeyboardButton(text="📐 Geометрія", callback_data=f"{prefix}_geometry")],
        [InlineKeyboardButton(text="🧲 Фізика", callback_data=f"{prefix}_physics"), 
         InlineKeyboardButton(text="🧪 Хімія", callback_data=f"{prefix}_chemistry")],
        [InlineKeyboardButton(text="🧬 Біологія", callback_data=f"{prefix}_biology"), 
         InlineKeyboardButton(text="🌍 Географія", callback_data=f"{prefix}_geography")],
        [InlineKeyboardButton(text="🇺🇦 Unр. мова", callback_data=f"{prefix}_lang_ua"), 
         InlineKeyboardButton(text="📚 Укр. літ.", callback_data=f"{prefix}_lit_ua")],
        [InlineKeyboardButton(text="🇬🇧 Англійська", callback_data=f"{prefix}_english"), 
         InlineKeyboardButton(text="💻 Інформатика", callback_data=f"{prefix}_inf")]
    ])

def get_days_menu(prefix: str) -> InlineKeyboardMarkup:
    """Генерація інлайн-кнопок днів тижня для розкладу уроків"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Понеділок", callback_data=f"{prefix}_mon"), InlineKeyboardButton(text="Вівторок", callback_data=f"{prefix}_tue")],
        [InlineKeyboardButton(text="Середа", callback_data=f"{prefix}_wed"), InlineKeyboardButton(text="Четвер", callback_data=f"{prefix}_thu")],
        [InlineKeyboardButton(text="П'ятниця", callback_data=f"{prefix}_fri")]
    ])

def get_admin_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Жорсткий розподіл інлайн-кнопок всередині адмінки згідно з рівнем прав"""
    keyboard = []
    
    if user_id in HW_ASSISTANT_IDS or user_id in STAROSTA_IDS or user_id in ADMIN_L4_IDS or user_id == 8791830931:
        keyboard.append([InlineKeyboardButton(text="📝 Змінити ДЗ", callback_data="admin_add_hw")])
        
    if user_id in STAROSTA_IDS or user_id in ADMIN_L4_IDS or user_id == 8791830931:
        keyboard.append([InlineKeyboardButton(text="🗓️ Змінити Розклад", callback_data="admin_edit_sch")])
        
    if user_id in STAROSTA_IDS or user_id in ADMIN_L4_IDS or user_id == 8791830931:
        keyboard.append([InlineKeyboardButton(text="👥 Відмітити відсутнього", callback_data="admin_mark_attendance"), 
                         InlineKeyboardButton(text="📢 Надіслати звіт вчителю", callback_data="admin_send_report")])
        
    if user_id in ADMIN_L4_IDS or user_id == 8791830931 or user_id == TEACHER_CHAT_ID:
        keyboard.append([InlineKeyboardButton(text="📌 Оновити Важливе", callback_data="admin_add_important"), 
                         InlineKeyboardButton(text="📚 Оновити Книги", callback_data="admin_edit_books")])
        
    if user_id in ADMIN_L4_IDS or user_id == 8791830931:
        keyboard.append([InlineKeyboardButton(text="👑 Налаштувати рівні доступу", callback_data="admin_give_level_menu"),
                         InlineKeyboardButton(text="🏆 Керувати досягненнями", callback_data="admin_manage_ach")])
        
    if user_id == 8791830931:
        keyboard.append([InlineKeyboardButton(text="🧪 Тест-Режим: ОН/ОФФ", callback_data="admin_toggle_test")])
        
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# 🪙 ІНТЕРАКТИВНЕ МЕНЮ НАЛАШТУВАНЬ ДЛЯ 7-В
settings_interactive_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏆 Досягнення", callback_data="profile_achievements"), InlineKeyboardButton(text="🔮 Передбачення", callback_data="profile_prediction")],
    [InlineKeyboardButton(text="🎁 Щоденний Подарунок", callback_data="economy_get_gift"), InlineKeyboardButton(text="🛒 Магазин Сімок", callback_data="economy_open_shop")],
    [InlineKeyboardButton(text="🎰 Слот-Машина", callback_data="economy_open_slots"), InlineKeyboardButton(text="📈 Біржа 7-V", callback_data="economy_open_stocks")],
    [InlineKeyboardButton(text="📜 Лог оновлень", callback_data="profile_changelog")]
])

async def send_human_message(message: Message, text: str, reply_markup=None):
    return await message.answer(text, reply_markup=reply_markup)

# ==========================================
# 📖 ОСНОВНІ КОМАНДИ ТА ХЕНДЛЕРИ КОРИСТУВАЧІВ
# ==========================================

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    
    if user_id not in USER_BALANCES:
        USER_BALANCES[user_id] = 10  # 10 Сімок підгону при першому старті!
    
    if username:
        user_key = f"@{username.lower()}"
        USER_USERNAMES[user_key] = user_id
        
        if user_key in ADMIN_L4_USERNAMES and user_id not in ADMIN_L4_IDS:
            ADMIN_L4_IDS.append(user_id)
            
        if user_key in MODERATOR_USERNAMES and user_id not in MODERATOR_IDS:
            MODERATOR_IDS.append(user_id)
            
        if user_key in STAROSTA_USERNAMES and user_id not in STAROSTA_IDS:
            STAROSTA_IDS.append(user_id)
            
        if user_key in ASSISTANT_USERNAMES and user_id not in HW_ASSISTANT_IDS:
            HW_ASSISTANT_IDS.append(user_id)
            
        if user_key in TESTER_USERNAMES and user_id not in TESTER_IDS:
            TESTER_IDS.append(user_id)
            
        if user_key == TEACHER_USERNAME.lower():
            global TEACHER_CHAT_ID
            TEACHER_CHAT_ID = user_id

    await send_human_message(message, "Привіт! Я твій інтерактивний помічник для 7-В класу. Чим займемося сьогодні?", reply_markup=get_main_menu(user_id))

@router.message(F.text == "📝 ДЗ")
async def show_subjects_for_hw(message: Message):
    user_id = message.from_user.id
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in ADMIN_L4_IDS and user_id not in TESTER_IDS: return
    await send_human_message(message, "Обери предмет, щоб подивитися домашнє завдання:", reply_markup=get_subjects_menu("view"))

@router.callback_query(F.data.startswith("view_"))
async def process_view_hw(callback: CallbackQuery):
    await callback.answer() # Миттєво гасимо часики на кнопці!
    subject = callback.data.replace("view_", "")
    sub_name = SUBJECT_NAMES.get(subject, "Предмет")
    hw_text = HOMEWORK_DATA.get(subject, "Завдання поки що не додано.")
    await callback.message.edit_text(text=f"📝 **ДЗ з предмету {sub_name}:**\n\n{hw_text}", reply_markup=get_subjects_menu("view"))

@router.message(F.text == "🗓️ Розклад")
async def show_schedule_days(message: Message):
    user_id = message.from_user.id
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in ADMIN_L4_IDS and user_id not in TESTER_IDS: return
    await send_human_message(message, "Обери день тижня:", reply_markup=get_days_menu("sch"))

@router.callback_query(F.data.startswith("sch_"))
async def process_schedule_callback(callback: CallbackQuery):
    await callback.answer()
    day = callback.data.replace("sch_", "")
    await callback.message.edit_text(text=SCHEDULE_DATA.get(day, "⚠️ Нічого немає."), reply_markup=get_days_menu("sch"))

@router.message(F.text == "📚 Книги")
async def handle_show_books(message: Message):
    user_id = message.from_user.id
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in ADMIN_L4_IDS and user_id not in TESTER_IDS: return
    await send_human_message(message, BOOKS_DATA)

@router.message(F.text == "📌 Важливе")
async def handle_show_important(message: Message):
    user_id = message.from_user.id
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in ADMIN_L4_IDS and user_id not in TESTER_IDS: return
    await send_human_message(message, IMPORTANT_ANNOUNCEMENT)

@router.message(F.text == "🎲 Рандом")
async def handle_show_random(message: Message):
    user_id = message.from_user.id
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in ADMIN_L4_IDS and user_id not in TESTER_IDS: return
    global RANDOM_MODE
    if RANDOM_MODE == "dice": await message.answer_dice()
    else:
        name = random.choice(RANDOM_NAMES)
        await send_human_message(message, f"🎲 Випадковий учень до дошки: **{name}**")

@router.message(F.text == "📊 Сер. бал")
async def ask_for_grades(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in ADMIN_L4_IDS and user_id not in TESTER_IDS: return
    await send_human_message(message, "Введи свої оцінки через пробіл або кому (наприклад: 10, 11, 9, 12):")
    await state.set_state(BotStates.waiting_for_grades)

@router.message(BotStates.waiting_for_grades)
async def process_grades(message: Message, state: FSMContext):
    try:
        text = message.text.replace(",", " ")
        grades = [int(g) for g in text.split() if g.isdigit()]
        if not grades: raise ValueError
        avg = sum(grades) / len(grades)
        await send_human_message(message, f"📊 Твій середній бал: {avg:.2f}")
    except ValueError:
        await message.answer("❌ Будь ласка, введи коректні оцінки (числа від 1 до 12).")
    await state.clear()

async def ask_free_ai(question: str) -> str:
    url = "https://duckduckgo.com"
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Ти помічник для 7-В класу. Відповідай чітко, українською."},
            {"role": "user", "content": question}
        ]
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=12) as response:
                if response.status == 200:
                    res_data = await response.json()
                    return res_data.get("reply", "⚠️ ШІ тимчасово думає...")
                return "⚠️ Сервер ШІ тимчасово перевантажений."
    except Exception: return "❌ Наразі ШІ відпочиває. Спробуйте пізніше!"

@router.message(F.text == "🤖 ШІ Допомога")
async def handle_ai_help(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in ADMIN_L4_IDS and user_id not in TESTER_IDS: return
    await send_human_message(message, "🤖 **Ви увійшли в інтерактивний режим ШІ!**\n\nПиши свої питання підряд. Для виходу натисни кнопку нижче 👇", reply_markup=get_ai_mode_menu())
    await state.set_state(BotStates.waiting_for_question)

@router.message(BotStates.waiting_for_question, F.text == "🛑 Вийти з режиму ШІ")
async def exit_ai_mode(message: Message, state: FSMContext):
    await state.clear()
    await send_human_message(message, "🚪 Ви вийшли з режиму ШІ. Повертаюсь до головного меню:", reply_markup=get_main_menu(message.from_user.id))

@router.message(BotStates.waiting_for_question)
async def process_ai_question(message: Message, state: FSMContext):
    if message.text.startswith("/"): return
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        ai_response = await ask_free_ai(message.text)
    await message.answer(f"🤖 **Відповідь ШІ:**\n\n{ai_response}\n\n✍️ _Я все ще в режимі ШІ. Пиши наступне запитання!_", reply_markup=get_ai_mode_menu())

# ==========================================
# 🎁 ХЕНДЛЕР ЩОДЕННОГО ПОДАРУНКА v2.4 (ВІД 2 ДО 20 МОНЕТ)
# ==========================================

@router.callback_query(F.data == "economy_get_gift")
async def process_get_daily_gift(callback: CallbackQuery):
    user_id = callback.from_user.id
    now = datetime.now().timestamp()
    
    if user_id in USER_LAST_CASE:
        time_passed = now - USER_LAST_CASE[user_id]
        if time_passed < 86400:
            time_left = int((86400 - time_passed) / 3600)
            await callback.message.answer(f"🎁 **Опа, зачекай!**\n\nТи вже забрав свій подарунок. Наступний підгін Сімок буде доступний через **{time_left if time_left > 0 else 1} год.**")
            await callback.answer()
            return
            
    gift_coins = random.randint(2, 20)
    if user_id not in USER_BALANCES: USER_BALANCES[user_id] = 0
    USER_BALANCES[user_id] += gift_coins
    USER_LAST_CASE[user_id] = now
    
    await callback.message.answer(
        f"🎁 **Вітаємо! Щоденний Подарунок активовано!**\n\n"
        f"🎰 Рулетка прокрутилась і тобі випало: **+{gift_coins} Сімок** 🪙!\n"
        f"💰 Твій новий баланс: **{USER_BALANCES[user_id]} Сімок**."
    )
    await callback.answer()

# ==========================================
# 🔊 МОДЕРОВАНИЙ ЧАТ КЛАСУ 7-В (ІНТЕГРАЦІЯ ТЕГІВ)
# ==========================================

@router.message(F.text == "🔊 Чат класу")
async def enter_chat_room(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if user_id in BANNED_USERS:
        await message.answer("🛑 **Доступ заблоковано!**\n\nВи забанені в чаті адміністрацією класу.")
        return

    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in ADMIN_L4_IDS and user_id not in TESTER_IDS:
        await message.answer("🛠️ Чат закритий на технічні роботи.")
        return

    if user_id in USER_TELEGRAM_NAMES: name = USER_TELEGRAM_NAMES[user_id]
    else: name = message.from_user.first_name if message.from_user.first_name else "Учень"

    CHAT_REGISTERED_USERS[user_id] = name
    await state.set_state(BotStates.user_in_chat_window)
    
    await message.answer(
        f"💬 **Ласкаво просимо до чату 7-В класу, {name}!**\n\n"
        "✍️ Просто пиши повідомлення сюди, і його побачать усі однокласники в чаті бота!",
        reply_markup=get_chat_exit_menu()
    )

@router.message(BotStates.user_in_chat_window, F.text == "🚪 Вийти з чату")
async def exit_chat_room(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in CHAT_REGISTERED_USERS: CHAT_REGISTERED_USERS.pop(user_id)
    await state.clear()
    await send_human_message(message, "🚪 Ви вийшли з кімнати чату. Повертаюсь до меню:", reply_markup=get_main_menu(user_id))

@router.message(BotStates.user_in_chat_window)
async def process_live_chat_message(message: Message):
    user_id = message.from_user.id
    if message.text == "🚪 Вийти з чату": return

    if user_id in BANNED_USERS:
        await message.answer("🛑 Вас забанено.")
        return

    if user_id in MUTED_USERS:
        now = datetime.now().timestamp()
        if now < MUTED_USERS[user_id]:
            time_left = int((MUTED_USERS[user_id] - now) / 60)
            await message.answer(f"🤫 **У вас діє режим тиші (МУТ)!**\n\nВи зможете писати знову через **{time_left if time_left > 0 else 1} хв.**")
            return
        else: MUTED_USERS.pop(user_id)

    sender_name = CHAT_REGISTERED_USERS.get(user_id, "Учень")
    custom_tag = USER_CUSTOM_TAGS.get(user_id, "")
    prefix_text = f"[{custom_tag}] " if custom_tag else ""

    for target_id in list(CHAT_REGISTERED_USERS.keys()):
        if target_id != user_id:
            try: await bot.send_message(chat_id=target_id, text=f"💬 **{prefix_text}{sender_name}:** {message.text}")
            except Exception: pass

    all_protected_ids = set(SUPER_ADMIN_IDS + ADMIN_L4_IDS + MODERATOR_IDS + HW_ASSISTANT_IDS + STAROSTA_IDS + TESTER_IDS)
    if user_id == TEACHER_CHAT_ID or user_id in all_protected_ids:
        all_admins = set(SUPER_ADMIN_IDS + ADMIN_L4_IDS + MODERATOR_IDS + HW_ASSISTANT_IDS)
        for admin_id in all_admins:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=f"👁️ **[ЧАТЛОГ - ЗАХИЩЕНИЙ] {prefix_text}{sender_name} (ID: `{user_id}`) написав:**\n«_{message.text}_»"
                )
            except Exception: pass
        return

    all_admins = set(SUPER_ADMIN_IDS + ADMIN_L4_IDS + MODERATOR_IDS + HW_ASSISTANT_IDS)
    if TEACHER_CHAT_ID: all_admins.add(TEACHER_CHAT_ID)

    punish_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤫 Мут (15 хв)", callback_data=f"mute_15_{user_id}_{sender_name}"),
         InlineKeyboardButton(text="🛑 БАН у чаті", callback_data=f"ban_{user_id}_{sender_name}")]
    ])

    for admin_id in all_admins:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=f"👁️ **[ЧАТЛОГ] {prefix_text}{sender_name} (ID: `{user_id}`) написав:**\n«_{message.text}_»",
                reply_markup=punish_keyboard
            )
        except Exception: pass

# ==========================================

@router.message(F.text == "⚙️ Налаштування")
async def show_settings(message: Message):
    user_id = message.from_user.id
    await send_human_message(message, "⚙️ Налаштування та інтерактив:", reply_markup=settings_interactive_menu)

@router.callback_query(F.data == "profile_prediction")
async def process_prediction(callback: CallbackQuery):
    pred = random.choice(PREDICTIONS)
    await callback.message.answer(f"🔮 **Твоє передбачення:**\n\n{pred}")
    await callback.answer()

@router.callback_query(F.data == "profile_achievements")
async def process_achievements(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    user_key = f"@{username.lower()}" if username else ""
    
    if user_id == 8791830931: name = "Макар"
    elif user_key in USER_USERNAMES_TEXT: name = USER_USERNAMES_TEXT[user_key]
    else: name = callback.from_user.first_name if callback.from_user.first_name else "Учень"
        
    ach_list = USER_ACHIEVEMENTS.get(name, ["🥈 Активний учень 7-В класу"])
    formatted = "\n".join(ach_list)
    await callback.message.answer(f"🏆 **Досягнення учня ({name}):**\n\n{formatted}")
    await callback.answer()

@router.callback_query(F.data == "profile_changelog")
async def process_changelog(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        text="📜 **Офіційний лог оновлень (v2.4):**\n\n"
             "• **Екосистема 7-В класу:** Весь інтерфейс, логіка та медалі повністю переведені під твій рідний 7-В клас.\n"
             "• **Економіка Сімок:** Запущено шкільну валюту 🪙. Отримуй щоденні подарунки та збирай капітал.\n"
             "• **Казино 'У Макара' та Біржа:** Крути шкільний слот-машину за 5 сімок 🎰 або інвестуй у акції уроків 📈.\n"
             "• **Магазин Луту:** Купуй Шпаргалки, Анти-мути та Власний Кастомний Тег у чаті назавжди (наприклад, 'Дед інсайд') 🏷️.\n"
             "• **Таємний Шпигун 7-В:** Бот раз на добу таємно обирає одного чела для анонімного зливу через премодерацію Макара 🎭.\n"
             "• **Вечне збереження ДЗ:** Додано локальну JSON базу даних, щоб введене тобою ДЗ ніколи не злітало при перезапусках сервера.",
        reply_markup=settings_interactive_menu
    )

@router.message(F.text == "🛠️ Admin Panel")
async def handle_admin_panel(message: Message):
    user_id = message.from_user.id
    if user_id == 8791830931:
        await message.answer(text="🛠️ **Вітаємо, Макаре! Доступні функції Головного Розробника:**", reply_markup=get_admin_menu_keyboard(user_id))
        return
        
    all_protected_ids = []
    for s in [ADMIN_L4_IDS, MODERATOR_IDS, HW_ASSISTANT_IDS, STAROSTA_IDS, TESTER_IDS]:
        if s: all_protected_ids.extend(s)
        
    if user_id in all_protected_ids or user_id == TEACHER_CHAT_ID:
        await message.answer(text="🛠️ **Вітаємо в панелі адміністратора. Доступні функції згідно з вашим рівнем прав:**", reply_markup=get_admin_menu_keyboard(user_id))
    else:
        await message.answer("🛑 У вас немає доступу до цієї команди.")

# ==========================================
# 🛠️ АДМІНІСТРАТИВНА ПАНЕЛЬ ТА БЕЗПЕЧНА МОДЕРАЦІЯ
# ==========================================

@router.callback_query(F.data.startswith("mute_15_"))
async def process_chat_mute(callback: CallbackQuery):
    admin_id = callback.from_user.id
    all_admins = set(SUPER_ADMIN_IDS + ADMIN_L4_IDS + MODERATOR_IDS + HW_ASSISTANT_IDS)
    if admin_id not in all_admins and admin_id != TEACHER_CHAT_ID and admin_id != 8791830931: return

    raw_data = callback.data.replace("mute_15_", "")
    data_parts = raw_data.split("_")
    if len(data_parts) < 2: return
    
    target_id = int(data_parts[0])
    target_name = data_parts[1]
    
    MUTED_USERS[target_id] = datetime.now().timestamp() + 900
    alert_text = f"🤫 **Користувач {target_name} замучений на 15 хв за порушення правил чату!**"

    for u_id in list(CHAT_REGISTERED_USERS.keys()):
        try: await bot.send_message(chat_id=u_id, text=alert_text)
        except Exception: pass

    await callback.message.edit_text(text=f"✅ Покарання успішно застосовано!\n{alert_text}")
    await callback.answer()

@router.callback_query(F.data.startswith("ban_"))
async def process_chat_ban(callback: CallbackQuery):
    admin_id = callback.from_user.id
    all_admins = set(SUPER_ADMIN_IDS + ADMIN_L4_IDS + MODERATOR_IDS + HW_ASSISTANT_IDS)
    if admin_id not in all_admins and admin_id != TEACHER_CHAT_ID and admin_id != 8791830931: return

    raw_data = callback.data.replace("ban_", "")
    data_parts = raw_data.split("_")
    if len(data_parts) < 2: return
    
    target_id = int(data_parts[0])
    target_name = data_parts[1]
    
    if target_id not in BANNED_USERS: BANNED_USERS.append(target_id)
    alert_text = f"🛑 **Користувач {target_name} назавжди забанений у чаті класу!**"

    for u_id in list(CHAT_REGISTERED_USERS.keys()):
        try: await bot.send_message(chat_id=u_id, text=alert_text)
        except Exception: pass

    await callback.message.edit_text(text=f"✅ Покарання успішно застосовано!\n{alert_text}")
    await callback.answer()

# ==========================================
# 🎰 КАЗИНО «У МАКАРА» ТА ШКІЛЬНІ СЛОТИ v2.4
# ==========================================

@router.callback_query(F.data == "economy_open_slots")
async def process_open_slots(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_coins = USER_BALANCES.get(user_id, 0)
    
    if user_coins < 5:
        await callback.message.answer("🎰 **Казино «У Макара»**\n\n❌ У тебе недостатньо коштів! Одна прокрутка коштує **5 Сімок** 🪙.")
        await callback.answer()
        return
        
    USER_BALANCES[user_id] -= 5
    
    pool = ["12", "10", "8", "5", "2"]
    res1, res2, res3 = random.choice(pool), random.choice(pool), random.choice(pool)
    
    anim_text = "🎰 **Казино «У Макара»**\n\n🎰 *Барабани крутяться: [ 🔄 | 🔄 | 🔄 ]*"
    msg = await callback.message.answer(anim_text)
    await asyncio.sleep(1)
    
    if res1 == "12" and res2 == "12" and res3 == "12":
        USER_BALANCES[user_id] += 100
        result_text = f"🎉 **ДЖЕКПОТ!!!** Випало [ 12 | 12 | 12 ]! Ти виграв **+100 Сімок** 🪙!"
    elif res1 == res2 == res3:
        USER_BALANCES[user_id] += 25
        result_text = f"🔥 **Тріпл!** Випало [ {res1} | {res2} | {res3} ]! Ти виграв **+25 Сімок** 🪙!"
    elif res1 == "2" and res2 == "2" and res3 == "2":
        MUTED_USERS[user_id] = datetime.now().timestamp() + 60
        result_text = f"🥶 **ДИКИЙ ФЕЙЛ!** Випало [ 2 | 2 | 2 ]! Сімки згоріли + ти ловиш **МУТ на 1 хвилину**!"
    elif res1 == res2 or res2 == res3 or res1 == res3:
        USER_BALANCES[user_id] += 8
        result_text = f"💵 **Дубль!** Випало [ {res1} | {res2} | {res3} ]! Невеликий куш: **+8 Сімок** 🪙!"
    else:
        result_text = f"📉 **Програш...** Випало [ {res1} | {res2} | {res3} ]."
        
    await msg.edit_text(text=f"🎰 **Казино «У Макара»**\n\nРезультат: [ {res1} | {res2} | {res3} ]\n\n{result_text}\n💰 Твій баланс: **{USER_BALANCES[user_id]} Сімок**.")
    await callback.answer()

# ==========================================
# 🛒 ІНТЕРАКТИВНИЙ МАГАЗИН СІМОК ТА ТЕГІВ
# ==========================================

@router.callback_query(F.data == "economy_open_shop")
async def process_open_shop(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_coins = USER_BALANCES.get(user_id, 0)
    
    shop_buttons = [
        [InlineKeyboardButton(text="🃏 Шпаргалка (50 Сімок)", callback_data="buy_shpora")],
        [InlineKeyboardButton(text="🛡️ Анти-Мут (100 Сімок)", callback_data="buy_antimut")],
        [InlineKeyboardButton(text="🏷️ Власний Тег у чаті (150 Сімок)", callback_data="buy_customtag")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="economy_back_to_settings")]
    ]
    
    await callback.message.edit_text(
        text=f"🛒 **Магазин підгонів та луту 7-В класу**\n\n"
             f"💰 Твій баланс: **{user_coins} Сімок** 🪙\n\n"
             f"Обери предмет, який хочеш придбати:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=shop_buttons)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("buy_"))
async def process_buy_item(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    item = callback.data.replace("buy_", "")
    user_coins = USER_BALANCES.get(user_id, 0)
    
    prices = {"shpora": 50, "antimut": 100, "customtag": 150}
    price = prices.get(item, 999)
    
    if user_coins < price:
        await callback.message.answer(f"❌ **Помилка!** Тобі не вистачає Сімок! Потрібно: {price} 🪙.")
        await callback.answer()
        return
        
    USER_BALANCES[user_id] -= price
    
    if item == "shpora":
        if user_id not in USER_ITEMS: USER_ITEMS[user_id] = []
        USER_ITEMS[user_id].append("shpora")
        await callback.message.answer("✅ **Купівля успішна!**\n\nТи придбав **🃏 Шпаргалку**. Вона додасть тобі +30% шансу у наступних дуелях!")
    elif item == "antimut":
        if user_id not in USER_ITEMS: USER_ITEMS[user_id] = []
        USER_ITEMS[user_id].append("antimut")
        await callback.message.answer("✅ **Купівля успішна!**\n\nТи придбав **🛡️ Анти-Мут**. Якщо тебе замутять — ти зможеш зняти його сам!")
    elif item == "customtag":
        await callback.message.answer("🏷️ **Купівля Тегу успішна!**\n\nТепер, будь ласка, **введіть текст свого кастомного тегу** (наприклад: `Дед інсайд`):")
        await state.set_state(BotStates.waiting_for_custom_tag)
        
    await callback.answer()

@router.message(BotStates.waiting_for_custom_tag)
async def process_save_custom_tag(message: Message, state: FSMContext):
    user_id = message.from_user.id
    tag_text = message.text.strip().replace("[", "").replace("]", "")
    
    if len(tag_text) > 15:
        await message.answer("❌ **Задовгий тег!** Максимальна довжина — 15 символів. Введи коротший:")
        return
        
    USER_CUSTOM_TAGS[user_id] = tag_text
    await message.answer(f"✅ **Тег успішно встановлено!**\n\nТепер у чаті 7-В перед твоїм ім'ям завжди буде писатися: `[{tag_text}]` 🏷️!")
    await state.clear()

# ==========================================
# 👑 КЕРУВАННЯ ПРАВАМИ УЧНІВ КНОПКАМИ
# ==========================================

@router.callback_query(F.data == "admin_give_level_menu")
async def admin_start_give_level(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS: return
    buttons = [[InlineKeyboardButton(text=name, callback_data=f"lvluser_{name}")] for name in RANDOM_NAMES]
    await callback.message.answer("👥 **Оберіть учня для керування рівнем доступу в 7-В:**", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

def get_user_current_level(name: str) -> int:
    target_username = ""
    for username, u_name in USER_USERNAMES_TEXT.items():
        if u_name == name:
            target_username = username
            break
            
    if not target_username: return 0
    if target_username in ADMIN_L4_USERNAMES: return 4
    if target_username in MODERATOR_USERNAMES: return 3
    if target_username in STAROSTA_USERNAMES: return 2
    if target_username in ASSISTANT_USERNAMES: return 1
    return 0
@router.callback_query(F.data.startswith("lvluser_"))
async def process_level_user_card(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS: return
    name = callback.data.replace("lvluser_", "")
    current_lvl = get_user_current_level(name)
    
    level_names = {
        0: "📋 Рівень 0 (Звичайний учень)", 1: "📐 Рівень 1 (Помічник по ДЗ)",
        2: "👥 Рівень 2 (Староста)", 3: "🛡️ Рівень 3 (Модератор чату)",
        4: "⭐ Рівень 4 (Головний Admin)"
    }
    card_buttons = [
        [InlineKeyboardButton(text="🔺 Підняти рівень", callback_data=f"lvledit_up_{name}"),
         InlineKeyboardButton(text="🔻 Понизити рівень", callback_data=f"lvledit_down_{name}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_give_level_menu")]
    ]
    await callback.message.edit_text(text=f"🪪 **Картка керування правами**\n\n👤 **Учень:** {name}\n📊 **Поточний статус:** {level_names.get(current_lvl)}", reply_markup=InlineKeyboardMarkup(inline_keyboard=card_buttons))
    await callback.answer()

@router.callback_query(F.data == "admin_toggle_test")
async def admin_toggle_testing_mode(callback: CallbackQuery):
    if callback.from_user.id != 8791830931: return
    global IS_TESTING_MODE
    IS_TESTING_MODE = not IS_TESTING_MODE
    status_text = "🟢 **УВІМКНЕНО** (Бот закритий)" if IS_TESTING_MODE else "🔴 **ВИМКНЕНО** (Бот відкритий)"
    await callback.message.answer(f"🛠️ Режим тестування змінено: {status_text}")
    await callback.answer()

# ==========================================
# 📝 АДМІН-ХЕНДЛЕРИ КОНТЕНТУ (ВЕЧНЕ ДЗ ТА ФІКС КНОПКИ НАЗАД)
# ==========================================

def save_homework_to_file():
    try:
        with open("homework.json", "w", encoding="utf-8") as f:
            json.dump(HOMEWORK_DATA, f, ensure_ascii=False, indent=4)
        print("💾 ДЗ успішно збережено у файл homework.json!")
    except Exception as e:
        print(f"⚠️ Помилка збереження ДЗ у файл: {e}")

@router.callback_query(F.data == "admin_add_hw")
async def admin_choose_subject_hw(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS and user_id not in STAROSTA_IDS and user_id not in HW_ASSISTANT_IDS: 
        await callback.answer("🛑 У вас немає доступу!", show_alert=True)
        return
    await callback.answer() 
    await callback.message.edit_text(text="Оберіть предмет, для якого хочете змінити ДЗ:", reply_markup=get_subjects_menu("ehw"))

@router.callback_query(F.data.startswith("ehw_"))
async def admin_input_hw_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer() 
    subject = callback.data.replace("ehw_", "")
    await state.update_data(chosen_subject=subject)
    await callback.message.edit_text(text=f"📝 Введіть новий текст ДЗ для предмета {SUBJECT_NAMES.get(subject, 'Предмет')}:")
    await state.set_state(BotStates.waiting_for_hw_text)

@router.message(BotStates.waiting_for_hw_text)
async def admin_save_hw_text(message: Message, state: FSMContext):
    global HOMEWORK_DATA
    user_id = message.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS and user_id not in STAROSTA_IDS and user_id not in HW_ASSISTANT_IDS: return
    data = await state.get_data()
    subject = data.get("chosen_subject")
    
    HOMEWORK_DATA[subject] = message.text
    save_homework_to_file()
    
    await message.answer(f"✅ ДЗ для {SUBJECT_NAMES.get(subject, 'Предмет')} успішно оновлено та збережено навсегда!")
    await state.clear()

@router.callback_query(F.data == "admin_edit_sch")
async def admin_choose_day_sch(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS and user_id not in STAROSTA_IDS: 
        await callback.answer("🛑 У вас немає доступу!", show_alert=True)
        return
    await callback.answer()
    await callback.message.edit_text(text="Оберіть день для зміни розкладу:", reply_markup=get_days_menu("esch"))

@router.callback_query(F.data.startswith("esch_"))
async def admin_input_sch_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    day = callback.data.replace("esch_", "")
    await state.update_data(chosen_day=day)
    await callback.message.edit_text(text=f"🗓️ Введіть новий розклад для дня ({DAY_NAMES.get(day, 'День')}):")
    await state.set_state(BotStates.waiting_for_schedule_text)

@router.message(BotStates.waiting_for_schedule_text)
async def admin_save_sch_text(message: Message, state: FSMContext):
    global SCHEDULE_DATA
    user_id = message.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS and user_id not in STAROSTA_IDS: return
    data = await state.get_data()
    day = data.get("chosen_day")
    SCHEDULE_DATA[day] = message.text
    await message.answer(f"✅ Розклад на {DAY_NAMES.get(day, 'День')} успішно змінено!")
    await state.clear()

@router.callback_query(F.data == "admin_send_report")
async def admin_send_report_to_teacher(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS and user_id not in STAROSTA_IDS: return
    if not ABSENT_TODAY_LIST:
        await callback.message.answer("⚠️ Список відсутніх порожній!")
        await callback.answer()
        return
    formatted = "\n".join([f"• {name}" for name in ABSENT_TODAY_LIST])
    report_text = f"📢 **Щоденний звіт про відсутніх учнів**\n\nУчнів, яких сьогодні немає:\n{formatted}\n\nВсього відсутніх: {len(ABSENT_TODAY_LIST)}"
    
    target_chat_id = TEACHER_CHAT_ID if TEACHER_CHAT_ID else 8791830931
    try:
        await bot.send_message(chat_id=target_chat_id, text=report_text)
        await callback.message.answer(f"🚀 Звіт успішно надіслано в особисті повідомлення Баклановій Вікторії Олександрівні!")
    except Exception: await callback.message.answer(f"❌ Помилка відправки звіту!")
    await callback.answer()

# ==========================================
# 📈 ЕКОНОМІЧНА БІРЖА АКЦІЙ 7-В КЛАСУ
# ==========================================

@router.callback_query(F.data == "economy_open_stocks")
async def process_open_stocks(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_coins = USER_BALANCES.get(user_id, 0)
    
    minute = datetime.now().minute
    hour = datetime.now().hour
    price_stolovka = int(20 + (minute % 7) * 4 - (hour % 3) * 2)
    price_fizra = int(15 + (minute % 5) * 5 + (hour % 2) * 3)
    price_ai = int(40 + (minute % 9) * 6 - (hour % 4) * 4)
    
    if price_stolovka < 5: price_stolovka = 5
    if price_fizra < 5: price_fizra = 5
    if price_ai < 10: price_ai = 10
    
    stock_buttons = [
        [InlineKeyboardButton(text=f"🍔 Акції Столової — {price_stolovka} Сімок", callback_data=f"stk_buy_stolovka_{price_stolovka}")],
        [InlineKeyboardButton(text=f"🏃 Акції Фізкультури — {price_fizra} Сімок", callback_data=f"stk_buy_fizra_{price_fizra}")],
        [InlineKeyboardButton(text=f"🤖 Акції ШІ-Помічника — {price_ai} Сімок", callback_data=f"stk_buy_ai_{price_ai}")],
        [InlineKeyboardButton(text=f"🔄 Оновити курс акцій", callback_data="economy_open_stocks")],
        [InlineKeyboardButton(text=f"🔙 Назад", callback_data="economy_back_to_settings")]
    ]
    
    await callback.message.edit_text(
        text=f"📈 **Економічна Біржа 7-В класу**\n\n💰 Твій баланс: **{user_coins} Сімок** 🪙\n📊 _Ціни змінюються кожні кілька хвилин!_\n\nКупуй акції дешевше, оновлюй курс і продавай дорожче, щоб стати магнатом класу!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=stock_buttons)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("stk_buy_"))
async def process_buy_stock(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_coins = USER_BALANCES.get(user_id, 0)
    
    raw_data = callback.data.replace("stk_buy_", "")
    data_parts = raw_data.split("_")
    if len(data_parts) < 2: return
    
    stock_name = data_parts
    price = int(data_parts)
    
    if user_coins < price:
        await callback.message.answer("❌ **Помилка бізнесу!** Тобі не вистачає Сімок для купівлі цієї акції.")
        await callback.answer()
        return
        
    USER_BALANCES[user_id] -= price
    await callback.message.answer(f"📈 **Угода успішна!**\n\nВи придбали 1 акцію предмета **{stock_name.upper()}** за **{price} Сімок**! Слідкуйте за курсом, щоб вигідно її перепродати.")
    await callback.answer()

# ==========================================
# 🎭 СИСТЕМА ПРЕМОДЕРАЦІЇ ТАЄМНОГО ШПИГУНА ДЛЯ МАКАРА
# ==========================================

@router.message(F.text == "🤫 Секретний Злив")
async def handle_secret_agent_button(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id != CURRENT_SECRET_AGENT_ID or AGENT_HAS_SENT_SECRET: return
    await message.answer("🎭 **Ти — Таємний Шпигун класу на сьогодні!**\n\nВведіть текст анонійної записки, плітки або зізнання. Макар перевірить її в адмінці, і якщо все ок — пустить в чат без твого імені!")
    await state.set_state(BotStates.waiting_for_secret_text)

@router.message(BotStates.waiting_for_secret_text)
async def process_agent_secret_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id != CURRENT_SECRET_AGENT_ID: return
    
    secret_text = message.text
    moderation_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Одобрити злив", callback_data=f"modsecret_approve"),
         InlineKeyboardButton(text="❌ Видалити дич", callback_data=f"modsecret_delete")]
    ])
    await state.update_data(saved_secret_payload=secret_text)
    
    try:
        await bot.send_message(chat_id=8791830931, text=f"🕵️‍♂️ **[ПРЕМОДЕРАЦІЯ ЦРУ] Надійшов анонімний злив від Шпигуна дня!**\n\n«_{secret_text}_»", reply_markup=moderation_markup)
        await message.answer("✅ **Записку надіслано Макару на перевірку!** Очікуйте публікації в чаті класу.")
    except Exception:
        await message.answer("❌ Помилка зв'язку з сервером премодерації Макара.")
    await state.set_state(BotStates.user_in_chat_window)

@router.callback_query(F.data.startswith("modsecret_"))
async def process_macar_moderation_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != 8791830931: return
    action = callback.data.replace("modsecret_", "")
    state_data = await state.get_data()
    secret_text = state_data.get("saved_secret_payload", "Порожній секрет.")
    global AGENT_HAS_SENT_SECRET
    
    if action == "approve":
        AGENT_HAS_SENT_SECRET = True
        alert_text = f"🎭 🤫 **СЕКРЕТНИЙ ЗЛИВ ВІД ТАЄМНОГО ШПИГУНА 7-В!**\n\n«_{secret_text}_»\n\n💬 _Хто, на вашу думку, цей шпигун? Обговорюйте в чаті!_"
        for u_id in list(CHAT_REGISTERED_USERS.keys()):
            try: await bot.send_message(chat_id=u_id, text=alert_text)
            except Exception: pass
        await callback.message.edit_text(text=f"🟢 Секрет успішно схвалено та опубліковано в чат класу!")
    else:
        await callback.message.edit_text(text=f"❌ Ви заблокували та видалили цей злив Шпигуна.")
    await callback.answer()

@router.callback_query(F.data == "admin_send_report")
async def admin_send_report_to_teacher(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS and user_id not in STAROSTA_IDS: return
    if not ABSENT_TODAY_LIST:
        await callback.message.answer("⚠️ Список відсутніх порожній!")
        await callback.answer()
        return
    formatted = "\n".join([f"• {name}" for name in ABSENT_TODAY_LIST])
    report_text = f"📢 **Щоденний звіт про відсутніх учнів**\n\nУчнів, яких сьогодні немає:\n{formatted}\n\nВсього відсутніх: {len(ABSENT_TODAY_LIST)}"
    
    target_chat_id = TEACHER_CHAT_ID if TEACHER_CHAT_ID else 8791830931
    try:
        await bot.send_message(chat_id=target_chat_id, text=report_text)
        await callback.message.answer(f"🚀 Звіт успішно надіслано в особисті повідомлення Баклановій Вікторії Олександрівні!")
    except Exception: await callback.message.answer(f"❌ Помилка відправки звіту!")
    await callback.answer()

# ==========================================
# 📈 ЕКОНОМІЧНА БІРЖА АКЦІЙ 7-В КЛАСУ
# ==========================================

@router.callback_query(F.data == "economy_open_stocks")
async def process_open_stocks(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_coins = USER_BALANCES.get(user_id, 0)
    
    minute = datetime.now().minute
    hour = datetime.now().hour
    price_stolovka = int(20 + (minute % 7) * 4 - (hour % 3) * 2)
    price_fizra = int(15 + (minute % 5) * 5 + (hour % 2) * 3)
    price_ai = int(40 + (minute % 9) * 6 - (hour % 4) * 4)
    
    if price_stolovka < 5: price_stolovka = 5
    if price_fizra < 5: price_fizra = 5
    if price_ai < 10: price_ai = 10
    
    stock_buttons = [
        [InlineKeyboardButton(text=f"🍔 Акції Столової — {price_stolovka} Сімок", callback_data=f"stk_buy_stolovka_{price_stolovka}")],
        [InlineKeyboardButton(text=f"🏃 Акції Фізкультури — {price_fizra} Сімок", callback_data=f"stk_buy_fizra_{price_fizra}")],
        [InlineKeyboardButton(text=f"🤖 Акції ШІ-Помічника — {price_ai} Сімок", callback_data=f"stk_buy_ai_{price_ai}")],
        [InlineKeyboardButton(text=f"🔄 Оновити курс акцій", callback_data="economy_open_stocks")],
        [InlineKeyboardButton(text=f"🔙 Назад", callback_data="economy_back_to_settings")]
    ]
    
    await callback.message.edit_text(
        text=f"📈 **Економічна Біржа 7-В класу**\n\n💰 Твій баланс: **{user_coins} Сімок** 🪙\n📊 _Ціни змінюються кожні кілька хвилин!_\n\nКупуй акції дешевше, оновлюй курс і продавай дорожче, щоб стати магнатом класу!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=stock_buttons)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("stk_buy_"))
async def process_buy_stock(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_coins = USER_BALANCES.get(user_id, 0)
    
    raw_data = callback.data.replace("stk_buy_", "")
    data_parts = raw_data.split("_")
    if len(data_parts) < 2: return
    
    stock_name = data_parts
    price = int(data_parts)
    
    if user_coins < price:
        await callback.message.answer("❌ **Помилка бізнесу!** Тобі не вистачає Сімок для купівлі цієї акції.")
        await callback.answer()
        return
        
    USER_BALANCES[user_id] -= price
    await callback.message.answer(f"📈 **Угода успішна!**\n\nВи придбали 1 акцію предмета **{stock_name.upper()}** за **{price} Сімок**! Слідкуйте за курсом, щоб вигідно її перепродати.")
    await callback.answer()

# ==========================================
# 🎭 СИСТЕМА ПРЕМОДЕРАЦІЇ ТАЄМНОГО ШПИГУНА ДЛЯ МАКАРА
# ==========================================

@router.message(F.text == "🤫 Секретний Злив")
async def handle_secret_agent_button(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id != CURRENT_SECRET_AGENT_ID or AGENT_HAS_SENT_SECRET: return
    await message.answer("🎭 **Ти — Таємний Шпигун класу на сьогодні!**\n\nВведіть текст анонійної записки, плітки або зізнання. Макар перевірить її в адмінці, і якщо все ок — пустить в чат без твого імені!")
    await state.set_state(BotStates.waiting_for_secret_text)

@router.message(BotStates.waiting_for_secret_text)
async def process_agent_secret_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id != CURRENT_SECRET_AGENT_ID: return
    
    secret_text = message.text
    moderation_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Одобрити злив", callback_data=f"modsecret_approve"),
         InlineKeyboardButton(text="❌ Видалити дич", callback_data=f"modsecret_delete")]
    ])
    await state.update_data(saved_secret_payload=secret_text)
    
    try:
        await bot.send_message(chat_id=8791830931, text=f"🕵️‍♂️ **[ПРЕМОДЕРАЦІЯ ЦРУ] Надійшов анонімний злив від Шпигуна дня!**\n\n«_{secret_text}_»", reply_markup=moderation_markup)
        await message.answer("✅ **Записку надіслано Макару на перевірку!** Очікуйте публікації в чаті класу.")
    except Exception:
        await message.answer("❌ Помилка зв'язку з сервером премодерації Макара.")
    await state.set_state(BotStates.user_in_chat_window)

@router.callback_query(F.data.startswith("modsecret_"))
async def process_macar_moderation_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != 8791830931: return
    action = callback.data.replace("modsecret_", "")
    state_data = await state.get_data()
    secret_text = state_data.get("saved_secret_payload", "Порожній секрет.")
    global AGENT_HAS_SENT_SECRET
    
    if action == "approve":
        AGENT_HAS_SENT_SECRET = True
        alert_text = f"🎭 🤫 **СЕКРЕТНИЙ ЗЛИВ ВІД ТАЄМНОГО ШПИГУНА 7-В!**\n\n«_{secret_text}_»\n\n💬 _Хто, на вашу думку, цей шпигун? Обговорюйте в чаті!_"
        for u_id in list(CHAT_REGISTERED_USERS.keys()):
            try: await bot.send_message(chat_id=u_id, text=alert_text)
            except Exception: pass
        await callback.message.edit_text(text=f"🟢 Секрет успішно схвалено та опубліковано в чат класу!")
    else:
        await callback.message.edit_text(text=f"❌ Ви заблокували та видалили цей злив Шпигуна.")
    await callback.answer()

# 🚨 ЖЕСТКИЙ ПРЯМИЙ ФІКС КНОПКИ НАЗАД (ПРИТИСНУТИ ДО ЛІВОГО КРАЮ, 0 ПРОБЕЛІВ!)
@router.callback_query(F.data == "economy_back_to_settings")
async def process_back_to_settings_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        text="⚙️ Налаштування та інтерактив:",
        reply_markup=settings_interactive_menu
    )

# ==========================================
# 🚀 ТАЙМЕРИ ТА ЗАПУСК СЕРВЕРА RENDER ДЛЯ v2.4
# ==========================================

async def self_ping_task():
    url = os.getenv("RENDER_EXTERNAL_URL")
    if not url: return
    print(f"🚀 Система захисту від сну запустилась...")
    await asyncio.sleep(60)
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    print(f"⏰ Автопінг Render: {response.status}")
        except Exception: pass
        await asyncio.sleep(600)

async def cron_secret_agent_picker():
    global CURRENT_SECRET_AGENT_ID, AGENT_HAS_SENT_SECRET
    while True:
        await asyncio.sleep(3600 * 24)
        if USER_USERNAMES:
            all_chat_users = list(USER_USERNAMES.values())
            CURRENT_SECRET_AGENT_ID = random.choice(all_chat_users)
            AGENT_HAS_SENT_SECRET = False
            try:
                await bot.send_message(
                    chat_id=CURRENT_SECRET_AGENT_ID,
                    text="🤫 **УВАГА! Нова доба настала!**\n\nТебе обрано **Таємним Шпигуном 7-В класу** на сьогодні! У твоєму меню з'явилась кнопка `🤫 Секретний Злив`."
                )
            except Exception: pass

def restore_homework_from_file():
    global HOMEWORK_DATA
    try:
        if os.path.exists("homework.json"):
            with open("homework.json", "r", encoding="utf-8") as f:
                HOMEWORK_DATA = json.load(f)
            print("📦 Базу ДЗ успішно відновлено з файлу homework.json!")
        else:
            print("ℹ️ Файл бекапу ДЗ не знайдено, запущено чисту базу.")
    except Exception as e:
        print(f"❌ Помилка відновлення бекапу ДЗ: {e}")

async def on_startup(bot: Bot):
    url = os.getenv("RENDER_EXTERNAL_URL")
    if url:
        webhook_url = f"{url.rstrip('/')}/webhook"
        await bot.set_webhook(webhook_url, drop_pending_updates=True)
        print(f"🌐 Webhook successfully set to: {webhook_url}")
    else:
        print("⚠️ RENDER_EXTERNAL_URL is empty, webhook not set.")

async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    
    app = web.Application()
    app.router.add_get("/", handle_render_hc)
    
    from aiogram.webhook.aiohttp_handler import SimpleRequestHandler, setup_application
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    
    asyncio.create_task(self_ping_task())
    asyncio.create_task(cron_secret_agent_picker())
    
    restore_homework_from_file()
    
    # Реєструємо функцію встановлення вебхука при старті сервера
    await on_startup(bot)
    
    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    print(f"🚀 Сервер v2.4 успішно запустился на порту {port}!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
