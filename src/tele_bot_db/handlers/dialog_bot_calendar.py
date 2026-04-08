from datetime import datetime
from database.crud import Calendar

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler, 
    ContextTypes, 
    ConversationHandler, 
    MessageHandler, 
    filters
)

calendars = Calendar()

NAME, DATE, TIME, USER_DETAIL, ID_USER, UPDATE_USER, NEW_VALUE, DEL_ID_EVENT = range(8)


def validate_time(time_str: str) -> bool:
    """Проверяет, является ли строка корректным временем (ЧЧ:ММ)."""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

def validate_date(date_str: str) -> bool:
    """Проверяет, является ли строка корректной датой (ДД-ММ-ГГГГ)."""
    try:
        datetime.strptime(date_str, "%d-%m-%Y")
        return True
    except ValueError:
        return False

FIELD_CONFIG = {
    'название': {'key': 'name', 'validator': lambda x: len(x) > 0},
    'дата': {'key': 'date', 'validator': validate_date},
    'время': {'key': 'time', 'validator': validate_time},
    'описание': {'key': 'details', 'validator': lambda x: len(x) > 0},
}

async def start_create_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает процесс создания события."""
    assert update.message is not None

    await update.message.reply_text("📌 Введите название события:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получает название события от пользователя."""
    assert context.user_data is not None
    assert update.message is not None

    context.user_data['name'] = update.message.text
    await update.message.reply_text("📅 Введите дату события (ДД-ММ-ГГГГ):")
    return DATE

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем дату события от пользователя. (ДД-ММ-ГГГГ)"""
    assert update.message is not None
    assert context.user_data is not None

    date_str = update.message.text.strip() # type: ignore
    if not validate_date(date_str):
      await update.message.reply_text("⚠️ Неверный формат даты. Попробуйте ещё раз (ДД-ММ-ГГГГ).")
      return DATE

    context.user_data['date'] = date_str
    await update.message.reply_text("⏰ Введите время события (ЧЧ:ММ):")
    return TIME

async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем время (ЧЧ:ММ)"""
    assert update.message is not None
    assert context.user_data is not None
    
    time_str = update.message.text.strip() # type: ignore

    if not validate_time(time_str):
      await update.message.reply_text("⚠️ Неверный формат времени. Попробуйте ещё раз (ЧЧ:ММ).")
      return TIME

    context.user_data['time'] = time_str
    await update.message.reply_text("📝 Введите описание события:")
    return USER_DETAIL


async def get_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """"Завершает процесс создания события, сохраняя данные в базу календаря."""
    assert context.user_data is not None
    assert update.message is not None

    context.user_data['details'] = update.message.text

    # Здесь можно вызвать 
    name = context.user_data['name']
    date = context.user_data['date']
    time = context.user_data['time']
    details = context.user_data['details']

    calendars.create_event(name, date, time, details) # type: ignore

    await update.message.reply_text(
        f"Событие создано! 👍\n\n"
        f"📌 Название: {context.user_data['name']}\n\n"
        f"📅 Дата: {context.user_data['date']}\n\n"
        f"⏰ Время: {context.user_data['time']}\n\n"
        f"📝 Описание: {context.user_data['details']}"
    )
    context.user_data.clear()
    return ConversationHandler.END


async def start_get_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
   """Инициализирует процесс поиска события по ID."""
   assert update.message is not None
   await update.message.reply_text("Введите id события:")
   return ID_USER

async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # 1. Защита от None для message и user_data
    assert update.message is not None
    assert context.user_data is not None

    user_input = update.message.text
    
    try:
        event_id = int(user_input) # type: ignore
        event = calendars.get_event(event_id)
        
        if event:
            # Если событие найдено (event — это словарь)
            response_text = (
                f"✅ Событие найдено!\n\n"
                f"📌 Название: {event.get('name', 'Нет названия')}\n\n"
                f"📅 Дата: {event.get('date', 'Нет даты')}\n\n"
                f"⏰ Время: {event.get('time', 'Нет времени')}\n\n"
                f"📝 Описание: {event.get('details', 'Нет описания')}"
            )
            await update.message.reply_text(response_text)
            context.user_data.clear()
            return ConversationHandler.END
        else:
            # Если event вернул None
            await update.message.reply_text(
                f"⚠️ Событие с ID {event_id} не найдено.\n"
                f"Или введите команду для отмены /cancel"
            )
            return ID_USER
    except ValueError:
        # Если пользователь ввел не число (например, "привет")
        await update.message.reply_text(
            "❌ Пожалуйста, введите числовой ID события.\n"
            f"Или введите команду для отмены /cancel"
        )
        return ID_USER


async def start_all_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Выводит все события"""
    assert update.message is not None

    all_events = calendars.get_all_events()
    if not all_events:
        await update.message.reply_text("⚠️ Нет событий.")
    else:
      await update.message.reply_text(all_events)
    return ConversationHandler.END

async def start_update_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    assert update.message is not None
    await update.message.reply_text("Введите id события которое хотите изменить:")
    return ID_USER

async def get_update_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int: 
    """Получаем ID события для изменения"""
    assert update.message is not None
    assert context.user_data is not None

    user_input = update.message.text
    try:
      event_id = int(user_input) # type: ignore
      context.user_data['event_id'] = event_id
      event = calendars.get_event(event_id)
      if event:
          await update.message.reply_text(
              "Что изменить? Напишите: название, дата, время или описание."
          )
          return UPDATE_USER
      else:
          await update.message.reply_text(
              "⚠️ Такого ID события нет попробуйте еще. \nили введите команду для отмены /cancel"
              )
          return ID_USER
    except ValueError:
      await update.message.reply_text(
          "❌ Пожалуйста, введите числовой ID события. \nили введите команду для отмены /cancel"
          )
      return ID_USER


async def set_new_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Управляет процессом обновления поля."""
    assert update.message is not None
    assert context.user_data is not None

    text = update.message.text.strip() # type: ignore
    if not text:
        await update.message.reply_text("⚠️ Значение не может быть пустым.")
        return NEW_VALUE

    # Извлекаем данные из контекста
    event_id = context.user_data.get('event_id')
    field_to_edit = context.user_data.get('field_to_edit')

    # Проверяем, есть ли наше поле в конфигурации
    config = FIELD_CONFIG.get(field_to_edit) # type: ignore
    if not config:
        await update.message.reply_text("❌ Ошибка: Неизвестное поле для редактирования.")
        context.user_data.clear()
        return ConversationHandler.END

    # 2. Валидация
    validator = config['validator']
    if not validator(text):
        await update.message.reply_text(f"⚠️ Неверный формат для '{field_to_edit}'.")
        return NEW_VALUE

    # 3. Обновление данных
    field_key = config['key']
    # Используем распаковку словаря для передачи аргумента в update_event
    success = calendars.update_event(event_id, **{field_key: text}) # type: ignore

    if success:
        await update.message.reply_text(f"✅ Поле '{field_to_edit}' обновлено на '{text}'.")
        context.user_data.clear()
        return ConversationHandler.END
    else:
        await update.message.reply_text("⚠️ Произошла ошибка при сохранении в базе.")
        return NEW_VALUE # Возвращаем состояние, чтобы пользователь мог попробовать еще раз


async def apply_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Определяем, какое поле нужно изменить, и просим новое значение."""
    assert update.message is not None
    assert context.user_data is not None
    
    field_to_edit = update.message.text.lower() # type: ignore
    valid_fields = ['название', 'дата', 'время', 'описание']

    if field_to_edit in valid_fields:
        # Сохраняем в контекст, ЧТО мы будем менять
        context.user_data['field_to_edit'] = field_to_edit
        await update.message.reply_text(f"Введите новое значение для '{field_to_edit}':")
        # Переходим в состояние ввода нового значения
        return NEW_VALUE 
    else:
        await update.message.reply_text(
            "⚠️ Некорректный выбор. Напишите: название, дата, время или описание."
            )
        return UPDATE_USER


async def start_del_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    assert update.message is not None
    await update.message.reply_text("❌ Введите id события которое хотите удалить:")
    return DEL_ID_EVENT

async def delit_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Удаляет событие по введенному ID и сообщает о результате."""
    assert update.message is not None
    user_input = update.message.text
    try:
      event_id = int(user_input) # type: ignore
    except ValueError:
      await update.message.reply_text(
         "❌ Введите корректный числовой ID события или /cancel для отмены."
        )
      return DEL_ID_EVENT

    # Попытка удаления и проверка результата
    success = calendars.delete_event(event_id)
    if success:
        await update.message.reply_text(f"✅ Событие с ID {event_id} успешно удалено.")
        context.user_data.clear() # type: ignore
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            f"⚠️ Событие с ID {event_id} не найдено. Попробуйте другой ID или /cancel."
        )
        return DEL_ID_EVENT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменяет действие."""
    assert update.message is not None

    if context.user_data is not None: 
      context.user_data.clear()
    await update.message.reply_text("✅ Действие отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Настройка ConversationHandler
create_event_handler = ConversationHandler(
    entry_points=[CommandHandler('create_event', start_create_event)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_date)],
        TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
        USER_DETAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_details)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)


get_event_handler = ConversationHandler(
    entry_points=[CommandHandler('get_event', start_get_event)],
    states={
        ID_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_user_id)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

get_all_event_handler = ConversationHandler(
    entry_points=[CommandHandler('all_event', start_all_event)],
    states={
        ...: [],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

update_event_handler = ConversationHandler(
    entry_points=[CommandHandler('update_event', start_update_event)],
    states={
        ID_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_update_event)],
        UPDATE_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, apply_edit)],
        NEW_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_new_value)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

del_event_handler = ConversationHandler(
    entry_points=[CommandHandler('del_event', start_del_event)],
    states={
        DEL_ID_EVENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, delit_event)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)