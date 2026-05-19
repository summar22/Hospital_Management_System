from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.models import DoctorProfile, PatientProfile
from appointments.models import AvailabilitySlot, Booking
from appointments.forms import AvailabilitySlotForm
from django.conf import settings
import requests

@login_required
def home(request):
    if request.user.is_doctor:
        return redirect('dashboard:doctor_dashboard')
    elif request.user.is_patient:
        return redirect('dashboard:patient_dashboard')
    return render(request, 'dashboard/home.html')

@login_required
def doctor_dashboard(request):
    if not request.user.is_doctor:
        return redirect('dashboard:home')
    
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('accounts:doctor_profile_create')
    
    doctor_profile = request.user.doctor_profile
    slots = AvailabilitySlot.objects.filter(doctor=doctor_profile).order_by('date', 'start_time')
    bookings = Booking.objects.filter(slot__doctor=doctor_profile).select_related('patient', 'slot')
    
    return render(request, 'dashboard/doctor_dashboard.html', {
        'doctor_profile': doctor_profile,
        'slots': slots,
        'bookings': bookings,
    })

@login_required
def create_availability_slot(request):
    if not request.user.is_doctor:
        return redirect('dashboard:home')
    
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('accounts:doctor_profile_create')
    
    if request.method == 'POST':
        form = AvailabilitySlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.doctor = request.user.doctor_profile
            slot.save()
            messages.success(request, 'Availability slot created successfully.')
            return redirect('dashboard:doctor_dashboard')
    else:
        form = AvailabilitySlotForm()
    
    return render(request, 'dashboard/create_availability_slot.html', {'form': form})

@login_required
def delete_availability_slot(request, slot_id):
    if not request.user.is_doctor:
        return redirect('dashboard:home')
    
    slot = get_object_or_404(AvailabilitySlot, id=slot_id, doctor=request.user.doctor_profile)
    
    if slot.is_booked:
        messages.error(request, 'Cannot delete a booked slot.')
        return redirect('dashboard:doctor_dashboard')
    
    slot.delete()
    messages.success(request, 'Availability slot deleted successfully.')
    return redirect('dashboard:doctor_dashboard')

@login_required
def patient_dashboard(request):
    if not request.user.is_patient:
        return redirect('dashboard:home')
    
    if not hasattr(request.user, 'patient_profile'):
        return redirect('accounts:patient_profile_create')
    
    patient_profile = request.user.patient_profile
    my_bookings = Booking.objects.filter(patient=patient_profile).select_related('slot', 'slot__doctor')
    
    # Get all available slots (future slots that are not booked)
    available_slots = AvailabilitySlot.objects.filter(
        is_booked=False,
        date__gte=timezone.now().date()
    ).select_related('doctor').order_by('date', 'start_time')
    
    doctors = DoctorProfile.objects.all()
    
    return render(request, 'dashboard/patient_dashboard.html', {
        'patient_profile': patient_profile,
        'my_bookings': my_bookings,
        'available_slots': available_slots,
        'doctors': doctors,
    })

@login_required
def book_slot(request, slot_id):
    if not request.user.is_patient:
        return redirect('dashboard:home')
    
    if not hasattr(request.user, 'patient_profile'):
        return redirect('accounts:patient_profile_create')
    
    try:
        slot = AvailabilitySlot.objects.get(id=slot_id, is_booked=False)
    except AvailabilitySlot.DoesNotExist:
        messages.error(request, 'This slot is not available or has already been booked.')
        return redirect('dashboard:patient_dashboard')
    
    if request.method == 'POST':
        reason = request.POST.get('reason_for_visit', '')
        
        try:
            booking = Booking.create_booking(
                slot_id=slot_id,
                patient_profile=request.user.patient_profile,
                reason_for_visit=reason
            )
            
            # Trigger BOOKING_CONFIRMATION email
            try:
                requests.post(
                    f"{settings.EMAIL_SERVICE_URL}/send-email",
                    json={
                        'trigger': 'BOOKING_CONFIRMATION',
                        'email': request.user.email,
                        'data': {
                            'patient_name': request.user.get_full_name(),
                            'doctor_name': slot.doctor.user.get_full_name(),
                            'date': str(slot.date),
                            'start_time': str(slot.start_time),
                            'end_time': str(slot.end_time),
                        }
                    },
                    timeout=5
                )
            except requests.RequestException:
                # Log error but don't block booking
                pass
            
            # Create Google Calendar events
            create_calendar_events(booking)
            
            messages.success(request, 'Booking confirmed successfully!')
            return redirect('dashboard:patient_dashboard')
            
        except Exception as e:
            messages.error(request, str(e))
            return redirect('dashboard:patient_dashboard')
    
    return render(request, 'dashboard/book_slot.html', {'slot': slot})

def create_calendar_events(booking):
    """Create Google Calendar events for both doctor and patient"""
    from .calendar_utils import create_event
    
    slot = booking.slot
    patient = booking.patient.user
    doctor = slot.doctor.user
    
    # Create event for patient
    if patient.google_calendar_token:
        try:
            doctor_name = doctor.get_full_name() or doctor.username
            create_event(
                patient.google_calendar_token,
                f'Appointment with Dr. {doctor_name}',
                slot.date,
                slot.start_time,
                slot.end_time,
                f'Appointment with {slot.doctor.specialization}'
            )
        except Exception as e:
            print(f"Failed to create patient calendar event: {e}")
    
    # Create event for doctor
    if doctor.google_calendar_token:
        try:
            patient_name = patient.get_full_name() or patient.username
            create_event(
                doctor.google_calendar_token,
                f'Appointment with {patient_name}',
                slot.date,
                slot.start_time,
                slot.end_time,
                f'Patient: {patient_name}'
            )
        except Exception as e:
            print(f"Failed to create doctor calendar event: {e}")
