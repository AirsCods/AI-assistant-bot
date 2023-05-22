from bot.handlers import router
from interfaces.telegram import TelegramInterface
from interfaces.web import WebInterface
from loader import bot_core

if __name__ == "__main__":
    # инициализация интерфейсов и передача им ядра
    telegram_interface = TelegramInterface(bot_core, router)
    web_interface = WebInterface(bot_core)

    # запуск интерфейсов
    telegram_interface.start()
    web_interface.start()
