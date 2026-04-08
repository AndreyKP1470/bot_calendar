from telegram.ext import BaseHandler, CommandHandler

from handlers.commands import  start, command_help
from handlers.dialog_bot_calendar import create_event_handler, get_event_handler, update_event_handler, del_event_handler, get_all_event_handler
# Определение кортежа с обработчиками
# Тип tuple[BaseHandler, ...] указывает, что это кортеж из одного или более BaseHandler
HANDLERS: tuple[BaseHandler, ...] = (
    CommandHandler("start", start),
    CommandHandler("help", command_help),
    # calendar
    create_event_handler,
    get_event_handler,
    update_event_handler,
    del_event_handler,
    get_all_event_handler
)