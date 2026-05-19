from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    ROLE_CHOICES = [
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='PATIENT')
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Phone number must be valid')],
        blank=True
    )
    google_calendar_token = models.JSONField(null=True, blank=True)
    
    @property
    def is_doctor(self):
        return self.role == 'DOCTOR'
    
    @property
    def is_patient(self):
        return self.role == 'PATIENT'

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    qualification = models.CharField(max_length=200)
    experience_years = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"
