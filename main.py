import asyncio
import logging
import random
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.chat_action import ChatActionSender
from aiohttp import web

BOT_TOKEN = "8706179100:AAFC3NJTy0xi89EabaPOMlyJwjcxiibyZOE"
ADMIN_IDS = [8791830931]  # ФИКС: Твой новый ID прописан!
STAROSTA_CHAT_ID = 8791830931  # ФИКС: Отчеты прилетят тебе!

HOMEWORK_DATA = {}
IMPORTANT_ANNOUNCEMENT = "📌 **Важливі оголошення:**\n\nНаразі немає нових оголошень від адміністрації."
BOOKS_DATA = "📚 **Електронні підручники для 7 класу:**\n\nТут будуть посилання на завантаження твоїх підручників."
ABSENT_TODAY_LIST = []
RANDOM_NAMES = ["Андрій", "Марічка", "Олександр", "Дмитро", "Мирослава", "Максим", "Ангеліна", "Роман", "Ілля", "Вероніка", "Емілія", "Софія", "Данило", "Ковальчук", "Колодинський", "Владислав", "Назарій", "Едуард", "Матвій", "Михайло", "Єва", "Альберт", "Нікіта", "Маргарита", "Ілона", "Макар", "Станіслав"]
RANDOM_MODE = "dice"

LESSON_BELLS = {
    1: ("08:30", "09:15"),
    2: ("09:35", "10:20"),
    3: ("10:40", "11:25"),
    4: ("11:45", "12:30"),
    5: ("12:50", "13:35"),
    6: ("13:45", "14:30"),
    7: ("14:40", "15:25")
}

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
PREDICTIONS = ["🌟 Сьогодні твій щасливий день! Все буде спокійно.", "⚡ Обережно! На фізрі доведеться побігати.", "🧠 Ідеальний час, щоб підняти бал з алгебри!", "🍕 У їдальні сьогодні смачні булочки!"]

class BotStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_grades = State()
    waiting_for_hw_text = State()
    waiting_for_important_text = State()
    waiting_for_books_text = State()
    waiting_for_schedule_text = State()
    waiting_for_absence_info = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

async def handle_render_hc(request):
    return web.Response(text="OK")

def get_main_menu(user_id: int) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🗓️ Розклад"), KeyboardButton(text="📝 ДЗ")],
        [KeyboardButton(text="🤖 ШІ Допомога"), KeyboardButton(text="📊 Сер. бал")],
        [KeyboardButton(text="📚 Книги"), KeyboardButton(text="📌 Важливе")],
        [KeyboardButton(text="🎲 Рандом"), KeyboardButton(text="🔔 Дзвінки")],
        [KeyboardButton(text="⚙️ Налаштування")]
    ]
    if user_id in ADMIN_IDS:
        buttons.append([KeyboardButton(text="🛠️ Admin Panel")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_ai_mode_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🛑 Вийти з режиму ШІ")]], resize_keyboard=True)

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
    [InlineKeyboardButton(text="🏆 Досягнення", callback_data="profile_achievements"), InlineKeyboardButton(text="🔮 Передбачення", callback_data="profile_prediction")],
    [InlineKeyboardButton(text="📜 Лог оновлень", callback_data="profile_changelog")]
])

async def send_human_message(message: Message, text: str, reply_markup=None):
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        delay = max(1.0, min((len(text) * 0.03) + random.uniform(0.4, 1.0), 3.0))
        await asyncio.sleep(delay)
    return await message.answer(text, reply_markup=reply_markup)

# ==========================================
# 📖 ОСНОВНІ КОМАНДИ ТА ХЕНДЛЕРИ КОРИСТУВАЧІВ
# ==========================================

@router.message(Command("start"))
async def cmd_start(message: Message):
    await send_human_message(message, "Привіт! Я твій помічник для 7 класу. Чим займемося сьогодні?", reply_markup=get_main_menu(message.from_user.id))

@router.message(F.text == "📝 ДЗ")
async def show_subjects_for_hw(message: Message):
    await send_human_message(message, "Обери предмет, щоб подивитися домашнє завдання:", reply_markup=get_subjects_menu("view"))

@router.callback_query(F.data.startswith("view_"))
async def process_view_hw(callback: CallbackQuery):
    subject = callback.data.split("_", maxsplit=1)[1]
    sub_name = SUBJECT_NAMES.get(subject, "Предмет")
    hw_text = HOMEWORK_DATA.get(subject, "Завдання поки що не додано.")
    await callback.message.edit_text(text=f"📝 **ДЗ з предмету {sub_name}:**\n\n{hw_text}", reply_markup=get_subjects_menu("view"))
    await callback.answer()

@router.message(F.text == "🗓️ Розклад")
async def show_schedule_days(message: Message):
    await send_human_message(message, "Обери день тижня:", reply_markup=get_days_menu("sch"))

@router.callback_query(F.data.startswith("sch_"))
async def process_schedule_callback(callback: CallbackQuery):
    day = callback.data.split("_", maxsplit=1)[1]
    await callback.message.edit_text(text=SCHEDULE_DATA.get(day, "⚠️ Нічого немає."), reply_markup=get_days_menu("sch"))
    await callback.answer()

@router.message(F.text == "🔔 Дзвінки")
async def show_bells_and_timer(message: Message):
    now = datetime.now()
    current_str = now.strftime("%H:%M")
    current_time = datetime.strptime(current_str, "%H:%M")
    
    status_text = "🏫 **Зараз уроків немає (навчальний день закінчився або ще не почався).**"
    bells_list = "🔔 **Розклад дзвінків:**\n"
    for num, (start, end) in LESSON_BELLS.items():
        bells_list += f"{num}. {start} - {end}\n"
    
    in_school_hours = False
    for num, (start, end) in LESSON_BELLS.items():
        start_t = datetime.strptime(start, "%H:%M")
        end_t = datetime.strptime(end, "%H:%M")
        
        if start_t <= current_time <= end_t:
            time_left = int((end_t - current_time).total_seconds() / 60)
            status_text = f"📚 **Зараз іде {num}-й урок!**\n⏳ До перерви залишилось: **{time_left} хв.**"
            in_school_hours = True
            break
            
    if not in_school_hours:
        for num in range(1, len(LESSON_BELLS)):
            end_current = datetime.strptime(LESSON_BELLS[num][1], "%H:%M")
            start_next = datetime.strptime(LESSON_BELLS[num+1][0], "%H:%M")
            
            if end_current <= current_time <= start_next:
                time_left = int((start_next - current_time).total_seconds() / 60)
                status_text = f"🥪 **Зараз перерва після {num}-го уроку!**\n🏃‍♂️ До початку {num+1}-го уроку залишилось: **{time_left} хв.**"
                break

    full_response = f"{bells_list}\n📊 **Статус зараз:**\n{status_text}"
    await send_human_message(message, full_response)

@router.message(F.text == "📚 Книги")
async def show_books(message: Message):
    await send_human_message(message, BOOKS_DATA)

@router.message(F.text == "📌 Важливе")
async def show_important(message: Message):
    await send_human_message(message, IMPORTANT_ANNOUNCEMENT)

@router.message(F.text == "🎲 Рандом")
async def show_random(message: Message):
    global RANDOM_MODE
    if RANDOM_MODE == "dice":
        await message.answer_dice()
    else:
        name = random.choice(RANDOM_NAMES)
        await send_human_message(message, f"🎲 Випадковий учень до дошки: **{name}**")

@router.message(F.text == "📊 Сер. бал")
async def ask_for_grades(message: Message, state: FSMContext):
    await send_human_message(message, "Введи свої оцінки через пробіл або кому (наприклад: 8, 11, 4, 2):")
    await state.set_state(BotStates.waiting_for_grades)

@router.message(BotStates.waiting_for_grades)
async def process_grades(message: Message, state: FSMContext):
    try:
        text = message.text.replace(",", " ")
        grades = [int(g) for g in text.split() if g.isdigit()]
        if not grades:
            raise ValueError
        avg = sum(grades) / len(grades)
        await send_human_message(message, f"📊 Твій середній бал: {avg:.2f}")
    except ValueError:
        await send_human_message(message, "❌ Будь ласка, введи коректні оцінки (числа від 1 до 12).")
    await state.clear()

@router.message(F.text == "🤖 ШІ Допомога")
async def ai_help(message: Message, state: FSMContext):
    await send_human_message(
        message, 
        "🤖 **Ви увійшли в regime інтелектуального помічника!**\n\n"
        "Тепер ви можете писати мені будь-які питання один за одним БЕЗ повторного натискання кнопок.\n"
        "Щоб повернутися до звичайного меню, натисніть кнопку нижче 👇",
        reply_markup=get_ai_mode_menu()
    )
    await state.set_state(BotStates.waiting_for_question)

@router.message(BotStates.waiting_for_question, F.text == "🛑 Вийти з режиму ШІ")
async def exit_ai_mode(message: Message, state: FSMContext):
    await state.clear()
    await send_human_message(message, "🚪 Ви вийшли з режиму ШІ. Повертаюсь до головного меню:", reply_markup=get_main_menu(message.from_user.id))

@router.message(BotStates.waiting_for_question)
async def process_ai_question(message: Message, state: FSMContext):
    if message.text.startswith("/"):
        return
    await send_human_message(
        message, 
        f"🤖 **Відповідь ШІ на питання:** «_{message.text}_»\n\n"
        f"Порада: Для детального розв'язку переглянь параграф у підручнику. Я готовий до наступного питання!",
        reply_markup=get_ai_mode_menu()
    )

@router.message(F.text == "⚙️ Налаштування")
async def show_settings(message: Message):
    await send_human_message(message, "⚙️ Налаштування та інтерактив:", reply_markup=settings_interactive_menu)

@router.callback_query(F.data == "profile_prediction")
async def process_prediction(callback: CallbackQuery):
    pred = random.choice(PREDICTIONS)
    await callback.message.answer(f"🔮 **Твоє передбачення:**\n\n{pred}")
    await callback.answer()

@router.callback_query(F.data == "profile_achievements")
async def process_achievements(callback: CallbackQuery):
    await callback.message.answer("🏆 **Твої досягнення:**\n\n🥇 Перший запуск бота\n🥈 Активний учень 7 класу")
    await callback.answer()

@router.callback_query(F.data == "profile_changelog")
async def process_changelog(callback: CallbackQuery):
    await callback.message.answer("📜 **Лог оновлень (v2.2):**\n\n• Додано Більше імен до режиму Рандом")
    await callback.answer()

# ==========================================
# 🛠️ АДМІНІСТРАТИВНА ПАНЕЛЬ ТА КЕРУВАННЯ
# ==========================================

@router.message(F.text == "🛠️ Admin Panel")
async def admin_panel(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await send_human_message(message, "🛠️ Вітаємо в панелі адміністратора. Оберіть дію:", reply_markup=admin_actions_menu)
    else:
        await send_human_message(message, "🛑 У вас немає доступу до цієї команди.")

@router.callback_query(F.data == "admin_add_hw")
async def admin_choose_subject_hw(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer("Оберіть предмет, для якого хочете змінити ДЗ:", reply_markup=get_subjects_menu("edit_hw"))
    await callback.answer()

@router.callback_query(F.data.startswith("edit_hw_"))
async def admin_input_hw_text(callback: CallbackQuery, state: FSMContext):
    subject = callback.data.split("_", maxsplit=2)[2]
    await state.update_data(chosen_subject=subject)
    await callback.message.answer(f"Введіть новий текст ДЗ для предмета {SUBJECT_NAMES.get(subject, 'Предмет')}:")
    await state.set_state(BotStates.waiting_for_hw_text)
    await callback.answer()

@router.message(BotStates.waiting_for_hw_text)
async def admin_save_hw_text(message: Message, state: FSMContext):
    global HOMEWORK_DATA
    data = await state.get_data()
    subject = data.get("chosen_subject")
    HOMEWORK_DATA[subject] = message.text
    await message.answer(f"✅ ДЗ для {SUBJECT_NAMES.get(subject, 'Предмет')} успішно оновлено!")
    await state.clear()

@router.callback_query(F.data == "admin_edit_sch")
async def admin_choose_day_sch(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer("Оберіть день для зміни розкладу:", reply_markup=get_days_menu("edit_sch"))
    await callback.answer()

@router.callback_query(F.data.startswith("edit_sch_"))
async def admin_input_sch_text(callback: CallbackQuery, state: FSMContext):
    day = callback.data.split("_", maxsplit=2)[2]
    await state.update_data(chosen_day=day)
    await callback.message.answer(f"Введіть новий розклад для дня ({DAY_NAMES.get(day, 'День')}):")
    await state.set_state(BotStates.waiting_for_schedule_text)
    await callback.answer()

@router.message(BotStates.waiting_for_schedule_text)
async def admin_save_sch_text(message: Message, state: FSMContext):
    global SCHEDULE_DATA
    data = await state.get_data()
    day = data.get("chosen_day")
    SCHEDULE_DATA[day] = message.text
    await message.answer(f"✅ Розклад на {DAY_NAMES.get(day, 'День')} успішно змінено!")
    await state.clear()

@router.callback_query(F.data == "admin_add_important")
async def admin_input_important(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer("Введіть текст нового важливого оголошення:")
    await state.set_state(BotStates.waiting_for_important_text)
    await callback.answer()

@router.message(BotStates.waiting_for_important_text)
async def admin_save_important(message: Message, state: FSMContext):
    global IMPORTANT_ANNOUNCEMENT
    IMPORTANT_ANNOUNCEMENT = message.text
    await message.answer("✅ Важливе оголошення оновлено!")
    await state.clear()

@router.callback_query(F.data == "admin_edit_books")
async def admin_input_books(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer("Введіть новий список книг / посилань:")
    await state.set_state(BotStates.waiting_for_books_text)
    await callback.answer()

@router.message(BotStates.waiting_for_books_text)
async def admin_save_books(message: Message, state: FSMContext):
    global BOOKS_DATA
    BOOKS_DATA = message.text
    await message.answer("✅ Список книг успішно оновлено!")
    await state.clear()

@router.callback_query(F.data == "admin_config_random")
async def admin_config_random_mode(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Смайл кубика (Dice)", callback_data="set_rand_dice")],
        [InlineKeyboardButton(text="👥 Випадкове ім'я учня", callback_data="set_rand_name")]
    ])
    await callback.message.answer("Оберіть режим роботи кнопки Рандом:", reply_markup=menu)
    await callback.answer()

@router.callback_query(F.data.startswith("set_rand_"))
async def admin_set_random_mode(callback: CallbackQuery):
    global RANDOM_MODE
    mode = callback.data.split("_", maxsplit=2)[2]
    RANDOM_MODE = mode
    mode_text = "Кубик (Dice)" if mode == "dice" else "Вибір учня зі списку"
    await callback.message.answer(f"✅ Режим рандому змінено на: **{mode_text}**")
    await callback.answer()

@router.callback_query(F.data == "admin_mark_attendance")
async def admin_start_attendance(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    await callback.message.answer("📝 Введіть прізвища або імена учнів, які сьогодні відсутні (через кому або з нового рядка):")
    await state.set_state(BotStates.waiting_for_absence_info)
    await callback.answer()

@router.message(BotStates.waiting_for_absence_info)
async def admin_save_attendance(message: Message, state: FSMContext):
    global ABSENT_TODAY_LIST
    text = message.text.replace("\n", ",")
    ABSENT_TODAY_LIST = [name.strip() for name in text.split(",") if name.strip()]
    if ABSENT_TODAY_LIST:
        formatted = "\n".join([f"• {n}" for n in ABSENT_TODAY_LIST])
        await message.answer(f"✅ Список збережено (Всього: {len(ABSENT_TODAY_LIST)}):\n{formatted}")
    else:
        await message.answer("⚠️ Список порожній.")
    await state.clear()

@router.callback_query(F.data == "admin_send_report")
async def admin_send_report_to_starosta(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    if not ABSENT_TODAY_LIST:
        await callback.message.answer("⚠️ Список відсутніх порожній!")
        await callback.answer()
        return
    formatted = "\n".join([f"• {name}" for name in ABSENT_TODAY_LIST])
    report_text = f"📢 **Щоденний звіт про відсутніх**\n\nУчнів, яких немає:\n{formatted}\n\nВсього: {len(ABSENT_TODAY_LIST)}"
    try:
        await bot.send_message(chat_id=STAROSTA_CHAT_ID, text=report_text)
        await callback.message.answer("🚀 Звіт надіслано старості!")
    except Exception as e:
        await callback.message.answer(f"❌ Помилка відправки! Перевірте ID старости.")
    await callback.answer()

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

    print(" Bot polling started...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
