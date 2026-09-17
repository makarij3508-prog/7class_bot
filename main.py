import asyncio
import logging
import random
import os
import aiohttp
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.chat_action import ChatActionSender
from aiohttp import web

# 🚨 ТВІЙ ЧИСТИЙ ТОКЕН БОТА
BOT_TOKEN = "8735817305:AAGSh53VV7GvWpDGA0XAE8IkklyoQ8ebivo"

# 👑 TVІЙ ЖОРСТКИЙ ID СУПЕР-АДМІНА (МАКАР — РІВЕНЬ 5)
SUPER_ADMIN_IDS = [8791830931]

# 🪪 СИСТЕМА ПРАВ ПО ЮЗЕРНЕЙМАХ
ADMIN_L4_USERNAMES = ["@пример_админа_л4"]  # Головний Адмін (Рівень 4)
MODERATOR_USERNAMES = []                     # Модератори чату (Рівень 3)
STAROSTA_USERNAMES = []                      # Старости (Рівень 2)
ASSISTANT_USERNAMES = []                     # Помічники по ДЗ (Рівень 1)
TESTER_USERNAMES = []                        # Тестувальники

# 👑 ЮЗЕРНЕЙМ КЛАСНОГО КЕРІВНИКА
TEACHER_USERNAME = "@пример_учителя"

# 📊 Внутрішні динамічні списки ID
ADMIN_L4_IDS = []
MODERATOR_IDS = []
HW_ASSISTANT_IDS = []
STAROSTA_IDS = []
TESTER_IDS = []
TEACHER_CHAT_ID = 0

# Словники зв'язків
USER_TELEGRAM_NAMES = {8791830931: "Макар"}
USER_USERNAMES = {}

# 💬 БАЗА ДАНИХ ШКІЛЬКОГО ЧАТУ, МУТІВ ТА БАНІВ
CHAT_REGISTERED_USERS = {}
BANNED_USERS = []
MUTED_USERS = {}

# 🛠️ ГЛОБАЛЬНИЙ РЕЖИМ ТЕСТУВАННЯ
IS_TESTING_MODE = False

HOMEWORK_DATA = {}
IMPORTANT_ANNOUNCEMENT = "📌 **Важливі оголошення:**\n\nНаразі немає нових оголошень від адміністрації."
BOOKS_DATA = "📚 **Електронні підручники для 7 класу:**\n\nТут будуть посилання на завантаження підручників."
ABSENT_TODAY_LIST = []
RANDOM_MODE = "dice"

# 👥 ПОВНА БАЗА ДАНИХ ТВОГО КЛАСУ
RANDOM_NAMES = [
    "Олександр", "Андрій", "Данило", "Колодинський Богдан", "Ковалевчук Богдан", 
    "Мирослава", "Матвій", "Софія", "Михайло", "Макар", "Ілона", "Марічка", 
    "Маргарита", "Ангеліна", "Нікіта", "Альберт", "Єва", "Роман", "Владислав", 
    "Назарій", "Едуард", "Станіслав", "Артем", "Емілія", "Вероніка", "Ілля", "Дмитро", "Макс"
]
USER_ACHIEVEMENTS = {name: ["🥇 Перший запуск бота", "🥈 Активний учень 7 класу"] for name in RANDOM_NAMES}

# База ніків однокласників зі скриншота
USER_USERNAMES_TEXT = {
    "@llona_x": "Ілона", "@selarkin": "Роман", "@play.funtime.su": "Едуард",
    "@marri_chk": "Марічка", "@myveronichkam": "Вероніка", "@Red_tea21": "Назарій",
    "@Mi42a": "Мирослава", "@sanichka_gg": "Олександр", "@shadow123446": "Емілія",
    "@ezhik_lite": "Артем", "@Vladore1488": "Колодинський Богдан", "@Sharik_xd": "Ковальчук Богдан"
}

SCHEDULE_DATA = {
    "mon": "🗓️ **Понеділок:**\n1. ЗБД / Зар. літ.\n2. Фізика\n3. Фізкультура\n4. Укр. література\n5. Алгебра\n6. Англійська\n7. Географія",
    "tue": "🗓️ **Вівторок:**\n1. Історія\n2. Біологія\n3. Геометрія\n4. Укр. мова\n5. ЗБД\n6. Інформатика\n7. Технології",
    "wed": "🗓️ **Середа:**\n1. Укр. мова\n2. Хімія\n3. Зар. література\n4. Фізкультура\n5. Алгебра\n6. Англійська\n7. Географія",
    "thu": "🗓️ **Четвер:**\n1. Англ. / Біологія\n2. Фізика\n3. Мистецтво\n4. Укр. мова\n5. Геометрія\n6. Інформатика\n7. Історія",
    "fri": "🗓️ **П'ятниця:**\n1. Історія\n2. Мистецтво\n3. Англійська\n4. Укр. література\n5. Фізкультура\n6. Біологія\n7. Алгебра"
}

SUBJECT_NAMES = {
    "algebra": "📐 Алгебра", "geometry": "📐 Геометрія", "physics": "🧲 Фізика", "chemistry": "🧪 Хімія",
    "biology": "🧬 Біологія", "geography": "🌍 Географія", "hist_ua": "📜 Історія Укр.", "hist_world": "🏰 Всесвітня iст.",
    "lang_ua": "🇺🇦 Укр. мова", "lit_ua": "📚 Укр. літ.", "english": "🇬🇧 Англійська", "lit_world": "🗺️ Зарубіжна літ.",
    "inf": "💻 Інформатика", "tech": "🛠️ Технології", "art": "🎨 Мистецтво", "zbd": "🌱 ЗБД"
}
DAY_NAMES = {"mon": "Понеділок", "tue": "Вівторок", "wed": "Середа", "thu": "Четвер", "fri": "П'ятниця"}

PREDICTIONS = [
    "🌟 Сьогодні твій щасливий день! Все буде спокійно.",
    "⚡ Обережно! На фізрі доведеться побігати.",
    "🧠 Ідеальний час, щоб підняти бал з алгебри!",
    "🍕 У їдальні сьогодні смачні булочки!",
    "🎒 Перевір рюкзак просто зараз!",
    "🍀 Сьогодні тебе омине виклик до дошки. Везунчик!"
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
    user_in_chat_window = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

async def handle_render_hc(request):
    return web.Response(text="OK")

def get_main_menu(user_id: int) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🗓️ Розклад"), KeyboardButton(text="📝 ДЗ")],
        [KeyboardButton(text="🤖 ШІ Допомога"), KeyboardButton(text="🔊 Чат класу")],
        [KeyboardButton(text="📚 Книги"), KeyboardButton(text="📌 Важливе")],
        [KeyboardButton(text="🎲 Рандом"), KeyboardButton(text="⚙️ Налаштування")]
    ]
    if (user_id in SUPER_ADMIN_IDS or user_id in ADMIN_L4_IDS or user_id in MODERATOR_IDS or 
        user_id in HW_ASSISTANT_IDS or user_id in STAROSTA_IDS or user_id in TESTER_IDS or user_id == TEACHER_CHAT_ID):
        buttons.append([KeyboardButton(text="🛠️ Admin Panel")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_ai_mode_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🛑 Вийти з режиму ШІ")]], resize_keyboard=True)

def get_chat_exit_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🚪 Вийти з чату")]], resize_keyboard=True)

def get_subjects_menu(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📐 Алгебра", callback_data=f"{prefix}_algebra"), InlineKeyboardButton(text="📐 Геометрія", callback_data=f"{prefix}_geometry")],
        [InlineKeyboardButton(text="🧲 Фізика", callback_data=f"{prefix}_physics"), InlineKeyboardButton(text="🧪 Хімія", callback_data=f"{prefix}_chemistry")],
        [InlineKeyboardButton(text="🧬 Біологія", callback_data=f"{prefix}_biology"), InlineKeyboardButton(text="🌍 Географія", callback_data=f"{prefix}_geography")],
        [InlineKeyboardButton(text="📜 Історія Укр.", callback_data=f"{prefix}_hist_ua"), InlineKeyboardButton(text="🏰 Всесвітня iст.", callback_data=f"{prefix}_hist_world")],
        [InlineKeyboardButton(text="🇺🇦 Укр. мова", callback_data=f"{prefix}_lang_ua"), InlineKeyboardButton(text="📚 Укр. літ.", callback_data=f"{prefix}_lit_ua")],
        [InlineKeyboardButton(text="🇬🇧 Англійська", callback_data=f"{prefix}_english"), InlineKeyboardButton(text="🗺️ Зарубіжна літ.", callback_data=f"{prefix}_lit_world")],
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
    if user_id in HW_ASSISTANT_IDS or user_id in STAROSTA_IDS or user_id in ADMIN_L4_IDS or user_id in SUPER_ADMIN_IDS:
        keyboard.append([InlineKeyboardButton(text="📝 Змінити ДЗ", callback_data="admin_add_hw")])
    if user_id in STAROSTA_IDS or user_id in ADMIN_L4_IDS or user_id in SUPER_ADMIN_IDS:
        keyboard.append([InlineKeyboardButton(text="🗓️ Змінити Розклад", callback_data="admin_edit_sch")])
    if user_id in STAROSTA_IDS or user_id in ADMIN_L4_IDS or user_id in SUPER_ADMIN_IDS:
        keyboard.append([InlineKeyboardButton(text="👥 Відмітити відсутнього", callback_data="admin_mark_attendance"), 
                         InlineKeyboardButton(text="📢 Надіслати звіт вчителю", callback_data="admin_send_report")])
    if user_id in ADMIN_L4_IDS or user_id in SUPER_ADMIN_IDS or user_id == TEACHER_CHAT_ID:
        keyboard.append([InlineKeyboardButton(text="📌 Оновити Важливе", callback_data="admin_add_important"), 
                         InlineKeyboardButton(text="📚 Оновити Книги", callback_data="admin_edit_books")])
    if user_id in ADMIN_L4_IDS or user_id in SUPER_ADMIN_IDS:
        keyboard.append([InlineKeyboardButton(text="👑 Налаштувати рівні доступу", callback_data="admin_give_level_menu")])
    if user_id in SUPER_ADMIN_IDS:
        keyboard.append([InlineKeyboardButton(text="🧪 Тест-Режим: ОН/ОФФ", callback_data="admin_toggle_test")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

settings_interactive_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏆 Досягнення", callback_data="profile_achievements"), InlineKeyboardButton(text="🔮 Передбачення", callback_data="profile_prediction")],
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
    
    # 🪪 АВТО-ПРИВ'ЯЗКА РОЛЕЙ ПО ЮЗЕРНЕЙМАХ ПРИ СТАРТІ БОТА
    if username:
        user_key = f"@{username.lower()}"
        USER_USERNAMES[user_key] = user_id
        
        # Перевіряємо роль Головного Адміна (Рівень 4)
        if user_key in ADMIN_L4_USERNAMES and user_id not in ADMIN_L4_IDS:
            ADMIN_L4_IDS.append(user_id)
            print(f"✨ Роль Головного Адміна (Рівень 4) активована для {user_key}")
            
        # Перевіряємо роль Модератора чату (Рівень 3)
        if user_key in MODERATOR_USERNAMES and user_id not in MODERATOR_IDS:
            MODERATOR_IDS.append(user_id)
            print(f"✨ Роль Модератора чату (Рівень 3) активована для {user_key}")
            
        # Перевіряємо роль Старости (Рівень 2)
        if user_key in STAROSTA_USERNAMES and user_id not in STAROSTA_IDS:
            STAROSTA_IDS.append(user_id)
            print(f"✨ Роль Старости (Рівень 2) активована для {user_key}")
            
        # Перевіряємо роль помічника по ДЗ (Рівень 1)
        if user_key in ASSISTANT_USERNAMES and user_id not in HW_ASSISTANT_IDS:
            HW_ASSISTANT_IDS.append(user_id)
            print(f"✨ Роль Помічника по ДЗ (Рівень 1) активована для {user_key}")
            
        # Перевіряємо роль тестувальника
        if user_key in TESTER_USERNAMES and user_id not in TESTER_IDS:
            TESTER_IDS.append(user_id)
            print(f"✨ Роль Teстувальника активована для {user_key}")
            
        # Перевіряємо роль Класного Керівника (Вчителя)
        if user_key == TEACHER_USERNAME.lower():
            global TEACHER_CHAT_ID
            TEACHER_CHAT_ID = user_id
            print(f"✨ Класний Керівник (Вчитель) успішно авторизований: {user_key}")

    await send_human_message(message, "Привіт! Я твій помічник для 7 класу. Чим займемося сьогодні?", reply_markup=get_main_menu(user_id))

@router.message(F.text == "📝 ДЗ")
async def show_subjects_for_hw(message: Message):
    user_id = message.from_user.id
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in ADMIN_L4_IDS and user_id not in TESTER_IDS: return
    await send_human_message(message, "Обери предмет, щоб подивитися домашнє завдання:", reply_markup=get_subjects_menu("view"))

# 🚨 АБСОЛЮТНИЙ ФИКС КНОПКИ ДЗ: Вирізаємо чисту назву предмета
@router.callback_query(F.data.startswith("view_"))
async def process_view_hw(callback: CallbackQuery):
    subject = callback.data.replace("view_", "")
    sub_name = SUBJECT_NAMES.get(subject, "Предмет")
    hw_text = HOMEWORK_DATA.get(subject, "Завдання поки що не додано.")
    await callback.message.edit_text(text=f"📝 **ДЗ з предмету {sub_name}:**\n\n{hw_text}", reply_markup=get_subjects_menu("view"))
    await callback.answer()

@router.message(F.text == "🗓️ Розклад")
async def show_schedule_days(message: Message):
    user_id = message.from_user.id
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in ADMIN_L4_IDS and user_id not in TESTER_IDS: return
    await send_human_message(message, "Обери день тижня:", reply_markup=get_days_menu("sch"))

# 🚨 АБСОЛЮТНИЙ ФИКС КНОПКИ РАСПИСАНИЯ: Вирізаємо чистий день тижня
@router.callback_query(F.data.startswith("sch_"))
async def process_schedule_callback(callback: CallbackQuery):
    day = callback.data.replace("sch_", "")
    await callback.message.edit_text(text=SCHEDULE_DATA.get(day, "⚠️ Нічого немає."), reply_markup=get_days_menu("sch"))
    await callback.answer()

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
    await send_human_message(message, "Введи souvenirs оцінки через пробіл або кому (наприклад: 10, 11, 9, 12):")
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
    url = "https://pollinations.ai"
    payload = {
        "messages": [
            {"role": "system", "content": "Ти помічник для 7 класу. Відповідай чітко, українською."},
            {"role": "user", "content": question}
        ], "private": True
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=15) as response:
                if response.status == 200: return await response.text()
                return "⚠️ Сервер ШІ тимчасово перевантажений."
    except Exception: return "❌ Не вдалося з'єднатися з ШІ."

@router.message(F.text == "🤖 ШІ Допомога")
async def handle_ai_help(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in ADMIN_L4_IDS and user_id not in TESTER_IDS: return
    await send_human_message(message, "🤖 **Ви увійшли в інтерактивний режим ШІ!**\n\nПиши souvenirs питання підряд. Для виходу натисни кнопку нижче 👇", reply_markup=get_ai_mode_menu())
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
# 🔊 МОДЕРОВАНИЙ ЧАТ КЛАСУ (МУТ / БАН)
# ==========================================

@router.message(F.text == "🔊 Чат класу")
async def enter_chat_room(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if user_id in BANNED_USERS:
        await message.answer("🛑 **Доступ заблоковано!**\n\nВи забанені в чаті адміністрацією класу за порушення правил.")
        return

    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in ADMIN_L4_IDS and user_id not in TESTER_IDS:
        await message.answer("🛠️ Чат закритий на технічні роботи.")
        return

    if user_id in USER_TELEGRAM_NAMES: name = USER_TELEGRAM_NAMES[user_id]
    else: name = message.from_user.first_name if message.from_user.first_name else "Учень"

    CHAT_REGISTERED_USERS[user_id] = name
    await state.set_state(BotStates.user_in_chat_window)
    
    await message.answer(
        f"💬 **Ласкаво просимо до чату класу, {name}!**\n\n"
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
        else:
            MUTED_USERS.pop(user_id)

    sender_name = CHAT_REGISTERED_USERS.get(user_id, "Учень")

    for target_id in list(CHAT_REGISTERED_USERS.keys()):
        if target_id != user_id:
            try: await bot.send_message(chat_id=target_id, text=f"💬 **[{sender_name}]:** {message.text}")
            except Exception: pass

    all_protected_ids = set(SUPER_ADMIN_IDS + ADMIN_L4_IDS + MODERATOR_IDS + HW_ASSISTANT_IDS + STAROSTA_IDS + TESTER_IDS)
    if user_id == TEACHER_CHAT_ID or user_id in all_protected_ids:
        all_admins = set(SUPER_ADMIN_IDS + ADMIN_L4_IDS + MODERATOR_IDS + HW_ASSISTANT_IDS)
        for admin_id in all_admins:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=f"👁️ **[ЧАТЛОГ - ЗАХИЩЕНИЙ] {sender_name} (ID: `{user_id}`) написав:**\n«_{message.text}_»"
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
                text=f"👁️ **[ЧАТЛОГ] {sender_name} (ID: `{user_id}`) написав:**\n«_{message.text}_»",
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
    
    if user_id == 8791830931:
        name = "Макар"
    elif user_key in USER_USERNAMES_TEXT:
        name = USER_USERNAMES_TEXT[user_key]
    else:
        name = callback.from_user.first_name if callback.from_user.first_name else "Учень"
        
    ach_list = USER_ACHIEVEMENTS.get(name, ["🥇 Перший запуск бота", "🥈 Активний учень 7 класу"])
    formatted = "\n".join(ach_list)
    await callback.message.answer(f"🏆 **Досягнення учня ({name}):**\n\n{formatted}")
    await callback.answer()

@router.callback_query(F.data == "profile_changelog")
async def process_changelog(callback: CallbackQuery):
    await callback.message.answer(
        "📜 **Офіційний лог оновлень (v2.1):**\n\n"
        "• **Екосистема 5 рівнів:** Повністю перебудовано рівні доступу (від Помічника ДЗ до Головного Розробника Макара).\n"
        "• **VIP-роль Вчителя:** Класний керівник отримала окремий кабінет, звіти від старости та модерацію учнів.\n"
        "• **Абсолютний імунітет:** Адмін-склад захищений від випадкових мутів/банів з боку вчителя чи інших адмінів.\n"
        "• **Авто-алерти чату:** Будь-які покарання миттєво публікуються системою в загальну кімнату чату класу.\n"
        "• **Стабільність 24/7:** Покращено систему захисту від сну Render та фіксації токенів."
    )
    await callback.answer()

# 🚨 АБСОЛЮТНИЙ ФИКС КНОПКИ АДМИН ПАНЕЛИ ДЛЯ МАКАРА ПРИ ПУСТЫХ СПИСКАХ ОДНОКЛАССНИКОВ
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
# 🛠️ АДМІНІСТРАТИВНА ПАНЕЛЬ ТА КЕРУВАННЯ
# ==========================================

async def admin_panel(message: Message):
    user_id = message.from_user.id
    
    if user_id == 8791830931:
        await message.answer("🛠️ Вітаємо, Макаре! Доступні функції Головного Розробника:", reply_markup=get_admin_menu_keyboard(user_id))
        return
        
    all_protected_ids = []
    for s in [ADMIN_L4_IDS, MODERATOR_IDS, HW_ASSISTANT_IDS, STAROSTA_IDS, TESTER_IDS]:
        if s: all_protected_ids.extend(s)
        
    if user_id in all_protected_ids or user_id == TEACHER_CHAT_ID:
        await message.answer("🛠️ Вітаємо в панелі адміністратора. Доступні функції згідно з вашим рівнем прав:", reply_markup=get_admin_menu_keyboard(user_id))
    else:
        await message.answer("🛑 У вас немає доступу до цієї команди.")

# 🚨 ОБРОБКА МУТУ ТА БАНУ З ЧАТЛОГІВ
@router.callback_query(F.data.startswith("mute_15_") | F.data.startswith("ban_"))
async def process_chat_punishment(callback: CallbackQuery):
    admin_id = callback.from_user.id
    
    all_admins = []
    for s in [ADMIN_L4_IDS, MODERATOR_IDS, HW_ASSISTANT_IDS]:
        if s: all_admins.extend(s)
        
    if admin_id not in all_admins and admin_id != TEACHER_CHAT_ID and admin_id != 8791830931: return

    data_parts = callback.data.split("_")
    action = data_parts
    
    if action == "mute":
        target_id = int(data_parts)
        target_name = data_parts
        MUTED_USERS[target_id] = datetime.now().timestamp() + 900
        alert_text = f"🤫 **Користувач {target_name} замучений на 15 хв за порушення правил чату!**"
    else:
        target_id = int(data_parts)
        target_name = data_parts
        if target_id not in BANNED_USERS: BANNED_USERS.append(target_id)
        alert_text = f"🛑 **Користувач {target_name} назавжди забанений у чаті класу!**"

    for user_id in list(CHAT_REGISTERED_USERS.keys()):
        try: await bot.send_message(chat_id=user_id, text=alert_text)
        except Exception: pass

    await callback.message.edit_text(text=f"✅ Покарання успішно застосовано!\n{alert_text}")
    await callback.answer()

# 👑 КНОПКА «НАЛАШТУВАТИ РІВНІ ДОСТУПУ» — СПИСОК УЧНІВ КНОПКАМИ
@router.callback_query(F.data == "admin_give_level_menu")
async def admin_start_give_level(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS: return
    
    # Виводимо список усіх 28 учнів кнопками
    buttons = [[InlineKeyboardButton(text=name, callback_data=f"lvluser_{name}")] for name in RANDOM_NAMES]
    await callback.message.answer("👥 **Оберіть учня для керування рівнем доступу:**", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

# 📊 Внутрішня функція: дізнатися поточний рівень учня за ім'ям
def get_user_current_level(name: str) -> int:
    target_username = ""
    for username, u_name in USER_USERNAMES_TEXT.items():
        if u_name == name:
            target_username = username
            break
            
    if not target_username:
        return 0
        
    if target_username in ADMIN_L4_USERNAMES: return 4
    if target_username in MODERATOR_USERNAMES: return 3
    if target_username in STAROSTA_USERNAMES: return 2
    if target_username in ASSISTANT_USERNAMES: return 1
    return 0

# 🧠 КАРТКА УЧНЯ: КНОПКИ «ПІДНЯТИ» ТА «ПОНИЗИТИ»
@router.callback_query(F.data.startswith("lvluser_"))
async def process_level_user_card(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS: return
    
    name = callback.data.replace("lvluser_", "")
    current_lvl = get_user_current_level(name)
    
    level_names = {
        0: "📋 Рівень 0 (Звичайний учень)",
        1: "📐 Рівень 1 (Помічник по ДЗ)",
        2: "👥 Рівень 2 (Староста / Зам. старости)",
        3: "🛡️ Рівень 3 (Модератор чату)",
        4: "⭐ Рівень 4 (Головний Адміністратор)"
    }
    
    card_buttons = [
        [InlineKeyboardButton(text="🔺 Підняти рівень", callback_data=f"lvledit_up_{name}"),
         InlineKeyboardButton(text="🔻 Понизити рівень", callback_data=f"lvledit_down_{name}")],
        [InlineKeyboardButton(text="🔙 Назад до списку", callback_data="admin_give_level_menu")]
    ]
    
    await callback.message.edit_text(
        text=f"🪪 **Картка керування правами**\n\n"
             f"👤 **Учень:** {name}\n"
             f"📊 **Поточний статус:** {level_names.get(current_lvl)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=card_buttons)
    )
    await callback.answer()

# ⚡ АВТОМАТИЧНА ЗМІНА РІВНЯ НА ЛЕТУ ЧЕРЕЗ КНОПКИ ЧЕРЕЗ REPLACE
@router.callback_query(F.data.startswith("lvledit_"))
async def process_level_change_action(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS: return
    
    data = callback.data.replace("lvledit_", "")
    action = "up" if data.startswith("up_") else "down"
    name = data.replace("up_", "").replace("down_", "")
    
    target_username = ""
    for username, u_name in USER_USERNAMES_TEXT.items():
        if u_name == name:
            target_username = username
            break
            
    if not target_username:
        await callback.message.answer(f"⚠️ Помилка! Учня {name} немає в списку прив'язаних юзернеймів Частини 1Б. Спочатку додайте його нік!")
        await callback.answer()
        return
        
    current_lvl = get_user_current_level(name)
    new_lvl = current_lvl + 1 if action == "up" else current_lvl - 1
    
    if new_lvl > 4 or new_lvl < 0:
        await callback.answer("🛑 Далі змінювати рівень неможливо!", show_alert=True)
        return
        
    if new_lvl == 4 and user_id != 8791830931:
        await callback.answer("🛑 Тільки Макар (Рівень 5) може піднімати користувачів до Рівня 4!", show_alert=True)
        return
        
    if current_lvl == 4 and user_id != 8791830931:
        await callback.answer("🛑 Тільки Макар може знижувати права Головного Адміністратора!", show_alert=True)
        return

    for lst in [ADMIN_L4_USERNAMES, MODERATOR_USERNAMES, STAROSTA_USERNAMES, ASSISTANT_USERNAMES]:
        if target_username in lst: lst.remove(target_username)
        
    target_id = USER_USERNAMES.get(target_username)
    if target_id:
        for lst_id in [ADMIN_L4_IDS, MODERATOR_IDS, STAROSTA_IDS, HW_ASSISTANT_IDS]:
            if target_id in lst_id: lst_id.remove(target_id)

    if new_lvl == 1:
        ASSISTANT_USERNAMES.append(target_username)
        if target_id: HW_ASSISTANT_IDS.append(target_id)
    elif new_lvl == 2:
        STAROSTA_USERNAMES.append(target_username)
        if target_id: STAROSTA_IDS.append(target_id)
    elif new_lvl == 3:
        MODERATOR_USERNAMES.append(target_username)
        if target_id: MODERATOR_IDS.append(target_id)
    elif new_lvl == 4:
        ADMIN_L4_USERNAMES.append(target_username)
        if target_id: ADMIN_L4_IDS.append(target_id)

    level_names = {
        0: "📋 Рівень 0 (Звичайний учень)",
        1: "📐 Рівень 1 (Помічник по ДЗ)",
        2: "👥 Рівень 2 (Староста / Зам. старости)",
        3: "🛡️ Рівень 3 (Модератор чату)",
        4: "⭐ Рівень 4 (Головний Адміністратор)"
    }
    
    card_buttons = [
        [InlineKeyboardButton(text="🔺 Підняти рівень", callback_data=f"lvledit_up_{name}"),
         InlineKeyboardButton(text="🔻 Понизити рівень", callback_data=f"lvledit_down_{name}")],
        [InlineKeyboardButton(text="🔙 Назад до списку", callback_data="admin_give_level_menu")]
    ]
    
    await callback.message.edit_text(
        text=f"✅ **Рівень успішно змінено!**\n\n"
             f"👤 **Учень:** {name}\n"
             f"📊 **Новий статус:** {level_names.get(new_lvl)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=card_buttons)
    )
    await callback.answer(f"Рівень для {name} змінено на {new_lvl}!")

@router.callback_query(F.data == "admin_toggle_test")
async def admin_toggle_testing_mode(callback: CallbackQuery):
    if callback.from_user.id != 8791830931: return
    global IS_TESTING_MODE
    IS_TESTING_MODE = not IS_TESTING_MODE
    status_text = "🟢 **УВІМКНЕНО** (Бот закритий)" if IS_TESTING_MODE else "🔴 **ВИМКНЕНО** (Бот відкритий)"
    await callback.message.answer(f"🛠️ Режим тестування змінено: {status_text}")
    await callback.answer()

@router.callback_query(F.data == "admin_manage_ach")
async def admin_start_manage_ach(callback: CallbackQuery):
    if callback.from_user.id != 8791830931 and callback.from_user.id not in ADMIN_L4_IDS: return
    buttons = [[InlineKeyboardButton(text=name, callback_data=f"achuser_{name}")] for name in RANDOM_NAMES]
    await callback.message.answer("Оберіть учня, якому хочете додати або змінити досягнення:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@router.callback_query(F.data.startswith("achuser_"))
async def admin_chosen_user_for_ach(callback: CallbackQuery, state: FSMContext):
    name = callback.data.replace("achuser_", "")
    await state.update_data(target_student=name)
    await callback.message.answer(f"✍️ Введіть текст нового досягнення для учня **{name}**:")
    await state.set_state(BotStates.admin_input_achievement)
    await callback.answer()

@router.message(BotStates.admin_input_achievement)
async def admin_save_user_achievement(message: Message, state: FSMContext):
    if message.from_user.id != 8791830931 and message.from_user.id not in ADMIN_L4_IDS: return
    data = await state.get_data()
    name = data.get("target_student")
    if name in USER_ACHIEVEMENTS: USER_ACHIEVEMENTS[name].append(message.text)
    else: USER_ACHIEVEMENTS[name] = [message.text]
    await message.answer(f"✅ Досягнення для **{name}** успішно додано!")
    await state.clear()

# ==========================================
# 🚀 АВТОПІНГ ДЛЯ ЗАХИСТУ ВІД СНУ (RENDER)
# ==========================================
async def self_ping_task():
    url = os.getenv("RENDER_EXTERNAL_URL")
    if not url:
        print("⚠️ Змінна RENDER_EXTERNAL_URL порожня. Автопінг вимкнено.")
        return
    print(f"🚀 Система захисту від сну запущена для сайту: {url}")
    await asyncio.sleep(60)
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    print(f"⏰ Автопінг відправлено! Статус Render: {response.status}")
        except Exception as e: print(f"❌ Помилка автопінгу: {e}")
        await asyncio.sleep(600)

# ==========================================
# 🚀 ЗАПУСК БОТА ТА ВЕБ-СЕРВЕРА ДЛЯ RENDER
# ==========================================
async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    
    app = web.Application()
    app.router.add_get("/", handle_render_hc)
    app.router.add_get("/webhook", handle_render_hc)
    
    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f" Web-server started on port {port}")

    asyncio.create_task(self_ping_task())

    print(" Bot polling started...")
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print(" Checking sessions...")
        await asyncio.sleep(10)
    except Exception as e: print(f"Пропуск очищення сесії: {e}")

    try: await dp.start_polling(bot)
    finally: await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
