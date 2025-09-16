#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест API перевода
"""

import os
import sys
import django
import json

# Настройка Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vocab.settings")

# Добавляем корневую директорию в PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

django.setup()

from django.http import HttpRequest
from words.views import translate_word

def test_translation_api():
    print("🔄 Тестируем API перевода...")
    
    # Тест 1: Русское слово
    print("\n📝 Тест 1: Русское слово 'продажа'")
    req = HttpRequest()
    req.method = 'POST'
    req._body = json.dumps({'text': 'продажа'}).encode('utf-8')
    
    try:
        result = translate_word(req)
        response_data = json.loads(result.content.decode('utf-8'))
        print(f"✅ Статус: {result.status_code}")
        print(f"✅ Ответ: {response_data}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 2: Слово покупка
    print("\n📝 Тест 2: Русское слово 'покупка'")
    req2 = HttpRequest()
    req2.method = 'POST'
    req2._body = json.dumps({'text': 'покупка'}).encode('utf-8')
    
    try:
        result2 = translate_word(req2)
        response_data2 = json.loads(result2.content.decode('utf-8'))
        print(f"✅ Статус: {result2.status_code}")
        print(f"✅ Ответ: {response_data2}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 3: Английское слово
    print("\n📝 Тест 3: Английское слово 'hello'")
    req3 = HttpRequest()
    req3.method = 'POST'
    req3._body = json.dumps({'text': 'hello'}).encode('utf-8')
    
    try:
        result3 = translate_word(req3)
        response_data3 = json.loads(result3.content.decode('utf-8'))
        print(f"✅ Статус: {result3.status_code}")
        print(f"✅ Ответ: {response_data3}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 4: Прямая проверка Google Translate
    print("\n📝 Тест 4: Прямая проверка Google Translate")
    try:
        from googletrans import Translator
        translator = Translator()
        
        result = translator.translate('продажа', src='ru', dest='en')
        print(f"✅ 'продажа' -> '{result.text}' (RU->EN)")
        
        result2 = translator.translate('покупка', src='ru', dest='en')
        print(f"✅ 'покупка' -> '{result2.text}' (RU->EN)")
        
        result3 = translator.translate('покупка', src='auto', dest='en')
        print(f"✅ 'покупка' -> '{result3.text}' (AUTO->EN)")
        
    except Exception as e:
        print(f"❌ Ошибка Google Translate: {e}")

if __name__ == "__main__":
    test_translation_api()