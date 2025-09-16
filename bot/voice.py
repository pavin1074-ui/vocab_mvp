# bot/voice.py
import tempfile
from gtts import gTTS

def synthesize_text_to_mp3(text: str, lang: str = 'en') -> str:
    """
    Генерирует MP3-файл озвучки текста и возвращает путь к файлу.
    Файл создаётся в системе временных файлов и должен быть удалён после отправки.
    Прямой асинхронности здесь нет; обработчик может запустить в пуле потоков.
    """
    # Используем NamedTemporaryFile без удалении сразу, чтобы можно было открыть повторно
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
        tts = gTTS(text=text, lang=lang)
        tts.save(tf.name)
        return tf.name


def synthesize_text_to_mp3_advanced(text: str, lang: str = 'en', tld: str = 'com', slow: bool = False) -> str:
    """
    Расширенная функция для генерации аудио с выбором голоса.
    
    Args:
        text: Текст для озвучивания
        lang: Язык (по умолчанию 'en')
        tld: Домен для разных акцентов ('com', 'co.uk', 'com.au', 'ca', 'co.in')
        slow: Медленное воспроизведение
    
    Returns:
        Путь к MP3 файлу
    """
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
        tts = gTTS(text=text, lang=lang, tld=tld, slow=slow)
        tts.save(tf.name)
        return tf.name


# Доступные голоса и акценты
VOICE_OPTIONS = {
    'en': {
        'com': 'English (US)',
        'co.uk': 'English (UK)',
        'com.au': 'English (Australia)',
        'ca': 'English (Canada)',
        'co.in': 'English (India)'
    },
    'ru': {
        'com': 'Russian'
    },
    'es': {
        'com': 'Spanish (Spain)',
        'com.mx': 'Spanish (Mexico)'
    },
    'fr': {
        'com': 'French (France)',
        'ca': 'French (Canada)'
    },
    'de': {
        'com': 'German'
    },
    'it': {
        'com': 'Italian'
    }
}


def get_available_voices():
    """Возвращает список доступных голосов"""
    return VOICE_OPTIONS

