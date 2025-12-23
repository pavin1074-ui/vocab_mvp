# words/gigachat_client.py

import time
import uuid
import requests
import urllib3
from django.conf import settings

# Отключаем предупреждения SSL (только для разработки)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GigaChatClient:
    def __init__(self) -> None:
        self.access_token: str | None = None
        self.token_expires_at: int = 0  # хранится в миллисекундах

    def _get_token(self) -> str:
        """Получает новый access_token"""
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        auth_key = settings.GIGACHAT_AUTH_KEY

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': f'Basic {auth_key}',
            'RqUID': str(uuid.uuid4()),
        }
        data = {'scope': 'GIGACHAT_API_PERS'}

        response = requests.post(
            url,
            headers=headers,
            data=data,
            verify=False,
            timeout=10
        )

        if response.status_code == 200:
            payload = response.json()
            self.access_token = payload.get('access_token')
            self.token_expires_at = payload.get('expires_at', 0)
            if not self.access_token:
                raise Exception("❌ access_token отсутствует в ответе сервера")
            return self.access_token
        else:
            raise Exception(f"❌ Ошибка авторизации: {response.status_code}, {response.text}")

    def get_access_token(self) -> str:
        """Возвращает актуальный токен (если срок истёк — обновляет)"""
        current_time_ms = int(time.time() * 1000)
        if not self.access_token or current_time_ms >= self.token_expires_at:
            print("🔄 Обновляем access_token...")
            return self._get_token()
        return self.access_token


# Глобальный клиент
client = GigaChatClient()

# Пример использования (раскомментируйте и используйте в вашем окружении)
# try:
#     token = client.get_access_token()
#     print("Token:", token)
# except Exception as e:
#     print("Ошибка:", e)