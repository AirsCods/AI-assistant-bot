from bot.loader import bot
from bot.handlers import dp
from interfaces.telegram import TelegramInterface

if __name__ == "__main__":
    # инициализация интерфейсов и передача им ядра
    telegram_interface = TelegramInterface(bot=bot, dp=dp)
    # web_interface = WebInterface(bot_core)

    # запуск интерфейсов
    telegram_interface.start()
    # web_interface.start()
