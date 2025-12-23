# test_token.py
import os
import sys
import django
import uuid
import requests
import urllib3
from django.conf import settings

# Добавляем путь к проекту, чтобы Django мог найти settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Указываем, где лежат настройки Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vocab.settings")

# Инициализируем Django
django.setup()

# Отключаем предупреждения о SSL (разработка)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === Получаем AUTH_KEY из настроек ===
AUTH_KEY = settings.GIGACHAT_AUTH_KEY

# === URL для получения токена ===
url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

# === Заголовки запроса ===
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'Authorization': f'Basic {AUTH_KEY}',
    'RqUID': str(uuid.uuid4()),  # уникальный ID для каждого запроса
}

# === Тело запроса ===
data = {
    'scope': 'GIGACHAT_API_PERS'
}

# === Отправляем запрос ===
try:
    response = requests.post(url, headers=headers, data=data, verify=False, timeout=10)

    # Проверяем ответ
    if response.status_code == 200:
        token_data = response.json()
        print("✅ УСПЕХ! Токен получен:")
        # берём значения с безопасной проверкой ключей
        access_token = token_data.get('access_token')
        expires_at = token_data.get('expires_at')
        if access_token:
            print(f"Access Token: {access_token}")
        else:
            print("Нет access_token в ответе.")

        if expires_at:
            print(f"Действует до: {expires_at}")
        else:
            print("Нет expires_at в ответе.")
    else:
        print(f"❌ Ошибка {response.status_code}:")
        print(response.text)
except Exception as e:
    print(f"🚨 Ошибка при выполнении запроса: {e}")