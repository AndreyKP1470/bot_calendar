from telegram import Update
from telegram.ext import ContextTypes

# --- Простые обработчики команд ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    user = update.effective_user
    user_id = user.id
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Добро пожаловать! {user.first_name} Я помогу вам вести заметки.\n/help - список команд"
    )

async def command_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    commands = """Доступные команды:
/start - начать работу с ботом
/help - показать это меню
/cancel - отменить текущее действие
/create_event - добавить событие
/get_event - показать событие
/update_event - изменить событие
/del_event - удалить событие
/all_event - показать все события"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=commands
    )

# echo_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, start)