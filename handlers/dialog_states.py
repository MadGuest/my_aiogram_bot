from aiogram.fsm.state import State, StatesGroup

class PaymentStates(StatesGroup):
    name = State() # Описание/примечание
    category = State() # Категория
    due_date = State() # Дедлайн оплаты


class TransactionStates(StatesGroup):
    name = State()
    category = State()