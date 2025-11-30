#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки функциональности проекта Vocab MVP
"""

import os
import sys
import django
from datetime import datetime

# Настройка Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vocab.settings")

# Добавляем корневую директорию в PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

django.setup()

def test_translation():
    """Тестируем переводчик"""
    print("\n🔄 Тестируем переводчик...")
    try:
        from googletrans import Translator
        translator = Translator()
        
        # Тест 1: EN -> RU
        result = translator.translate('hello', src='en', dest='ru')
        print(f"✅ EN->RU: 'hello' -> '{result.text}'")
        
        # Тест 2: RU -> EN
        result = translator.translate('привет', src='ru', dest='en')
        print(f"✅ RU->EN: 'привет' -> '{result.text}'")
        
        print("✅ Переводчик работает корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка переводчика: {e}")
        return False

def test_tts():
    """Тестируем синтез речи"""
    print("\n🔊 Тестируем TTS...")
    try:
        from bot.voice import synthesize_text_to_mp3, get_available_voices
        
        # Тест генерации аудио
        audio_path = synthesize_text_to_mp3("hello", lang='en')
        if os.path.exists(audio_path):
            print(f"✅ Аудио файл создан: {audio_path}")
            os.remove(audio_path)  # Удаляем тестовый файл
            print("✅ Тестовый файл удален")
        else:
            print("❌ Аудио файл не создан")
            return False
            
        # Тест доступных голосов
        voices = get_available_voices()
        print(f"✅ Доступные голоса: {len(voices)} языков")
        
        print("✅ TTS работает корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка TTS: {e}")
        return False

def test_database():
    """Тестируем базу данных"""
    print("\n🗄️ Тестируем базу данных...")
    try:
        from vocab.models import TelegramUser
        from words.models import Word
        from django.utils import timezone
        
        # Создаем тестового пользователя
        test_user, created = TelegramUser.objects.get_or_create(
            telegram_id=999999,
            defaults={'username': 'test_user'}
        )
        
        if created:
            print("✅ Тестовый пользователь создан")
        else:
            print("✅ Тестовый пользователь найден")
        
        # Создаем тестовое слово
        test_word, created = Word.objects.get_or_create(
            user=test_user,
            text='test',
            defaults={
                'translation': 'тест',
                'next_review': timezone.now()
            }
        )
        
        if created:
            print("✅ Тестовое слово создано")
        else:
            print("✅ Тестовое слово найдено")
            
        # Проверяем количество слов у пользователя
        word_count = Word.objects.filter(user=test_user).count()
        print(f"✅ Слов у пользователя: {word_count}")
        
        print("✅ База данных работает корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False

def test_bot_imports():
    """Тестируем импорты бота"""
    print("\n🤖 Тестируем импорты бота...")
    try:
        import bot.telegram_bot
        print("✅ Telegram бот импортируется успешно")
        
        # Проверяем, что все нужные компоненты импортированы
        from bot.telegram_bot import main_menu_kb, translator
        print("✅ Компоненты бота загружены")
        
        print("✅ Бот готов к запуску!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта бота: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🎯 Vocab MVP - Комплексное тестирование")
    print("=" * 50)
    
    tests = [
        ("Переводчик", test_translation),
        ("Синтез речи", test_tts), 
        ("База данных", test_database),
        ("Telegram бот", test_bot_imports)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОШЕЛ" if result else "❌ ПРОВАЛИЛСЯ"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"🎯 ИТОГ: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ! Проект готов к использованию!")
        print("\n📋 Инструкции по запуску:")
        print("1. Веб-сервер: python manage.py runserver")
        print("2. Telegram бот: python bot\\telegram_bot.py")
        print("3. Откройте http://127.0.0.1:8000/ в браузере")
    else:
        print(f"⚠️ {total - passed} тест(ов) провалились. Проверьте ошибки выше.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)