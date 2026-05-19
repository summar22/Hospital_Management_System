from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/slot/create/', views.create_availability_slot, name='create_availability_slot'),
    path('doctor/slot/delete/<int:slot_id>/', views.delete_availability_slot, name='delete_availability_slot'),
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/book/<int:slot_id>/', views.book_slot, name='book_slot'),
]
