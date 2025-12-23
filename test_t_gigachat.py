import requests

def test_translation(token):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": "GigaChat",
        "messages": [{"role": "user", "content": "Привет! Расскажи, кто ты?"}],
        "temperature": 0.5
    }
    response = requests.post(url, json=payload, headers=headers, verify=False)
    print(response.json())