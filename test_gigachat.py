# test_gigachat.py
import requests
import uuid
import urllib3

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

payload = 'scope=GIGACHAT_API_PERS'
headers = {
  'Content-Type': 'application/x-www-form-urlencoded',
  'Accept': 'application/json',
  'RqUID': str(uuid.uuid4()),  # ✅ Уникальный каждый раз
  'Authorization': 'Basic MDE5YjQxZmYtNThmYS03ZjRlLWJmZDgtMjU1OTAzMjc2M2YzOjRmMWE0NWY0LTAxNmYtNDk4ZS1iZDRmLWFhNWQyMDg1YWNhYw=='
}

try:
    response = requests.post(url, headers=headers, data=payload, verify=False, timeout=10)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Ошибка: {e}")