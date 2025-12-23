###vocab_mvp/vocab/gigachat_translate
# vocab/gigachat_translate.py

import os
import requests
import logging
import uuid
import time
from dotenv import load_dotenv

# Настройки логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

# Заголовки и URL
GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
GIGACHAT_TOKEN_URL = "https://ngw.devices.sberbank.ru/api/v2/oauth"  # Правильный URL

# Получаем ключ авторизации
GIGACHAT_AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")  # из .env

# Кэш токена
_token_cache = None
_token_expires_at = 0  # время истечения в миллисекундах


def get_gigachat_access_token() -> str:
    """Возвращает валидный access_token. Если токен отсутствует или просрочен — запрашивает новый."""
    global _token_cache, _token_expires_at

    current_time_ms = int(time.time() * 1000)
    if _token_cache and current_time_ms < _token_expires_at:
        return _token_cache

    # Генерируем уникальный RqUID
    headers = {
        "Authorization": f"Basic {GIGACHAT_AUTH_KEY}",
        "Content-Type": "application/x-www-form-urlencoded",
        "RqUID": str(uuid.uuid4()),
        "Accept": "application/json"
    }
    data = {"scope": "GIGACHAT_API_PERS"}

    try:
        response = requests.post(
            GIGACHAT_TOKEN_URL,
            headers=headers,
            data=data,
            verify=False,  # Отключаем проверку SSL (только для разработки)
            timeout=10
        )
        response.raise_for_status()
        payload = response.json()
        _token_cache = payload.get("access_token")
        _token_expires_at = payload.get("expires_at", 0)
        if not _token_cache:
            raise ValueError("access_token отсутствует в ответе сервера")

        logger.info("✅ Новый access_token получен")
        return _token_cache
    except Exception as e:
        logger.error(f"❌ Ошибка получения access_token: {e}")
        raise


def gigachat_translate(text: str, src: str = 'en', dest: str = 'ru') -> str:
    """Переводит текст с помощью GigaChat. src, dest — 'en', 'ru' и т.п."""
    logger.info(f"Перевод: '{text}' с {src} на {dest}")

    system_prompt = (
        "Ты переводчик. Переводи кратко и точно, без пояснений и лишних слов. "
        f"Исходный язык: {src}, целевой язык: {dest}."
    )

    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        "temperature": 0.1,
        "max_tokens": 256,
    }

    try:
        token = get_gigachat_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            GIGACHAT_API_URL,
            headers=headers,
            json=payload,
            verify=False,  # Отключаем SSL (только для разработки)
            timeout=20
        )
        response.raise_for_status()
        result = response.json()
        # Обработка возможных структур ответа
        translation = None
        try:
            translation = result["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError):
            # Попытка альтернативного формата, если API вернул данные в другом виде
            translation = result.get("translation") or result.get("text") or ""
        if not translation:
            raise ValueError("Не удалось извлечь перевод из ответа сервера")
        return translation
    except Exception as e:
        logger.error(f"❌ Ошибка перевода: {e}")
        raise


if __name__ == "__main__":
    # Пример использования
    sample_text = "Hello, world!"
    try:
        translated = gigachat_translate(sample_text, src='en', dest='ru')
        print("Перевод:", translated)
    except Exception as e:
        print("Ошибка выполнения:", e)