# test_giga.py
from vocab.gigachat_translate import get_gigachat_access_token, gigachat_translate

try:
    token = get_gigachat_access_token()
    print("✅ Токен получен:", token[:50] + "...")
except Exception as e:
    print("❌ Ошибка токена:", e)

try:
    translation = gigachat_translate("hello", src="en", dest="ru")
    print("✅ Перевод:", translation)
except Exception as e:
    print("❌ Ошибка перевода:", e)