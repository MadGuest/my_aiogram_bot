from aiogram.fsm.state import State, StatesGroup

class ActionStates(StatesGroup):
    income = State()
    outcome = State()
    transfer = State()

class PaymentStates(StatesGroup):
    name = State() # Описание/примечание
    category = State() # Категория
    due_date = State() # Дедлайн оплаты


class TransactionStates(StatesGroup):
    description = State()
    category = State()
    finish = State()