#words/models.py:

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.db import models
from django.utils import timezone


def word_image_upload_path(instance, filename):
    return f"word_images/user_{instance.user.id}/{filename}"


class Word(models.Model):
    # ссылка на пользователя из приложения vocab, без прямого импорта, чтобы не было циклических импортов
    user = models.ForeignKey(
        'vocab.TelegramUser',
        on_delete=models.CASCADE,
        related_name='words'
    )
    text = models.CharField(max_length=255)
    translation = models.CharField(max_length=255)
    source_lang = models.CharField(
        max_length=10,
        default='en',
        help_text='Language of the original word (en/ru)'
    )
    next_review = models.DateTimeField(default=timezone.now)
    interval = models.IntegerField(default=1)
    repetitions = models.IntegerField(default=0)
    ease_factor = models.FloatField(default=2.5)

    # картинка для слова
    image = models.ImageField(upload_to=word_image_upload_path, null=True, blank=True)

    def __str__(self):
        return f"{self.text} ({self.user})"

