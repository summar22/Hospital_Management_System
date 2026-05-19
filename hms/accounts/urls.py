from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('doctor/profile/create/', views.doctor_profile_create, name='doctor_profile_create'),
    path('patient/profile/create/', views.patient_profile_create, name='patient_profile_create'),
    path('google/login/', views.google_calendar_init, name='google_login'),
    path('google/callback/', views.google_calendar_callback, name='google_callback'),
]
