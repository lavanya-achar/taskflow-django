from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('billing/', views.billing_view, name='billing'),
    path('settings/', views.settings_view, name='settings'),
    path('switch-mode/', views.switch_mode, name='switch_mode'),
    path('delete-account/', views.delete_account, name='delete_account'),
]
