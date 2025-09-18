# vocab/views.py
from .models import Word
from gtts import gTTS
from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import TelegramUser, Card, Repetition
from .serializers import TelegramUserSerializer, CardSerializer
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TelegramUser

from .models import Word
from random import choice
from django.shortcuts import render



from django.shortcuts import render
from django.http import HttpResponse
from .models import Word
from random import choice

def test_view(request):
    words = Word.objects.all()
    if not words.exists():
        return HttpResponse("Нет доступных слов для тестирования.")
    word = choice(words)
    return render(request, 'test_page.html', {'word': word})








def test_view(request):
    words = Word.objects.all()
    word = choice(words) if words.exists() else None
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


def tts_view(request, word_id):
    word = Word.objects.get(pk=word_id)
    tts = gTTS(text=word.text, lang='en')
    response = HttpResponse(content_type='audio/mpeg')
    tts.write_to_fp(response)
    return response

