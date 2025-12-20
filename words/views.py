### words/views.py
import io
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.shortcuts import get_object_or_404
from io import BytesIO
import logging
from .models import Word
from django.urls import reverse_lazy
from gtts import gTTS
from django.http import HttpResponse
from django.shortcuts import render
import random
from .models import Word
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from vocab.gigachat_translate import gigachat_translate
import logging
from vocab.models import TelegramUser

def register_user(request):
    if request.method == 'POST':
        telegram_id = request.POST.get('telegram_id')
        username = request.POST.get('username')

        user, created = TelegramUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={'username': username}
        )

        if created:
            return JsonResponse({'status': 'created'})
        else:
            return JsonResponse({'status': 'exists'})
    return JsonResponse({'error': 'Invalid method'}, status=405)


def test_view(request):
    words = Word.objects.all()
    if words.exists():
        word = random.choice(words)
        return render(request, 'test_page.html', {'word': word.text})
    else:
        return render(request, 'test_page.html', {'message': 'No words available. Please add words first.'})





class RegisterUser(APIView):
    def post(self, request):
        telegram_id = request.data.get('telegram_id')
        username = request.data.get('username')

        user, created = TelegramUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={'username': username}
        )

        if created:
            return Response({'status': 'created'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'exists'}, status=status.HTTP_200_OK)


def home(request):
    return render(request, 'words/home.html')


# --- CRUD ---
class WordListView(ListView):
    model = Word
    template_name = 'word_list.html'
    context_object_name = 'words'


class WordDetailView(DetailView):
    model = Word
    template_name = 'word_detail.html'


class WordCreateView(CreateView):
    model = Word
    fields = ['text', 'translation']
    template_name = 'word_form.html'
    success_url = reverse_lazy('word-list')
    
    def form_valid(self, form):
        # Получаем или создаем тестового пользователя
        from vocab.models import TelegramUser
        test_user, created = TelegramUser.objects.get_or_create(
            telegram_id=12345,  # Тестовый ID
            defaults={'username': 'test_user'}
        )
        form.instance.user = test_user
        
        # Переводим автоматически, если перевод пустой
        if not form.instance.translation and form.instance.text:
            try:
                form.instance.translation = gigachat_translate(
                    form.instance.text,
                    src="en",
                    dest="ru",
                )
            except Exception:
                pass




@csrf_exempt
def translate_word(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    text = data.get('text', '').strip()
    if not text:
        return JsonResponse({'error': 'Text is required'}, status=400)

    def has_cyrillic(t):
        return any('а' <= c.lower() <= 'я' or c.lower() == 'ё' for c in t)

    def has_latin(t):
        return any('a' <= c.lower() <= 'z' for c in t)

    is_cyrillic = has_cyrillic(text)
    is_latin = has_latin(text)

    if is_cyrillic and not is_latin:
        src, dest = 'ru', 'en'
    elif is_latin and not is_cyrillic:
        src, dest = 'en', 'ru'
    else:
        src, dest = 'en', 'ru'

    try:
        translated = gigachat_translate(text, src=src, dest=dest)
    except Exception as e:
        logger.exception("GigaChat translate failed")
        return JsonResponse({'error': f'Translation failed: {e}'}, status=500)

    return JsonResponse({
        'translation': translated,
        'source_lang': src,
        'dest_lang': dest,
    })




def generate_audio(request, pk, text_type='word'):
    word = get_object_or_404(Word, pk=pk)

    # Выбираем текст
    if text_type == 'word':
        text = word.text
    else:
        text = word.translation

    text = text.strip()
    if not text:
        return HttpResponse("Пустой текст", status=400)

    # Определяем язык
    def detect_language(text):
        text = text.lower()
        if any('а' <= c <= 'я' or c == 'ё' for c in text):
            return 'ru'
        if any('a' <= c <= 'z' for c in text):
            return 'en'
        return 'en'

    lang = detect_language(text)

    try:
        tts = gTTS(text=text, lang=lang)
        audio_io = BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)

        response = HttpResponse(audio_io.read(), content_type='audio/mpeg')
        response['Content-Disposition'] = f'inline; filename="{text_type}.mp3"'
        return response
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return HttpResponse(f"Ошибка TTS: {e}", status=500)



def speak_text(request):
    """
    Озвучивает любой текст (для формы добавления слова)
    Пример: /words/speak/?text=hello&lang=en
    """
    text = request.GET.get('text', '').strip()
    lang = request.GET.get('lang', 'en')  # по умолчанию английский

    if not text:
        return HttpResponse(status=400)

    # Определяем язык по тексту, если не указан
    if lang == 'auto':
        lang = 'ru' if any('а' <= c.lower() <= 'я' or c.lower() == 'ё' for c in text) else 'en'

    try:
        # Создаём аудио
        tts = gTTS(text=text, lang=lang)
        audio_io = io.BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)

        # Отправляем как MP3
        response = HttpResponse(audio_io, content_type='audio/mpeg')
        response['Content-Disposition'] = 'inline'
        return response
    except Exception as e:
        print(f"Ошибка TTS: {e}")
        return HttpResponse(status=500)


