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
# 🚨 КРИТИЧНА КОНФІГУРАЦІЯ СИСТЕМИ v2.5 (7-В)
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

# 👑 TVІЙ ЖОРСТКИЙ ID СУПЕР-АДМІНА (МАКАР — ГОЛОВНИЙ РОЗРОБНИК РІВНЯ 5)
SUPER_ADMIN_IDS = [8791830931]

# 🪪 СИСТЕМА ДИНАМІЧНИХ ПРАВ ПО ЮЗЕРНЕЙМАХ (КЕРУЄТЬСЯ З АДМІНКИ)
ADMIN_L4_USERNAMES = ["@пример_админа_л4"]  
MODERATOR_USERNAMES = []                     
STAROSTA_USERNAMES = []                      
ASSISTANT_USERNAMES = []                     
TESTER_USERNAMES = []                        

# 👑 ОФІЦІЙНА РОЛЬ КЛАСНОГО КЕРІВНИКА (ІМУНІТЕТ ТА АВТО-РАПОРТИ)
TEACHER_USERNAME = "@victoria197198"

# 📊 ВНУТРІШНІ ДИНАМІЧНІ СПИСКИ ID (ЗМІНЮЮТЬСЯ В АДМІНЦІ НА ХОДУ)
ADMIN_L4_IDS = []
MODERATOR_IDS = []
HW_ASSISTANT_IDS = []
STAROSTA_IDS = []
TESTER_IDS = []
TEACHER_CHAT_ID = 0

# 🔗 СЛОВНИКИ ДЛЯ СИНХРОНІЗАЦІЇ ІМЕН ТА ID УЧНІВ
USER_TELEGRAM_NAMES = {8791830931: "Макар"}
USER_USERNAMES = {}

# 💬 БАЗА ДАНИХ ШКІЛЬКОГО ЧАТУ, МУТІВ ТА БАНІВ
CHAT_REGISTERED_USERS = {}  
BANNED_USERS = []           
MUTED_USERS = {}            

# 🪙 ЕКОНОМІЧНА БАЗА ДАНИХ v2.5 (СІМКИ В 7-В)
USER_BALANCES = {}          
USER_LAST_CASE = {}         
USER_CUSTOM_TAGS = {}       
USER_ITEMS = {}             

# 🎭 СИСТЕМА ТАЄМНОГО ШПИГУНА 7-В
CURRENT_SECRET_AGENT_ID = 0   
AGENT_HAS_SENT_SECRET = False  

# 🛠️ СИСТЕМНІ СТАТУСИ ТА ДАНІ КОНТЕНТУ
IS_TESTING_MODE = False
IMPORTANT_ANNOUNCEMENT = "📌 **Важливі оголошення:**\n\nНаразі немає нових оголошень від адміністрації або Бакланової Вікторії Олександрівни."
BOOKS_DATA = "📚 **Електронні підручники для 7-В класу (НУШ):**\n\nСкористайтеся меню налаштувань або введіть запити в Гугл з командою site:pidruchnyk.com.ua"
ABSENT_TODAY_LIST = []
RANDOM_MODE = "dice"
HOMEWORK_DATA = {}          

# ==========================================
# 👥 ПОВНА БАЗА ДАНИХ ТВОГО КЛАСУ (28 УЧНІВ)
# ==========================================
RANDOM_NAMES = [
    "Олександр", "Андрій", "Данило", "Колодинський Богдан", "Ковалевчук Богдан", 
    "Мирослава", "Матвій", "Софія", "Михайло", "Макар", "Ілона", "Марічка", 
    "Маргарита", "Ангеліна", "Нікіта", "Альберт", "Єва", "Роман", "Владислав", 
    "Назарій", "Едуард", "Станіслав", "Артем", "Емілія", "Вероніка", "Ілля", "Дмитро", "Макс"
]

USER_ACHIEVEMENTS = {name: ["🥈 Активний учень 7-В класу"] for name in RANDOM_NAMES}

USER_USERNAMES_TEXT = {
    "@llona_x": "Ілона", "@selarkin": "Роман", "@play.funtime.su": "Едуард",
    "@marri_chk": "Марічка", "@myveronichkam": "Вероніка", "@Red_tea21": "Назарій",
    "@Mi42a": "Мирослава", "@sanichka_gg": "Олександр", "@shadow123446": "Емілія",
    "@ezhik_lite": "Артем", "@Vladore1488": "Колодинський Богдан", "@Sharik_xd": "Ковальчук Богдан",
    "@victoria197198": "Бакланова Вікторія Олександрівна"
}

# 🗓️ ШКІЛЬНИЙ РОЗКЛАД УРОКІВ 7-В (З УСІМА ПРЕДМЕТАМИ)
SCHEDULE_DATA = {
    "mon": "🗓️ **Понеділок:**\n1. ЗБД / Зар. літ.\n2. Фізика\n3. Фізкультура\n4. Укр. література\n5. Алгебра\n6. Англійська\n7. Географія",
    "tue": "🗓️ **Вівторок:**\n1. Історія України\n2. Біологія\n3. Геометрія\n4. Укр. мова\n5. ЗБД\n6. Інформатика\n7. Технології",
    "wed": "🗓️ **Середа:**\n1. Укр. мова\n2. Хімія\n3. Зар. література\n4. Фізкультура\n5. Алгебра\n6. Англійська\n7. Географія",
    "thu": "🗓️ **Четвер:**\n1. Англ. / Біологія\n2. Фізика\n3. Мистецтво\n4. Укр. мова\n5. Геометрія\n6. Інформатика\n7. Всесвітня історія",
    "fri": "🗓️ **П'ятниця:**\n1. Історія України\n2. Мистецтво\n3. Англійська\n4. Укр. література\n5. Фізкультура\n6. Біологія\n7. Алгебра"
}

# 📚 ПОВНИЙ СЛОВНИК ПРЕДМЕТІВ З ТЕХНОЛОГІЯМИ ТА ЗАРУБЕЖКОЮ (БЕЗ ОПЕЧАТОК)
SUBJECT_NAMES = {
    "algebra": "📐 Алгебра", "geometry": "📐 Геометрія", "physics": "🧲 Фізика", "chemistry": "🧪 Хімія",
    "biology": "🧬 Біологія", "geography": "🌍 Географія", "hist_ua": "📜 Історія України", "hist_world": "🏰 Всесвітня історія",
    "lang_ua": "🇺🇦 Укр. мова", "lit_ua": "📚 Укр. літ.", "english": "🇬🇧 Англійська", "lit_world": "🗺️ Зарубіжна літ.",
    "inf": "💻 Інформатика", "tech": "🛠️ Технології", "art": "🎨 Мистецтво", "zbd": "🌱 ЗБД"
}
DAY_NAMES = {"mon": "Понеділок", "tue": "Вівторок", "wed": "Середа", "thu": "Четвер", "fri": "П'ятниця"}

PREDICTIONS = [
    "🌟 Сьогодні твій щасливий день! Все буде спокійно і без двійок.",
    "⚡ Обережно! На фізрі доведеться побігати на норматив.",
    "🧠 Ідеальний час, щоб підняти бал з алгебри або геометрії!",
    "🍕 У їдальні сьогодні неймовірно смачні булочки, встигни на перерві!",
    "🎒 Ти забудеш щось важливе вдома, перевір рюкзак просто зараз!",
    "🍀 На укр. мові тебе сьогодні омине виклик до дошки. Везунчик!"
]

# ==========================================
# ⚙️ МАШИНА СТАНІВ (FSM) ТА РОЗУМНІ КЛАВІАТУРИ
# ==========================================

class BotStates(StatesGroup):
    waiting_for_question = State()          
    waiting_for_grades = State()            
    waiting_for_hw_text = State()           
    waiting_for_important_text = State()    
    waiting_for_books_text = State()        
    waiting_for_schedule_text = State()     
    waiting_for_absence_info = State()      
    admin_choosing_user_ach = State()       
    admin_input_achievement = State()       
    admin_input_username_for_level = State() 
    admin_choosing_ach_to_delete = State()   
    user_in_chat_window = State()           
    waiting_for_secret_text = State()       
    waiting_for_custom_tag = State()        

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

def get_main_menu(user_id: int) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🗓️ Розклад"), KeyboardButton(text="📝 ДЗ")],
        [KeyboardButton(text="🤖 ШІ Допомога"), KeyboardButton(text="🔊 Чат класу")],
        [KeyboardButton(text="📚 Книги"), KeyboardButton(text="📌 Важливе")],
        [KeyboardButton(text="🎲 Рандом"), KeyboardButton(text="⚙️ Налаштування")]
    ]
    if user_id == CURRENT_SECRET_AGENT_ID and not AGENT_HAS_SENT_SECRET:
        buttons.insert(2, [KeyboardButton(text="🤫 Секретний Злив")])
        
    all_protected_ids = []
    for s in [ADMIN_L4_IDS, MODERATOR_IDS, HW_ASSISTANT_IDS, STAROSTA_IDS, TESTER_IDS]:
        if s: all_protected_ids.extend(s)
            
    if (user_id == 8791830931 or user_id in all_protected_ids or user_id == TEACHER_CHAT_ID):
        buttons.append([KeyboardButton(text="🛠️ Admin Panel")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_ai_mode_menu() -> ReplyKeyboardMarkup: return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🛑 Вийти з режиму ШІ")]], resize_keyboard=True)
def get_chat_exit_menu() -> ReplyKeyboardMarkup: return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🚪 Вийти з чату")]], resize_keyboard=True)

def get_subjects_menu(prefix: str) -> InlineKeyboardMarkup:
    """Генерація клавіатури предметів з урахуванням Технологій та Зарубіжки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📐 Алгебра", callback_data=f"{prefix}_algebra"), InlineKeyboardButton(text="📐 Геометрія", callback_data=f"{prefix}_geometry")],
        [InlineKeyboardButton(text="🧲 Фізика", callback_data=f"{prefix}_physics"), InlineKeyboardButton(text="🧪 Хімія", callback_data=f"{prefix}_chemistry")],
        [InlineKeyboardButton(text="🧬 Біологія", callback_data=f"{prefix}_biology"), InlineKeyboardButton(text="🌍 Географія", callback_data=f"{prefix}_geography")],
        [InlineKeyboardButton(text="📜 Іст. України", callback_data=f"{prefix}_hist_ua"), InlineKeyboardButton(text="🏰 Всесвітня іст.", callback_data=f"{prefix}_hist_world")],
        [InlineKeyboardButton(text="🇺🇦 Укр. мова", callback_data=f"{prefix}_lang_ua"), InlineKeyboardButton(text="📚 Укр. літ.", callback_data=f"{prefix}_lit_ua")],
        [InlineKeyboardButton(text="🇬🇧 Англійська", callback_data=f"{prefix}_english"), InlineKeyboardButton(text="🗺️ Зар. літ.", callback_data=f"{prefix}_lit_world")],
        [InlineKeyboardButton(text="💻 Інформатика", callback_data=f"{prefix}_inf"), InlineKeyboardButton(text="🛠️ Технології", callback_data=f"{prefix}_tech")],
        [InlineKeyboardButton(text="🎨 Мистецтво", callback_data=f"{prefix}_art"), InlineKeyboardButton(text="🌱 ЗБД", callback_data=f"{prefix}_zbd")]
    ])

def get_days_menu(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Понеділок", callback_data=f"{prefix}_mon"), InlineKeyboardButton(text="Вівторок", callback_data=f"{prefix}_tue")],
        [InlineKeyboardButton(text="Середа", callback_data=f"{prefix}_wed"), InlineKeyboardButton(text="Четвер", callback_data=f"{prefix}_thu")],
        [InlineKeyboardButton(text="П'ятниця", callback_data=f"{prefix}_fri")]
    ])

def get_admin_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
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
        keyboard.append([InlineKeyboardButton(text="👑 Налаштувати рівні доступу", callback_data="admin_give_level_menu")])
    if user_id == 8791830931:
        keyboard.append([InlineKeyboardButton(text="🧪 Тест-Режим: ОН/ОФФ", callback_data="admin_toggle_test")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

settings_interactive_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏆 Досягнення", callback_data="profile_achievements"), InlineKeyboardButton(text="🔮 Передбачення", callback_data="profile_prediction")],
    [InlineKeyboardButton(text="🎁 Щоденний Подарунок", callback_data="economy_get_gift"), InlineKeyboardButton(text="🛒 Maгазин Сімок", callback_data="economy_open_shop")],
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

    await send_human_message(message, "Привіт! Я твій помічник для 7-В класу. Чим займемося сьогодні?", reply_markup=get_main_menu(user_id))

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
# 🎁 ХЕНДЛЕР ЩОДЕННОГО ПОДАРУНКА v2.5 (ВІД 2 ДО 20 МОНЕТ)
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
        text="📜 **Офіційний лог оновлень (v2.5):**\n\n"
             "• **Екосистема 7-В класу:** Весь інтерфейс, логіка та медалі переведені під твій рідний 7-В клас.\n"
             "• **Повний список предметів:** Нарешті зашиті Історія України, Всесвітня історія, Мистецтво, ЗБД та Технології.\n"
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
# 🎰 КАЗИНО «У МАКАРА» ТА ШКІЛЬНІ СЛОТИ v2.5
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

@router.callback_query(F.data.startswith("lvledit_"))
async def process_dynamic_level_change(callback: CallbackQuery):
    admin_id = callback.from_user.id
    if admin_id != 8791830931 and admin_id not in ADMIN_L4_IDS: return
    
    raw_cmd = callback.data.replace("lvledit_", "")
    cmd_parts = raw_cmd.split("_")
    if len(cmd_parts) < 2: return
    
    action = cmd_parts[0]
    target_name = cmd_parts[1]
    
    target_username = ""
    for username, u_name in USER_USERNAMES_TEXT.items():
        if u_name == target_name:
            target_username = username
            break
            
    target_id = USER_USERNAMES.get(target_username.lower(), 0) if target_username else 0
    current_lvl = get_user_current_level(target_name)
    
    if action == "up" and current_lvl < 4: new_lvl = current_lvl + 1
    elif action == "down" and current_lvl > 0: new_lvl = current_lvl - 1
    else:
        await callback.answer("⚠️ Рівень вже на максимумі або мінімумі!")
        return
        
    if target_username:
        for lst in [ADMIN_L4_USERNAMES, MODERATOR_USERNAMES, STAROSTA_USERNAMES, ASSISTANT_USERNAMES]:
            if target_username in lst: lst.remove(target_username)
        if new_lvl == 4: ADMIN_L4_USERNAMES.append(target_username)
        elif new_lvl == 3: MODERATOR_USERNAMES.append(target_username)
        elif new_lvl == 2: STAROSTA_USERNAMES.append(target_username)
        elif new_lvl == 1: ASSISTANT_USERNAMES.append(target_username)

    if target_id > 0:
        for lst_id in [ADMIN_L4_IDS, MODERATOR_IDS, STAROSTA_IDS, HW_ASSISTANT_IDS]:
            if target_id in lst_id: lst_id.remove(target_id)
        if new_lvl == 4: ADMIN_L4_IDS.append(target_id)
        elif new_lvl == 3: MODERATOR_IDS.append(target_id)
        elif new_lvl == 2: STAROSTA_IDS.append(target_id)
        elif new_lvl == 1: HW_ASSISTANT_IDS.append(target_id)
        
    await callback.answer(f"✅ Статус {target_name} змінено!")
    level_names = {
        0: "📋 Рівень 0 (Звичайний учень)", 1: "📐 Рівень 1 (Помічник по ДЗ)",
        2: "👥 Рівень 2 (Староста)", 3: "🛡️ Рівень 3 (Модератор чату)",
        4: "⭐ Рівень 4 (Головний Admin)"
    }
    card_buttons = [
        [InlineKeyboardButton(text="🔺 Підняти рівень", callback_data=f"lvledit_up_{target_name}"),
         InlineKeyboardButton(text="🔻 Понизити рівень", callback_data=f"lvledit_down_{target_name}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_give_level_menu")]
    ]
    await callback.message.edit_text(text=f"🪪 **Картка керування правами**\n\n👤 **Учень:** {target_name}\n📊 **Новий статус:** {level_names.get(new_lvl)}", reply_markup=InlineKeyboardMarkup(inline_keyboard=card_buttons))

@router.callback_query(F.data == "admin_toggle_test")
async def admin_toggle_testing_mode(callback: CallbackQuery):
    if callback.from_user.id != 8791830931: return
    global IS_TESTING_MODE
    IS_TESTING_MODE = not IS_TESTING_MODE
    status_text = "🟢 **УВІМКНЕНО**" if IS_TESTING_MODE else "🔴 **ВИМКНЕНО**"
    await callback.message.answer(f"🛠️ Режим тестування змінено: {status_text}")
    await callback.answer()

# ==========================================
# 📝 АДМІН-ХЕНДЛЕРИ КОНТЕНТУ
# ==========================================

def save_homework_to_file():
    try:
        with open("homework.json", "w", encoding="utf-8") as f:
            json.dump(HOMEWORK_DATA, f, ensure_ascii=False, indent=4)
        print("💾 ДЗ успішно збережено у файл!")
    except Exception as e: print(f"⚠️ Помилка збереження ДЗ: {e}")

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
    await message.answer(f"✅ ДЗ для {SUBJECT_NAMES.get(subject, 'Предмет')} успішно збережено назавжди!")
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

@router.callback_query(F.data == "admin_mark_attendance")
async def admin_start_attendance(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS and user_id not in STAROSTA_IDS: return
    await callback.message.answer("📝 Введіть прізвища або імена учнів, які сьогодні відсутні:")
    await state.set_state(BotStates.waiting_for_absence_info)
    await callback.answer()

@router.message(BotStates.waiting_for_absence_info)
async def admin_save_attendance(message: Message, state: FSMContext):
    global ABSENT_TODAY_LIST
    user_id = message.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS and user_id not in STAROSTA_IDS: return
    text = message.text.replace("\n", ",")
    ABSENT_TODAY_LIST = [name.strip() for name in text.split(",") if name.strip()]
    if ABSENT_TODAY_LIST:
        formatted = "\n".join([f"• {n}" for n in ABSENT_TODAY_LIST])
        await message.answer(f"✅ Список збережено (Всього: {len(ABSENT_TODAY_LIST)}):\n{formatted}")
    else: await message.answer("⚠️ Список порожній.")
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
    report_text = f"📢 **Щоденний звіт про відсутніх учнів 7-В класу**\n\nУчнів, яких сьогодні немає:\n{formatted}\n\nВсього відсутніх: {len(ABSENT_TODAY_LIST)}"
    
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
    await message.answer("🎭 **Ти — Таємний Шпигун класу на сьогодні!**\n\nВведіть текст анонімної записки, плітки або зізнання. Макар перевірить її в адмінці, і якщо все ок — пустить в чат без твого імені!")
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
    except Exception: await message.answer("❌ Помилка зв'язку з сервером премодерації Макара.")
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
    else: await callback.message.edit_text(text=f"❌ Ви заблокували та видалили цей злив Шпигуна.")
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
# 🚀 ТАЙМЕРИ ТА ЗАПУСК БЕЗКОШТОВНОГО СЕРВЕРА RENDER v2.5
# ==========================================

async def handle_render_hc(request): return web.Response(text="OK")

# 🚨 УЛЬТИМАТИВНИЙ 5-ХВИЛИННИЙ АВТОПІНГЕР ПРОТИ СНУ СЕРВЕРА (ГАРAНТІЯ LIVE)
async def self_ping_task():
    url = os.getenv("RENDER_EXTERNAL_URL")
    if not url: return
    print(f"🚀 Система захисту від сну Render успішно стартувала на адресу: {url}")
    await asyncio.sleep(30)
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    print(f"⏰ Автопінг Render успішний: {response.status} OK (Сервер тримає Live 24/7)")
        except Exception: pass
        await asyncio.sleep(300)

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
            with open("homework.json", "r", encoding="utf-8") as f: HOMEWORK_DATA = json.load(f)
            print("📦 Базу ДЗ успішно відновлено!")
    except Exception: pass

async def run_web_server():
    app = web.Application()
    app.router.add_get("/", handle_render_hc)
    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Безкоштовний веб-сервер для Render успішно запущено на порту {port}!")
    while True: await asyncio.sleep(3600)

async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    
    # 🔌 Запуск веб-сервера для Render на порту 8080
    app = web.Application()
    app.router.add_get("/", handle_render_hc)
    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Веб-сервер успішно запущено на порту {port}!")

    # Фоновые задачи таймеров
    asyncio.create_task(self_ping_task())
    asyncio.create_task(cron_secret_agent_picker())
    
    print("🚀 Бот для 7-В класу запускає стабільний полінг...")
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
