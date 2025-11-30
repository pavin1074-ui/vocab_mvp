#vocab/utils.py:

import requests

DJANGO_API_URL = "http://127.0.0.1:8000/api/"  # пример, поправь под свой

def register_user(telegram_id, username):
    r = requests.post(
        f'{DJANGO_API_URL}register/',
        json={'telegram_id': telegram_id, 'username': username}
    )
    return r


from datetime import datetime, timedelta

def sm2(repetition, grade):
    # grade: 0-5, качество ответа, 5 — отлично
    if grade < 3:
        repetition.repetitions = 0
        repetition.interval = 1
    else:
        if repetition.repetitions == 0:
            repetition.interval = 1
        elif repetition.repetitions == 1:
            repetition.interval = 6
        else:
            repetition.interval = int(repetition.interval * repetition.easiness)
        repetition.repetitions += 1
    repetition.easiness += (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    if repetition.easiness < 1.3:
        repetition.easiness = 1.3
    repetition.next_review = datetime.now() + timedelta(days=repetition.interval)
    repetition.save()



def get_word_difficulty(word: str) -> str:
    w = word.strip().lower()
    if len(w) <= 4:
        return 'beginner'
    elif len(w) <= 7:
        return 'intermediate'
    else:
        return 'advanced'
