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

BOT_TOKEN = "8735817305:AAEzAlm9A4H" + "HYu7AojGXV-FI2pB1GcXJS8k"

SUPER_ADMIN_IDS = [8791830931]


ADMIN_L4_USERNAMES = ["@пример_админа_л4"]  
MODERATOR_USERNAMES = []                     
STAROSTA_USERNAMES = []                      
ASSISTANT_USERNAMES = []                     
TESTER_USERNAMES = []                        

TEACHER_USERNAME = "@victoria197198"


ADMIN_L4_IDS = []
MODERATOR_IDS = []
HW_ASSISTANT_IDS = []
STAROSTA_IDS = []
TESTER_IDS = []
TEACHER_CHAT_ID = 0


USER_TELEGRAM_NAMES = {8791830931: "Макар"}
USER_USERNAMES = {}


CHAT_REGISTERED_USERS = {}  
BANNED_USERS = []           
MUTED_USERS = {}            


USER_BALANCES = {}          
USER_LAST_CASE = {}         
USER_CUSTOM_TAGS = {}       
USER_ITEMS = {}             

CURRENT_SECRET_AGENT_ID = 0   
AGENT_HAS_SENT_SECRET = False  

IS_TESTING_MODE = False
IMPORTANT_ANNOUNCEMENT = "📌 **Важливі оголошення:**\n\nНаразі немає нових оголошень від адміністрації або Бакланової Вікторії Олександрівни."
BOOKS_DATA = "📚 **Електронні підручники для 7-В класу (НУШ):**\n\nСкористайтеся меню налаштувань або введіть запити в Гугл з командою site:pidruchnyk.com.ua"
ABSENT_TODAY_LIST = []
RANDOM_MODE = "dice"
HOMEWORK_DATA = {}          


RANDOM_NAMES = [
    "Олександр", "Андрій", "Данило", "Колодинський Богдан", "Ковальчук Богдан", 
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

SCHEDULE_DATA = {
    "mon": "🗓️ **Понеділок:**\n1. ЗБД / Зар. літ.\n2. Фізика\n3. Фізкультура\n4. Укр. література\n5. Алгебра\n6. Англійська\n7. Географія",
    "tue": "🗓️ **Вівторок:**\n1. Історія України\n2. Біологія\n3. Геометрія\n4. Укр. мова\n5. ЗБД\n6. Інформатика\n7. Технології",
    "wed": "🗓️ **Середа:**\n1. Укр. мова\n2. Хімія\n3. Зар. література\n4. Фізкультура\n5. Алгебра\n6. Англійська\n7. Географія",
    "thu": "🗓️ **Четвер:**\n1. Англ. / Біологія\n2. Фізика\n3. Мистецтво\n4. Укр. мова\n5. Геометрія\n6. Інформатика\n7. Всесвітня історія",
    "fri": "🗓️ **П'ятниця:**\n1. Історія України\n2. Мистецтво\n3. Англійська\n4. Укр. література\n5. Фізкультура\n6. Біологія\n7. Алгебра"
}

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
        keyboard.append([InlineKeyboardButton(text="👑 Налаштувати рівні доступу", callback_data="admin_give_level_menu"),
                         InlineKeyboardButton(text="🏆 Керувати досягненнями", callback_data="admin_manage_ach")])
    if user_id == 8791830931:
        keyboard.append([InlineKeyboardButton(text="🧪 Тест-Режим: ON/ОFF", callback_data="admin_toggle_test")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

settings_interactive_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏆 Досягнення", callback_data="profile_achievements"), InlineKeyboardButton(text="🔮 Передбачення", callback_data="profile_prediction")],
    [InlineKeyboardButton(text="🎁 Щоденний Подарунок", callback_data="economy_get_gift"), InlineKeyboardButton(text="🛒 Магазин Сімок", callback_data="economy_open_shop")],
    [InlineKeyboardButton(text="🎰 Слот-Машина", callback_data="economy_open_slots"), InlineKeyboardButton(text="📈 Біржа 7-V", callback_data="economy_open_stocks")],
    [InlineKeyboardButton(text="🔔 Дзвінки", callback_data="profile_bells"), InlineKeyboardButton(text="📜 Лог оновлень", callback_data="profile_changelog")]
])

async def send_human_message(message: Message, text: str, reply_markup=None):
    return await message.answer(text, reply_markup=reply_markup)

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    
 user_id not in USER_BALANCES:
        USER_BALANCES[user_id] = 10  
    
    if username:
        user_key = f"@{username.lower()}"
        USER_USERNAMES[user_key] = user_id
        if user_key in ADMIN_L4_USERNAMES and user_id not in ADMIN_L4_IDS: ADMIN_L4_IDS.append(user_id)
        if user_key in MODERATOR_USERNAMES and user_id not in MODERATOR_IDS: MODERATOR_IDS.append(user_id)
        if user_key in STAROSTA_USERNAMES and user_id not in STAROSTA_IDS: STAROSTA_IDS.append(user_id)
        if user_key in ASSISTANT_USERNAMES and user_id not in HW_ASSISTANT_IDS: HW_ASSISTANT_IDS.append(user_id)
        if user_key in TESTER_USERNAMES and user_id not in TESTER_IDS: TESTER_IDS.append(user_id)
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
    await callback.answer()
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

async def ask_free_ai(question: str) -> str:
    encoded_prompt = aiohttp.helpers.urlencode({"prompt": f"Ти помічник для 7-В класу. Тобі пише учень. Відповідай чітко, коротко, виключно українською мовою. Питання: {question}"})
    url = f"https://pollinations.ai?{encoded_prompt}&model=openai"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    text_response = await response.text()
                    if text_response.strip(): return text_response.strip()
                return "⚠️ Сервер ШІ трохи задумався, надішли питання ще раз!"
    except Exception:
        return "❌ ШІ тимчасово відпочиває. Спробуй ще раз за пару секунд!"



@router.callback_query(F.data == "economy_get_gift")
async def process_get_daily_gift(callback: CallbackQuery):
    user_id = callback.from_user.id
    now = datetime.now().timestamp()
    if user_id in USER_LAST_CASE and now - USER_LAST_CASE[user_id] < 86400:
        time_left = int((86400 - (now - USER_LAST_CASE[user_id])) / 3600)
        await callback.message.answer(f"🎁 **Опа, зачекай!**\n\nТи вже забрав свій підгін. Наступний куш доступний через **{time_left if time_left > 0 else 1} god.**")
        await callback.answer(); return
    gift_coins = random.randint(2, 20)
    if user_id not in USER_BALANCES: USER_BALANCES[user_id] = 0
    USER_BALANCES[user_id] += gift_coins
    USER_LAST_CASE[user_id] = now
    await callback.message.answer(f"🎁 **Щоденний Подарунок активовано!**\n\n🎰 Тобі випало: **+{gift_coins} Сімок** 🪙!\n💰 Баланс: **{USER_BALANCES[user_id]} Сімок**.")
    await callback.answer()

@router.message(F.text == "🔊 Чат класу")
async def enter_chat_room(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in BANNED_USERS:
        await message.answer("🛑 **Доступ заблоковано!** Ви забанені в чаті.")
        return
    name = USER_TELEGRAM_NAMES.get(user_id, message.from_user.first_name if message.from_user.first_name else "Учень")
    CHAT_REGISTERED_USERS[user_id] = name
    await state.set_state(BotStates.user_in_chat_window)
    await message.answer(f"💬 **Ласкаво просимо до чату 7-В класу, {name}!**\n\n✍️ Пиши сюди повідомлення, і його побачать усі однокласники!", reply_markup=get_chat_exit_menu())

@router.message(BotStates.user_in_chat_window, F.text == "🚪 Вийти з чату")
async def exit_chat_room(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in CHAT_REGISTERED_USERS: CHAT_REGISTERED_USERS.pop(user_id)
    await state.clear()
    await send_human_message(message, "🚪 Ви вийшли з чату. Повертаюсь до меню:", reply_markup=get_main_menu(user_id))

@router.message(BotStates.user_in_chat_window)
async def process_live_chat_message(message: Message):
    user_id = message.from_user.id
    if message.text == "🚪 Вийти з чату": return
    if user_id in BANNED_USERS: return
    if user_id in MUTED_USERS and datetime.now().timestamp() < MUTED_USERS[user_id]:
        time_left = int((MUTED_USERS[user_id] - datetime.now().timestamp()) / 60)
        await message.answer(f"🤫 **У вас МУТ!** Буде знято через **{time_left if time_left > 0 else 1} хв.**"); return
    sender_name = CHAT_REGISTERED_USERS.get(user_id, "Учень")
    custom_tag = USER_CUSTOM_TAGS.get(user_id, "")
    prefix_text = f"[{custom_tag}] " if custom_tag else ""
    for target_id in list(CHAT_REGISTERED_USERS.keys()):
        if target_id != user_id:
            try: await bot.send_message(chat_id=target_id, text=f"💬 **{prefix_text}{sender_name}:** {message.text}")
            except Exception: pass
    all_admins = set(SUPER_ADMIN_IDS + ADMIN_L4_IDS + MODERATOR_IDS + HW_ASSISTANT_IDS)
    punish_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🤫 Мут 15 хв", callback_data=f"mute_15_{user_id}_{sender_name}"), InlineKeyboardButton(text="🛑 БАН у чаті", callback_data=f"ban_{user_id}_{sender_name}")]])
    for admin_id in all_admins:
        try: await bot.send_message(chat_id=admin_id, text=f"👁️ **[ЧАТЛОГ] {prefix_text}{sender_name}:** {message.text}", reply_markup=punish_keyboard)
        except Exception: pass


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
        text="📜 **Офіційні оновлення бота (Версія v2.6 Olympic):**\n\n"
             "• 📚 **Повний розклад 7-В класу:** Додано абсолютно всі пропущені уроки. Тепер Історія України, Всесвітня історія, Мистецтво, ЗБД, Зарубіжна література та Технології на місці!\n\n"
             "• 📝 **Вічне збереження ДЗ:** Запущено локальну JSON базу даних. Введене адмінами домашнє завдання більше НІКОЛИ не злітає при перезапусках сервера.\n\n"
             "• 👑 **Керування правами на ходу:** Повністю виправлено адмін-панель. Кнопки підвищення та пониження рівнів тепер миттєво змінюють права учнів у пам'яті бота.\n\n"
             "• 🪙 **Економіка Сімок та Магазин:** Збирай щоденні подарунки, купуй Шпаргалки для дуелей, Анти-Мути або свій Кастомний Тег у чаті назавжди.\n\n"
             "• 🎰 **Казино 'У Макара' та Біржа:** Випробуй удачу на слот-машині за 5 сімок або інвестуй у акції шкільних уроків з динамічним курсом.\n\n"
             "• 🎭 **Таємний Шпигун:** Бот раз на добу анонімно обирає одного учня для секретного зливу пліток через премодерацію Макара.",
        reply_markup=settings_interactive_menu
    )

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
    
    msg = await callback.message.answer("🎰 **Казино «У Макара»**\n\n🎰 *Барабани крутяться: [ 🔄 | 🔄 | 🔄 ]*")
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

@router.callback_query(F.data == "economy_open_shop")
async def process_open_shop(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_coins = USER_BALANCES.get(user_id, 0)
    shop_buttons = [
        [InlineKeyboardButton(text="🃏 Шпаргалка (50 Сімок)", callback_data="buy_shpora")],
        [InlineKeyboardButton(text="🛡️ Anti-Мут (100 Сімок)", callback_data="buy_antimut")],
        [InlineKeyboardButton(text="🏷️ Власний Тег у чаті (150 Сімок)", callback_data="buy_customtag")],
        [InlineKeyboardButton(text="🏆 Купити Досягнення (250 Сімок)", callback_data="buy_achievement_pack")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="economy_back_to_settings")]
    ]
    await callback.message.edit_text(
        text=f"🛒 **Магазин луту 7-В класу**\n\n💰 Твій баланс: **{user_coins} Сімок**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=shop_buttons)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("buy_"))
async def process_buy_item(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    item = callback.data.replace("buy_", "")
    user_coins = USER_BALANCES.get(user_id, 0)
    
    prices = {"shpora": 50, "antimut": 100, "customtag": 150, "achievement_pack": 250}
    price = prices.get(item, 999)
    
    if user_coins < price:
        await callback.message.answer(f"❌ **Помилка фінансів!** Тобі не вистачає Сімок! Потрібно: {price} 🪙.")
        await callback.answer()
        return
        
    USER_BALANCES[user_id] -= price
    
    tax_amount = int(price * 0.3)
    USER_BALANCES[8791830931] = USER_BALANCES.get(8791830931, 0) + tax_amount
    for l4_id in ADMIN_L4_IDS:
        if l4_id != 8791830931:
            USER_BALANCES[l4_id] = USER_BALANCES.get(l4_id, 0) + tax_amount

    if item == "shpora":
        if user_id not in USER_ITEMS: USER_ITEMS[user_id] = []
        USER_ITEMS[user_id].append("shpora")
        await callback.message.answer(f"🃏 **Купівля успішна!** Придбано Шпаргалку (+30% до дуелей).\n💸 Макару та Адмінам сплачено податок: **{tax_amount} Сімок**!")
    elif item == "antimut":
        if user_id not in USER_ITEMS: USER_ITEMS[user_id] = []
        USER_ITEMS[user_id].append("antimut")
        await callback.message.answer(f"🛡️ **Купівля успішна!** Придбано Одноразовий Анти-Мут.\n💸 Макару та Адмінам сплачено податок: **{tax_amount} Сімок**!")
    elif item == "customtag":
        await callback.message.answer(f"🏷️ **Купівля успішна!** Сплачено податок {tax_amount} 🪙.\nВведіть текст вашого кастомного тегу (до 15 символів):")
        await state.set_state(BotStates.waiting_for_custom_tag)
    elif item == "achievement_pack":
        await callback.message.answer("💸 **250 Сімок зарезервовано!**\n\n✍️ Тепер введіть текст досягнення (з емодзі), яке ви хочете собі купити. Запит відправиться Макару на перевірку!")
        await state.set_state(BotStates.admin_input_achievement)
        await state.update_data(buyer_user_id=user_id, buyer_tax=tax_amount)
        
    await callback.answer()


@router.message(BotStates.waiting_for_custom_tag)
async def process_save_custom_tag(message: Message, state: FSMContext):
    user_id = message.from_user.id
    tag_text = message.text.strip().replace("[", "").replace("]", "")
    if len(tag_text) > 15:
        await message.answer("❌ Задовгий тег! Введи коротший:")
        return
    USER_CUSTOM_TAGS[user_id] = tag_text
    await message.answer(f"✅ Встановлено тег: `[{tag_text}]` 🏷️!")
    await state.clear()

@router.callback_query(F.data == "economy_open_stocks")
async def process_open_stocks(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_coins = USER_BALANCES.get(user_id, 0)
    minute, hour = datetime.now().minute, datetime.now().hour
    price_stolovka = max(5, int(20 + (minute % 7) * 4 - (hour % 3) * 2))
    price_fizra = max(5, int(15 + (minute % 5) * 5 + (hour % 2) * 3))
    price_ai = max(10, int(40 + (minute % 9) * 6 - (hour % 4) * 4))
    stock_buttons = [
        [InlineKeyboardButton(text=f"🍔 Столова: {price_stolovka} 🪙", callback_data="stk_none"), 
         InlineKeyboardButton(text="🟢 Купити", callback_data=f"stk_buy_stolovka_{price_stolovka}"), 
         InlineKeyboardButton(text="🔴 Продати", callback_data=f"stk_sell_stolovka_{price_stolovka}")],
        [InlineKeyboardButton(text=f"🏃 Фізра: {price_fizra} 🪙", callback_data="stk_none"), 
         InlineKeyboardButton(text="🟢 Купити", callback_data=f"stk_buy_fizra_{price_fizra}"), 
         InlineKeyboardButton(text="🔴 Продати", callback_data=f"stk_sell_fizra_{price_fizra}")],
        [InlineKeyboardButton(text=f"🤖 ШІ-Помічник: {price_ai} 🪙", callback_data="stk_none"), 
         InlineKeyboardButton(text="🟢 Купити", callback_data=f"stk_buy_ai_{price_ai}"), 
         InlineKeyboardButton(text="🔴 Продати", callback_data=f"stk_sell_ai_{price_ai}")],
        [InlineKeyboardButton(text="🔄 Оновити курс акцій", callback_data="economy_open_stocks")], 
        [InlineKeyboardButton(text="🔙 Назад", callback_data="economy_back_to_settings")]
    ]
    await callback.message.edit_text(text=f"📈 **Економічна Біржа 7-В класу**\n\n💰 Твій баланс: **{user_coins} Сімок** 🪙\n📊 Курс змінюється щохвилини!", reply_markup=InlineKeyboardMarkup(inline_keyboard=stock_buttons))
    await callback.answer()

@router.callback_query(F.data.startswith("stk_buy_"))
async def process_buy_stock(callback: CallbackQuery):
    user_id = callback.from_user.id
    raw_data = callback.data.replace("stk_buy_", "").split("_")
    if len(raw_data) < 2: await callback.answer("⚠️ Помилка!"); return
    stock_name, price = raw_data[0], int(raw_data[1])
    if USER_BALANCES.get(user_id, 0) < price: await callback.message.answer("❌ Недостатньо Сімок!"); await callback.answer(); return
    USER_BALANCES[user_id] -= price
    if user_id not in USER_ITEMS: USER_ITEMS[user_id] = []
    USER_ITEMS[user_id].append(f"stock_{stock_name}")
    await callback.message.answer(f"📈 **Угода успішна!** Придбано 1 акцію **{stock_name.upper()}** за **{price} Сімок**!"); await callback.answer()

@router.callback_query(F.data.startswith("stk_sell_"))
async def process_sell_stock(callback: CallbackQuery):
    user_id = callback.from_user.id
    raw_data = callback.data.replace("stk_sell_", "").split("_")
    if len(raw_data) < 2: await callback.answer("⚠️ Помилка!"); return
    stock_name, price = raw_data[0], int(raw_data[1])
    stock_key = f"stock_{stock_name}"
    if user_id not in USER_ITEMS or stock_key not in USER_ITEMS[user_id]: await callback.message.answer("❌ У тебе немає цих акцій!"); await callback.answer(); return
    USER_ITEMS[user_id].remove(stock_key)
    USER_BALANCES[user_id] = USER_BALANCES.get(user_id, 0) + price
    await callback.message.answer(f"📈 **Угода успішна!** Продано 1 акцію **{stock_name.upper()}** за **{price} Сімок**!"); await callback.answer()


def get_user_current_level(name: str) -> int:
    target_username = ""
    for username, u_name in USER_USERNAMES_TEXT.items():
        if u_name == name: target_username = username; break
    if not target_username: return 0
    if target_username in ADMIN_L4_USERNAMES: return 4
    if target_username in MODERATOR_USERNAMES: return 3
    if target_username in STAROSTA_USERNAMES: return 2
    if target_username in ASSISTANT_USERNAMES: return 1
    return 0

@router.callback_query(F.data == "admin_give_level_menu")
async def admin_start_give_level(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS: return
    buttons = [[InlineKeyboardButton(text=name, callback_data=f"lvluser_{name}")] for name in RANDOM_NAMES]
    await callback.message.answer("👥 **Оберіть учня для права доступу:**", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@router.callback_query(F.data.startswith("lvluser_"))
async def process_level_user_card(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS: return
    await callback.answer()
    name = callback.data.replace("lvluser_", "")
    current_lvl = get_user_current_level(name)
    level_names = {0: "📋 Рівень 0 (Учень)", 1: "📐 Рівень 1 (Помічник)", 2: "👥 Рівень 2 (Староста)", 3: "🛡️ Рівень 3 (Модератор)", 4: "⭐ Рівень 4 (Admin)"}
    card_buttons = [[InlineKeyboardButton(text="🔺 Підняти", callback_data=f"lvledit_up_{name}"), InlineKeyboardButton(text="🔻 Понизити", callback_data=f"lvledit_down_{name}")], [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_give_level_menu")]]
    await callback.message.edit_text(text=f"🪪 **Картка керування правами**\n\n👤 **Учень:** {name}\n📊 **Статус:** {level_names.get(current_lvl)}", reply_markup=InlineKeyboardMarkup(inline_keyboard=card_buttons))

@router.callback_query(F.data.startswith("lvledit_"))
async def process_dynamic_level_change(callback: CallbackQuery):
    admin_id = callback.from_user.id
    if admin_id != 8791830931 and admin_id not in ADMIN_L4_IDS: return
    raw_cmd = callback.data.replace("lvledit_", "").split("_")
    if len(raw_cmd) < 2: return
    
    action = raw_cmd[0]
    target_name = raw_cmd[1]
    
    target_username = ""
    for username, u_name in USER_USERNAMES_TEXT.items():
        if u_name == target_name: target_username = username; break
    current_lvl = get_user_current_level(target_name)
    if action == "up" and current_lvl < 4: new_lvl = current_lvl + 1
    elif action == "down" and current_lvl > 0: new_lvl = current_lvl - 1
    else: await callback.answer("⚠️ Границя!"); return
    
    if not target_username:
        target_username = f"@{target_name.lower()}_temp"
        USER_USERNAMES_TEXT[target_username] = target_name
    for lst in [ADMIN_L4_USERNAMES, MODERATOR_USERNAMES, STAROSTA_USERNAMES, ASSISTANT_USERNAMES]:
        if target_username in lst: lst.remove(target_username)
    if new_lvl == 4: ADMIN_L4_USERNAMES.append(target_username)
    elif new_lvl == 3: MODERATOR_USERNAMES.append(target_username)
    elif new_lvl == 2: STAROSTA_USERNAMES.append(target_username)
    elif new_lvl == 1: ASSISTANT_USERNAMES.append(target_username)
    
    target_id = USER_USERNAMES.get(target_username.lower(), 0)
    if target_id > 0:
        for lst_id in [ADMIN_L4_IDS, MODERATOR_IDS, STAROSTA_IDS, HW_ASSISTANT_IDS]:
            if target_id in lst_id: lst_id.remove(target_id)
        if new_lvl == 4: ADMIN_L4_IDS.append(target_id)
        elif new_lvl == 3: MODERATOR_IDS.append(target_id)
        elif new_lvl == 2: STAROSTA_IDS.append(target_id)
        elif new_lvl == 1: HW_ASSISTANT_IDS.append(target_id)
        
    await callback.answer(f"✅ Статус {target_name} змінено на Рівень {new_lvl}!")
    level_names = {0: "📋 Рівень 0 (Учень)", 1: "📐 Рівень 1 (Помічник)", 2: "👥 Рівень 2 (Староста)", 3: "🛡️ Рівень 3 (Модератор)", 4: "⭐ Рівень 4 (Admin)"}
    card_buttons = [[InlineKeyboardButton(text="🔺 Підняти", callback_data=f"lvledit_up_{target_name}"), InlineKeyboardButton(text="🔻 Понизити", callback_data=f"lvledit_down_{target_name}")], [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_give_level_menu")]]
    await callback.message.edit_text(text=f"🪪 **Картка керування правами**\n\n👤 **Учень:** {target_name}\n📊 **Новий статус:** {level_names.get(new_lvl)}", reply_markup=InlineKeyboardMarkup(inline_keyboard=card_buttons))

def save_homework_to_file():
    try:
        with open("homework.json", "w", encoding="utf-8") as f: json.dump(HOMEWORK_DATA, f, ensure_ascii=False, indent=4)
    except Exception: pass

@router.callback_query(F.data == "admin_add_hw")
async def admin_choose_subject_hw(callback: CallbackQuery):
    if callback.from_user.id != 8791830931 and callback.from_user.id not in ADMIN_L4_IDS and callback.from_user.id not in STAROSTA_IDS and callback.from_user.id not in HW_ASSISTANT_IDS: return
    await callback.answer()
    await callback.message.edit_text(text="Оберіть предмет, для якого хочете змінити ДЗ:", reply_markup=get_subjects_menu("ehw"))

@router.callback_query(F.data.startswith("ehw_"))
async def admin_input_hw_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    subject = callback.data.replace("ehw_", "")
    await state.update_data(chosen_subject=subject)
    await callback.message.answer(f"📝 **[ВВЕДЕННЯ ДЗ]** Введіть новий текст ДЗ для предмета {SUBJECT_NAMES.get(subject, 'Предмет')}:")
    await state.set_state(BotStates.waiting_for_hw_text)

@router.message(BotStates.waiting_for_hw_text)
async def admin_save_hw_text(message: Message, state: FSMContext):
    data = await state.get_data()
    subject = data.get("chosen_subject")
    HOMEWORK_DATA[subject] = message.text
    save_homework_to_file()
    await message.answer(f"✅ ДЗ для {SUBJECT_NAMES.get(subject, 'Предмет')} успішно оновлено та збережено назавжди!")
    await state.clear()

@router.callback_query(F.data == "admin_edit_sch")
async def admin_choose_day_sch(callback: CallbackQuery):
    if callback.from_user.id != 8791830931 and callback.from_user.id not in ADMIN_L4_IDS and callback.from_user.id not in STAROSTA_IDS: return
    await callback.answer()
    await callback.message.edit_text(text="Оберіть день для зміни розкладу:", reply_markup=get_days_menu("esch"))

@router.callback_query(F.data.startswith("esch_"))
async def admin_input_sch_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    day = callback.data.replace("esch_", "")
    await state.update_data(chosen_day=day)
    await callback.message.answer(f"🗓️ **[ВВЕДЕННЯ РОЗКЛАДУ]** Введіть новий розклад для дня ({DAY_NAMES.get(day, 'День')}):")
    await state.set_state(BotStates.waiting_for_schedule_text)

@router.message(BotStates.waiting_for_schedule_text)
async def admin_save_sch_text(message: Message, state: FSMContext):
    data = await state.get_data()
    day = data.get("chosen_day")
    SCHEDULE_DATA[day] = message.text
    await message.answer(f"✅ Розклад на {DAY_NAMES.get(day, 'День')} успішно змінено!")
    await state.clear()

@router.callback_query(F.data == "admin_add_important")
async def admin_start_edit_important(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("📌 **[ОГОЛОШЕННЯ]** Введіть новий текст для розділу 'Важливе':")
    await state.set_state(BotStates.waiting_for_important_text)

@router.message(BotStates.waiting_for_important_text)
async def admin_save_important_text(message: Message, state: FSMContext):
    global IMPORTANT_ANNOUNCEMENT
    IMPORTANT_ANNOUNCEMENT = message.text
    await message.answer("✅ **Розділ 'Важливе' успішно оновлено!**")
    await state.clear()

@router.callback_query(F.data == "admin_edit_books")
async def admin_start_edit_books(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("📚 **[БІБЛІОТЕКА]** Введіть новий текст або посилання для розділу 'Книги':")
    await state.set_state(BotStates.waiting_for_books_text)

@router.message(BotStates.waiting_for_books_text)
async def admin_save_books_text(message: Message, state: FSMContext):
    global BOOKS_DATA
    BOOKS_DATA = message.text
    await message.answer("✅ **Список підручників успішно оновлено!**")
    await state.clear()

@router.callback_query(F.data == "admin_toggle_test")
async def admin_toggle_testing_mode(callback: CallbackQuery):
    if callback.from_user.id != 8791830931: return
    global IS_TESTING_MODE
    IS_TESTING_MODE = not IS_TESTING_MODE
    status_text = "🟢 ON" if IS_TESTING_MODE else "🔴 OFF"
    await callback.message.edit_text(text=f"🛠️ Тест-Режим змінено: {status_text}", reply_markup=get_admin_menu_keyboard(callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == "profile_bells")
async def process_smart_school_bells(callback: CallbackQuery):
    await callback.answer()
    from datetime import timedelta
    now = datetime.now() + timedelta(hours=3)
    weekday = now.weekday()
    if weekday >= 5:
        await callback.message.edit_text(text="🛌 **Зараз немає уроків!**\n\nНе заглядуй сюди, коли немає навчання, йди відпочивай! Сьогодні вихідний! 🎉", reply_markup=settings_interactive_menu)
        return
    ua_hour = now.hour
    current_minutes = ua_hour * 60 + now.minute
    schedule_blocks = [
        {"lesson": 1, "start": 8*60+30, "end": 9*60+15},
        {"lesson": 2, "start": 9*60+35, "end": 10*60+20},
        {"lesson": 3, "start": 10*60+40, "end": 11*60+25},
        {"lesson": 4, "start": 11*60+45, "end": 12*60+30},
        {"lesson": 5, "start": 12*60+50, "end": 13*60+35},
        {"lesson": 6, "start": 13*60+45, "end": 14*60+30},
        {"lesson": 7, "start": 14*60+40, "end": 15*60+25}
    ]
    if current_minutes < schedule_blocks[0]["start"]:
        await callback.message.edit_text(text="☕ **Навчання ще не почалося!** Уроки стартують о 08:30. Не заглядуй сюди завчасно! 😉", reply_markup=settings_interactive_menu)
        return
    if current_minutes > schedule_blocks[-1]["end"]:
        await callback.message.edit_text(text="🎒 **Зараз немає уроків!** Всі уроки на сьогодні закінчилися! Не заглядуй сюди, коли немає навчання, йди гуляти на вулицю! 🛑🔥", reply_markup=settings_interactive_menu)
        return
    for block in schedule_blocks:
        if block["start"] <= current_minutes <= block["end"]:
            await callback.message.edit_text(text=f"📚 **ЗАРАЗ ЙДЕ {block['lesson']}-й УРОК!**\n\n⏱️ Урок закінчиться о **{int(block['end']/60):02d}:{block['end']%60:02d}**.\n\nПовністю фокусуйся на навчанні, відклади телефон і **іди вчись, не відволікайся!** 👨‍💻❌📱", reply_markup=settings_interactive_menu)
            return
    await callback.message.edit_text(text="🍕 **ЗАРАЗ ІДЕ ПЕРЕРВА!** Уроку немає, відпочивай! Сходи в їдальню за булочкою, подихай свіжим повітрям і готуйся до наступного уроку! 🏃‍♂️💨", reply_markup=settings_interactive_menu)


@router.callback_query(F.data == "economy_back_to_settings")
async def process_back_to_settings_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(text="⚙️ Налаштування та інтерактив:", reply_markup=settings_interactive_menu)

async def handle_render_hc(request): return web.Response(text="OK")

async def self_ping_task():
    url = os.getenv("RENDER_EXTERNAL_URL")
    if not url: return
    await asyncio.sleep(30)
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp: print(f"⏰ Автопінг Render: {resp.status} OK")
        except Exception: pass
        await asyncio.sleep(300)

async def cron_secret_agent_picker():
    global CURRENT_SECRET_AGENT_ID, AGENT_HAS_SENT_SECRET
    while True:
        await asyncio.sleep(86400)
        if USER_USERNAMES: CURRENT_SECRET_AGENT_ID = random.choice(list(USER_USERNAMES.values())); AGENT_HAS_SENT_SECRET = False

def restore_homework_from_file():
    global HOMEWORK_DATA
    try:
        if os.path.exists("homework.json"):
            with open("homework.json", "r", encoding="utf-8") as f: HOMEWORK_DATA = json.load(f)
    except Exception: pass

async def run_web_server():
    app = web.Application(); app.router.add_get("/", handle_render_hc)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080))).start()
    while True: await asyncio.sleep(3600)

@router.message(F.text == "🛠️ Admin Panel")
async def handle_admin_panel(message: Message):
    user_id = message.from_user.id
    if user_id == 8791830931:
        await message.answer(text="🛠️ **Вітаємо, Макаре! Функції Розробника v2.6:**", reply_markup=get_admin_menu_keyboard(user_id)); return
    all_protected_ids = []
    for s in [ADMIN_L4_IDS, MODERATOR_IDS, HW_ASSISTANT_IDS, STAROSTA_IDS, TESTER_IDS]:
        if s: all_protected_ids.extend(s)
    if user_id in all_protected_ids or user_id == TEACHER_CHAT_ID:
        await message.answer(text="🛠️ **Панель Адміністратора:**", reply_markup=get_admin_menu_keyboard(user_id))
    else: await message.answer("🛑 Немає доступу.")


def save_homework_to_file():
    try:
        with open("homework.json", "w", encoding="utf-8") as f: 
            json.dump(HOMEWORK_DATA, f, ensure_ascii=False, indent=4)
    except Exception: pass

@router.callback_query(F.data == "admin_add_hw")
async def admin_choose_subject_hw(callback: CallbackQuery):
    if callback.from_user.id != 8791830931 and callback.from_user.id not in ADMIN_L4_IDS and callback.from_user.id not in STAROSTA_IDS and callback.from_user.id not in HW_ASSISTANT_IDS: return
    await callback.answer()
    await callback.message.edit_text(text="Оберіть предмет, для якого хочете змінити ДЗ:", reply_markup=get_subjects_menu("ehw"))

@router.callback_query(F.data.startswith("ehw_"))
async def admin_input_hw_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    subject = callback.data.replace("ehw_", "")
    await state.update_data(chosen_subject=subject)
    await callback.message.answer(f"📝 **[ВВЕДЕННЯ ДЗ]** Введіть новий текст ДЗ для предмета {SUBJECT_NAMES.get(subject, 'Предмет')}:")
    await state.set_state(BotStates.waiting_for_hw_text)

@router.message(BotStates.waiting_for_hw_text)
async def admin_save_hw_text(message: Message, state: FSMContext):
    data = await state.get_data()
    subject = data.get("chosen_subject")
    HOMEWORK_DATA[subject] = message.text
    save_homework_to_file()
    await message.answer(f"✅ ДЗ для {SUBJECT_NAMES.get(subject, 'Предмет')} успішно оновлено та збережено назавжди!")
    await state.clear()

@router.callback_query(F.data == "admin_edit_sch")
async def admin_choose_day_sch(callback: CallbackQuery):
    if callback.from_user.id != 8791830931 and callback.from_user.id not in ADMIN_L4_IDS and callback.from_user.id not in STAROSTA_IDS: return
    await callback.answer()
    await callback.message.edit_text(text="Оберіть день для зміни розкладу:", reply_markup=get_days_menu("esch"))

@router.callback_query(F.data.startswith("esch_"))
async def admin_input_sch_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    day = callback.data.replace("esch_", "")
    await state.update_data(chosen_day=day)
    await callback.message.answer(f"🗓️ **[ВВЕДЕННЯ РОЗКЛАДУ]** Введіть новий розклад для дня ({DAY_NAMES.get(day, 'День')}):")
    await state.set_state(BotStates.waiting_for_schedule_text)

@router.message(BotStates.waiting_for_schedule_text)
async def admin_save_sch_text(message: Message, state: FSMContext):
    data = await state.get_data()
    day = data.get("chosen_day")
    SCHEDULE_DATA[day] = message.text
    await message.answer(f"✅ Розклад на {DAY_NAMES.get(day, 'День')} успішно змінено!")
    await state.clear()

@router.callback_query(F.data == "admin_add_important")
async def admin_start_edit_important(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("📌 **[ОГОЛОШЕННЯ]** Введіть новий текст для розділу 'Важливе':")
    await state.set_state(BotStates.waiting_for_important_text)

@router.message(BotStates.waiting_for_important_text)
async def admin_save_important_text(message: Message, state: FSMContext):
    global IMPORTANT_ANNOUNCEMENT
    IMPORTANT_ANNOUNCEMENT = message.text
    await message.answer("✅ **Розділ 'Важливе' успішно оновлено!**")
    await state.clear()

@router.callback_query(F.data == "admin_edit_books")
async def admin_start_edit_books(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("📚 **[БІБЛІОТЕКА]** Введіть новий текст або посилання для розділу 'Книги':")
    await state.set_state(BotStates.waiting_for_books_text)

@router.message(BotStates.waiting_for_books_text)
async def admin_save_books_text(message: Message, state: FSMContext):
    global BOOKS_DATA
    BOOKS_DATA = message.text
    await message.answer("✅ **Список підручників успішно оновлено!**")
    await state.clear()

@router.callback_query(F.data == "admin_toggle_test")
async def admin_toggle_testing_mode(callback: CallbackQuery):
    if callback.from_user.id != 8791830931: return
    global IS_TESTING_MODE
    IS_TESTING_MODE = not IS_TESTING_MODE
    status_text = "🟢 ОН" if IS_TESTING_MODE else "🔴 ОФФ"
    await callback.message.edit_text(text=f"🛠️ Тест-Режим змінено: {status_text}", reply_markup=get_admin_menu_keyboard(callback.from_user.id))
    await callback.answer()

@router.callback_query(F.data == "admin_mark_attendance")
async def admin_start_attendance(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS and user_id not in STAROSTA_IDS: return
    await callback.answer()
    await callback.message.answer("📝 **[ВІДВІДУВАННІСТЬ]** Введіть прізвища або імена учнів, які сьогодні відсутні (через кому або з нового рядка):")
    await state.set_state(BotStates.waiting_for_absence_info)

@router.message(BotStates.waiting_for_absence_info)
async def admin_save_attendance(message: Message, state: FSMContext):
    global ABSENT_TODAY_LIST
    user_id = message.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS and user_id not in STAROSTA_IDS: return
    text = message.text.replace("\n", ",")
    ABSENT_TODAY_LIST = [name.strip() for name in text.split(",") if name.strip()]
    if ABSENT_TODAY_LIST:
        formatted = "\n".join([f"• {n}" for n in ABSENT_TODAY_LIST])
        await message.answer(f"✅ **Список збережено!** (Всього відсутніх: {len(ABSENT_TODAY_LIST)}):\n\n{formatted}")
    else:
        await message.answer("⚠️ Список порожній.")
    await state.clear()

@router.callback_query(F.data == "admin_send_report")
async def admin_send_report_to_teacher(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS and user_id not in STAROSTA_IDS: return
    if not ABSENT_TODAY_LIST:
        await callback.message.answer("⚠️ Список відсутніх порожній! Спочатку відмітьте прогульників.")
        await callback.answer()
        return
    formatted = "\n".join([f"• {name}" for name in ABSENT_TODAY_LIST])
    report_text = f"📢 **Щоденний звіт про відсутніх учнів 7-В класу**\n\nУчнів, яких сьогодні немає:\n{formatted}\n\nВсього відсутніх: {len(ABSENT_TODAY_LIST)}"
    target_chat_id = TEACHER_CHAT_ID if TEACHER_CHAT_ID else 8791830931
    try:
        await bot.send_message(chat_id=target_chat_id, text=report_text)
        await callback.message.answer("🚀 **Звіт успішно надіслано в особисті повідомлення Баклановій Вікторії Олександрівні!**")
    except Exception:
        await callback.message.answer("❌ **Помилка відправки!** Класний керівник ще не запустив бота або заблокував його.")
    await callback.answer()

@router.callback_query(F.data == "admin_manage_ach")
async def admin_start_manage_achievements(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS: return
    await callback.answer()
    buttons = [[InlineKeyboardButton(text=name, callback_data=f"achuser_{name}")] for name in RANDOM_NAMES]
    await callback.message.answer("🏆 **[ДОСЯГНЕННЯ]** Оберіть учня для видачі або видалення медалей:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("achuser_"))
async def process_admin_ach_user_card(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS: return
    await callback.answer()
    name = callback.data.replace("achuser_", "")
    await state.update_data(ach_target_name=name)
    ach_list = USER_ACHIEVEMENTS.get(name, ["🥈 Активний учень 7-В класу"])
    formatted = "\n".join(ach_list)
    
    buttons = [
        [InlineKeyboardButton(text="➕ Додати нове досягнення", callback_data="achaction_add")],
        [InlineKeyboardButton(text="🗑️ Очистити всі досягнення", callback_data="achaction_clear")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_manage_ach")]
    ]
    await callback.message.answer(f"🏆 **Керування досягненнями учня: {name}**\n\nПоточні медалі:\n{formatted}", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("achaction_"))
async def process_admin_ach_action(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS: return
    await callback.answer()
    action = callback.data.replace("achaction_", "")
    state_data = await state.get_data()
    name = state_data.get("ach_target_name")
    
    if action == "clear":
        USER_ACHIEVEMENTS[name] = ["🥈 Активний учень 7-В класу"]
        await callback.message.answer(f"✅ Усі кастомні досягнення учня **{name}** успішно анульовані!")
    elif action == "add":
        await callback.message.answer(f"✍️ Введіть текст нового досягнення (з емодзі) для учня **{name}**:")
        await state.set_state(BotStates.admin_input_achievement)

@router.message(BotStates.admin_input_achievement)
async def admin_save_new_achievement(message: Message, state: FSMContext):
    user_id = message.from_user.id
    state_data = await state.get_data()
    buyer_id = state_data.get("buyer_user_id")
    
    if buyer_id:
        ach_text = message.text
        buyer_name = USER_TELEGRAM_NAMES.get(buyer_id, message.from_user.first_name if message.from_user.first_name else "Учень")
        confirm_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🟢 Схвалити медаль", callback_data=f"buyach_approve_{buyer_id}"),
             InlineKeyboardButton(text="❌ Відхилити (Бек Сімок)", callback_data=f"buyach_reject_{buyer_id}")]
        ])
        await state.update_data(pending_ach_text=ach_text)
        try:
            await bot.send_message(
                chat_id=8791830931,
                text=f"👑 **[ЦРУ МАГАЗИН] Учень {buyer_name} (ID: `{buyer_id}`) купив досягнення за 250 Сімок!**\n\nТекст медалі:\n«_{ach_text}_»\n\nЩо робимо, Босс?",
                reply_markup=confirm_markup
            )
            await message.answer("✅ **Запит на купівлю медалі успішно надіслано Макару!** Якщо він відхилить — 250 Сімок повернуться на твій баланс.")
        except Exception:
            await message.answer("❌ Помилка зв'язку з сервером премодерації.")
        return
        
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS: return
    name = state_data.get("ach_target_name")
    if name not in USER_ACHIEVEMENTS: USER_ACHIEVEMENTS[name] = []
    USER_ACHIEVEMENTS[name].append(message.text)
    await message.answer(f"✅ Досягнення успішно додано для **{name}**!")
    await state.clear()

    
    if name not in USER_ACHIEVEMENTS: USER_ACHIEVEMENTS[name] = []
    USER_ACHIEVEMENTS[name].append(message.text)
    await message.answer(f"✅ Досягнення успішно додано для **{name}**!")
    await state.clear()


@router.callback_query(F.data == "profile_bells")
async def process_smart_school_bells(callback: CallbackQuery):
    await callback.answer()
    from datetime import timedelta
    now = datetime.now() + timedelta(hours=3)
    weekday = now.weekday()
    if weekday >= 5:
        await callback.message.edit_text(text="🛌 **Зараз немає уроків!**\n\nНе заглядуй сюди, коли немає навчання, йди відпочивай! Сьогодні вихідний! 🎉", reply_markup=settings_interactive_menu)
        return
    ua_hour = now.hour
    current_minutes = ua_hour * 60 + now.minute
    schedule_blocks = [
        {"lesson": 1, "start": 8*60+30, "end": 9*60+15},
        {"lesson": 2, "start": 9*60+35, "end": 10*60+20},
        {"lesson": 3, "start": 10*60+40, "end": 11*60+25},
        {"lesson": 4, "start": 11*60+45, "end": 12*60+30},
        {"lesson": 5, "start": 12*60+50, "end": 13*60+35},
        {"lesson": 6, "start": 13*60+45, "end": 14*60+30},
        {"lesson": 7, "start": 14*60+40, "end": 15*60+25}
    ]
    if current_minutes < schedule_blocks[0]["start"]:
        await callback.message.edit_text(text="☕ **Навчання ще не почалося!** Уроки стартують о 08:30. Не заглядуй сюди завчасно! 😉", reply_markup=settings_interactive_menu)
        return
    if current_minutes > schedule_blocks[-1]["end"]:
        await callback.message.edit_text(text="🎒 **Зараз немає уроків!** Всі уроки на сьогодні закінчилися! Не заглядуй сюди, коли немає навчання, йди гуляти на вулицю! 🛑🔥", reply_markup=settings_interactive_menu)
        return
    for block in schedule_blocks:
        if block["start"] <= current_minutes <= block["end"]:
            await callback.message.edit_text(text=f"📚 **ЗАРАЗ ЙДЕ {block['lesson']}-й УРОК!**\n\n⏱️ Урок закінчиться о **{int(block['end']/60):02d}:{block['end']%60:02d}**.\n\nПовністю фокусуйся на навчанні, відклади телефон і **іди вчись, не відволікайся!** 👨‍💻❌📱", reply_markup=settings_interactive_menu)
            return
    await callback.message.edit_text(text="🍕 **ЗАРАЗ ІДЕ ПЕРЕМІНА!** Уроку немає, відпочивай! Сходи в їдальню за булочкою, подихай свіжим повітрям і готуйся до наступного кабінету! 🏃‍♂️💨", reply_markup=settings_interactive_menu)

@router.callback_query(F.data == "economy_back_to_settings")
async def process_back_to_settings_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(text="⚙️ Налаштування та інтерактив:", reply_markup=settings_interactive_menu)

async def handle_render_hc(request): 
    return web.Response(text="OK")

async def self_ping_task():
    url = os.getenv("RENDER_EXTERNAL_URL")
    if not url: return
    await asyncio.sleep(30)
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp: print(f"⏰ Автопінг Render: {resp.status} OK")
        except Exception: pass
        await asyncio.sleep(300)

async def cron_secret_agent_picker():
    global CURRENT_SECRET_AGENT_ID, AGENT_HAS_SENT_SECRET
    while True:
        await asyncio.sleep(86400)
        if USER_USERNAMES: CURRENT_SECRET_AGENT_ID = random.choice(list(USER_USERNAMES.values())); AGENT_HAS_SENT_SECRET = False

def restore_homework_from_file():
    global HOMEWORK_DATA
    try:
        if os.path.exists("homework.json"):
            with open("homework.json", "r", encoding="utf-8") as f: HOMEWORK_DATA = json.load(f)
    except Exception: pass

async def run_web_server():
    app = web.Application()
    app.router.add_get("/", handle_render_hc)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080))).start()
    while True: await asyncio.sleep(3600)

@router.message(F.text == "🛠️ Admin Panel")
async def handle_admin_panel(message: Message):
    user_id = message.from_user.id
    if user_id == 8791830931:
        await message.answer(text="🛠️ **Вітаємо, Макаре! Функції Розробника v2.6:**", reply_markup=get_admin_menu_keyboard(user_id))
        return
    all_protected_ids = []
    for s in [ADMIN_L4_IDS, MODERATOR_IDS, HW_ASSISTANT_IDS, STAROSTA_IDS, TESTER_IDS]:
        if s: all_protected_ids.extend(s)
    if user_id in all_protected_ids or user_id == TEACHER_CHAT_ID:
        await message.answer(text="🛠️ **Панель Адміністратора:**", reply_markup=get_admin_menu_keyboard(user_id))
    else: 
        await message.answer("🛑 Немає доступу.")

@router.callback_query(F.data.startswith("buyach_"))
async def process_macar_shop_moderation(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != 8791830931: return
    await callback.answer()
    
    raw_cmd = callback.data.replace("buyach_", "").split("_")
    action, buyer_id = raw_cmd, int(raw_cmd)
    
    state_data = await state.get_data()
    ach_text = state_data.get("pending_ach_text", "🏆 Нове досягнення")
    tax = state_data.get("buyer_tax", 75)
    buyer_name = USER_TELEGRAM_NAMES.get(buyer_id, "Учень")
    
    if action == "approve":
        username_key = ""
        for username, u_name in USER_USERNAMES_TEXT.items():
            u_id = USER_USERNAMES.get(username.lower(), 0)
            if u_id == buyer_id: username_key = u_name; break
        if not username_key: username_key = buyer_name
        
        if username_key not in USER_ACHIEVEMENTS: USER_ACHIEVEMENTS[username_key] = []
        USER_ACHIEVEMENTS[username_key].append(ach_text)
        
        try: await bot.send_message(chat_id=buyer_id, text=f"🎉 **Макар схвалив твою покупку!**\n\nНове досягнення «{ach_text}» додано у твій профіль!")
        except Exception: pass
        await callback.message.edit_text(f"🟢 **Успішно схвалено!** Медаль видана {username_key}. Налог 30% ({tax} Сімок) зафіксовано на балансах адмінів!")
    
    elif action == "reject":
        USER_BALANCES[buyer_id] = USER_BALANCES.get(buyer_id, 0) + 250
        USER_BALANCES[8791830931] -= tax
        for l4_id in ADMIN_L4_IDS:
            if l4_id != 8791830931: USER_BALANCES[l4_id] -= tax
            
        try: await bot.send_message(chat_id=buyer_id, text=center("❌ **Макар відхилив твій запит на досягнення!**\n\nТекст не пройшов цензуру. 250 Сімок повністю повернуто на твій баланс."))
        except Exception: pass
        await callback.message.edit_text(f"❌ **Ви відхилили запит.** 250 Сімок повернуто учню на базу, податок скасовано.")
        
    await state.clear()

@router.message(Command("pay"))
async def universal_pay_system_command(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    
    if len(args) < 3:
        await message.answer("⚠️ **Формат переказу Сімок:**\n`/pay @username кількість повідомлення`\n\nПриклад:\n`/pay @marri_chk 250 для любимої` 💌")
        return
        
    target_username = args[1].strip().lower()
    
    try:
        amount = int(args[2])
    except ValueError:
        await message.answer("❌ Кількість монет має бути цілим числом!")
        return
        
    if amount <= 0:
        await message.answer("❌ Сума переказу має бути більшою за 0!")
        return
        
    # Перевірка балансу (Макар має нескінченний чит, тому його баланс не обмежує)
    sender_balance = USER_BALANCES.get(user_id, 0)
    if user_id != 8791830931 and sender_balance < amount:
        await message.answer(f"❌ **Недостатньо Сімок!** Твій поточний баланс: **{sender_balance} Сімок** 🪙.")
        return
        
    # Шукаємо отримувача в базі ID
    target_id = USER_USERNAMES.get(target_username, 0)
    if target_id == 0:
        await message.answer(f"❌ **Учня {target_username} не знайдено в базі!** Він повинен хоча б раз натиснути `/start` у боті.")
        return
        
    if target_id == user_id:
        await message.answer("🧠 Хитрун! Не можна переводити Сімки самому собі!")
        return
        
    # Збираємо повідомлення/коментар, якщо він є
    comment_text = " ".join(args[3:]) if len(args) > 3 else "Без коментаря"
    
    # Списуємо у відправника (якщо це не Макар з читом)
    if user_id != 8791830931:
        USER_BALANCES[user_id] -= amount
        
    # Нараховуємо отримувачу
    USER_BALANCES[target_id] = USER_BALANCES.get(target_id, 0) + amount
    
    sender_name = USER_TELEGRAM_NAMES.get(user_id, message.from_user.first_name if message.from_user.first_name else "Учень")
    
    await message.answer(f"💸 **Переказ успішний!**\n\nВи відправили **{amount} Сімок** 🪙 для **{target_username}**.\n💬 Коментар: «_{comment_text}_»")
    
    try:
        await bot.send_message(
            chat_id=target_id,
            text=f"🎁 **Тобі прилетів грошовий переказ!**\n\n👤 **Відправник:** {sender_name}\n🪙 **Сума:** +{amount} Сімок\n💌 **Повідомлення:** «_{comment_text}_»\n\nПеревір свій оновлений баланс у налаштуваннях! 🎉"
        )
    except Exception:
        pass


async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    asyncio.create_task(self_ping_task())
    asyncio.create_task(cron_secret_agent_picker())
    restore_homework_from_file()
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await asyncio.gather(run_web_server(), dp.start_polling(bot))
    finally: 
        await bot.session.close()

if __name__ == "__main__": 
    asyncio.run(main())
