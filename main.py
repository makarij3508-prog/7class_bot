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

BOT_TOKEN = "8735817305:AAGSh53VV7GvWpDGA0XAE8IkklyoQ8ebivo"

# 👑 ТВОЙ ID СУПЕР-АДМИНА (МАКАР) — Работает напрямую
SUPER_ADMIN_IDS = {8791830931}

# 🪪 СИСТЕМА ПРАВ ПО ЮЗЕРНЕЙМАМ (Вписывай ники одноклассников сюда!)
MODERATOR_USERNAMES = ["@play.funtime.su"]  # Рівень 2
ASSISTANT_USERNAMES = ["@sanichka_gg"]                         # Рівень 1
TESTER_USERNAMES = ["@пример_тестировщика"]                           # Тестировщики

# 📢 ЮЗЕРНЕЙМ СТАРОСТЫ (Кому летит отчёт) — Сюда впиши ник старосты
STAROSTA_USERNAME = "@myveronichkam"

# 📊 Внутренние списки ID (Заполняются ботом автоматически на лету)
MODERATOR_IDS = []
HW_ASSISTANT_IDS = []
TESTER_IDS = []
STAROSTA_CHAT_ID = 0  # Сюда автоматически запишется ID старосты, когда он нажмет /start

# Словники динамических связок
USER_TELEGRAM_NAMES = {
    "8791830931": "Макар",
    "@llona_x": "Ілона",
    "@selarkin": "Роман",
    "@play.funtime.su": "Едуард",
    "@marri_chk": "Марічка",
    "@myveronichkam": "Вероніка",
    "@Red_tea21": "Назарій",
    "@Mi42a": "Мирослава",
    "@sanichka_gg": "Олександр",
    "@shadow123446": "Емілія",
    "@ezhik_lite": "Артем",
    "@Vladore1488": "Колодинський Богдан",
    "@Sharik_xd": "Ковальчук Богдан"
}

USER_USERNAMES = {}  # Цей рядок лишаємо повністю порожнім

# 💬 БАЗА ДАНИХ ШКІЛЬКОГО ЧАТУ, МУТІВ ТА БАНІВ
CHAT_REGISTERED_USERS = {}  # ID -> ім'я тех, кто в чате
BANNED_USERS = []           # Чёрный список (ID забаненных)
MUTED_USERS = {}            # ID -> timestamp окончания мута

# 🛠️ ГЛОБАЛЬНИЙ РЕЖИМ ТЕСТУВАННЯ
IS_TESTING_MODE = False

HOMEWORK_DATA = {}
IMPORTANT_ANNOUNCEMENT = "📌 **Важливі оголошення:**\n\nНаразі немає нових оголошень від адміністрації."
BOOKS_DATA = "📚 **Електронні підручники для 7 класу:**\n\nТут будуть посилання на завантаження твоїх підручників."
ABSENT_TODAY_LIST = []
RANDOM_MODE = "dice"

# 👥 ПОВА БАЗА ДАНИХ ТВОГО КЛАСУ (28 учнів)
RANDOM_NAMES = [
    "Олександр", "Андрій", "Данило", "Колодинський Богдан", "Ковалевчук Богдан", 
    "Мирослава", "Матвій", "Софія", "Михайло", "Макар", "Ілона", "Марічка", 
    "Маргарита", "Ангеліна", "Нікіта", "Альберт", "Єва", "Роман", "Владислав", 
    "Назарій", "Едуард", "Станіслав", "Артем", "Емілія", "Вероніка", "Ілля", "Дмитро", "Макс"
]
USER_ACHIEVEMENTS = {name: ["🥇 Перший запуск бота", "🥈 Активний учень 7 класу"] for name in RANDOM_NAMES}

SCHEDULE_DATA = {
    "mon": "🗓️ **Понеділок:**\n1. ЗБД / Зар. літ.\n2. Фізика\n3. Фізкультура\n4. Укр. література\n5. Алгебра\n6. Англійська\n7. Географія",
    "tue": "🗓️ **Вівторок:**\n1. Історія\n2. Біологія\n3. Геометрія\n4. Укр. мова\n5. ЗБД\n6. Інформатика\n7. Технології",
    "wed": "🗓️ **Середа:**\n1. Укр. мова\n2. Хімія\n3. Зар. література\n4. Фізкультура\n5. Алгебра\n6. Англійська\n7. Географія",
    "thu": "🗓️ **Четвер:**\n1. Англ. / Біологія\n2. Фізика\n3. Мистецтво\n4. Укр. мова\n5. Геометрія\n6. Інформатика\n7. Історія",
    "fri": "🗓️ **P'ятниця:**\n1. Історія\n2. Мистецтво\n3. Англійська\n4. Укр. література\n5. Фізкультура\n6. Біологія\n7. Алгебра"
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
    "🍕 У їдальні сьогодні неймовірно смачні булочки, встигни на перерві!",
    "🎒 Ти забудеш щось важливе вдома, перевір рюкзак просто зараз!",
    "🍀 На укр. мові тебе сьогодні омине виклик до дошки. Везунчик!",
    "🤫 Хтось із класу готує для тебе приємний сюрприз або секрет.",
    "📈 Твій середній бал скоро злетить вгору, продовжуй в тому ж дусі!",
    "🦉 Сьогодні вчитель фізики буде в дуже доброму гуморі.",
    "🎨 Чудовий день для творчості, на мистецтві буде легка тема!"
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
    admin_input_username_for_level = State()  # Состояние для ввода @username
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
    if user_id in SUPER_ADMIN_IDS or user_id in MODERATOR_IDS or user_id in HW_ASSISTANT_IDS or user_id in TESTER_IDS:
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
    if user_id in HW_ASSISTANT_IDS or user_id in MODERATOR_IDS or user_id in SUPER_ADMIN_IDS:
        keyboard.append([InlineKeyboardButton(text="📝 Змінити ДЗ", callback_data="admin_add_hw")])
    if user_id in MODERATOR_IDS or user_id in SUPER_ADMIN_IDS:
        keyboard.append([InlineKeyboardButton(text="🗓️ Змінити Розклад", callback_data="admin_edit_sch")])
        keyboard.append([InlineKeyboardButton(text="📌 Оновити Важливе", callback_data="admin_add_important"), InlineKeyboardButton(text="📚 Оновити Книги", callback_data="admin_edit_books")])
        keyboard.append([InlineKeyboardButton(text="🎲 Налаштувати Рандом", callback_data="admin_config_random"), InlineKeyboardButton(text="🏆 Керувати досягненнями", callback_data="admin_manage_ach")])
        keyboard.append([InlineKeyboardButton(text="👥 Відмітити відсутнього", callback_data="admin_mark_attendance"), InlineKeyboardButton(text="📢 Надіслати звіт старості", callback_data="admin_send_report")])
    if user_id in SUPER_ADMIN_IDS:
        keyboard.append([
            InlineKeyboardButton(text="🧪 Тест-Режим: ОН/ОФФ", callback_data="admin_toggle_test"),
            InlineKeyboardButton(text="👑 Призначити Адміна", callback_data="admin_give_level_menu")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

settings_interactive_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏆 Досягнення", callback_data="profile_achievements"), InlineKeyboardButton(text="🔮 Передбачення", callback_data="profile_prediction")],
    [InlineKeyboardButton(text="📜 Лог оновлень", callback_data="profile_changelog")]
])

async def send_human_message(message: Message, text: str, reply_markup=None):
    # Мгновенная отправка без симуляции печати и зависаний!
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
        
        # Перевіряємо роль модератора (Рівень 2)
        if user_key in MODERATOR_USERNAMES and user_id not in MODERATOR_IDS:
            MODERATOR_IDS.append(user_id)
            print(f"✨ Роль Модератора автоматично видана для {user_key}")
            
        # Перевіряємо роль помічника по ДЗ (Рівень 1)
        if user_key in ASSISTANT_USERNAMES and user_id not in HW_ASSISTANT_IDS:
            HW_ASSISTANT_IDS.append(user_id)
            print(f"✨ Роль Помічника по ДЗ автоматично видана для {user_key}")
            
        # Перевіряємо роль тестувальника
        if user_key in TESTER_USERNAMES and user_id not in TESTER_IDS:
            TESTER_IDS.append(user_id)
            print(f"✨ Роль Teстувальника автоматично видана для {user_key}")
            
        # Перевіряємо роль старости
        if user_key == STAROSTA_USERNAME.lower():
            global STAROSTA_CHAT_ID
            STAROSTA_CHAT_ID = user_id
            print(f"✨ ID Старости класу автоматично прив'язано до {user_key}")

    await send_human_message(message, "Привіт! Я твій помічник для 7 класу. Чим займемося сьогодні?", reply_markup=get_main_menu(user_id))

@router.message(F.text == "📝 ДЗ")
async def show_subjects_for_hw(message: Message):
    user_id = message.from_user.id
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in MODERATOR_IDS and user_id not in HW_ASSISTANT_IDS and user_id not in TESTER_IDS: return
    await send_human_message(message, "Обери предмет, щоб подивитися домашнє завдання:", reply_markup=get_subjects_menu("view"))

@router.callback_query(F.data.startswith("view_"))
async def process_view_hw(callback: CallbackQuery):
    data_parts = callback.data.split("_", maxsplit=1)
    subject = data_parts[1] if len(data_parts) > 1 else ""
    sub_name = SUBJECT_NAMES.get(subject, "Предмет")
    hw_text = HOMEWORK_DATA.get(subject, "Завдання поки що не додано.")
    await callback.message.edit_text(text=f"📝 **ДЗ з предмету {sub_name}:**\n\n{hw_text}", reply_markup=get_subjects_menu("view"))
    await callback.answer()

@router.message(F.text == "🗓️ Розклад")
async def show_schedule_days(message: Message):
    user_id = message.from_user.id
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in MODERATOR_IDS and user_id not in HW_ASSISTANT_IDS and user_id not in TESTER_IDS: return
    await send_human_message(message, "Обери день тижня:", reply_markup=get_days_menu("sch"))

@router.callback_query(F.data.startswith("sch_"))
async def process_schedule_callback(callback: CallbackQuery):
    data_parts = callback.data.split("_", maxsplit=1)
    day = data_parts[1] if len(data_parts) > 1 else ""
    await callback.message.edit_text(text=SCHEDULE_DATA.get(day, "⚠️ Нічого немає."), reply_markup=get_days_menu("sch"))
    await callback.answer()

@router.message(F.text == "📚 Книги")
async def handle_show_books(message: Message):
    user_id = message.from_user.id
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in MODERATOR_IDS and user_id not in HW_ASSISTANT_IDS and user_id not in TESTER_IDS: return
    await send_human_message(message, BOOKS_DATA)

@router.message(F.text == "📌 Важливе")
async def handle_show_important(message: Message):
    user_id = message.from_user.id
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in MODERATOR_IDS and user_id not in HW_ASSISTANT_IDS and user_id not in TESTER_IDS: return
    await send_human_message(message, IMPORTANT_ANNOUNCEMENT)

@router.message(F.text == "🎲 Рандом")
async def handle_show_random(message: Message):
    user_id = message.from_user.id
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in MODERATOR_IDS and user_id not in HW_ASSISTANT_IDS and user_id not in TESTER_IDS: return
    global RANDOM_MODE
    if RANDOM_MODE == "dice": await message.answer_dice()
    else:
        name = random.choice(RANDOM_NAMES)
        await send_human_message(message, f"🎲 Випадковий учень до дошки: **{name}**")

@router.message(F.text == "📊 Сер. бал")
async def ask_for_grades(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in MODERATOR_IDS and user_id not in HW_ASSISTANT_IDS and user_id not in TESTER_IDS: return
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
    url = "https://pollinations.ai"
    payload = {
        "messages": [
            {"role": "system", "content": "Ти помічник для 7 класу. Відповідай чітко, коротко, українською."},
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
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in MODERATOR_IDS and user_id not in HW_ASSISTANT_IDS and user_id not in TESTER_IDS: return
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
# 🔊 МОДЕРОВАНИЙ ЧАТ КЛАСУ (МУТ / БАН)
# ==========================================

@router.message(F.text == "🔊 Чат класу")
async def enter_chat_room(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    # Глобальна перевірка на бан
    if user_id in BANNED_USERS:
        await message.answer("🛑 **Доступ заблоковано!**\n\nВи забанені в чаті адміністрацією класу за порушення правил.")
        return

    # Перевірка на тех. роботи для чату
    if IS_TESTING_MODE and user_id not in SUPER_ADMIN_IDS and user_id not in MODERATOR_IDS and user_id not in HW_ASSISTANT_IDS and user_id not in TESTER_IDS:
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

    # Перевірка на Мут
    if user_id in MUTED_USERS:
        now = datetime.now().timestamp()
        if now < MUTED_USERS[user_id]:
            time_left = int((MUTED_USERS[user_id] - now) / 60)
            await message.answer(f"🤫 **У вас діє режим тиші (МУТ)!**\n\nВи зможете писати знову через **{time_left if time_left > 0 else 1} хв.**")
            return
        else:
            MUTED_USERS.pop(user_id)

    sender_name = CHAT_REGISTERED_USERS.get(user_id, "Учень")

    # Розсилаємо всім учасникам у чаті
    for target_id in list(CHAT_REGISTERED_USERS.keys()):
        if target_id != user_id:
            try: await bot.send_message(chat_id=target_id, text=f"💬 **[{sender_name}]:** {message.text}")
            except Exception: pass

    # Лог чату для ВСІХ АДМІНІВ з інлайн-кнопками покарання
    all_admins = set(SUPER_ADMIN_IDS + MODERATOR_IDS + HW_ASSISTANT_IDS)
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
    if user_id in USER_TELEGRAM_NAMES: name = USER_TELEGRAM_NAMES[user_id]
    else: name = RANDOM_NAMES[user_id % len(RANDOM_NAMES)]
        
    ach_list = USER_ACHIEVEMENTS.get(name, ["Поки що немає досягнень"])
    formatted = "\n".join(ach_list)
    await callback.message.answer(f"🏆 **Досягнення учня ({name}):**\n\n{formatted}")
    await callback.answer()

@router.callback_query(F.data == "profile_changelog")
async def process_changelog(callback: CallbackQuery):
    await callback.message.answer(
        "📜 **Офіційний лог оновлень (v2.0):**\n\n"
        "• **Повна прив'язка по Юзернеймах:** І модератори, і учні, і староста з тестувальниками додаються через @username. Більше ніяких ID!\n"
        "• **Модерований Чат класу:** Інтегровано мут на 15 хв та бан з автоматичними повідомленнями в чат.\n"
        "• **Робота 24/7:** Інтегровано систему фонового автопінгу від сну на Render."
    )
    await callback.answer()

@router.message(F.text == "🛠️ Admin Panel")
async def handle_admin_panel(message: Message): await admin_panel(message)

# ==========================================
# 🛠️ АДМІНІСТРАТИВНА ПАНЕЛЬ ТА КЕРУВАННЯ
# ==========================================

async def admin_panel(message: Message):
    user_id = message.from_user.id
    if user_id in SUPER_ADMIN_IDS or user_id in MODERATOR_IDS or user_id in HW_ASSISTANT_IDS:
        await send_human_message(message, "🛠️ Вітаємо в панелі адміністратора. Доступні функції згідно з вашим рівнем прав:", reply_markup=get_admin_menu_keyboard(user_id))
    else:
        await send_human_message(message, "🛑 У вас немає доступу до цієї команди.")

# 🚨 АДМІН-КНОПКИ: ОБРОБКА МУТУ ТА БАНУ З ЧАТЛОГІВ
@router.callback_query(F.data.startswith("mute_15_") | F.data.startswith("ban_"))
async def process_chat_punishment(callback: CallbackQuery):
    admin_id = callback.from_user.id
    all_admins = set(SUPER_ADMIN_IDS + MODERATOR_IDS + HW_ASSISTANT_IDS)
    if admin_id not in all_admins: return

    data_parts = callback.data.split("_")
    action = data_parts[0]
    
    if action == "mute":
        target_id = int(data_parts[2])
        target_name = data_parts[3]
        # Вішаємо мут на 15 хвилин від поточного часу
        MUTED_USERS[target_id] = datetime.now().timestamp() + 900
        alert_text = f"🤫 **Користувач {target_name} замучений на 15 хв за порушення правил чату!**"
    else:
        target_id = int(data_parts[1])
        target_name = data_parts[2]
        if target_id not in BANNED_USERS: BANNED_USERS.append(target_id)
        alert_text = f"🛑 **Користувач {target_name} назавжди забанений у чаті класу!**"

    # Автоматично надсилаємо системне повідомлення в загальну кімнату чату класу
    for user_id in list(CHAT_REGISTERED_USERS.keys()):
        try: await bot.send_message(chat_id=user_id, text=alert_text)
        except Exception: pass

    await callback.message.edit_text(text=f"✅ Покорання успішно застосовано!\n{alert_text}")
    await callback.answer()

# 👑 СУПЕР-АДМІН: ПРИЗНАЧЕННЯ НОВОГО АДМІНА ПО ЮЗЕРНЕЙМУ
@router.callback_query(F.data == "admin_give_level_menu")
async def admin_start_give_level(callback: CallbackQuery):
    if callback.from_user.id not in SUPER_ADMIN_IDS: return
    buttons = [[InlineKeyboardButton(text=name, callback_data=f"giveadm_{name}")] for name in RANDOM_NAMES]
    await callback.message.answer("👑 **Оберіть учня, якого хочете зробити адміністратором:**", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@router.callback_query(F.data.startswith("giveadm_"))
async def admin_chosen_user_for_level(callback: CallbackQuery, state: FSMContext):
    data_parts = callback.data.split("_", maxsplit=1)
    name = data_parts[1] if len(data_parts) > 1 else "Учень"
    await state.update_data(chosen_admin_name=name)
    level_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📐 Рівень 1 (Помічник по ДЗ)", callback_data="setlevel_1")],
        [InlineKeyboardButton(text="⭐ Рівень 2 (Модератор / Староста)", callback_data="setlevel_2")]
    ])
    await callback.message.answer(f"Який рівень прав ви хочете надати учню **{name}**?", reply_markup=level_menu)
    await callback.answer()

@router.callback_query(F.data.startswith("setlevel_"))
async def admin_input_id_for_level(callback: CallbackQuery, state: FSMContext):
    data_parts = callback.data.split("_", maxsplit=1)
    level = int(data_parts[1]) if len(data_parts) > 1 else 1
    await state.update_data(chosen_level=level)
    await callback.message.answer("⚙️ Тепер, будь ласка, **введіть юзернейм цього учня** (наприклад: `@andrey`):")
    await state.set_state(BotStates.admin_input_username_for_level)
    await callback.answer()

@router.message(BotStates.admin_input_username_for_level)
async def admin_save_level_by_username(message: Message, state: FSMContext):
    if message.from_user.id not in SUPER_ADMIN_IDS: return
    
    target_username = message.text.strip().lower()
    if not target_username.startswith("@"): target_username = f"@{target_username}"
    
    data = await state.get_data()
    name = data.get("chosen_admin_name")
    level = data.get("chosen_level")
    
    # Записуємо ник у глобальні списки Части 1
    if level == 1:
        if target_username not in ASSISTANT_USERNAMES: ASSISTANT_USERNAMES.append(target_username)
        role_text = "📐 Рівень 1 (Помічник по ДЗ)"
    elif level == 2:
        if target_username not in MODERATOR_USERNAMES: MODERATOR_USERNAMES.append(target_username)
        role_text = "⭐ Рівень 2 (Модератор / Староста)"

    # Якщо учень вже запускав бота і його ID є в базі, прилетить миттєвий апгрейд
    target_id = USER_USERNAMES.get(target_username)
    if target_id:
        if level == 1 and target_id not in HW_ASSISTANT_IDS: HW_ASSISTANT_IDS.append(target_id)
        if level == 2 and target_id not in MODERATOR_IDS: MODERATOR_IDS.append(target_id)
        status = "(Користувача розпізнано, права активовано!)"
    else:
        status = "(Користувач ще не запускав бота, права активуються автоматично при його першому старті!)"
        
    await message.answer(f"✅ Учня **{name}** успішно внесено до списків ролей!\n\n**Посада:** {role_text}\n**Юзернейм:** `{target_username}`\n⚙️ {status}")
    await state.clear()

@router.callback_query(F.data == "admin_toggle_test")
async def admin_toggle_testing_mode(callback: CallbackQuery):
    global IS_TESTING_MODE
    if callback.from_user.id not in SUPER_ADMIN_IDS: return
    IS_TESTING_MODE = not IS_TESTING_MODE
    status_text = "🟢 **УВІМКНЕНО** (Бот закритий)" if IS_TESTING_MODE else "🔴 **ВИМКНЕНО** (Бот відкритий)"
    await callback.message.answer(f"🛠️ Режим тестування змінено: {status_text}")
    await callback.answer()

@router.callback_query(F.data == "admin_manage_ach")
async def admin_start_manage_ach(callback: CallbackQuery):
    if callback.from_user.id not in SUPER_ADMIN_IDS and callback.from_user.id not in MODERATOR_IDS: return
    buttons = [[InlineKeyboardButton(text=name, callback_data=f"achuser_{name}")] for name in RANDOM_NAMES]
    await callback.message.answer("Оберіть учня, якому хочете додати або змінити досягнення:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@router.callback_query(F.data.startswith("achuser_"))
async def admin_chosen_user_for_ach(callback: CallbackQuery, state: FSMContext):
    data_parts = callback.data.split("_", maxsplit=1)
    name = data_parts[1] if len(data_parts) > 1 else "Учень"
    await state.update_data(target_student=name)
    await callback.message.answer(f"✍️ Введіть текст нового досягнення для учня **{name}**:")
    await state.set_state(BotStates.admin_input_achievement)
    await callback.answer()

@router.message(BotStates.admin_input_achievement)
async def admin_save_user_achievement(message: Message, state: FSMContext):
    if message.from_user.id not in SUPER_ADMIN_IDS and message.from_user.id not in MODERATOR_IDS: return
    data = await state.get_data()
    name = data.get("target_student")
    if name in USER_ACHIEVEMENTS: USER_ACHIEVEMENTS[name].append(message.text)
    else: USER_ACHIEVEMENTS[name] = [message.text]
    await message.answer(f"✅ Досягнення для **{name}** успішно додано!")
    await state.clear()

@router.callback_query(F.data == "admin_add_hw")
async def admin_choose_subject_hw(callback: CallbackQuery):
    if callback.from_user.id not in SUPER_ADMIN_IDS and callback.from_user.id not in MODERATOR_IDS and callback.from_user.id not in HW_ASSISTANT_IDS: return
    await callback.message.answer("Оберіть предмет, для якого хочете змінити ДЗ:", reply_markup=get_subjects_menu("edit_hw"))
    await callback.answer()

@router.callback_query(F.data.startswith("edit_hw_"))
async def admin_input_hw_text(callback: CallbackQuery, state: FSMContext):
    data_parts = callback.data.split("_", maxsplit=2)
    subject = data_parts[2] if len(data_parts) > 2 else ""
    await state.update_data(chosen_subject=subject)
    await callback.message.answer(f"Введіть новий текст ДЗ для предмета {SUBJECT_NAMES.get(subject, 'Предмет')}:")
    await state.set_state(BotStates.waiting_for_hw_text)
    await callback.answer()

@router.message(BotStates.waiting_for_hw_text)
async def admin_save_hw_text(message: Message, state: FSMContext):
    global HOMEWORK_DATA
    if message.from_user.id not in SUPER_ADMIN_IDS and message.from_user.id not in MODERATOR_IDS and message.from_user.id not in HW_ASSISTANT_IDS: return
    data = await state.get_data()
    subject = data.get("chosen_subject")
    HOMEWORK_DATA[subject] = message.text
    await message.answer(f"✅ ДЗ для {SUBJECT_NAMES.get(subject, 'Предмет')} успішно оновлено!")
    await state.clear()

@router.callback_query(F.data == "admin_edit_sch")
async def admin_choose_day_sch(callback: CallbackQuery):
    if callback.from_user.id not in SUPER_ADMIN_IDS and callback.from_user.id not in MODERATOR_IDS: return
    await callback.message.answer("Оберіть день для зміни розкладу:", reply_markup=get_days_menu("edit_sch"))
    await callback.answer()

@router.callback_query(F.data.startswith("edit_sch_"))
async def admin_input_sch_text(callback: CallbackQuery, state: FSMContext):
    data_parts = callback.data.split("_", maxsplit=2)
    day = data_parts[2] if len(data_parts) > 2 else ""
    await state.update_data(chosen_day=day)
    await callback.message.answer(f"Введіть новий розклад для дня ({DAY_NAMES.get(day, 'День')}):")
    await state.set_state(BotStates.waiting_for_schedule_text)
    await callback.answer()

@router.message(BotStates.waiting_for_schedule_text)
async def admin_save_sch_text(message: Message, state: FSMContext):
    global SCHEDULE_DATA
    if message.from_user.id not in SUPER_ADMIN_IDS and message.from_user.id not in MODERATOR_IDS: return
    data = await state.get_data()
    day = data.get("chosen_day")
    SCHEDULE_DATA[day] = message.text
    await message.answer(f"✅ Розклад на {DAY_NAMES.get(day, 'День')} успішно змінено!")
    await state.clear()

@router.callback_query(F.data == "admin_add_important")
async def admin_input_important(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in SUPER_ADMIN_IDS and callback.from_user.id not in MODERATOR_IDS: return
    await callback.message.answer("Введіть текст нового важливого оголошення:")
    await state.set_state(BotStates.waiting_for_important_text)
    await callback.answer()

@router.message(BotStates.waiting_for_important_text)
async def admin_save_important(message: Message, state: FSMContext):
    global IMPORTANT_ANNOUNCEMENT
    if message.from_user.id not in SUPER_ADMIN_IDS and message.from_user.id not in MODERATOR_IDS: return
    IMPORTANT_ANNOUNCEMENT = message.text
    await message.answer("✅ Важливе оголошення оновлено!")
    await state.clear()

@router.callback_query(F.data == "admin_edit_books")
async def admin_input_books(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in SUPER_ADMIN_IDS and callback.from_user.id not in MODERATOR_IDS: return
    await callback.message.answer("Введіть новий список книг / посилань:")
    await state.set_state(BotStates.waiting_for_books_text)
    await callback.answer()

@router.message(BotStates.waiting_for_books_text)
async def admin_save_books(message: Message, state: FSMContext):
    global BOOKS_DATA
    if message.from_user.id not in SUPER_ADMIN_IDS and message.from_user.id not in MODERATOR_IDS: return
    BOOKS_DATA = message.text
    await message.answer("✅ Список книг успішно оновлено!")
    await state.clear()

@router.callback_query(F.data == "admin_config_random")
async def admin_config_random_mode(callback: CallbackQuery):
    if callback.from_user.id not in SUPER_ADMIN_IDS and callback.from_user.id not in MODERATOR_IDS: return
    menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Смайл кубика (Dice)", callback_data="set_rand_dice")],
        [InlineKeyboardButton(text="👥 Випадкове ім'я учня", callback_data="set_rand_name")]
    ])
    await callback.message.answer("Оберіть режим роботи кнопки Рандом:", reply_markup=menu)
    await callback.answer()

@router.callback_query(F.data.startswith("set_rand_"))
async def admin_set_random_mode(callback: CallbackQuery):
    global RANDOM_MODE
    if callback.from_user.id not in SUPER_ADMIN_IDS and callback.from_user.id not in MODERATOR_IDS: return
    data_parts = callback.data.split("_", maxsplit=2)
    mode = data_parts[2] if len(data_parts) > 2 else "dice"
    RANDOM_MODE = mode
    mode_text = "Кубик (Dice)" if mode == "dice" else "Вибір учня зі списку"
    await callback.message.answer(f"✅ Режим рандому змінено на: **{mode_text}**")
    await callback.answer()

@router.callback_query(F.data == "admin_mark_attendance")
async def admin_start_attendance(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in SUPER_ADMIN_IDS and callback.from_user.id not in MODERATOR_IDS: return
    await callback.message.answer("📝 Введіть прізвища або імена учнів, які сьогодні відсутні (через кому або з нового рядка):")
    await state.set_state(BotStates.waiting_for_absence_info)
    await callback.answer()

@router.message(BotStates.waiting_for_absence_info)
async def admin_save_attendance(message: Message, state: FSMContext):
    global ABSENT_TODAY_LIST
    if message.from_user.id not in SUPER_ADMIN_IDS and message.from_user.id not in MODERATOR_IDS: return
    text = message.text.replace("\n", ",")
    ABSENT_TODAY_LIST = [name.strip() for name in text.split(",") if name.strip()]
    if ABSENT_TODAY_LIST:
        formatted = "\n".join([f"• {n}" for n in ABSENT_TODAY_LIST])
        await message.answer(f"✅ Список збережено (Всього: {len(ABSENT_TODAY_LIST)}):\n{formatted}")
    else: await message.answer("⚠️ Список порожній.")
    await state.clear()

@router.callback_query(F.data == "admin_send_report")
async def admin_send_report_to_starosta(callback: CallbackQuery):
    if callback.from_user.id not in SUPER_ADMIN_IDS and callback.from_user.id not in MODERATOR_IDS: return
    if not STAROSTA_CHAT_ID:
        await callback.message.answer("⚠️ Староста ще не запустив бота, його ID не знайдено!")
        await callback.answer()
        return
    if not ABSENT_TODAY_LIST:
        await callback.message.answer("⚠️ Список відсутніх порожній!")
        await callback.answer()
        return
    formatted = "\n".join([f"• {name}" for name in ABSENT_TODAY_LIST])
    report_text = f"📢 **Щоденний звіт про відсутніх**\n\nУчнів, яких немає:\n{formatted}\n\nВсього: {len(ABSENT_TODAY_LIST)}"
    try:
        await bot.send_message(chat_id=STAROSTA_CHAT_ID, text=report_text)
        await callback.message.answer("🚀 Звіт надіслано старості!")
    except Exception: await callback.message.answer(f"❌ Помилка відправки! Перевірте статус старости.")
    await callback.answer()

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
                    print(f"⏰ [Принт кожні 10 хв] Автопінг відправлено! Статус сервера Render: {response.status}")
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
    
    # 🚨 ЖЕСТКИЙ ФИКС КОНФЛИКТА ТОКЕНА
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("⏳ Очищення сесій... Чекаємо 10 секунд для скидання конфлікту токена...")
        await asyncio.sleep(10)
    except Exception as e:
        print(f"Пропуск очищення сесії: {e}")

    try: await dp.start_polling(bot)
    finally: await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
