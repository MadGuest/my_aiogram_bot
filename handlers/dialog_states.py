from aiogram.fsm.state import State, StatesGroup

class PaymentStates(StatesGroup):
    name = State()
    category = State()
    due_date = State()
    finish = State()