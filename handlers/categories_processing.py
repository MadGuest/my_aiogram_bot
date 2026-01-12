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
    CategoriesCallbackFactory,
    categories_list_keyboard,
    category_back_to_edit_keyboard,
    category_delete_confirm_keyboard,
    category_edit_keyboard,
    category_types_keyboard,
    category_add_keyboard,
    category_back_to_add_keyboard,
    category_back_to_list_keyboard,
    category_rename_keyboard,
    category_details_keyboard,
)


CATEGORY_TYPE_TEXT = {"income": "💰 Доход", "expense": "🛒 Расход"}

logger = logging.getLogger(__name__)

router = Router()


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

    # Message и CallbackQuery требуют разных способов обработки
    if isinstance(event, Message):
        chat_id = event.chat.id
        message_id = event.message_id
        is_message = True

    else:  # CallbackQuery
        chat_id = event.message.chat.id
        message_id = event.message.message_id
        is_message = False

    async with ChatActionSender.typing(bot=event.bot, chat_id=chat_id):
        # Получаем список категорий из БД
        categories_list = await db.get_categories_list()
        # Чтобы избежать проблем с ограничением на размер callback_data
        # и не передавать названия категорий по сети, сохраняем в state
        # соответствие id и имени/типа категории
        # category_mapping = {cat.id: (cat.name, cat.type) for cat in categories_list}
        # await state.update_data(category_mapping=category_mapping)

    # Заголовок сообщения для пользователя по умолчанию
    message_content = "<b>📂 Список категорий пуст</b>\n"

    # Получаем клавиатуру с кнопками "Добавить" и "Отмена"
    footer_keyboard = category_add_keyboard()

    # Если категорий в БД еще нет, показываем сообщение по умолчанию
    # и кнопки "Добавить" и "Отмена"
    if not categories_list:
        keyboard = footer_keyboard

    # Или меняем заголовок на "Список категорий"
    # строим клавиатуру из полученных категорий
    # и добавляем к ней снизу кнопки "Добавити" и "Отмена"
    else:
        # Создаем список ID категорий для построения клавиатуры
        message_content = "<b>📂 Список категорий</b>\n"
        # Пока оставляем передачу "сырого" списка категорий из БД
        keyboard = categories_list_keyboard(categories_list)
        keyboard.attach(footer_keyboard)

    # Окончательная клавиатура
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
    SuppressTextFilter(suppress_text=True),
)
async def handle_unstated_text(message: Message, state: FSMContext):
    logger.info("Сработал текстовый фильтр")
    await message.delete()
    # Отправляем сообщение с кнопкой, которая сразу же "нажимается"
    await message.answer(
        "Выберите вариант кнопкой",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Понятно", callback_data=f"auto_alert:{message.text}"
                    )
                ]
            ]
        ),
    )


# Обработка ввода текста там, где это нежелательно
@router.callback_query(F.data.startswith("auto_alert:"))
async def auto_show_alert(callback: CallbackQuery):
    text = callback.data.split(":", 1)[1]
    await callback.answer()
    await callback.message.delete()  # Удаляем сообщение с кнопкой


# Обработчик кнопки "Отмена". Удаляет сообщение
@router.callback_query(CategoriesCallbackFactory.filter(F.action == "cancel"))
async def handle_cancel_category(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()


# Обработчик команды /categories
# Вывод списка категорий с кнопкой "Добавить"
@router.message(Command("categories"))
@router.callback_query(CategoriesCallbackFactory.filter(F.action == "back_to_list"))
async def categories_menu(event: Message | CallbackQuery, state: FSMContext):
    """
    Обработчик для отображения списка категорий

    Отлавливает команду /categories или коллбэк от кнопки 'Назад к списку'

    Отправляет пользователю кнопки категорий +
    'Добавить' и 'Отмена'

    Текстовый ввод от пользователя подавляется

    """

    # Устанавливаем флаг подавления текста
    await state.update_data(suppress_text=True)

    # Показываем список категорий и кнопки действия с ними
    await show_categories_list(event)

    await state.set_state(Category.waiting_type)


@router.callback_query(CategoriesCallbackFactory.filter(F.action == "add"))
async def handle_add_category(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для добавления новой категории

    Отлавливает коллбэк от кнопки 'Добавить'

    Отправляет пользователю кнопки:
    'Доход', 'Расход', 'Назад к списку' и 'Отмена' и предложение выбрать тип

    Текстовый ввод от пользователя подавляется

    """

    logger.info("Попали в обработчик добавления категории")

    # Устанавливаем флаг запрета на ввод текста
    await state.update_data(suppress_text=True)

    # Клавиатура с кнопками "Доход", "Расход", "Назад к списку"
    keyboard = category_types_keyboard()
    reply_markup = keyboard.as_markup()

    await callback.message.edit_text(
        text=f"<b>✚ Новая категория</b>\n\n"
        f"<b>⭕️Тип:\n</b>"
        f"⭕️Название: \n\n"
        f"⬇️ Выберите тип ⬇️",
        reply_markup=reply_markup,
    )
    # Запоминаем ID сообщения
    await state.update_data(initial_message_id=callback.message.message_id)
    # Устанавливаем состояние для следующего шага (Название)
    await state.set_state(Category.waiting_name)


@router.callback_query(
    Category.waiting_name, CategoriesCallbackFactory.filter(F.action == "type")
)
async def capture_category_type(
    callback: CallbackQuery, callback_data: CategoriesCallbackFactory, state: FSMContext
):
    """
    Обработчик коллбэков от клавиатуры выбора типа категории

    Отлавливает коллбэки от кнопок 'Доход', 'Расход'

    Отправляет пользователю кнопки:
    'Назад и 'Отмена' и предложение ввести название
    Текстовый ввод от пользователя разрешен

    """

    logger.info("Попали в обработчик типа категории")

    # Сбрасываем флаг запрета на ввод текста
    await state.update_data(suppress_text=False)

    # Получаем выбранный пользователем тип из коллбэка
    category_type = callback_data.type

    # Получаем клавиатуру с кнопками:
    # Назад - вернуться к выбору типа
    # Отмена - очистить чат
    keyboard = category_back_to_add_keyboard()
    reply_markup = keyboard.as_markup()

    # Сохраняем тип для категории в state data
    await state.update_data(type=category_type)

    # Получаем текст типа на русском для сообщения
    category_type = CATEGORY_TYPE_TEXT.get(category_type)

    # На месте предыдущего сообщения показываем сообщение для шага ввода названия
    await callback.message.edit_text(
        text=f"<b>✚ Новая категория</b>\n\n"
        f"✅ Тип: {category_type}\n"
        f"⭕️ Название: \n\n"
        f"⬇️ Введите название ⬇️",
        reply_markup=reply_markup,
    )
    await state.set_state(Category.finish)


# Обработчик названия
# Сохраняет название и показывает сообщение с результатом добавления
@router.message(Category.finish)
async def capture_category_name(message: Message, state: FSMContext):
    """
    Обработчик ввода названия

    Отлавливает ссобщение от пользователя
    Cохраняет название в state data

    Отправляет пользователю кнопки:
    'Назад к списку' и 'Отмена' и сообщение со статусом операции
    Текстовый ввод от пользователя подавляется

    """

    logger.info("Попали в обработчик названия категории")

    # Устанавливаем флаг запрета на ввод текста
    await state.update_data(suppress_text=True)

    # Сохраняем название в state data
    await state.update_data(name=message.text)

    # Достаем данные из state_data
    data = await state.get_data()
    category_type = data.get("type")
    category_name = data.get("name")
    initial_message = data.get("initial_message_id")

    # Заменяем текст типа категории на русский с эмодзи
    category_type_text = CATEGORY_TYPE_TEXT.get(category_type)

    # Получаем клавиатуру с кнопками:
    # Назад к списку - вернуться в список категорий
    # Отмена - очистить чат
    keyboard = category_back_to_list_keyboard()
    reply_markup = keyboard.as_markup()

    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        # Сохраняем категорию в БД
        save = await db.add_category(name=category_name, type=category_type)

        if not save:
            # Логируем ошибку
            logger.info(f"Ошибка сохранения категории: {save}")

        # Удаляем ответ пользователя
        await message.delete()

        # Текст для статуса
        status = "Успех ✅" if save else "Ошибка ⭕️"

        await message.bot.edit_message_text(
            text=f"<b>✚ Новая категория</b>\n\n"
            f"✅ Тип: {category_type_text}\n"
            f"✅ Название: {data.get('name')}\n"
            f"Статус: {status}",
            reply_markup=reply_markup,
            chat_id=message.chat.id,
            message_id=initial_message,
        )

    # Устанавливаем состояние, чтобы cработал фильтр для подавления ввода текста
    await state.set_state(Category.finish_waiting_name)


@router.callback_query(CategoriesCallbackFactory.filter(F.action == "select"))
async def handle_category_selection(
    callback: CallbackQuery, callback_data: CategoriesCallbackFactory
):
    """
    Обработчик для отображения инфо о категории и меню действий с ней

    Отлавливает коллбэк от нажатия на кнопку категории в списке

    Отправляет пользователю сообщение с деталями категории и кнопки:
    'Удалить', 'Редактировать', 'Назад к списку' и 'Отмена'

    Текстовый ввод от пользователя подавляется

    """

    logger.info(f"Выбрана категория: {callback_data}")

    # Получаем id категории из callback_data
    category_id = callback_data.id

    async with ChatActionSender.typing(
        bot=callback.bot, chat_id=callback.message.chat.id
    ):

        # Получаем категорию из БД
        category = await db.get_category_by_id(category_id)

    logger.info(f"Получена категория из БД: {category}")

    if category:
        # Извлекаем название и тип категории
        category_name, category_type = category

        # Получаем клавиатуру с кнопками:
        # Удалить - удалить категорию
        # Редактировать - изменить категорию
        # Назад к списку - вернуться в список категорий
        # Отмена - очистить чат
        keyboard = category_details_keyboard(category_id)
        reply_markup = keyboard.as_markup()

        # Получаем текст для сообщения с инфо о категории
        answer_content = format_category_info(
            category_name, category_type, category_id, "Выберите действие"
        )

        # Отправляем пользователю ответ
        await callback.message.edit_text(
            text=answer_content, parse_mode="HTML", reply_markup=reply_markup
        )

    await callback.answer()


@router.callback_query(CategoriesCallbackFactory.filter(F.action == "delete"))
async def handle_category_delete_confirmation(
    callback: CallbackQuery, callback_data: CategoriesCallbackFactory
):
    """
    Обработчик для удаления категории

    Отлавливает коллбэк от кнопки 'Удалить'

    Отправляет пользователю кнопки:
    'Да, удалить', 'Нет, отмена'

    Текстовый ввод от пользователя подавляется

    """

    logger.info(f"Попали в обработчик удаления категории. Категория: {callback_data}")

    # Получаем ID из callback data
    category_id = callback_data.id

    # Получаем клавиатуру с кнопками:
    # Да, удалить - подтвердить удаление
    # Нет, отменить - отказаться от удаления

    keyboard = category_delete_confirm_keyboard(category_id)
    reply_markup = keyboard.as_markup()

    # Отправляем пользователю запрос на подтверждение
    await callback.message.edit_text(
        text="⚠️ Вы уверены, что хотите удалить эту категорию?",
        reply_markup=reply_markup,
    )
    await callback.answer()


@router.callback_query(CategoriesCallbackFactory.filter(F.action == "confirm_delete"))
async def handle_delete_execution(
    callback: CallbackQuery, callback_data: CategoriesCallbackFactory, state: FSMContext
):
    """
    Обработчик для подтверждения удаления категории

    Отлавливает коллбэк от кнопки 'Да, удалить'

    Отправляет пользователю сообщение со статусом удаления категории

    Текстовый ввод от пользователя подавляется

    """

    # Получаем ID категории
    category_id = callback_data.id

    async with ChatActionSender.typing(
        bot=callback.message.bot, chat_id=callback.message.chat.id
    ):

        logger.info(f"Удаляем категорию {category_id}")
        # Получаем название категории из БД
        category_name = await db.get_category_name_by_id(category_id)

        # Удаляем категорию
        await db.delete_category_by_id(category_id)

        # Название для сообщения
        deleted_name = category_name[0]

    # Показываем уведомление
    await callback.answer(f"✅ Категория '{deleted_name}' удалена!", show_alert=True)

    # Возвращаемся к списку категорий
    await show_categories_list(callback)


@router.callback_query(CategoriesCallbackFactory.filter(F.action == "edit"))
async def handle_category_selection(
    callback: CallbackQuery, callback_data: CategoriesCallbackFactory, state: FSMContext
):
    """
    Обработчик для меню редактирования категории

    Отлавливает коллбэк от кнопки 'Редактировать'

    Отправляет пользователю сообщение со статусом удаления категории

    Текстовый ввод от пользователя подавляется

    """

    # Забираем ID категории из callback_data
    category_id = callback_data.id

    # # Достаем из state инфо о категории (чтобы не дергать БД)
    # data = state.get_data({'category_mapping'})
    # category_name = data.get('name')
    # category_type = data.get('type')

    logger.info(
        f"Попали в обработчик редактирования категории:\ncallback_data= {callback_data}\nstate= {state}"
    )

    # Получаем клавиатуру с кнопками:
    # переименовать - изменить название категории
    # Назад - вернуться к предыдущему шагу
    # Отмена - стереть сообщение
    keyboard = category_edit_keyboard(category_id)
    reply_markup = keyboard.as_markup()

    async with ChatActionSender.typing(
        bot=callback.bot, chat_id=callback.message.chat.id
    ):

        # Получаем категорию из БД
        category = await db.get_category_by_id(category_id)

    category_name, category_type = category

    # Получаем текст сообщения для пользователя
    answer_content = format_category_info(
        category_name, category_type, category_id, "Выберите действие"
    )

    # Отправляем ответ
    await callback.message.edit_text(
        text=answer_content,
        reply_markup=reply_markup,
    )
    await callback.answer()


@router.callback_query(CategoriesCallbackFactory.filter(F.action == "rename"))
async def handle_category_rename(
    callback: CallbackQuery, callback_data: CategoriesCallbackFactory, state: FSMContext
):
    """
    Обработчик для переименования категории

    Отлавливает коллбэк от кнопки 'Переименовать'

    Отправляет пользователю предложение ввести новое название для категории

    Текстовый ввод от пользователя не подавляется

    """

    # Сбрасываем флаг запрета на ввод текста
    await state.update_data(suppress_text=False)

    logger.info(f"Обработчик переименования категории {callback_data}")

    # Получаем id название и тип категории
    category_id = callback_data.id
    async with ChatActionSender.typing(
        bot=callback.bot, chat_id=callback.message.chat.id
    ):

        # Получаем категорию из БД
        category = await db.get_category_by_id(category_id)

    category_name, category_type = category

    # Получаем клавиатуру с кнопками:
    # переименовать - изменить название категории
    # Назад - вернуться к предыдущему шагу
    # Отмена - стереть сообщение
    keyboard = category_rename_keyboard(category_id)
    reply_markup = keyboard.as_markup()

    # Получаем текс для сообщения
    answer_content = format_category_info(
        category_name, category_type, category_id, "Введите новое название"
    )

    # Отправляем ответ
    await callback.message.edit_text(
        text=answer_content,
        reply_markup=reply_markup,
    )

    # ID сообщения которое будем редактировать на следующем шаге
    await state.update_data(initial_message_id=callback.message.message_id)
    # ID категории
    await state.update_data(category_id=category_id)
    # Состояние для следующего шага
    await state.set_state(Category.waiting_new_name)

    await callback.answer()


@router.message(Category.waiting_new_name)
async def capture_new_category_name(message: Message, state: FSMContext):
    """
    Обработчик нового названия категории

    Отлавливает ввод нового названия пользователем

    Сохраняет изменения категории в БД и отправляет сообщение с результатом

    Текстовый ввод от пользователя подавляется

    """

    logger.info(f"Попали в обработчик нового названия категории")
    # Устанавливаем флаг запрета на ввод текста
    await state.update_data(suppress_text=True)

    # Сохраняем новое название в state data
    await state.update_data(name=message.text)
    data = await state.get_data()
    # Извлекаем данные
    category_id = data.get("category_id")
    category_name = data.get("name")
    initial_message = data.get("initial_message_id")

    # Задаем клавиатура

    keyboard = [
        [
            InlineKeyboardButton(
                text="↩️ Назад к списку",
                callback_data=CategoriesCallbackFactory(action="back_to_list").pack(),
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

    # Отладочный хэндлер, ловит все, что не прошло фильтры
    @router.message()
    @router.callback_query()
    def echo(event: Message | CallbackQuery):
        logger.info("Эхо хэндлер")
