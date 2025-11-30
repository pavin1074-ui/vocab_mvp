# vocab/views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse
from .models import TelegramUser, Card, Repetition, UserSettings
from words.models import Word
from .serializers import TelegramUserSerializer, CardSerializer
from gtts import gTTS
from random import choice
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
import logging
from io import BytesIO
import re

# Настройка логирования

logger = logging.getLogger(__name__)

# === ОСНОВНОЙ ВЬЮХА ТЕСТА ===
def test_view(request):
    """Страница теста - показывает случайное слово и проверяет ответ"""
    words = Word.objects.all()
    if not words.exists():
        return render(request, 'test_page.html', {
            'message': 'Нет доступных слов для тестирования.'
        })

    if request.method == 'POST':
        word_id = request.POST.get('word_id')
        user_translation = request.POST.get('translation', '').strip().lower()

        # Очищаем от лишнего: пробелы, регистр, пунктуация
        user_translation = re.sub(r'[^\w\s]', '', user_translation).strip().lower()

        try:
            word = Word.objects.get(pk=word_id)
            correct_translation = word.translation.strip().lower()
            is_correct = user_translation == correct_translation

            # Новое случайное слово для следующего теста
            next_word = choice(list(words))

            return render(request, 'test_page.html', {
                'word': next_word,
                'result': 'correct' if is_correct else 'incorrect',
                'previous_word': word.text,
                'correct_translation': word.translation,
                'user_translation': request.POST.get('translation', '').strip()
            })
        except Word.DoesNotExist:
            logger.error(f"Word with id {word_id} does not exist")
            return render(request, 'test_page.html', {
                'word': choice(list(words)),
                'error': 'Слово не найдено.'
            })

    # GET-запрос — показываем случайное слово
    word = choice(list(words))
    return render(request, 'test_page.html', {'word': word})



@api_view(['POST'])
def register_user(request):
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



class RegisterTelegramUser(APIView):
    def post(self, request):
        telegram_id = request.data.get('telegram_id')
        username = request.data.get('username', '')
        if not telegram_id:
            return Response({'error': 'telegram_id required'}, status=400)
        user, created = TelegramUser.objects.get_or_create(telegram_id=telegram_id)
        user.username = username
        user.save()
        return Response({'status': 'OK'}, status=201 if created else 200)

class CardListCreateView(generics.ListCreateAPIView):
    serializer_class = CardSerializer

    def get_queryset(self):
        telegram_id = self.request.query_params.get('telegram_id')
        return Card.objects.filter(owner__telegram_id=telegram_id)

    def perform_create(self, serializer):
        telegram_id = self.request.data.get('telegram_id')
        owner = TelegramUser.objects.get(telegram_id=telegram_id)
        serializer.save(owner=owner)




#@login_required
def review_view(request):
    """
    Просмотр слов для повторения (алгоритм SM-2)
    """
    # try:
    #     telegram_user = request.user.telegramuser
    # except TelegramUser.DoesNotExist:
    #     return render(request, 'review.html', {
    #         'error': 'Пользователь не найден в боте.'
    #     })

    # Временно используем тестового пользователя
    try:
        # Пытаемся найти TelegramUser с telegram_id=12345
        telegram_user = TelegramUser.objects.get(telegram_id=12345)
    except TelegramUser.DoesNotExist:
        # Или создаём
        telegram_user = TelegramUser.objects.create(
            telegram_id=12345,
            username='test_user'
        )



    # Находим карточки, которые пора повторять
    due_repetitions = Repetition.objects.filter(
        card__owner=telegram_user,
        next_review__lte=timezone.now()
    ).select_related('card').order_by('next_review')

    if not due_repetitions.exists():
        return render(request, 'review.html', {
            'message': 'Нет слов для повторения. Молодец!'
        })

    # Берём первую карточку
    repetition = due_repetitions.first()
    card = repetition.card

    if request.method == 'POST':
        # Получаем оценку пользователя
        quality = int(request.POST.get('quality', 3))  # 1-плохо, 2-трудно, 3-хорошо, 4-отлично

        # Обновляем интервал по SM-2
        repetition.schedule_review(quality)

        # Перенаправляем на следующее слово
        return HttpResponseRedirect(reverse('review'))

    return render(request, 'review.html', {
        'card': card,
        'repetition': repetition,
        'due_count': due_repetitions.count()
    })




def progress_view(request):
    # временный тестовый пользователь
    try:
        telegram_user = TelegramUser.objects.get(telegram_id=12345)
    except TelegramUser.DoesNotExist:
        telegram_user = TelegramUser.objects.create(
            telegram_id=12345,
            username='test_user'
        )

    # читаем выбранную сложность из GET
    difficulty = request.GET.get('difficulty')  # 'beginner' / 'intermediate' / 'advanced' или None

    # базовый queryset карточек пользователя
    cards_qs = Card.objects.filter(owner=telegram_user)

    # если есть фильтр сложности — применяем
    if difficulty in dict(Card.DIFFICULTY_CHOICES).keys():
        cards_qs = cards_qs.filter(difficulty=difficulty)

    # общая статистика по (отфильтрованным) карточкам
    total_cards = cards_qs.count()

    # слова для повторения — тоже по отфильтрованным карточкам
    due_cards = Repetition.objects.filter(
        card__in=cards_qs,
        next_review__lte=timezone.now()
    ).count()

    # статистика по уровням сложности (из общего набора пользователя, чтобы блок "По уровням сложности"
    # всегда показывал картину по всем уровням; если хочешь, можно тоже считать только по cards_qs)
    difficulty_stats = Card.objects.filter(owner=telegram_user).values('difficulty').annotate(
        count=Count('difficulty')
    )

    difficulty_labels = dict(Card.DIFFICULTY_CHOICES)
    stats_by_level = {}
    for item in difficulty_stats:
        level = item['difficulty']
        stats_by_level[level] = {
            'label': difficulty_labels.get(level, level),
            'count': item['count']
        }

    # заполняем нулями отсутствующие уровни
    for level_key, level_label in Card.DIFFICULTY_CHOICES:
        if level_key not in stats_by_level:
            stats_by_level[level_key] = {'label': level_label, 'count': 0}

    return render(request, 'progress.html', {
        'total_cards': total_cards,
        'due_cards': due_cards,
        'stats_by_level': stats_by_level,
        'current_difficulty': difficulty,  # чтобы в шаблоне подсветить активную кнопку, если захочешь
    })


def settings_view(request):
    try:
        telegram_user = TelegramUser.objects.get(telegram_id=12345)
    except TelegramUser.DoesNotExist:
        telegram_user = TelegramUser.objects.create(
            telegram_id=12345,
            username='test_user'
        )

    settings, _ = UserSettings.objects.get_or_create(user=telegram_user)

    if request.method == 'POST':
        settings.first_interval = int(request.POST.get('first_interval', settings.first_interval))
        settings.second_interval = int(request.POST.get('second_interval', settings.second_interval))
        settings.interval_multiplier = float(request.POST.get('interval_multiplier', settings.interval_multiplier))
        settings.max_interval = int(request.POST.get('max_interval', settings.max_interval))
        settings.min_easiness = float(request.POST.get('min_easiness', settings.min_easiness))
        settings.save()
        return HttpResponseRedirect(reverse('settings') + '?saved=1')

    return render(request, 'settings.html', {
        'settings': settings,
        'saved': request.GET.get('saved')
    })
