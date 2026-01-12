import asyncio
import logging
from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter, Filter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import db

from keyboards.inline import (
    categories_list_keyboard,
    category_back_to_edit_keyboard,
    category_delete_confirm_keyboard,
    category_edit_keyboard,
    category_types_keyboard,
    category_add_keyboard,
    category_back_to_add_keyboard,
    category_back_to_list_keyboard,
    category_rename_keyboard,
    category_details_keyboard
)


CATEGORY_TYPE_TEXT = {"income": "💰 Доход", "expense": "🛒 Расход"}

logger = logging.getLogger(__name__)

router = Router()


class CategoriesCallback(CallbackData, prefix="cats"):
    id: int | None = None
    type: str | None = None
    name: str | None = None
    action: str | None = None



class Category(StatesGroup):
    waiting_name = State()  # category name
    waiting_type = State()  # type income|outcome
    waiting_new_name = State()  # новое название
    finish = State()
    finish_waiting_name = State()
    edit = State()


# Кастомный фильтр для подавления текстового ввода там, где ждем нажатия на кнопку
class SuppressTextFilter(Filter):
    def __init__(self, **data_filter):
        self.data_filter = data_filter

    async def __call__(self, message: Message, state: FSMContext) -> bool:
       
        # Проверка данных
        if self.data_filter:
            data = await state.get_data()
            flag = data.get("suppress_text", False)
            if flag:
                return True 
        
        return False

# Функция для отображения списка категорий
async def show_categories_list(event: Message | CallbackQuery):
    if isinstance(event, Message):
        chat_id = event.chat.id
        message_id = event.message_id
        is_message = True
    else:  # CallbackQuery
        chat_id = event.message.chat.id
        message_id = event.message.message_id
        is_message = False

    async with ChatActionSender.typing(bot=event.bot, chat_id=chat_id):
        categories_list = await db.get_categories_list()

    message_content = "<b>📂 Список категорий пуст</b>\n"

    footer_keyboard = category_add_keyboard()

    if not categories_list:
        keyboard = footer_keyboard
    else:
        message_content = "<b>📂 Список категорий</b>\n"
        keyboard = categories_list_keyboard(categories_list)
        keyboard.attach(footer_keyboard)

    reply_markup = keyboard.as_markup()

    # Обработка в зависимости от типа события
    if is_message:
        # Удаляем сообщение с командой
        await event.delete()
        # Отправляем новое сообщение
        await event.answer(
            text=message_content,
            reply_markup=reply_markup,
        )
    else:  # CallbackQuery
        # Редактируем существующее сообщение
        await event.message.edit_text(
            text=message_content,
            reply_markup=reply_markup,
        )
        # Отвечаем на callback, чтобы убрать часики
        await event.answer()


# Формат сообщения с деталями категории
def format_category_info(
    category_name: str, category_type: str, category_id: int, action_message: str
) -> str:
    """Форматирование информации о категории"""
    type_text = CATEGORY_TYPE_TEXT.get(category_type, category_type)
    return (
        f"<b>{category_name}</b>\n\n"
        f"Тип: {type_text}\n"
        f"ID: {category_id}\n\n"
        f"<b>⬇️ {action_message} ⬇️</b>"
    )

# Хэндлер для подавления текста там, где нам надо ждать только нажатия на кнопку
@router.message(
    F.text,
    SuppressTextFilter(
        suppress_text=True
    ),
)
async def handle_unstated_text(message: Message, state: FSMContext):
    logger.info("Сработал текстовый фильтр")
    await message.delete()
    # Отправляем сообщение с кнопкой, которая сразу же "нажимается"
    await message.answer(
        "Выберите вариант кнопкой",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="Понятно", 
                    callback_data=f"auto_alert:{message.text}"
                )]
            ]
        )
    )

# Обработка ввода текста там, где это нежелательно
@router.callback_query(F.data.startswith("auto_alert:"))
async def auto_show_alert(callback: CallbackQuery):
    text = callback.data.split(":", 1)[1]
    await callback.answer()
    await callback.message.delete()  # Удаляем сообщение с кнопкой

# Обработчик кнопки "Отмена". Удаляет сообщение
@router.callback_query(CategoriesCallback.filter(F.action == "cancel"))
async def handle_cancel_category(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()


# Обработчик команды /categories
# Вывод списка категорий с кнопкой "Добавить"
@router.message(Command("categories"))
@router.callback_query(CategoriesCallback.filter(F.action == "back_to_list"))
async def categories_menu(event: Message | CallbackQuery, state: FSMContext):
    # Показываем список категорий и кнопки действия с ними
    await show_categories_list(event)

    await state.set_state(Category.waiting_type)

    # Устанавливаем флаг запрета на ввод текста
    await state.update_data(suppress_text=True)


# Обработчик кнопки "Добавить"
# Показывает клавиатуру для выбора типа, текстовый ввод подавляется
@router.callback_query(CategoriesCallback.filter(F.action == "add"))
async def handle_add_category(callback: CallbackQuery, state: FSMContext):
    logger.info("Попали в обработчик добавления категории")

    # Устанавливаем флаг запрета на ввод текста
    await state.update_data(suppress_text=True)

    
    keyboard = category_types_keyboard()
    reply_markup = keyboard.as_markup()

    await callback.message.edit_text(
        "<b>✚ Новая категория</b>\n\n⬇️ Выберите тип ⬇️",
        reply_markup=reply_markup,
    )
    # Запоминаем ID сообщения
    await state.update_data(initial_message_id=callback.message.message_id)
    await state.set_state(Category.waiting_name)


# Обработчик нажатия на кнопку типа (Доход/расход)
# Сохраняет тип и запрашивает название
@router.callback_query(
    Category.waiting_name, CategoriesCallback.filter(F.action == "type")
)
async def capture_category_type(
    callback: CallbackQuery,
    callback_data: CategoriesCallback,
    state: FSMContext
):
    logger.info("Попали в обработчик типа категории")

    # Сбрасываем флаг запрета на ввод текста
    await state.update_data(suppress_text=False)

    category_type = callback_data.type
    keyboard = category_back_to_add_keyboard()

    reply_markup = keyboard.as_markup()
    await state.update_data(type=category_type)
    category_type = CATEGORY_TYPE_TEXT.get(category_type)
    await callback.message.edit_text(
        text=f"<b>✚ Новая категория</b>\n\n⭐ Тип: {category_type}\n⬇️ Введите название ⬇️",
        reply_markup=reply_markup,
    )
    await state.set_state(Category.finish)


# Обработчик названия 
# Сохраняет название и показывает сообщение с результатом добавления
@router.message(Category.finish)
async def capture_category_name(message: Message, state: FSMContext):
    logger.info("Попали в обработчик названия категории")

    # Сбрасываем флаг запрета на ввод текста
    await state.update_data(suppress_text=True)

    await state.update_data(name=message.text)
    data = await state.get_data()
    category_type = data.get("type")
    category_name = data.get("name")
    initial_message = data.get("initial_message_id")

    # Заменяем текст типа категории на русский с эмодзи
    category_type_text = CATEGORY_TYPE_TEXT.get(category_type)

    keyboard = category_back_to_list_keyboard()
    reply_markup = keyboard.as_markup()
    # Сохраняем категорию в БД
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        save = await db.add_category(name=category_name, type=category_type)
        if not save:
            logger.info(f"Ошибка сохранения категории: {save}")
        # Удаляем ответ пользователя
        await message.delete()

        status = "Успех ✅" if save else "Ошибка ⭕️"

        await message.bot.edit_message_text(
            text=f"<b>✚ Новая категория</b>\n\n"
                 f"⭐ Тип: {category_type_text}\n"
                 f"⭐ Название: {data.get('name')}\n"
                 "Статус: {status}",
            reply_markup=reply_markup,
            chat_id=message.chat.id,
            message_id=initial_message,
        )
    await state.set_state(Category.finish_waiting_name)


@router.callback_query(CategoriesCallback.filter(F.action == "select"))
async def handle_category_selection(
    callback: CallbackQuery, callback_data: CategoriesCallback
):
    logger.info(f"Выбрана категория: {callback_data}")
    category_id = callback_data.id
    category = await db.get_category_by_id(category_id)
    logger.info(category)
    if category:
        category_name, category_type = category

        keyboard = category_details_keyboard(category_id, category_name, category_type)
        reply_markup = keyboard.as_markup()

        answer_content = format_category_info(
            category_name, category_type, category_id, "Выберите действие"
        )

        await callback.message.edit_text(
            text=answer_content,
            parse_mode="HTML",
            reply_markup=reply_markup
        )

    await callback.answer()


@router.callback_query(CategoriesCallback.filter(F.action == "delete"))
async def handle_category_delete_confirmation(
    callback: CallbackQuery, callback_data: CategoriesCallback
):

    logger.info("Попали в обработчик удаления категории")
    logger.info(f"Выбрана категория: {callback_data}")
    category_id = callback_data.id

    keyboard = category_delete_confirm_keyboard(category_id)

    await callback.message.edit_text(
        text="⚠️ Вы уверены, что хотите удалить эту категорию?",
        reply_markup=keyboard.as_markup(),
    )
    await callback.answer()


@router.callback_query(CategoriesCallback.filter(F.action == "confirm_delete"))
async def handle_delete_execution(
    callback: CallbackQuery,
    callback_data: CategoriesCallback,
    state: FSMContext
):
    """Выполнить удаление категории"""
    category_id = callback_data.id

    # Обернуть это в чатэкшнсендер потом!!!
    async with ChatActionSender.typing(
        bot=callback.message.bot, chat_id=callback.message.chat.id
    ):
        logger.info(f"Удаляем категорию {category_id}")
        category_name = await db.get_category_name_by_id(category_id)
        # Удаляем категорию
        await db.delete_category_by_id(category_id)
        deleted_name = category_name[0]

    # Показываем уведомление
    await callback.answer(f"✅ Категория '{deleted_name}' удалена!", show_alert=True)

    # Возвращаемся к списку категорий
    await show_categories_list(callback)


@router.callback_query(CategoriesCallback.filter(F.action == "edit"))
async def handle_category_selection(
    callback: CallbackQuery,
    callback_data: CategoriesCallback,
    state: FSMContext
):

    category_id = callback_data.id
    category_name = callback_data.name
    category_type = callback_data.type

    logger.info(f"Попали в обработчик редактирования категории:\ncallback_data= {callback_data}\nstate= {state}")

    keyboard = category_edit_keyboard(category_id)

    reply_markup = keyboard.as_markup()

    answer_content = format_category_info(
        category_name, category_type, category_id, "Выберите действие"
    )

    await callback.message.edit_text(
        text=answer_content,
        reply_markup=reply_markup,
    )
    await callback.answer()


@router.callback_query(CategoriesCallback.filter(F.action == "change_name"))
async def handle_cnange_name(
    callback: CallbackQuery,
    callback_data: CategoriesCallback,
    state: FSMContext
):
    """Переименовать категорию"""
    # Сбрасываем флаг запрета на ввод текста
    await state.update_data(suppress_text=False)

    logger.info(f"Обработчик переименования категории {callback_data}")
    # Получаем id и название категории
    category_id = callback_data.id
    category_name, category_type = await db.get_category_by_id(category_id)

    keyboard = category_rename_keyboard(
        category_id,
        category_name,
        category_type
        )
    
    reply_markup = keyboard.as_markup()

    answer_content = format_category_info(
        category_name, category_type, category_id, "Введите новое название"
    )

    # А тут мы должны спросить новое название
    await callback.message.edit_text(
        text=answer_content,
        reply_markup=reply_markup,
    )
    await state.update_data(initial_message_id=callback.message.message_id)
    await state.update_data(category_id=category_id)
    await state.set_state(Category.waiting_new_name)
    await callback.answer()


@router.message(Category.waiting_new_name)
async def capture_new_category_name(message: Message, state: FSMContext):
    logger.info(f"Попали в обработчик нового названия категории")
    # Устанавливаем флаг запрета на ввод текста
    await state.update_data(suppress_text=True)

    await state.update_data(name=message.text)
    data = await state.get_data()
    category_id = data.get("category_id")
    category_name = data.get("name")
    initial_message = data.get("initial_message_id")
    logger.info(f"ID сообщения - {initial_message}")
    keyboard = [
        [
            InlineKeyboardButton(
                text="↩️ Назад к списку",
                callback_data=CategoriesCallback(action="back_to_list").pack(),
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    # Сохраняем категорию в БД
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        save = await db.update_name(category_id, category_name)
        if not save:
            logger.info(f"Ошибка сохранения категории: {save}")
        # Удаляем ответ пользователя
        await message.delete()

        await message.bot.edit_message_text(
            text=f"<b>✅ Категория изменена!</b>",
            reply_markup=reply_markup,
            chat_id=message.chat.id,
            message_id=initial_message,
        )
        await state.set_state(Category.finish_waiting_name)

    @router.message()
    @router.callback_query()
    def echo(event: Message | CallbackQuery):
        logger.info("Эхо хэндлер")
