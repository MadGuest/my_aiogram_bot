import asyncio
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

class SingleMessageDialog:
    '''
    Организует диалог с юзером в одном единственном сообщении    
    '''
    
    @staticmethod
    async def initial_message(message: Message,
                              state: FSMContext,
                              text: str="",
                              reply_markup: InlineKeyboardMarkup | None=None
                              ) -> None:
        dialog_bot=message.bot

        # if isinstance(message, Message) and message.text:
        try:
            await message.delete()
        except:
            pass
        
        bot_message = await message.answer(text, reply_markup=reply_markup)
        await state.update_data(
            prev_message_id = bot_message.message_id,
            dialog_bot=message.bot)

    @staticmethod
    async def next_step(update: Message|CallbackQuery,
                        state: FSMContext,
                        text: str,
                        reply_markup: InlineKeyboardMarkup | None=None
                        ) -> None:
        data = await state.get_data()
        dialog_bot = data.get("dialog_bot")
        prev_message_id = data.get("prev_message_id")

        if isinstance(update, Message) and update.text:
            try:
                await update.delete()
            except:
                pass

        if prev_message_id and update.chat and update.chat.id:
            try:
                await dialog_bot.edit_message_text(
                    text=text,
                    chat_id=update.chat.id,
                    message_id=prev_message_id,
                    reply_markup=reply_markup
                )
            except:
                bot_message = await update.message.reply(text,
                                                         reply_markup=reply_markup
                                                         )
                await state.update_data(prev_message_id=bot_message.message_id)

    @staticmethod
    async def last_step(update: Message|CallbackQuery,
                        state: FSMContext,
                        text: str,
                        reply_markup: InlineKeyboardMarkup | None=None
                        ) -> None:
        data = await state.get_data()
        dialog_bot = data.get("dialog_bot")
        prev_message_id = data.get("prev_message_id")

        if isinstance(update, Message):
            try:
                await update.delete()
            except:
                pass

        chat_id = update.chat.id

        if prev_message_id:
            try:
                await dialog_bot.edit_message_text(
                    text=text, 
                    chat_id=chat_id,
                    message_id=prev_message_id,
                    reply_markup=reply_markup
                )
                return
            except:
                try:
                    await dialog_bot.delete_message(chat_id, prev_message_id)
                except:
                    pass

            await dialog_bot.send_message(chat_id, text, reply_markup=reply_markup)
    




        

