from django.urls import path
from .views import temp
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='auth/login/', permanent=False), name='home'),
    path('temp/', temp, name='temp'),
]