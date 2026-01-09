import asyncio
import logging
from aiogram import Router, F, types
from aiogram.filters import Command
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
from keyboards.inline import get_categories_keyboard


logger = logging.getLogger(__name__)


class Category(StatesGroup):
    name = State()  # category name
    type = State()  # type income|outcome


router = Router()


async def show_categories_list(
    chat_id: int, message_id: int = None, bot=None, initial: bool = False
):
    """Функция для отображения списка категорий"""
    categories = await db.get_categories_list()
    message_content = "Список категорий пуст"

    if categories:
        message_content = "Список категорий:\n"
        for id, name, type, emoji in categories:
            type_text = "Приход" if type == "income" else "Расход"
            message_content += f"{name} - {type_text}\n"

    keyboard = []
    keyboard.append(
        [InlineKeyboardButton(text="➕ Добавить", callback_data="add_category")]
    )

    if message_id and bot:
        # Редактируем существующее сообщение
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=message_content,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        )
    elif bot and not initial:
        # Отправляем новое сообщение (если нужно)
        await bot.send_message(
            chat_id=chat_id,
            text=message_content,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        )
    else:
        # Для использования в categories_menu
        return message_content, InlineKeyboardMarkup(inline_keyboard=keyboard)


# Запрашиваем название категории
@router.message(Command("categories"))
async def categories_menu(message: Message):
    logger.info("Вызов /categories")
    await message.delete()
    message_content, reply_markup = await show_categories_list(
        message.chat.id, initial=True
    )
    await message.answer(text=message_content, reply_markup=reply_markup)


# Обработка редактирования
@router.callback_query(F.data == "add_category")
async def handle_add_category(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите название категории")
    # Запоминаем ID сообщения
    await state.update_data(initial_message_id=callback.message.message_id)
    await state.set_state(Category.name)


# Ловим и сохраняем название, запрашиваем тип
@router.message(F.text, Category.name)
async def capture_category_name(message: types.Message, state: FSMContext):
    keyboard = [
        [InlineKeyboardButton(text="➕ Приход", callback_data="category_income")],
        [InlineKeyboardButton(text="➖ Расход", callback_data="category_expense")],
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_category")
        ],  # Добавили кнопку отмены
    ]

    await state.update_data(name=message.text)
    await message.delete()
    data = await state.get_data()
    message_content = (
        f"Новая категория:\nНазвание: {data.get('name')}\nТип: ---\nВыберите тип:"
    )

    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        await asyncio.sleep(0.2)
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=data.get("initial_message_id"),
            text=message_content,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        )
    await state.set_state(Category.type)


@router.callback_query(F.data.startswith("category"), Category.type)
async def capture_category_type(callback: CallbackQuery, state: FSMContext):
    category_type = callback.data.split("_")[1]
    await state.update_data(type=category_type)
    data = await state.get_data()
    name = data.get("name")
    type = data.get("type")

    message_content = f"Новая категория:\nНазвание: {name}\nТип: {type}"
    save = await db.add_category(name, type)

    if save:
        message_content += "\n✅ Категория успешно добавлена"
    else:
        message_content += "\n❌ Ошибка добавления категории"

    logger.info(f"Сохраняем категорию: {save}")
    await state.clear()

    # Создаем клавиатуру с кнопкой "Назад к списку"
    keyboard = [
        [
            InlineKeyboardButton(
                text="⬅️ Назад к списку", callback_data="back_to_categories"
            )
        ]
    ]

    await callback.message.edit_text(
        text=message_content,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )
    await callback.answer()

    # Новая функция для возврата к списку


@router.callback_query(F.data == "back_to_categories")
async def handle_back_to_categories(callback: CallbackQuery):
    await show_categories_list(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        bot=callback.bot,
    )
    await callback.answer()


# Также можно добавить обработку кнопки "Назад" при добавлении категории
@router.callback_query(F.data == "cancel_category")
async def handle_cancel_category(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await show_categories_list(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        bot=callback.bot,
    )
    await callback.answer()
