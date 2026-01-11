from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from typing import Optional

EMOJI_MAPPING = {"income": "💰", "expense": "🛒"}


class ActionsCallbackFactory(CallbackData, prefix="act"):
    action: str
    value: Optional[int] = None


class CategoriesCallbackFactory(CallbackData, prefix="cats"):
    id: int | None = None
    type: str | None = None
    name: str | None = None
    action: str | None = None


def get_actions_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="💰Приход", callback_data=ActionsCallbackFactory(action="income")
    )
    builder.button(
        text="💸Расход", callback_data=ActionsCallbackFactory(action="outcome")
    )
    builder.button(
        text="➡️Перевод", callback_data=ActionsCallbackFactory(action="transfer")
    )
    builder.button(
        text="🧾Платёж", callback_data=ActionsCallbackFactory(action="payment")
    )
    builder.adjust(1)
    return builder.as_markup()


def categories_list_keyboard(categories: list):
    builder = InlineKeyboardBuilder()
    for category_id, category_name, category_type, emoji in categories:
        category_type_text = EMOJI_MAPPING.get(category_type)
        builder.button(
            text=f"{category_type_text} {category_name}",
            callback_data=CategoriesCallbackFactory(
                action="select",
                id=category_id,
            ),
        )
    builder.adjust(2)
    return builder


def category_types_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="💰 Доход",
        callback_data=CategoriesCallbackFactory(action="type", type="income"),
    )

    builder.button(
        text="🛒 Расход",
        callback_data=CategoriesCallbackFactory(action="type", type="income"),
    )

    builder.adjust(2)

    builder.button(
        text="↩️ Назад к списку",
        callback_data=CategoriesCallbackFactory(
            action="back_to_list",
        ),
    )

    builder.button(
        text="❌ Отмена",
        callback_data=CategoriesCallbackFactory(
            action="cancel",
        ),
    )

    builder.adjust(2,1,1)
    return builder


def category_add_keyboard():

    builder = InlineKeyboardBuilder()
    builder.button(
        text="➕ Добавить", callback_data=CategoriesCallbackFactory(action="add")
    )

    builder.button(
        text="❌ Отмена",
        callback_data=CategoriesCallbackFactory(
            action="cancel",
        ),
    )

    builder.adjust(1)

    return builder


def category_details_keyboard(category_id, category_name, category_type):
        
        builder = InlineKeyboardBuilder()
        builder.button(
                    text="🗑️ Удалить",
                    callback_data=CategoriesCallbackFactory(
                        action="delete", id=category_id
                    ),
                )

        builder.button(
                    text="✏️ Редактировать",
                    callback_data=CategoriesCallbackFactory(
                        action="edit",
                        name=category_name,
                        type=category_type,
                        id=category_id,
                    )
                )
        builder.button(
                    text="↩️ Назад к списку",
                    callback_data=CategoriesCallbackFactory(
                        action="back_to_list",
                        id=category_id,
                    )
        )

        builder.button(
                    text="❌ Отмена",
                    callback_data=CategoriesCallbackFactory(
                        action="cancel",
                    ),
                )
        
        builder.adjust(1)
        
        return builder



def category_rename_keyboard(category_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="↩️ Назад",
        callback_data=CategoriesCallbackFactory(action="edit", id=category_id),
    )

    builder.button(
        text="❌ Отмена",
        callback_data=CategoriesCallbackFactory(
            action="cancel",
        ),
    )

    builder.adjust(1)

    return builder


def category_delete_confirm_keyboard(category_id):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Да, удалить",
        callback_data=CategoriesCallbackFactory(
            action="confirm_delete", id=category_id
        ),
    )

    builder.button(
        text="❌ Нет, отмена",
        callback_data=CategoriesCallbackFactory(action="back_to_list"),
    )

    builder.adjust(1)

    return builder


def category_back_to_edit_keyboard(category_id):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="↩️ Назад",
        callback_data=CategoriesCallbackFactory(action="edit", id=category_id),
    )

    builder.button(
        text="❌ Отмена", callback_data=CategoriesCallbackFactory(action="cancel")
    )
    
    builder.adjust(1)

    return builder


def category_back_to_add_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="↩️ Назад",
        callback_data=CategoriesCallbackFactory(
            action="add",
        ),
    )

    builder.button(
        text="❌ Отмена",
        callback_data=CategoriesCallbackFactory(
            action="cancel",
        ),
    )

    builder.adjust(1)

    return builder

def category_back_to_list_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="↩️ Назад к списку",
        callback_data=CategoriesCallbackFactory(
            action="back_to_list",
        ),
    )

    builder.button(
        text="❌ Отмена",
        callback_data=CategoriesCallbackFactory(
            action="cancel",
        ),
    )

    builder.adjust(1)

    return builder


def category_edit_keyboard(category_id):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✏️ Переименовать",
                callback_data=CategoriesCallbackFactory(
                    action="change_name",
                    id=category_id
                ),
    )

    builder.button(
        text="↩️ Назад",
        callback_data=CategoriesCallbackFactory(
            action="select",
            id=category_id
        ),
    )

    builder.button(
        text="❌ Отмена",
        callback_data=CategoriesCallbackFactory(
            action="cancel",
        ),
    )

    builder.adjust(1)

    return builder


