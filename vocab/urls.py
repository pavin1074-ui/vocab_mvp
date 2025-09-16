# vocab/urls.py
from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
path('test/', views.test_view, name='test'),
    path('register/', views.register_user, name='register'),
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='words/')),  # Главная страница
    path('words/', include('words.urls')),  # Маршруты из words
]



