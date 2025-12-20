###vocab_mvp/vocab/gigachat_translate
import os
import requests
import logging

GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
GIGACHAT_TOKEN_URL = "https://gigachat.devices.sberbank.ru/api/v1/oauth/token"

GIGACHAT_AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")  # ключ авторизации из ЛК Сбера

_token_cache = None

logger = logging.getLogger(__name__)

def get_gigachat_access_token():
    global _token_cache
    if _token_cache:
        return _token_cache

    headers = {
        "Authorization": f"Basic {GIGACHAT_AUTH_KEY}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"scope": "GIGACHAT_API_PERS"}
    resp = requests.post(GIGACHAT_TOKEN_URL, headers=headers, data=data, timeout=10)
    resp.raise_for_status()
    access_token = resp.json()["access_token"]
    _token_cache = access_token
    return access_token


def gigachat_translate(text, src='en', dest='ru'):
    logger.info(f"Translating: '{text}' from {src} to {dest}")
    """
    Простейший перевод через GigaChat:
    src, dest — 'en' / 'ru'
    """
    system_prompt = (
        "Ты переводчик. Переводи кратко и точно без пояснений. "
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

    token = get_gigachat_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(GIGACHAT_API_URL, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"GigaChat error: {e}")
        raise  # Чтобы падение было видно
