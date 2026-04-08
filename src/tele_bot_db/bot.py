import logging
from handlers import HANDLERS
from telegram.ext import ApplicationBuilder
from config import AppSettings


class BotApplication:
    """
    Класс-обёртка для управления Telegram-ботом.
    Использует композицию (содержит объект приложения), а не наследование.
    """
    def __init__(self, app_settings: AppSettings):
        """Инициализирует бота, создает объект Application и регистрирует хендлеры."""
        self._settings = app_settings
        self.app = self._create_application()
        self._register_handlers()

    def _create_application(self):
        """Создает и настраивает объект Application."""
        logging.info("Инициализация Application...")
        return ApplicationBuilder().token(
            self._settings.TELEGRAM_BOT_TOKEN.get_secret_value()
        ).connect_timeout(30).read_timeout(30).build()

    def _register_handlers(self):
        """Регистрирует все обработчики из списка HANDLERS."""
        logging.info("Регистрация обработчиков...")
        for handler in HANDLERS:
            self.app.add_handler(handler)

    def run(self):
        """Запускает бесконечный цикл получения обновлений (polling)."""
        logging.info("Бот запущен. Начинаю опрос Telegram...")
        self.app.run_polling()

def configure_logging():
  # Настройка логирования 
  logging.basicConfig(
      format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
      level=logging.INFO
      )
  logging.getLogger("httpx").setLevel(logging.WARNING)

def create_app(app_settings: AppSettings) -> BotApplication:
    """Функция для создания экземпляра приложения."""
    application = BotApplication(app_settings)
    return application

if __name__ == '__main__':
    configure_logging()
    # Загружаем настройки из .env файла
    settings = AppSettings()

    bot_app = create_app(settings)

    # Запускаем бота
    bot_app.run()