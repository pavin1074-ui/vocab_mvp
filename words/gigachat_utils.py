# words/gigachat_utils.py
import requests
import urllib3
import uuid
import time
from django.conf import settings

# Отключаем предупреждения SSL (только для разработки)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GigaChatClient:
    def __init__(self):
        """Инициализация клиента"""
        self.access_token = None
        self.token_expires_at = 0  # время истечения в миллисекундах

    def _get_token(self):
        """Получает новый access_token"""
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        auth_key = settings.GIGACHAT_AUTH_KEY  # из .env

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': str(uuid.uuid4()),
            'Authorization': f'Basic {auth_key}'
        }
        payload = 'scope=GIGACHAT_API_PERS'

        try:
            response = requests.post(
                url,
                headers=headers,
                data=payload,
                verify=False,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data['access_token']
                self.token_expires_at = data['expires_at']  # в миллисекундах
                return self.access_token
            else:
                raise Exception(f"Auth failed: {response.status_code}, {response.text}")
        except Exception as e:
            raise Exception(f"Request error: {e}")

    def get_access_token(self):
        """Возвращает валидный токен (если просрочен — обновляет)"""
        current_time_ms = int(time.time() * 1000)
        if not self.access_token or current_time_ms >= self.token_expires_at:
            print("🔄 Обновляем access_token...")
            return self._get_token()
        return self.access_token


# Глобальный экземпляр клиента
client = GigaChatClient()