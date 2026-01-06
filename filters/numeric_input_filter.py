from aiogram.filters import BaseFilter
from aiogram.types import Message
from decimal import Decimal, InvalidOperation

class NumberFilter(BaseFilter):

    async def __call__(self, message: Message):

        try:
            number = Decimal(message.text.strip().replace(',', '.'))
            return {'number': number}
        except InvalidOperation:
            return False
        

class PositiveNumberFilter(NumberFilter):
    async def __call__(self, message: Message):
        result = await super().__call__(message)
        if result and result['number'] > 0:
            return result
        return False

class NegativeNumberFilter(NumberFilter):
    async def __call__(self, message: Message):
        result = await super().__call__(message)
        if result and result['number'] < 0:
            return result
        return False