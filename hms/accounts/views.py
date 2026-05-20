from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.conf import settings
import requests
from .forms import CustomUserCreationForm, DoctorProfileForm, PatientProfileForm
from .models import User, DoctorProfile, PatientProfile

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

def signup(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.save()
            
            # Trigger SIGNUP_WELCOME email
            try:
                requests.post(
                    f"{settings.EMAIL_SERVICE_URL}/send-email",
                    json={
                        'trigger': 'SIGNUP_WELCOME',
                        'email': user.email,
                        'data': {
                            'username': user.username,
                            'role': user.role
                        }
                    },
                    timeout=5
                )
            except requests.RequestException:
                # Log error but don't block signup
                pass
            
            # Redirect to profile creation based on role
            if user.role == 'DOCTOR':
                return redirect('accounts:doctor_profile_create')
            else:
                return redirect('accounts:patient_profile_create')
    else:
        user_form = CustomUserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': user_form})

@login_required
def doctor_profile_create(request):
    if request.user.role != 'DOCTOR':
        return redirect('dashboard:home')
    
    if hasattr(request.user, 'doctor_profile'):
        return redirect('dashboard:doctor_dashboard')
    
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('dashboard:doctor_dashboard')
    else:
        form = DoctorProfileForm()
    
    return render(request, 'accounts/doctor_profile_create.html', {'form': form})

@login_required
def patient_profile_create(request):
    if request.user.role != 'PATIENT':
        return redirect('dashboard:home')
    
    if hasattr(request.user, 'patient_profile'):
        return redirect('dashboard:patient_dashboard')
    
    if request.method == 'POST':
        form = PatientProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('dashboard:patient_dashboard')
    else:
        form = PatientProfileForm()
    
    return render(request, 'accounts/patient_profile_create.html', {'form': form})

import os
from google_auth_oauthlib.flow import Flow

@login_required
def google_calendar_init(request):
    if not settings.GOOGLE_CALENDAR_CLIENT_ID or not settings.GOOGLE_CALENDAR_CLIENT_SECRET:
        # Enable seamless demo mode
        token_data = {
            'token': 'mock_access_token_demo_mode',
            'refresh_token': 'mock_refresh_token_demo_mode',
            'token_uri': 'mock_uri',
            'client_id': 'mock_client_id',
            'client_secret': 'mock_client_secret',
            'scopes': ['https://www.googleapis.com/auth/calendar'],
            'is_mock': True
        }
        request.user.google_calendar_token = token_data
        request.user.save()
        
        from django.contrib import messages
        messages.success(request, "Google Calendar connected in Demo/Mock Mode!")
        
        if request.user.role == 'DOCTOR':
            return redirect('dashboard:doctor_dashboard')
        else:
            return redirect('dashboard:patient_dashboard')
            
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CALENDAR_CLIENT_ID,
                "client_secret": settings.GOOGLE_CALENDAR_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=['https://www.googleapis.com/auth/calendar']
    )
    flow.redirect_uri = settings.GOOGLE_CALENDAR_REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    request.session['oauth_state'] = state
    return redirect(authorization_url)

@login_required
def google_calendar_callback(request):
    state = request.session.get('oauth_state')
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CALENDAR_CLIENT_ID,
                "client_secret": settings.GOOGLE_CALENDAR_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=['https://www.googleapis.com/auth/calendar'],
        state=state
    )
    flow.redirect_uri = settings.GOOGLE_CALENDAR_REDIRECT_URI
    authorization_response = request.build_absolute_uri()
    
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    
    token_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
    }
    request.user.google_calendar_token = token_data
    request.user.save()
    
    from django.contrib import messages
    messages.success(request, "Google Calendar connected successfully!")
    
    if request.user.role == 'DOCTOR':
        return redirect('dashboard:doctor_dashboard')
    else:
        return redirect('dashboard:patient_dashboard')


from django.contrib.auth import logout as auth_logout
from django.contrib import messages

def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('accounts:login')


