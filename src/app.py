import asyncio

from loguru import logger

from bot.handlers.chat import router
from bot.loader import bot, llm, dp, user_storage, prompt_storage
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup():
    await llm.start_agent()
    await bot.delete_webhook()
    dp.include_router(router)
    await on_startup_notify(bot)


async def on_shutdown():
    await user_storage.close()
    await prompt_storage.close()


async def main():
    try:
        logger.info('------------Start polling.-------------')
        await on_startup()
        await set_default_commands(bot)
        await dp.start_polling(bot, close_bot_session=True)

    except Exception as err:
        logger.error(f'-----------Общая ошибка:---------\n{err}')

    finally:
        await on_shutdown()
        logger.info('App was closed.')


if __name__ == "__main__":
    logger.info('App was started.')
    asyncio.run(main())
