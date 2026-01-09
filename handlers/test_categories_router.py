from aiogram.filters.callback_data import CallbackData
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram import Router, F, types
from config import db

router = Router()


class CategoriesCallback(CallbackData, prefix="cats"):
    page: int = 0
    selected_id: int | None = None

# Callback data для удаления
class DeleteCallback(CallbackData, prefix="del"):
    category_id: int
    page: int = 0  # Сохраняем страницу для возврата

ITEMS_PER_PAGE = 5

@router.message(Command("test_categories"))
async def cmd_categories(message: Message):
    await show_categories_page(message, page=0)

async def show_categories_page(target: Message | CallbackQuery, page: int = 0):
    """Универсальная функция показа страницы категорий"""
    categories = await db.get_categories_list()
    
    # Пагинация
    total_pages = max(1, (len(categories) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    
    # Корректируем номер страницы, если он выходит за пределы
    if page < 0:
        page = 0
    if page >= total_pages and total_pages > 0:
        page = total_pages - 1
    
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    
    keyboard = []
    
    # Добавляем категории для текущей страницы
    for cat_id, name, cat_type, cat_emoji in categories[start_idx:end_idx]:
        button_text = f"{name} - {cat_type}"
        callback_data = CategoriesCallback(
            page=page,
            selected_id=cat_id
        ).pack()
        keyboard.append([InlineKeyboardButton(
            text=button_text, 
            callback_data=callback_data
        )])
    
    # Кнопки пагинации
    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=CategoriesCallback(page=page-1).pack()
        ))
    
    if page < total_pages - 1:
        pagination_buttons.append(InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data=CategoriesCallback(page=page+1).pack()
        ))
    
    if pagination_buttons:
        keyboard.append(pagination_buttons)
    
    # Кнопка "Добавить"
    keyboard.append([InlineKeyboardButton(
        text="➕ Добавить", 
        callback_data="add_category"
    )])
    
    text = f"📂 Список категорий (стр. {page + 1}/{total_pages}):"
    if not categories:
        text = "📂 Список категорий пуст"
    
    # Определяем, как отправлять сообщение
    if isinstance(target, Message):
        # Если это команда - отправляем новое сообщение
        await target.answer(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    else:
        # Если это callback - редактируем существующее
        await target.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )

@router.callback_query(CategoriesCallback.filter(F.selected_id.is_not(None)))
async def handle_category_selection(callback: CallbackQuery, callback_data: CategoriesCallback):
    print(f'handle category selection: {callback.data}')
    # Показать детали категории с кнопкой удаления
    await show_category_details(callback, callback_data.selected_id, callback_data.page)
    await callback.answer()

@router.callback_query(CategoriesCallback.filter(F.selected_id.is_(None)))
async def handle_page_selection(callback: CallbackQuery, callback_data: CategoriesCallback):
    print(f'handle page selection: {callback.data}')
    # Просто переключить страницу
    await show_categories_page(callback, callback_data.page)
    await callback.answer()


async def show_category_details(callback: CallbackQuery, category_id: int, page: int):
    # Получаем информацию о категории
    category = await db.get_category_by_id(category_id)
    
    if category:
        name, cat_type = category
        
        keyboard = [
            [
                InlineKeyboardButton(
                    text="🗑️ Удалить", 
                    callback_data=DeleteCallback(
                        category_id=category_id,
                        page=page
                    ).pack()
                ),
                InlineKeyboardButton(
                    text="✏️ Редактировать", 
                    callback_data=f"edit_{category_id}_{page}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="↩️ Назад к списку", 
                    callback_data=CategoriesCallback(page=page).pack()
                )
            ]
        ]
        
        await callback.message.edit_text(
            text=f"📁 Информация о категории:\n\n"
                 f"<b>Название:</b> {name}\n"
                 f"<b>Тип:</b> {cat_type}\n"
                 f"<b>ID:</b> {category_id}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    
    await callback.answer()

@router.callback_query(DeleteCallback.filter())
async def handle_delete_confirmation(callback: CallbackQuery, callback_data: DeleteCallback):
    """Показать подтверждение удаления"""
    category_id = callback_data.category_id
    page = callback_data.page
    
    keyboard = [
        [
            InlineKeyboardButton(
                text="✅ Да, удалить", 
                callback_data=f"confirm_delete_{category_id}_{page}"
            ),
            InlineKeyboardButton(
                text="❌ Нет, отмена", 
                callback_data=CategoriesCallback(
                    page=page,
                    selected_id=category_id
                ).pack()
            )
        ]
    ]
    
    await callback.message.edit_text(
        text="⚠️ Вы уверены, что хотите удалить эту категорию?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_delete_"))
async def handle_delete_execution(callback: CallbackQuery):
    """Выполнить удаление категории"""
    try:
        # Извлекаем данные из callback_data
        parts = callback.data.split("_")
        if len(parts) >= 4:
            category_id = int(parts[2])
            page = int(parts[3])
            
            # Получаем имя категории перед удалением для сообщения
            category_name = await db.get_category_name_by_id(category_id)
            
            # Удаляем категорию
            await db.delete_category_by_id(category_id)


            
            deleted_name = category_name[0] if category_name else "категорию"
            
            # После удаления нужно проверить, не пуста ли страница
            categories = await db.get_categories_list()
            total_pages = max(1, (len(categories) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
            
            # Если текущая страница стала пустой, переходим на предыдущую
            if page >= total_pages and page > 0:
                page = total_pages - 1
            
            
            # Показываем уведомление
            await callback.answer(f"✅ Категория '{deleted_name}' удалена!", show_alert=True)
            
            # Возвращаемся к списку категорий
            await show_categories_page(callback.message, page)
            
    except Exception as e:
        await callback.answer(f"❌ Ошибка при удалении: {str(e)}", show_alert=True)
        print(f"Error deleting category: {e}")

@router.callback_query(F.data == "add_category")
async def add_category(callback: CallbackQuery):
    """Обработчик кнопки Добавить"""
    # Здесь можно добавить FSM для ввода новой категории
    await callback.message.edit_text(
        "Введите название новой категории (отправьте сообщением):"
    )
    await callback.answer()

# Обработка возврата из любых состояний
@router.callback_query(F.data.startswith("back_to_page_"))
async def back_to_specific_page(callback: CallbackQuery):
    """Возврат на конкретную страницу"""
    try:
        page = int(callback.data.split("_")[-1])
        await show_categories_page(callback.message, page)
    except:
        await show_categories_page(callback.message, 0)
    await callback.answer()

# Альтернативный вариант: общий обработчик возврата
@router.callback_query(F.data == "back_to_list")
async def back_to_list(callback: CallbackQuery):
    """Возврат на первую страницу списка"""
    await show_categories_page(callback.message, 0)
    await callback.answer()

# Обработка редактирования
@router.callback_query(F.data.startswith("edit_"))
async def handle_edit_category(callback: CallbackQuery):
    """Начало редактирования категории"""
    try:
        parts = callback.data.split("_")
        if len(parts) >= 3:
            category_id = int(parts[1])
            page = int(parts[2]) if len(parts) > 2 else 0
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        text="✏️ Изменить название", 
                        callback_data=f"change_name_{category_id}_{page}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔄 Изменить тип", 
                        callback_data=f"change_type_{category_id}_{page}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="↩️ Назад", 
                        callback_data=CategoriesCallback(
                            page=page,
                            selected_id=category_id
                        ).pack()
                    )
                ]
            ]
            
            await callback.message.edit_text(
                "Что вы хотите изменить?",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    await callback.answer()