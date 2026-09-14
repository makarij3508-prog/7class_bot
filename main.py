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
ADMIN_IDS = [8362874168]  # Твой ID добавлен сюда напрямую!

# 🗓️ Точный расписание уроков 7 класса
SCHEDULE_DATA = {
    "mon": "🗓️ **Понеділок:**\n1. ЗБД / Зар. літ.\n2. Фізика\n3. Фізкультура\n4. Укр. література\n5. Алгебра\n6. Англійська\n7. Географія",
    "tue": "🗓️ **Вівторок:**\n1. Історія\n2. Біологія\n3. Геометрія\n4. Укр. мова\n5. ЗБД\n6. Інформатика\n7. Технології",
    "wed": "🗓️ **Середа:**\n1. Укр. мова\n2. Хімія\n3. Зар. література\n4. Фізкультура\n5. Алгебра\n6. Англійська\n7. Географія",
    "thu": "🗓️ **Четвер:**\n1. Англ. / Біологія\n2. Фізика\n3. Мистецтво\n4. Укр. мова\n5. Геометрія\n6. Інформатика\n7. Історія",
    "fri": "🗓️ **П'ятниця:**\n1. Історія\n2. Мистецтво\n3. Англійська\n4. Укр. література\n5. Фізкультура\n6. Біологія\n7. Алгебра"
}

class BotStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_grades = State()

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

subjects_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📐 Алгебра", callback_data="sub_algebra"), InlineKeyboardButton(text="📐 Геометрія", callback_data="sub_geometry")],
    [InlineKeyboardButton(text="🧲 Фізика", callback_data="sub_physics"), InlineKeyboardButton(text="🧪 Хімія", callback_data="sub_chemistry")],
    [InlineKeyboardButton(text="🧬 Біологія", callback_data="sub_biology"), InlineKeyboardButton(text="🌍 Географія", callback_data="sub_geography")],
    [InlineKeyboardButton(text="📜 Історія Укр.", callback_data="sub_hist_ua"), InlineKeyboardButton(text="🏰 Всесвітня iст.", callback_data="sub_hist_world")],
    [InlineKeyboardButton(text="🇺🇦 Укр. мова", callback_data="sub_lang_ua"), InlineKeyboardButton(text="📚 Укр. літ.", callback_data="sub_lit_ua")],
    [InlineKeyboardButton(text="🇬🇧 Англійська", callback_data="sub_english"), InlineKeyboardButton(text="🗺️ Зарубіжна літ.", callback_data="sub_lit_world")],
    [InlineKeyboardButton(text="💻 Інформатика", callback_data="sub_inf"), InlineKeyboardButton(text="🛠️ Технології", callback_data="sub_tech")],
    [InlineKeyboardButton(text="🎨 Мистецтво", callback_data="sub_art"), InlineKeyboardButton(text="🌱 ЗБД", callback_data="sub_zbd")]
])

schedule_days_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Понеділок", callback_data="sch_mon"), InlineKeyboardButton(text="Вівторок", callback_data="sch_tue")],
    [InlineKeyboardButton(text="Середа", callback_data="sch_wed"), InlineKeyboardButton(text="Четвер", callback_data="sch_thu")],
    [InlineKeyboardButton(text="П'ятниця", callback_data="sch_fri")]
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
    text = "Обери предмет, щоб подивитися або додати домашнє завдання:"
    await send_human_message(message, text, reply_markup=subjects_menu)

@router.message(F.text == "🗓️ Розклад")
async def show_schedule_days(message: Message):
    text = "Обери день тижня, щоб подивитися розклад уроків:"
    await send_human_message(message, text, reply_markup=schedule_days_menu)

@router.callback_query(F.data.startswith("sch_"))
async def process_schedule_callback(callback: CallbackQuery):
    day_parts = callback.data.split("_")
    day = day_parts[1]  # ИСПРАВЛЕНО: берем сам день недели ("mon", "tue" и т.д.)
    schedule_text = SCHEDULE_DATA.get(day, "⚠️ Розклад не знайдено.")
    await callback.message.edit_text(text=schedule_text, reply_markup=schedule_days_menu)
    await callback.answer()

@router.message(F.text == "📚 Книги")
async def show_books(message: Message):
    text = "📚 **Електронні підручники для 7 класу:**\n\nТут будуть посилання на завантаження твоїх підручників."
    await send_human_message(message, text)

@router.message(F.text == "📌 Важливе")
async def show_important(message: Message):
    text = "📌 **Важливі оголошення:**\n\nНаразі немає нових оголошень від старости чи вчителів."
    await send_human_message(message, text)

# 🛠️ РАБОЧАЯ АДМИНКА
@router.message(F.text == "🛠️ Admin Panel")
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    text = "👑 **Вітаю в панелі керування розробника!**\n\nБот працює стабільно на сервері Render. Усі системи функціонують у штатному режимі."
    await send_human_message(message, text)

# 🎲 НОВАЯ ЛОГИКА ДЛЯ РАНДОМА
@router.message(F.text == "🎲 Рандом")
async def cmd_random(message: Message):
    await message.answer("🎲 Кидаю кубик на удачу...")
    await bot.send_dice(chat_id=message.chat.id, emoji="🎲")

# ⚙️ НОВАЯ ЛОГИКА ДЛЯ НАСТРОЕК
@router.message(F.text == "⚙️ Налаштування")
async def cmd_settings(message: Message):
    text = (
        f"⚙️ **Налаштування профілю:**\n\n"
        f"👤 **Користувач:** {message.from_user.first_name}\n"
        f"🆔 **Твій ID:** `{message.from_user.id}`\n"
        f"🎒 **Клас:** 7 клас\n"
        f"🤖 **Версія бота:** 2.0 (Stable)"
    )
    await send_human_message(message, text)

# 📊 НОВАЯ ЛОГИКА ДЛЯ СРЕДНЕГО БАЛЛА
@router.message(F.text == "📊 Сер. бал")
async def cmd_average_welcome(message: Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_grades)
    text = "📊 **Калькулятор середнього балу**\n\nНапиши мені свої оцінки через кому (наприклад: `10, 9, 12, 11, 8`), і я порахую твій середній бал!"
    await send_human_message(message, text)

# Общие текстовые обработчики состояний
@router.message(BotStates.waiting_for_grades)
async def process_grades(message: Message, state: FSMContext):
    if message.text in ["🗓️ Розклад", "📝 ДЗ", "🤖 ШІ Допомога", "📊 Сер. бал", "📚 Книги", "📌 Важливе", "🎲 Рандом", "⚙️ Налаштування"]:
        await state.clear()
        if message.text == "📝 ДЗ": await show_subjects_for_hw(message)
        elif message.text == "🗓️ Розклад": await show_schedule_days(message)
        return

    try:
        raw_grades = message.text.replace(" ", "").split(",")
        grades = [int(g) for g in raw_grades if g.isdigit() and 1 <= int(g) <= 12]
        
        if not grades:
            await message.answer("⚠️ Будь ласка, введи коректні оцінки від 1 до 12 через кому!")
            return
            
        avg = sum(grades) / len(grades)
        await message.answer(f"📈 Твій середній бал за ці оцінки: **{avg:.2f}**")
    except Exception:
        await message.answer("⚠️ Сталася помилка при розрахунку. Перевір, чи правильно введені цифри!")

# 🤖 РЕЖИМ ШІ
@router.message(F.text == "🤖 ШІ Допомога")
async def ai_welcome(message: Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_question)
    text = "🤖 Напиши мені своє питання, і я безкоштовно допоможу розібратися!"
    await send_human_message(message, text)

@router.message(BotStates.waiting_for_question)
async def ai_answer(message: Message, state: FSMContext):
    if message.text in ["🗓️ Розклад", "📝 ДЗ", "🤖 ШІ Допомога", "📊 Сер. бал", "📚 Книги", "📌 Важливе", "🎲 Рандом", "⚙️ Налаштування"]:
        await state.clear()
        if message.text == "📝 ДЗ": await show_subjects_for_hw(message)
        elif message.text == "🗓️ Розклад": await show_schedule_days(message)
        elif message.text == "📚 Книги": await show_books(message)
        elif message.text == "📌 Важливе": await show_important(message)
        return

    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        try:
            import api_helper
            ans_text = await api_helper.get_free_ai_response(message.text)
        except Exception:
            ans_text = "⚠️ Ой, щось мої нейромережі перевантажені. Спробуй ще раз!"
    await message.answer(ans_text)

async def main():
    dp.include_router(router)
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.chat_action import ChatActionSender

BOT_TOKEN = "8706179100:AAFC3NJTy0xi89EabaPOMlyJwjcxiibyZOE"
ADMIN_IDS = [8362874168]

class AIState(StatesGroup):
    waiting_for_question = State()

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

subjects_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📐 Алгебра", callback_data="sub_algebra"), InlineKeyboardButton(text="📐 Геометрія", callback_data="sub_geometry")],
    [InlineKeyboardButton(text="🧲 Фізика", callback_data="sub_physics"), InlineKeyboardButton(text="🧪 Хімія", callback_data="sub_chemistry")],
    [InlineKeyboardButton(text="🧬 Біологія", callback_data="sub_biology"), InlineKeyboardButton(text="🌍 Географія", callback_data="sub_geography")],
    [InlineKeyboardButton(text="📜 Історія Укр.", callback_data="sub_hist_ua"), InlineKeyboardButton(text="🏰 Всесвітня іст.", callback_data="sub_hist_world")],
    [InlineKeyboardButton(text="🇺🇦 Укр. мова", callback_data="sub_lang_ua"), InlineKeyboardButton(text="📚 Укр. літ.", callback_data="sub_lit_ua")],
    [InlineKeyboardButton(text="🇬🇧 Англійська", callback_data="sub_english"), InlineKeyboardButton(text="🗺️ Зарубіжна літ.", callback_data="sub_lit_world")],
    [InlineKeyboardButton(text="💻 Інформатика", callback_data="sub_inf"), InlineKeyboardButton(text="🛠️ Технології", callback_data="sub_tech")],
    [InlineKeyboardButton(text="🎨 Мистецтво", callback_data="sub_art"), InlineKeyboardButton(text="🌱 ЗБД", callback_data="sub_zbd")]
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
    text = "Обери предмет, щоб подивитися або додати домашнє завдання:"
    await send_human_message(message, text, reply_markup=subjects_menu)

# НОВАЯ ЛОГИКА ДЛЯ КНОПКИ РОЗКЛАД
@router.message(F.text == "🗓️ Розклад")
async def show_schedule(message: Message):
    text = (
        "🗓️ **Розклад уроків (7 клас):**\n\n"
        "Поки що розклад не завантажено адміністратором. "
        "Ти зможеш додати його через адмін-панель трохи пізніше!"
    )
    await send_human_message(message, text)

# НОВАЯ ЛОГИКА ДЛЯ КНОПКИ КНИГИ
@router.message(F.text == "📚 Книги")
async def show_books(message: Message):
    text = (
        "📚 **Електронні підручники для 7 класу:**\n\n"
        "Тут будуть посилання на завантаження твоїх підручників. "
        "Ти зможеш додати потрібних авторів у будь-який момент!"
    )
    await send_human_message(message, text)

# НОВАЯ ЛОГИКА ДЛЯ КНОПКИ ВАЖЛИВЕ
@router.message(F.text == "📌 Важливе")
async def show_important(message: Message):
    text = (
        "📌 **Важливі оголошення:**\n\n"
        "Наразі немає нових оголошень від старости чи вчителів. "
        "Сюди будуть прилітати головні новини класу!"
    )
    await send_human_message(message, text)

@router.message(F.text == "🛠️ Admin Panel")
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    text = "👑 Вітаю в панелі керування! Тут ти зможеш оновлювати розклад та ДЗ."
    await send_human_message(message, text)

@router.message(F.text == "🤖 ШІ Допомога")
async def ai_welcome(message: Message, state: FSMContext):
    await state.set_state(AIState.waiting_for_question)
    text = "🤖 Напиши мені своє питання, і я безкоштовно допоможу розібратися!"
    await send_human_message(message, text)

@router.message(AIState.waiting_for_question)
async def ai_answer(message: Message, state: FSMContext):
    if message.text in ["🗓️ Розклад", "📝 ДЗ", "🤖 ШІ Допомога", "📊 Сер. бал", "📚 Книги", "📌 Важливе", "🎲 Рандом", "⚙️ Налаштування"]:
        await state.clear()
        if message.text == "📝 ДЗ": await show_subjects_for_hw(message)
        elif message.text == "🗓️ Розклад": await show_schedule(message)
        elif message.text == "📚 Книги": await show_books(message)
        elif message.text == "📌 Важливе": await show_important(message)
        return

    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        try:
            import api_helper
            ans_text = await api_helper.get_free_ai_response(message.text)
        except Exception:
            ans_text = "⚠️ Ой, щось мої нейромережі перевантажені. Спробуй ще раз!"
    await message.answer(ans_text)

async def main():
    dp.include_router(router)
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.chat_action import ChatActionSender

BOT_TOKEN = "8706179100:AAFC3NJTy0xi89EabaPOMlyJwjcxiibyZOE"
ADMIN_IDS = [8362874168]

class AIState(StatesGroup):
    waiting_for_question = State()

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

subjects_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📐 Алгебра", callback_data="sub_algebra"), InlineKeyboardButton(text="📐 Геометрія", callback_data="sub_geometry")],
    [InlineKeyboardButton(text="🧲 Фізика", callback_data="sub_physics"), InlineKeyboardButton(text="🧪 Хімія", callback_data="sub_chemistry")],
    [InlineKeyboardButton(text="🧬 Біологія", callback_data="sub_biology"), InlineKeyboardButton(text="🌍 Географія", callback_data="sub_geography")],
    [InlineKeyboardButton(text="📜 Історія Укр.", callback_data="sub_hist_ua"), InlineKeyboardButton(text="🏰 Всесвітня іст.", callback_data="sub_hist_world")],
    [InlineKeyboardButton(text="🇺🇦 Укр. мова", callback_data="sub_lang_ua"), InlineKeyboardButton(text="📚 Укр. літ.", callback_data="sub_lit_ua")],
    [InlineKeyboardButton(text="🇬🇧 Англійська", callback_data="sub_english"), InlineKeyboardButton(text="🗺️ Зарубіжна літ.", callback_data="sub_lit_world")],
    [InlineKeyboardButton(text="💻 Інформатика", callback_data="sub_inf"), InlineKeyboardButton(text="🛠️ Технології", callback_data="sub_tech")],
    [InlineKeyboardButton(text="🎨 Мистецтво", callback_data="sub_art"), InlineKeyboardButton(text="🌱 ЗБД", callback_data="sub_zbd")]
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
    text = "Обери предмет, щоб подивитися або додати домашнє завдання:"
    await send_human_message(message, text, reply_markup=subjects_menu)

@router.message(F.text == "🛠️ Admin Panel")
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    text = "👑 Вітаю в панелі керування! Тут ти зможеш оновлювати розклад та ДЗ."
    await send_human_message(message, text)

@router.message(F.text == "🤖 ШІ Допомога")
async def ai_welcome(message: Message, state: FSMContext):
    await state.set_state(AIState.waiting_for_question)
    text = "🤖 Напиши мені своє питання, і я безкоштовно допоможу розібратися!"
    await send_human_message(message, text)

@router.message(AIState.waiting_for_question)
async def ai_answer(message: Message, state: FSMContext):
    if message.text in ["🗓️ Розклад", "📝 ДЗ", "🤖 ШІ Допомога", "📊 Сер. бал", "📚 Книги", "📌 Важливе", "🎲 Рандом", "⚙️ Налаштування"]:
        await state.clear()
        if message.text == "📝 ДЗ": await show_subjects_for_hw(message)
        return

    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        try:
            import api_helper
            ans_text = await api_helper.get_free_ai_response(message.text)
        except Exception:
            ans_text = "⚠️ Ой, щось мої нейромережі перевантажені. Спробуй ще раз!"
    await message.answer(ans_text)

async def main():
    dp.include_router(router)
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.chat_action import ChatActionSender

BOT_TOKEN = "8706179100:AAFC3NJTy0xi89EabaPOMlyJwjcxiibyZOE"
ADMIN_IDS = [8362874168]

class AIState(StatesGroup):
    waiting_for_question = State()

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

subjects_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📐 Алгебра", callback_data="sub_algebra"), InlineKeyboardButton(text="📐 Геометрія", callback_data="sub_geometry")],
    [InlineKeyboardButton(text="🧲 Фізика", callback_data="sub_physics"), InlineKeyboardButton(text="🧪 Хімія", callback_data="sub_chemistry")],
    [InlineKeyboardButton(text="🧬 Біологія", callback_data="sub_biology"), InlineKeyboardButton(text="🌍 Географія", callback_data="sub_geography")],
    [InlineKeyboardButton(text="📜 Історія України", callback_data="sub_hist_ua"), InlineKeyboardButton(text="🏰 Всесвітня історія", callback_data="sub_hist_world")],
    [InlineKeyboardButton(text="🇺🇦 Укр. мова", callback_data="sub_lang_ua"), InlineKeyboardButton(text="📚 Укр. літ", callback_data="sub_lit_ua")],
    [InlineKeyboardButton(text="🇬🇧 Англійська", callback_data="sub_english"), InlineKeyboardButton(text="🗺️ Зарубіжна літ", callback_data="sub_lit_world")]
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
    text = "Обери предмет, щоб подивитися або додати домашнє завдання:"
    await send_human_message(message, text, reply_markup=subjects_menu)

@router.message(F.text == "🛠️ Admin Panel")
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS: return
    text = "👑 Вітаю в панелі керування! Тут ти зможеш оновлювати розклад та ДЗ."
    await send_human_message(message, text)

@router.message(F.text == "🤖 ШІ Допомога")
async def ai_welcome(message: Message, state: FSMContext):
    await state.set_state(AIState.waiting_for_question)
    text = "🤖 Напиши мені своє питання, і я безкоштовно допоможу розібратися!"
    await send_human_message(message, text)

@router.message(AIState.waiting_for_question)
async def ai_answer(message: Message, state: FSMContext):
    if message.text in ["🗓️ Розклад", "📝 ДЗ", "🤖 ШІ Допомога", "📊 Сер. бал", "📚 Книги", "📌 Важливе", "🎲 Рандом", "⚙️ Налаштування"]:
        await state.clear()
        if message.text == "📝 ДЗ": await show_subjects_for_hw(message)
        return

    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        try:
            import api_helper
            ans_text = await api_helper.get_free_ai_response(message.text)
        except Exception:
            ans_text = "⚠️ Ой, щось мої нейромережі перевантажені. Спробуй ще раз!"
    await message.answer(ans_text)

async def main():
    dp.include_router(router)
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
