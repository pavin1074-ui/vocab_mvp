#!/usr/bin/env python3
"""
Запуск Telegram бота для изучения словаря
"""

import asyncio
import logging
import sys
import os
from telegram_bot import bot, dp

# Настройка логирования без эмодзи
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота"""
    try:
        logger.info("Запуск VocabBot...")
        
        # Проверяем наличие токена
        if not os.getenv("BOT_TOKEN"):
            logger.error("Ошибка: BOT_TOKEN не найден в .env файле")
            return
            
        # Пробуем подключиться к API
        logger.info("Проверка подключения к Telegram API...")
        
        try:
            # Простое получение инфо о боте
            bot_info = await bot.get_me()
            logger.info(f"Подключен к боту: @{bot_info.username}")
        except Exception as conn_error:
            logger.error(f"Не удалось подключиться к Telegram API: {conn_error}")
            logger.error("Проверьте интернет-соединение и токен")
            return
        
        # Запускаем polling
        logger.info("Бот запущен и работает!")
        await dp.start_polling(bot, skip_updates=True)
        
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        try:
            await bot.session.close()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())