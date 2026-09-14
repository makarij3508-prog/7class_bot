import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.chat_action import ChatActionSender

BOT_TOKEN = "8706179100:AAFC3NJTy0xi89EabaPOMlyJwjcxiibyZOE"

ADMIN_IDS = [8362874168] 

# 🆔 ID старосты (или чата), куда полетит финальный отчет об отсутствующих
# По умолчанию отправляем тебе, но сюда можно вписать ID старосты
STAROSTA_CHAT_ID = 8362874168 

# Хранилище данных в памяти бота
HOMEWORK_DATA = {}
IMPORTANT_ANNOUNCEMENT = "📌 **Важливі оголошення:**\n\nНаразі немає нових оголошень від адміністрації."
BOOKS_DATA = "📚 **Електронні підручники для 7 класу:**\n\nТут будуть посилання на завантаження твоїх підручників."

# База посещаемости: ID ученика -> True (присутствует) или False (отсутствует)
ATTENDANCE_DATA = {}
# Список имен/фамилий текущих отсутствующих для дневного отчета
ABSENT_TODAY_LIST = []

RANDOM_NAMES = ["Андрій", "Марія", "Олександр", "Дмитро", "Олена", "Максим", "Анна"]
RANDOM_MODE = "dice" 

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
    "🌟 Сьогодні твій щасливий день! На уроках буде спокійно, а домашку спишеш у друга.",
    "⚡ Обережно! На наступному уроці фізкультури доведеться багато бігати. Готуй кросівки!",
    "🧠 Сьогодні твій мозок працює на 200%. Ідеальний час, щоб підняти середній бал з алгебри!",
    "🍕 У їдальні сьогодні буде щось дуже смачненьке. Не пропусти велику перерву!",
    "📋 Тебе можуть викликати до дошки, але не панікуй — ШІ помічник у боті завжди під рукою.",
    "🤫 На вчителя сьогодні найде добрий настрій — самостійної роботи не буде!"
]

class BotStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_grades = State()
    waiting_for_hw_text = State()
    waiting_for_important_text = State()
    waiting_for_books_text = State()
    waiting_for_schedule_text = State()
    waiting_for_names_list = State()
    waiting_for_absence_info = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

def get_main_menu(user_id: int) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🗓️ Розклад"), KeyboardButton(text="📝 ДЗ")],
        [KeyboardButton(text="🤖 ШІ Допомога"), KeyboardButton(text="📊 Сер. бал")],
        [KeyboardButton(text="📚 Книги"), KeyboardButton(text="📌 Важливе")],
        [KeyboardButton(text="🎲 Рандом"), KeyboardButton(text="⚙️ Налаштування")]
    ]
    if user_id in ADMIN_IDS:
        buttons.append([KeyboardButton(text="🛠️ Admin Panel")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

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

admin_actions_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📝 Змінити ДЗ", callback_data="admin_add_hw"), InlineKeyboardButton(text="🗓️ Змінити Розклад", callback_data="admin_edit_sch")],
    [InlineKeyboardButton(text="📌 Оновити Важливе", callback_data="admin_add_important"), InlineKeyboardButton(text="📚 Оновити Книги", callback_data="admin_edit_books")],
    [InlineKeyboardButton(text="🎲 Налаштувати Рандом", callback_data="admin_config_random")],
    [InlineKeyboardButton(text="👥 Відмітити відсутнього", callback_data="admin_mark_attendance"), InlineKeyboardButton(text="📢 Надіслати звіт старості", callback_data="admin_send_report")]
])

settings_interactive_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏆 Мої досягнення", callback_data="profile_achievements")],
    [InlineKeyboardButton(text="🔮 Передбачення на день", callback_data="profile_prediction")]
])

async def send_human_message(message: Message, text: str, reply_markup=None):
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        delay = max(1.0, min((len(text) * 0.03) + random.uniform(0.4, 1.0), 3.0))
        await asyncio.sleep(delay)
    return await message.answer(text, reply_markup=reply_markup)

@router.message(Command("start"))
async def cmd_start(message: Message):
    text = "Привіт! Я твій помічник для 7 класу. Чим займемося сьогодні?"
    await send_human_message(message, text, reply_markup=get_main_menu(message.from_user.id))

@router.message(F.text == "📝 ДЗ")
async def show_subjects_for_hw(message: Message):
    await send_human_message(message, "Обери предмет, щоб подивитися домашнє завдання:", reply_markup=get_subjects_menu("view"))

@router.callback_query(F.data.startswith("view_"))
async def process_view_hw(callback: CallbackQuery):
    subject = callback.data.split("_")
    sub_name = SUBJECT_NAMES.get(subject, "Предмет")
    hw_text = HOMEWORK_DATA.get(subject, "Завдання поки що не додано.")
    await callback.message.edit_text(text=f"📝 **ДЗ з предмету {sub_name}:**\n\n{hw_text}", reply_markup=get_subjects_menu("view"))
    await callback.answer()

@router.message(F.text == "🗓️ Розклад")
async def show_schedule_days(message: Message):
    await send_human_message(message, "Обери день тижня, щоб подивитися розклад уроків:", reply_markup=get_days_menu("sch"))

@router.callback_query(F.data.startswith("sch_"))
async def process_schedule_callback(callback: CallbackQuery):
    day = callback.data.split("_")
    schedule_text = SCHEDULE_DATA.get(day, "⚠️ Розклад не знайдено.")
    await callback.message.edit_text(text=schedule_text, reply_markup=get_days_menu("sch"))
    await callback.answer()

@router.message(F.text == "📚 Книги")
async def show_books(message: Message):
    await send_human_message(message, BOOKS_DATA)

@router.message(F.text == "📌 Важливе")
async def show_important(message: Message):
    await send_human_message(message, IMPORTANT_ANNOUNCEMENT)

@router.message(F.text == "🛠️ Admin Panel")
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    await send_human_message(message, "👑 **Панель керування адміністратора**\n\nОбери, яку інформацію ти хочеш оновити або сформуй звіт посещаемости:", reply_markup=admin_actions_menu)

# АДМИНКА ОБРАБОТЧИКИ (ДЗ, Важное, Книги, Расписание, Рандом)
@router.callback_query(F.data == "admin_add_hw")
async def admin_choose_subject_hw(callback: CallbackQuery):
    await callback.message.edit_text(text="📝 Обери предмет, для якого хочеш записати ДЗ:", reply_markup=get_subjects_menu("edit"))
    await callback.answer()

@router.callback_query(F.data.startswith("edit_"))
async def admin_write_hw_text(callback: CallbackQuery, state: FSMContext):
    subject = callback.data.split("_")
    await state.update_data(chosen_subject=subject)
    await state.set_state(BotStates.waiting_for_hw_text)
    await callback.message.edit_text(text=f"✍️ Надішліть текст ДЗ для предмету: **{SUBJECT_NAMES.get(subject)}**")
