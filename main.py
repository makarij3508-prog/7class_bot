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
