# Обработчик диалога добавления платежа

import asyncio
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from pydantic import BaseModel
from typing import Optional
from utils.single_message_dialog import SingleMessageDialog



class PaymentData(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[str] = None
    due_date: Optional[str] = None

    def format_message(self, next_prompt: str = None) -> str:
            """Форматирует сообщение для диалога"""
            lines = [
                f'🧾 <b>{"Новый платеж" if next_prompt else "Добавлен платеж"}</b>',
                f'Название: {self.name or "—"}',
                f'Категория: {self.category or "—"}',
                f'Сумма: {self.amount or "—"}',
                f'Дата: {self.due_date or "—"}',
            ]
            if next_prompt:
                lines.append(f'\n💬 {next_prompt}')
            return '\n'.join(lines)
    
    def to_db_dict(self) -> dict:
        """Конвертация для сохранения в БД"""
        return {
            'name': self.name,
            'category': self.category,
            'amount': self.amount,
            'due_date': self.due_date,
        }



# Состояния для добавления платежа
class PaymentStates(StatesGroup):
    name = State()
    category = State()
    amount = State()
    due_date = State()
    finish = State()


add_payment_router = Router()

smd = SingleMessageDialog()

# В том же файле можно добавить эту фабрику
def process_next_step(field_name: str, next_state: State, next_prompt: str):
    """Фабрика для создания обработчиков платежей"""
    async def handler(message: types.Message, state: FSMContext):
        data = await state.get_data()
        payment = PaymentData(**data.get('payment', {}))
        
        # Обновляем поле
        setattr(payment, field_name, message.text)
        
        # Формируем сообщение
        content = payment.format_message(next_prompt)
        
        # Сохраняем и переходим
        await state.update_data(payment=payment.model_dump())
        await smd.next_step(message, state, text=content)
        await state.set_state(next_state)
    
    return handler

def process_last_step(field_name: str):
    async def handler(message: types.Message, state: FSMContext):
        # Получаем и обновляем данные
        data = await state.get_data()
        payment = PaymentData(**data.get('payment', {}))
        setattr(payment, field_name, message.text)
        
        # Формируем финальное сообщение
        content = payment.format_message()  # без next_prompt
        
        # Завершаем диалог
        await smd.last_step(message, state, content)
        
        # Здесь можно сохранить в БД
        # db_payment = payment.to_db_dict()
        # await save_to_database(db_payment)
        
        await asyncio.sleep(0.1)
        await state.clear()
    
    return handler

@add_payment_router.message(Command("add_payment"))
async def add_payment_handler(message: types.Message, state: FSMContext):
    """Начало диалога добавления платежа"""
    payment = PaymentData()
    content = payment.format_message("Введите название платежа")
    
    await smd.initial_message(message, state, text=content)
    await state.update_data(payment=payment.model_dump())
    await state.set_state(PaymentStates.name)

# Тогда регистрация хэндлеров становится очень компактной:
add_payment_router.message(PaymentStates.name)(
    process_next_step('name', PaymentStates.category, 'Введите категорию')
)

add_payment_router.message(PaymentStates.category)(
    process_next_step('category', PaymentStates.amount, 'Введите сумму')
)

add_payment_router.message(PaymentStates.amount)(
    process_next_step('amount', PaymentStates.due_date, 'Введите дату')
)

add_payment_router.message(PaymentStates.due_date)(
    process_last_step('due_date')
)