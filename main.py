import asyncio
import logging
import random
import os
import aiohttp
import json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.chat_action import ChatActionSender
from aiohttp import web

# ==========================================
# 🚨 КРИТИЧНА КОНФІГУРАЦІЯ СИСТЕМИ v2.7 (7-В)
# ==========================================

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

# 🗄️ ОЛІМПІАДНА БАЗА ДАНИХ ID УЧНІВ (ЗВ'ЯЗОК ЮЗЕРНЕЙМ -> TELEGRAM ID)
USER_USERNAMES = {
    "@macar_dev_temp": 8791830931,
    "@ezhik_lite": 441394079,   # ID Артема (ArtemYch)
    "@ilona_x": 1122334455,
    "@marri_chk": 9988776655
}

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
    "Олександр", "Андрій", "Данило", "Колодинський Богдан", "Ковалевчук Богдан", 
    "Мирослава", "Матвій", "Софія", "Михайло", "Макар", "Ілона", "Марічка", 
    "Маргарита", "Ангеліна", "Нікіта", "Альберт", "Єва", "Роман", "Владислав", 
    "Назарій", "Едуард", "Станіслав", "Артем", "Емілія", "Вероніка", "Ілля", "Дмитро", "Макс"
]

USER_ACHIEVEMENTS = {name: ["🥈 \u0410\u043a\u0442\u0438\u0432\u043d\u0438\u0439 \u0443\u0447\u0435\u043d\u044c 7-\u0412 \u043a\u043b\u0430\u0441\u0443"] for name in RANDOM_NAMES}

USER_USERNAMES_TEXT = {
    "@ilona_x": "Ілона", "@selarkin": "Роман", "@play.funtime.su": "Едуард",
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
    "lang_ua": "🇺🇦 Укр. мова", "lit_ua": "📚 Укр. літ.", "english": "🇬🇧 Англійська", "lit_world": "🗺️ Зар. літ.",
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

async def send_human_message(message: Message, text: str, reply_markup=None):
    return await message.answer(text, reply_markup=reply_markup)

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
        keyboard.append([InlineKeyboardButton(text="🧪 Тест-Режим: ОН/ОФФ", callback_data="admin_toggle_test")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

settings_interactive_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏆 Досягнення", callback_data="profile_achievements"), InlineKeyboardButton(text="🔮 Передбачення", callback_data="profile_prediction")],
    [InlineKeyboardButton(text="🎁 Щоденний Подарунок", callback_data="economy_get_gift"), InlineKeyboardButton(text="🛒 Магазин Сімок", callback_data="economy_open_shop")],
    [InlineKeyboardButton(text="👑 Топ Шейхів класу", callback_data="economy_top_sheikhs")],
    [InlineKeyboardButton(text="🔔 Дзвінки", callback_data="profile_bells"), InlineKeyboardButton(text="📜 Лог оновлень", callback_data="profile_changelog")]
])


@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    if user_id not in USER_BALANCES:
        USER_BALANCES[user_id] = 10
    if username:
        user_key = f"@{username.lower()}"
        USER_USERNAMES[user_key] = user_id
        if user_key in ADMIN_L4_USERNAMES and user_id not in ADMIN_L4_IDS: ADMIN_L4_IDS.append(user_id)
        if user_key == TEACHER_USERNAME.lower():
            global TEACHER_CHAT_ID
            TEACHER_CHAT_ID = user_id
    await send_human_message(message, "Привіт! Я твій оновлений помічник для 7-В класу релізу v2.7! Чим займемося?", reply_markup=get_main_menu(user_id))

@router.message(F.text == "📝 ДЗ")
async def show_subjects_for_hw(message: Message):
    if IS_TESTING_MODE and message.from_user.id not in SUPER_ADMIN_IDS and message.from_user.id not in ADMIN_L4_IDS and message.from_user.id not in TESTER_IDS: return
    await send_human_message(message, "Обери предмет, щоб подивитися домашнє завдання:", reply_markup=get_subjects_menu("view"))

@router.callback_query(F.data.startswith("view_"))
async def process_view_hw(callback: CallbackQuery):
    await callback.answer()
    subject = callback.data.replace("view_", "")
    await callback.message.edit_text(text=f"📝 **ДЗ з предмету {SUBJECT_NAMES.get(subject, 'Предмет')}:**\n\n{HOMEWORK_DATA.get(subject, 'Завдання поки що не додано.')}", reply_markup=get_subjects_menu("view"))

@router.message(F.text == "🗓️ Розклад")
async def show_schedule_days(message: Message):
    if IS_TESTING_MODE and message.from_user.id not in SUPER_ADMIN_IDS and message.from_user.id not in ADMIN_L4_IDS and message.from_user.id not in TESTER_IDS: return
    await send_human_message(message, "Обери день тижня:", reply_markup=get_days_menu("sch"))

@router.callback_query(F.data.startswith("sch_"))
async def process_schedule_callback(callback: CallbackQuery):
    await callback.answer()
    day = callback.data.replace("sch_", "")
    await callback.message.edit_text(text=SCHEDULE_DATA.get(day, "⚠️ Нічого немає."), reply_markup=get_days_menu("sch"))

@router.message(F.text == "📚 Книги")
async def handle_show_books(message: Message):
    if IS_TESTING_MODE and message.from_user.id not in SUPER_ADMIN_IDS and message.from_user.id not in ADMIN_L4_IDS and message.from_user.id not in TESTER_IDS: return
    await send_human_message(message, BOOKS_DATA)

@router.message(F.text == "📌 Важливе")
async def handle_show_important(message: Message):
    if IS_TESTING_MODE and message.from_user.id not in SUPER_ADMIN_IDS and message.from_user.id not in ADMIN_L4_IDS and message.from_user.id not in TESTER_IDS: return
    await send_human_message(message, IMPORTANT_ANNOUNCEMENT)

@router.message(F.text == "🎲 Рандом")
async def handle_show_random(message: Message):
    if IS_TESTING_MODE and message.from_user.id not in SUPER_ADMIN_IDS and message.from_user.id not in ADMIN_L4_IDS and message.from_user.id not in TESTER_IDS: return
    global RANDOM_MODE
    if RANDOM_MODE == "dice": await message.answer_dice()
    else: await send_human_message(message, f"🎲 Випадковий учень до дошки: **{random.choice(RANDOM_NAMES)}**")

@router.message(F.text == "🤖 ШІ Допомога")
async def handle_ai_help(message: Message, state: FSMContext):
    if IS_TESTING_MODE and message.from_user.id not in SUPER_ADMIN_IDS and message.from_user.id not in ADMIN_L4_IDS and message.from_user.id not in TESTER_IDS: return
    await send_human_message(message, "🤖 **Ви увійшли в безсмертний режим ШІ!**\n\nПиши свої питання підряд.", reply_markup=get_ai_mode_menu())
    await state.set_state(BotStates.waiting_for_question)

@router.message(BotStates.waiting_for_question, F.text == "🛑 Вийти з режиму ШІ")
async def exit_ai_mode(message: Message, state: FSMContext):
    await state.clear()
    await send_human_message(message, "🚪 Режим ШІ закритий:", reply_markup=get_main_menu(message.from_user.id))

@router.message(BotStates.waiting_for_question)
async def process_ai_question(message: Message, state: FSMContext):
    if message.text.startswith("/"): return
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        encoded_prompt = aiohttp.helpers.urlencode({"prompt": f"Ти помічник для 7-В класу. Тобі пише учень. Відповідай чітко, коротко, виключно українською мовою. Питання: {message.text}"})
        url = f"https://pollinations.ai?{encoded_prompt}&model=openai"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15) as resp:
                    ai_response = await resp.text() if resp.status == 200 else "⚠️ Сервер ШІ трохи задумався, надішли ще раз!"
        except Exception: ai_response = "❌ Наразі ШІ відпочиває. Спробуйте пізніше!"
    await message.answer(f"🤖 **Відповідь ШІ:**\n\n{ai_response.strip()}", reply_markup=get_ai_mode_menu())

@router.message(F.text == "⚙️ Налаштування")
async def show_settings(message: Message):
    await send_human_message(message, "⚙️ Налаштування та інтерактив:", reply_markup=settings_interactive_menu)

@router.callback_query(F.data == "profile_prediction")
async def process_prediction(callback: CallbackQuery):
    await callback.message.answer(f"🔮 **Твоє передбачення:**\n\n{random.choice(PREDICTIONS)}")
    await callback.answer()

@router.callback_query(F.data == "profile_achievements")
async def process_achievements(callback: CallbackQuery):
    username = callback.from_user.username
    user_key = f"@{username.lower()}" if username else ""
    name = "Макар" if callback.from_user.id == 8791830931 else USER_USERNAMES_TEXT.get(user_key, callback.from_user.first_name)
    await callback.message.answer(f"🏆 **Досягнення учня ({name}):**\n\n" + "\n".join(USER_ACHIEVEMENTS.get(name, ["🥈 Активний учень 7-В класу"])))
    await callback.answer()

@router.callback_query(F.data == "profile_changelog")
async def process_changelog(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        text="📜 **Офіційні оновлення системи (Версія v2.7 Wall Street & CIA):**\n\n• 💳 **Банківська система переказів /pay:** Запущено повноцінні грошові перекази між учнями класу з текстовими чеками («на булочку» 🍔, «для любимої» 💌).\n• 💸 **Казначейство та Податкова Система:** Введено автоматичний налог 30% з усіх покупок у Магазині луту. Податок моментально нараховується на баланси Макара та Головних Adminів класу 🪙.\n• 🕵️‍♂️ **ЦРУ-Премодерація Досягнень:** Медалі тепер можна купувати самостійно за 250 Сімок! Текст спочатку летить Макару на узгодження.\n• 🤫 **Особистий Секретний Злив Макара:** Роль Шпигуна повністю автоматизована і раз на добу видається випадковому ученю з бази, а Макар отримує прихований ЦРУ-чек звіт.\n• 👑 **Фікс Адмінок та Уровнів на ходу:** Повністю виправлено логіку синхронізації Telegram ID.\n• 🧹 **Економічна зачистка:** З метою стабілізації валюти 7-В класу, з коду повністю видалені інструменти зливу балансу (Казино та Біржа акцій).", reply_markup=settings_interactive_menu
    )

@router.callback_query(F.data == "economy_get_gift")
async def process_get_daily_gift(callback: CallbackQuery):
    user_id = callback.from_user.id
    now = datetime.now().timestamp()
    if user_id in USER_LAST_CASE and now - USER_LAST_CASE[user_id] < 86400:
        await callback.message.answer(f"🎁 **Опа, зачекай!** Куш доступний через **{int((86400 - (now - USER_LAST_CASE[user_id])) / 3600)} год.**")
        await callback.answer(); return
    gift_coins = random.randint(2, 20)
    USER_BALANCES[user_id] = USER_BALANCES.get(user_id, 0) + gift_coins
    USER_LAST_CASE[user_id] = now
    await callback.message.answer(f"🎁 **Щоденний Подарунок активовано!** Випало: **+{gift_coins} Сімок** 🪙!\n💰 Баланс: **{USER_BALANCES[user_id]} Сімок**.")
    await callback.answer()

@router.callback_query(F.data == "economy_open_shop")
async def process_open_shop(callback: CallbackQuery):
    await callback.message.edit_text(text=f"🛒 **Магазин луту 7-В класу**\n\n💰 Твій баланс: **{USER_BALANCES.get(callback.from_user.id, 0)} Сімок** 🪙\n📊 _З кожної покупки стягується подарунок 30% на користь Макара та Адмінів!_", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🃏 Шпаргалка (50 Сімок)", callback_data="buy_shpora")], 
        [InlineKeyboardButton(text="🛡️ Anti-Мут (100 Сімок)", callback_data="buy_antimut")],
        [InlineKeyboardButton(text="🏷️ Власний Тег у чаті (150 Сімок)", callback_data="buy_customtag")], 
        [InlineKeyboardButton(text="🕵️‍♂️ Найняти Детектива (200 Сімок)", callback_data="buy_detective")],
        [InlineKeyboardButton(text="🏆 Купити Досягнення (250 Сімок)", callback_data="buy_achievement_pack")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="economy_back_to_settings")]
    ]))
    await callback.answer()

@router.callback_query(F.data.startswith("buy_"))
async def process_buy_item(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    item = callback.data.replace("buy_", "")
       prices = {"shpora": 50, "antimut": 100, "customtag": 150, "detective": 200, "achievement_pack": 250}
    price = prices.get(item, 999)
    if USER_BALANCES.get(user_id, 0) < price:
        await callback.message.answer(f"❌ Тобі не вистачає Сімок! Потрібно: {price} 🪙.")
        await callback.answer(); return
    USER_BALANCES[user_id] -= price
    tax_amount = int(price * 0.3)
    USER_BALANCES = USER_BALANCES.get(8791830931, 0) + tax_amount
    for l4_id in ADMIN_L4_IDS:
        if l4_id != 8791830931: USER_BALANCES[l4_id] = USER_BALANCES.get(l4_id, 0) + tax_amount
        
    if item == "shpora":
        if user_id not in USER_ITEMS: USER_ITEMS[user_id] = []
        USER_ITEMS[user_id].append("shpora")
        await callback.message.answer(f"🃏 **Купівля успішна!** Придбано Шпаргалку.\n💸 Макару та Адмінам сплачено податок: **{tax_amount} Сімок**!")
    elif item == "antimut":
        if user_id not in USER_ITEMS: USER_ITEMS[user_id] = []
        USER_ITEMS[user_id].append("antimut")
        await callback.message.answer(f"🛡️ **Купівля успішна!** Придбано Анти-Мут.\n💸 Макару та Адмінам сплачено податок: **{tax_amount} Сімок**!")
    elif item == "customtag":
        await callback.message.answer(f"🏷️ **Купівля успішна!** Сплачено податок {tax_amount} 🪙.\nВведіть текст вашого кастомного тегу (до 15 символів):")
        await state.set_state(BotStates.waiting_for_custom_tag)
    elif item == "detective":
        # 🕵️‍♂️ РОЗРАХУНОК ЦРУ-ПІДКАЗКИ ДЛЯ РОЗКРИТТЯ ТАЄМНОГО ШПИГУНА
        agent_name = "Макар"
        for username, u_name in USER_USERNAMES_TEXT.items():
            if USER_USERNAMES.get(username.lower(), 0) == CURRENT_SECRET_AGENT_ID:
                agent_name = u_name; break
        
        # Генеруємо базу розумних підказок
        first_letter = agent_name if agent_name else "М"
        half_index = len(RANDOM_NAMES) // 2
        is_in_first_half = agent_name in RANDOM_NAMES[:half_index] if agent_name in RANDOM_NAMES else True
        half_text = "у першій половині" if is_in_first_half else "у другій половині"
        
        clues = [
            f"🔍 **Звіт Детектива:** Реальне ім'я сьогоднішнього Шпигуна починається на букву **'{first_letter}'**!",
            f"🔍 **Звіт Детектива:** Довжина імені сьогоднішнього Шпигуна становить **{len(agent_name)} символів(и)**!",
            f"🔍 **Звіт Детектива:** Шпигун ховається {half_text} загального списку класу `RANDOM_NAMES`!"
        ]
        selected_clue = random.choice(clues)
        await callback.message.answer(f"🕵️‍♂️ **Детектива успішно найнято! Сплачено податок {tax_amount} 🪙.**\n\n{selected_clue}\n\n🤫 _Нікому не розповідай цей інсайд, вирахуй Шпигуна дня самостійно!_")
    elif item == "achievement_pack":
        await callback.message.answer("💸 **250 Сімок зарезервовано!**\n\n✍️ Тепер введіть текст досягнення (з емодзі), яке ви хочете собі купити:")
        await state.set_state(BotStates.admin_input_achievement)
        await state.update_data(buyer_user_id=user_id, buyer_tax=tax_amount)
    await callback.answer()

@router.message(BotStates.waiting_for_custom_tag)
async def process_save_custom_tag(message: Message, state: FSMContext):
    if len(message.text.strip()) > 15: await message.answer("❌ Задовгий тег!"); return
    USER_CUSTOM_TAGS[message.from_user.id] = message.text.strip().replace("[", "").replace("]", "")
    await message.answer(f"✅ Встановлено тег: `[{USER_CUSTOM_TAGS[message.from_user.id]}]` 🏷️!")
    await state.clear()

@router.message(F.text == "🔊 Чат класу")
async def enter_chat_room(message: Message, state: FSMContext):
    if message.from_user.id in BANNED_USERS: await message.answer("🛑 Ви забанені!"); return
    name = USER_TELEGRAM_NAMES.get(message.from_user.id, message.from_user.first_name)
    CHAT_REGISTERED_USERS[message.from_user.id] = name
    await state.set_state(BotStates.user_in_chat_window)
    await message.answer(f"💬 **Ласкаво просимо до чату 7-В класу, {name}!**", reply_markup=get_chat_exit_menu())

@router.message(BotStates.user_in_chat_window, F.text == "🚪 Вийти з чату")
async def exit_chat_room(message: Message, state: FSMContext):
    if message.from_user.id in CHAT_REGISTERED_USERS: CHAT_REGISTERED_USERS.pop(message.from_user.id)
    await state.clear()
    await send_human_message(message, "🚪 Ви вийшли з чату.", reply_markup=get_main_menu(message.from_user.id))

@router.message(BotStates.user_in_chat_window)
async def process_live_chat_message(message: Message):
    user_id = message.from_user.id
    if message.text == "🚪 Вийти з чату" or user_id in BANNED_USERS: return
    if user_id in MUTED_USERS and datetime.now().timestamp() < MUTED_USERS[user_id]:
        await message.answer("🤫 **У вас МУТ!**"); return
    sender_name = CHAT_REGISTERED_USERS.get(user_id, "Учень")
    custom_tag = USER_CUSTOM_TAGS.get(user_id, "")
    prefix_text = f"[{custom_tag}] " if custom_tag else ""
    for target_id in list(CHAT_REGISTERED_USERS.keys()):
        if target_id != user_id:
            try: await bot.send_message(chat_id=target_id, text=f"💬 **{prefix_text}{sender_name}:** {message.text}")
            except Exception: pass
    all_admins = set(SUPER_ADMIN_IDS + ADMIN_L4_IDS + MODERATOR_IDS + HW_ASSISTANT_IDS)
    punish_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🤫 Мут 15 хв", callback_data=f"mute_15_{user_id}_{sender_name}"), InlineKeyboardButton(text="🛑 БАН", callback_data=f"ban_{user_id}_{sender_name}")]])
    for admin_id in all_admins:
        try: await bot.send_message(chat_id=admin_id, text=f"👁️ **[ЧАТЛОГ] {prefix_text}{sender_name}:** {message.text}", reply_markup=punish_keyboard)
        except Exception: pass

@router.message(F.text == "🤫 Секретний Злив")
async def secret_leak_start(message: Message, state: FSMContext):
    global CURRENT_SECRET_AGENT_ID, AGENT_HAS_SENT_SECRET
    if message.from_user.id != CURRENT_SECRET_AGENT_ID or AGENT_HAS_SENT_SECRET: return
    await message.answer("🤫 **Режим Таємного Шпигуна активовано!** Введи ОДНЕ анонімне повідомлення:")
    await state.set_state(BotStates.waiting_for_secret_text)

@router.message(BotStates.waiting_for_secret_text)
async def secret_leak_process(message: Message, state: FSMContext):
    global CURRENT_SECRET_AGENT_ID, AGENT_HAS_SENT_SECRET
    if message.from_user.id != CURRENT_SECRET_AGENT_ID or AGENT_HAS_SENT_SECRET: return
    AGENT_HAS_SENT_SECRET = True
    for target_id in list(CHAT_REGISTERED_USERS.keys()):
        try: await bot.send_message(chat_id=target_id, text=f"🎭 **🎭 [ТАЄМНИЙ ШПИГУН 7-В]:** {message.text}")
        except Exception: pass
    try: await bot.send_message(chat_id=8791830931, text=f"👁️ **[ЦРУ ШПИГУН] Злив від {message.from_user.first_name} (ID: `{message.from_user.id}`):** {message.text}")
    except Exception: pass
    await message.answer("🚀 **Твій анонімний інсайд розісланий!**", reply_markup=get_main_menu(message.from_user.id))
    await state.clear()

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
    if callback.from_user.id != 8791830931 and callback.from_user.id not in ADMIN_L4_IDS: return
    await callback.answer()
    await callback.message.answer("👥 **Оберіть учня для права доступу:**", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=name, callback_data=f"lvluser_{name}")] for name in RANDOM_NAMES]))

@router.callback_query(F.data.startswith("lvluser_"))
async def process_level_user_card(callback: CallbackQuery):
    if callback.from_user.id != 8791830931 and callback.from_user.id not in ADMIN_L4_IDS: return
    await callback.answer()
    name = callback.data.replace("lvluser_", "")
    level_names = {0: "📋 Рівень 0 (Учень)", 1: "📐 Рівень 1 (Помічник)", 2: "👥 Рівень 2 (Староста)", 3: "🛡️ Рівень 3 (Модератор)", 4: "⭐ Рівень 4 (Admin)"}
    await callback.message.edit_text(text=f"🪪 **Картка правами**\n\n👤 **Учень:** {name}\n📊 **Статус:** {level_names.get(get_user_current_level(name))}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔺 Підняти", callback_data=f"lvledit_up_{name}"), InlineKeyboardButton(text="🔻 Понизити", callback_data=f"lvledit_down_{name}")], [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_give_level_menu")]]))

@router.callback_query(F.data.startswith("lvledit_"))
async def process_dynamic_level_change(callback: CallbackQuery):
    if callback.from_user.id != 8791830931 and callback.from_user.id not in ADMIN_L4_IDS: return
    raw_cmd = callback.data.replace("lvledit_", "").split("_")
    if len(raw_cmd) < 2: return
    action, target_name = raw_cmd[0], raw_cmd[1]
    target_username = ""
    for username, u_name in USER_USERNAMES_TEXT.items():
        if u_name == target_name: target_username = username.lower(); break
    if not target_username:
        target_username = f"@{target_name.lower()}_temp"
        USER_USERNAMES_TEXT[target_username] = target_name
    current_lvl = get_user_current_level(target_name)
    if action == "up" and current_lvl < 4: new_lvl = current_lvl + 1
    elif action == "down" and current_lvl > 0: new_lvl = current_lvl - 1
    else: await callback.answer("⚠️ Границя рівня!"); return
    for lst in [ADMIN_L4_USERNAMES, MODERATOR_USERNAMES, STAROSTA_USERNAMES, ASSISTANT_USERNAMES]:
        if target_username in lst: lst.remove(target_username)
    if new_lvl == 4: ADMIN_L4_USERNAMES.append(target_username)
    elif new_lvl == 3: MODERATOR_USERNAMES.append(target_username)
    elif new_lvl == 2: STAROSTA_USERNAMES.append(target_username)
    elif new_lvl == 1: ASSISTANT_USERNAMES.append(target_username)
    target_id = USER_USERNAMES.get(target_username, 0)
    if target_id > 0:
        for lst_id in [ADMIN_L4_IDS, MODERATOR_IDS, STAROSTA_IDS, HW_ASSISTANT_IDS]:
            if target_id in lst_id: lst_id.remove(target_id)
        if new_lvl == 4: ADMIN_L4_IDS.append(target_id)
        elif new_lvl == 3: MODERATOR_IDS.append(target_id)
        elif new_lvl == 2: STAROSTA_IDS.append(target_id)
        elif new_lvl == 1: HW_ASSISTANT_IDS.append(target_id)
    await callback.answer(f"✅ Статус {target_name} змінено!")
    level_names = {0: "📋 Рівень 0 (Учень)", 1: "📐 Рівень 1 (Помічник)", 2: "👥 Рівень 2 (Староста)", 3: "🛡️ Рівень 3 (Модератор)", 4: "⭐ Рівень 4 (Admin)"}
    await callback.message.edit_text(text=f"🪪 **Картка правами**\n\n👤 **Учень:** {target_name}\n📊 **Новий статус:** {level_names.get(new_lvl)}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔺 Підняти", callback_data=f"lvledit_up_{target_name}"), InlineKeyboardButton(text="🔻 Понизити", callback_data=f"lvledit_down_{target_name}")], [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_give_level_menu")]]))

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
    await message.answer(f"✅ ДЗ для {SUBJECT_NAMES.get(subject, 'Предмет')} успішно оновлено!")
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
    await callback.message.edit_text(text=f"🛠️ Тест-Режим змінено: {'🟢 ОН' if IS_TESTING_MODE else '🔴 ОФФ'}", reply_markup=get_admin_menu_keyboard(callback.from_user.id))
    await callback.answer()

@router.callback_query(F.data == "admin_mark_attendance")
async def admin_start_attendance(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != 8791830931 and callback.from_user.id not in ADMIN_L4_IDS and callback.from_user.id not in STAROSTA_IDS: return
    await callback.answer()
    await callback.message.answer("📝 **[ВІДВІДУВАННІСТЬ]** Введіть прізвища або імена учнів, які сьогодні відсутні (через кому):")
    await state.set_state(BotStates.waiting_for_absence_info)

@router.message(BotStates.waiting_for_absence_info)
async def admin_save_attendance(message: Message, state: FSMContext):
    global ABSENT_TODAY_LIST
    if message.from_user.id != 8791830931 and message.from_user.id not in ADMIN_L4_IDS and message.from_user.id not in STAROSTA_IDS: return
    text = message.text.replace("\n", ",")
    ABSENT_TODAY_LIST = [name.strip() for name in text.split(",") if name.strip()]
    await message.answer(f"✅ **Список збережено!** (Всього відсутніх: {len(ABSENT_TODAY_LIST)}):\n\n" + "\n".join([f"• {n}" for n in ABSENT_TODAY_LIST]))
    await state.clear()

@router.callback_query(F.data == "admin_send_report")
async def admin_send_report_to_teacher(callback: CallbackQuery):
    if callback.from_user.id != 8791830931 and callback.from_user.id not in ADMIN_L4_IDS and callback.from_user.id not in STAROSTA_IDS: return
    if not ABSENT_TODAY_LIST: await callback.message.answer("⚠️ Список відсутніх порожній!"); await callback.answer(); return
    report_text = f"📢 **Щоденний звіт про відсутніх учнів 7-В класу**\n\nУчнів, яких сьогодні немає:\n" + "\n".join([f"• {name}" for name in ABSENT_TODAY_LIST])
    try: await bot.send_message(chat_id=TEACHER_CHAT_ID if TEACHER_CHAT_ID else 8791830931, text=report_text); await callback.message.answer("🚀 **Звіт успішно надіслано вчителю!**")
    except Exception: await callback.message.answer("❌ Помилка відправки звіту.")
    await callback.answer()

@router.callback_query(F.data == "admin_manage_ach")
async def admin_start_manage_achievements(callback: CallbackQuery):
    if callback.from_user.id != 8791830931 and callback.from_user.id not in ADMIN_L4_IDS: return
    await callback.answer()
    await callback.message.answer("🏆 **[ДОСЯГНЕННЯ]** Оберіть учня для видачі медалей:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=name, callback_data=f"achuser_{name}")] for name in RANDOM_NAMES]))

@router.callback_query(F.data.startswith("achuser_"))
async def process_admin_ach_user_card(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != 8791830931 and callback.from_user.id not in ADMIN_L4_IDS: return
    await callback.answer()
    name = callback.data.replace("achuser_", "")
    await state.update_data(ach_target_name=name)
    await callback.message.answer(f"🏆 **Керування досягненнями: {name}**\n\nМедалі:\n" + "\n".join(USER_ACHIEVEMENTS.get(name, ["🥈 Активний учень 7-В класу"])), reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати нове досягнення", callback_data="achaction_add")], [InlineKeyboardButton(text="🗑️ Очистити всі", callback_data="achaction_clear")], [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_manage_ach")]
    ]))

@router.callback_query(F.data.startswith("achaction_"))
async def process_admin_ach_action(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != 8791830931 and callback.from_user.id not in ADMIN_L4_IDS: return
    await callback.answer()
    action = callback.data.replace("achaction_", "")
    state_data = await state.get_data()
    name = state_data.get("ach_target_name")
    if action == "clear":
        USER_ACHIEVEMENTS[name] = ["🥈 Активний учень 7-В класу"]
        await callback.message.answer(f"✅ Досягнення учня **{name}** анульовані!")
    elif action == "add":
        await callback.message.answer(f"✍️ Введіть текст нового досягнення для учня **{name}**:")
        await state.set_state(BotStates.admin_input_achievement)

@router.message(BotStates.admin_input_achievement)
async def admin_save_new_achievement(message: Message, state: FSMContext):
    user_id = message.from_user.id
    state_data = await state.get_data()
    buyer_id = state_data.get("buyer_user_id")
    if buyer_id:
        ach_text = message.text
        tax = state_data.get("buyer_tax", 75)
        buyer_name = USER_TELEGRAM_NAMES.get(buyer_id, message.from_user.first_name)
        confirm_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🟢 Схвалити медаль", callback_data=f"buyach_approve_{buyer_id}_{tax}"), InlineKeyboardButton(text="❌ Відхилити (Бек)", callback_data=f"buyach_reject_{buyer_id}_{tax}")]])
        if "pending_achievs" not in globals(): global pending_achievs; pending_achievs = {}
        pending_achievs[buyer_id] = ach_text
        try: await bot.send_message(chat_id=8791830931, text=f"👑 **[ЦРУ МАГАЗИН] Учень {buyer_name} (ID: `{buyer_id}`) купив досягнення!**\n\nТекст медалі:\n«_{ach_text}_»", reply_markup=confirm_markup); await message.answer("✅ **Запит на медаль успішно надіслано Макару!**")
        except Exception: await message.answer("❌ Помилка зв'язку з премодерацією.")
        await state.clear(); return
    if user_id != 8791830931 and user_id not in ADMIN_L4_IDS: return
    name = state_data.get("ach_target_name")
    if name not in USER_ACHIEVEMENTS: USER_ACHIEVEMENTS[name] = []
    USER_ACHIEVEMENTS[name].append(message.text)
    await message.answer(f"✅ Досягнення додано для **{name}**!")
    await state.clear()

@router.callback_query(F.data.startswith("buyach_"))
async def process_macar_shop_moderation(callback: CallbackQuery):
    if callback.from_user.id != 8791830931: return
    await callback.answer()
    raw_cmd = callback.data.replace("buyach_", "").split("_")
    action, buyer_id, tax = raw_cmd, int(raw_cmd), int(raw_cmd)
    ach_text = pending_achievs.get(buyer_id, "🏆 Нове досягнення") if "pending_achievs" in globals() else "🏆 Нове досягнення"
    username_key = ""
    for username, u_name in USER_USERNAMES_TEXT.items():
        if USER_USERNAMES.get(username.lower(), 0) == buyer_id: username_key = u_name; break
    if not username_key: username_key = USER_TELEGRAM_NAMES.get(buyer_id, "Учень")
    if action == "approve":
        if username_key not in USER_ACHIEVEMENTS: USER_ACHIEVEMENTS[username_key] = []
        USER_ACHIEVEMENTS[username_key].append(ach_text)
        USER_BALANCES = USER_BALANCES.get(8791830931, 0) + tax
        for l4_id in ADMIN_L4_IDS:
            if l4_id != 8791830931: USER_BALANCES[l4_id] = USER_BALANCES.get(l4_id, 0) + tax
        try: await bot.send_message(chat_id=buyer_id, text=f"🎉 **Макар схвалив твою покупку!** Медаль «{ach_text}» додана!")
        except Exception: pass
        await callback.message.edit_text(f"🟢 **Успішно схвалено!** Медаль видана {username_key}.\n💸 Нараховано податок: **+{tax} Сімок** 🪙!")
    elif action == "reject":
        USER_BALANCES[buyer_id] = USER_BALANCES.get(buyer_id, 0) + 250
        try: await bot.send_message(chat_id=buyer_id, text="❌ **Макар відхилив запит!** 250 Сімок повернуто на твій баланс.")
        except Exception: pass
        await callback.message.edit_text(f"❌ **Ви відхилили запит.** 250 Сімок повернуто учню, податок скасовано.")

@router.message(F.text.startswith("/pay"))
async def universal_pay_system_command(message: Message):
    args = message.text.split()
    if len(args) < 3: await message.answer("⚠️ **Формат:** `/pay @username_або_ID кількість повідомлення`\nПриклад: `/pay @ilona_x 250 для любимої` 💌"); return
    target_raw = args.strip()
    try: amount = int(args)
    except ValueError: await message.answer("❌ Кількість монет має бути цілим числом!"); return
    if amount <= 0: await message.answer("❌ Сума має бути більшою за 0!"); return
    if message.from_user.id != 8791830931 and USER_BALANCES.get(message.from_user.id, 0) < amount:
        await message.answer(f"❌ **Недостатньо Сімок!** Баланс: **{USER_BALANCES.get(message.from_user.id, 0)}** 🪙."); return
    target_id = int(target_raw) if target_raw.isdigit() else USER_USERNAMES.get(target_raw.lower(), 0)
    if target_id == 0 and not target_raw.isdigit(): await message.answer(f"❌ Користувача {target_raw} не знайдено!"); return
    if target_raw.isdigit():
        target_id = int(target_raw)
        if target_id not in USER_BALANCES: USER_BALANCES[target_id] = 0
    if target_id == message.from_user.id: await message.answer("🧠 Не можна переводити гроші самому собі!"); return
    comment_text = " ".join(args[3:]) if len(args) > 3 else "Без коментаря"
    if message.from_user.id != 8791830931: USER_BALANCES[message.from_user.id] -= amount
    USER_BALANCES[target_id] = USER_BALANCES.get(target_id, 0) + amount
    sender_name = USER_TELEGRAM_NAMES.get(message.from_user.id, message.from_user.first_name)
    await message.answer(f"💸 **Переказ успішний!** Відправлено **{amount} Сімок** для `{target_raw}`.\n💬 Коментар: «_{comment_text}_»")
    try: await bot.send_message(chat_id=target_id, text=f"🎁 **Тобі прилетів грошовий переказ!**\n👤 **Відправник:** {sender_name}\n🪙 **Сума:** +{amount} Сімок\n💌 **Повідомлення:** «_{comment_text}_»")
    except Exception: pass

@router.message(F.text.startswith("/give_coins"))
async def macar_universal_give_coins(message: Message):
    if message.from_user.id != 8791830931: return
    args = message.text.split()
    if len(args) < 3: await message.answer("⚠️ **Формат:** `/give_coins @username_або_ID кількість`\nПриклад: `/give_coins me 50000` 🪙"); return
    target_raw = args[1].strip()
    try: amount = int(args[2])
    except ValueError: await message.answer("❌ Кількість монет має бути цілим числом!"); return
    target_id = 8791830931 if target_raw.lower() == "me" or target_raw == "8791830931" else (int(target_raw) if target_raw.isdigit() else USER_USERNAMES.get(target_raw.lower(), 0))
    if target_id == 0: await message.answer(f"❌ Користувача {target_raw} не знайдено!"); return
    USER_BALANCES[target_id] = USER_BALANCES.get(target_id, 0) + amount
    await message.answer(f"🪙 **Успішно нараховано!** Рахунок `{target_raw}` поповнено на **+{amount} Сімок** 🪙!")
    try: await bot.send_message(chat_id=target_id, text=f"🎁 **Економічний підгін!** Макар нарахував тобі **{amount} Сімок**! 🪙")
    except Exception: pass

@router.callback_query(F.data == "profile_bells")
async def process_smart_school_bells(callback: CallbackQuery):
    await callback.answer(); now = datetime.now() + timedelta(hours=3); weekday = now.weekday()
    if weekday >= 5: await callback.message.edit_text(text="🛌 **Зараз немає уроків!** Сьогодні вихідний! 🎉", reply_markup=settings_interactive_menu); return
    current_minutes = now.hour * 60 + now.minute
    schedule_blocks = [
        {"lesson": 1, "start": 8*60+30, "end": 9*60+15}, {"lesson": 2, "start": 9*60+35, "end": 10*60+20},
        {"lesson": 3, "start": 10*60+40, "end": 11*60+25}, {"lesson": 4, "start": 11*60+45, "end": 12*60+30},
        {"lesson": 5, "start": 12*60+50, "end": 13*60+35}, {"lesson": 6, "start": 13*60+45, "end": 14*60+30},
        {"lesson": 7, "start": 14*60+40, "end": 15*60+25}
    ]
    if current_minutes < schedule_blocks[0]["start"]: await callback.message.edit_text(text="☕ **Навчання ще не почалося!** Уроки стартують о 08:30. 😉", reply_markup=settings_interactive_menu); return
    if current_minutes > schedule_blocks[-1]["end"]: await callback.message.edit_text(text="🎒 **Зараз немає уроків!** Всі уроки на сьогодні закінчилися! 🛑🔥", reply_markup=settings_interactive_menu); return
    for block in schedule_blocks:
        if block["start"] <= current_minutes <= block["end"]:
            await callback.message.edit_text(text=f"📚 **ЗАРАЗ ЙДЕ {block['lesson']}-й УРОК!**\n⏱️ Урок закінчиться о **{int(block['end']/60):02d}:{block['end']%60:02d}**.\n**іди вчись, не відволікайся!** 👨‍💻❌📱", reply_markup=settings_interactive_menu); return
    await callback.message.edit_text(text="🍕 **ЗАРАЗ ІДЕ ПЕРЕМІНА!** Сходи в їдальню за булочкою! 🏃‍♂️💨", reply_markup=settings_interactive_menu)

@router.callback_query(F.data == "economy_back_to_settings")
async def process_back_to_settings_callback(callback: CallbackQuery):
    await callback.answer(); await callback.message.edit_text(text="⚙️ Налаштування та інтерактив:", reply_markup=settings_interactive_menu)

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
    if user_id == 8791830931: await message.answer(text="🛠️ **Вітаємо, Макаре! Функції Розробника v2.7:**", reply_markup=get_admin_menu_keyboard(user_id)); return
    all_protected_ids = []
    for s in [ADMIN_L4_IDS, MODERATOR_IDS, HW_ASSISTANT_IDS, STAROSTA_IDS, TESTER_IDS]:
        if s: all_protected_ids.extend(s)
    if user_id in all_protected_ids or user_id == TEACHER_CHAT_ID: await message.answer(text="🛠️ **Панель Адміністратора:**", reply_markup=get_admin_menu_keyboard(user_id))
    else: await message.answer("🛑 Немає доступу.")

@router.callback_query(F.data == "economy_top_sheikhs")
async def process_top_sheikhs(callback: CallbackQuery):
    await callback.answer()
    if not USER_BALANCES:
        await callback.message.answer("📊 **База даних банку порожня!** Баланси учнів ще не ініціалізовані.")
        return
    sorted_balances = sorted(USER_BALANCES.items(), key=lambda x: x, reverse=True)
    top_text = "👑 **ТОП-10 НАЙБАГАТШИХ ШЕЙХІВ 7-В КЛАСУ** 🪙\n\n"
    medals = {1: "🥇", 2: "🥈", 3: "🥉", 4: "📋", 5: "📋", 6: "📋", 7: "📋", 8: "📋", 9: "📋", 10: "📋"}
    count = 1
    for u_id, balance in sorted_balances:
        if u_id == 8791830931: continue
        display_name = CHAT_REGISTERED_USERS.get(u_id, "")
        if not display_name:
            for username, name in USER_USERNAMES_TEXT.items():
                if USER_USERNAMES.get(username.lower(), 0) == u_id:
                    display_name = name; break
        if not display_name: display_name = f"Учень (ID: {str(u_id)[:4]}...)"
        top_text += f"{medals.get(count, '📋')} **{count} Місце:** {display_name} — **{balance} Сімок** 🪙\n"
        count += 1
        if count > 10: break
    top_text += "\n📊 _Заробляй Сімки кожного дня, роби перекази та купуй преміум лут, щоб очолити фінансовий рейтинг класу!_"
    await callback.message.edit_text(text=top_text, reply_markup=settings_interactive_menu)


async def main():
    logging.basicConfig(level=logging.INFO); dp.include_router(router)
    asyncio.create_task(self_ping_task()); asyncio.create_task(cron_secret_agent_picker())
    restore_homework_from_file()
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await asyncio.gather(run_web_server(), dp.start_polling(bot))
    finally: await bot.session.close()

if __name__ == "__main__": asyncio.run(main())
