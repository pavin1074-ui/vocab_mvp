#bot/utilis.py
import requests

def register_user(telegram_id, username):
    r = requests.post(
        f'{DJANGO_API_URL}register/',
        json={'telegram_id': telegram_id, 'username': username}
    )
    return r
