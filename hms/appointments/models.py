from django.db import models
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import User, DoctorProfile, PatientProfile

class AvailabilitySlot(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='availability_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['doctor', 'date', 'start_time']
        ordering = ['date', 'start_time']
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time")
        
        # Check if slot is in the past
        from datetime import datetime
        slot_datetime = timezone.make_aware(datetime.combine(self.date, self.start_time))
        if slot_datetime < timezone.now():
            raise ValidationError("Cannot create slots in the past")
    
    def __str__(self):
        return f"{self.doctor} - {self.date} {self.start_time} to {self.end_time}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    
    slot = models.OneToOneField(AvailabilitySlot, on_delete=models.CASCADE, related_name='booking')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    reason_for_visit = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def clean(self):
        if self.slot.is_booked and self.slot.booking != self:
            raise ValidationError("This slot is already booked")
    
    @classmethod
    def create_booking(cls, slot_id, patient_profile, reason_for_visit=''):
        """
        Create a booking with race condition handling using database-level locking.
        """
        from django.db import IntegrityError
        
        try:
            with transaction.atomic():
                # Lock the row to prevent race conditions
                slot = AvailabilitySlot.objects.select_for_update().get(id=slot_id)
                
                if slot.is_booked:
                    raise ValidationError("This slot is already booked")
                
                # Mark slot as booked
                slot.is_booked = True
                slot.save()
                
                # Create booking
                booking = cls.objects.create(
                    slot=slot,
                    patient=patient_profile,
                    reason_for_visit=reason_for_visit,
                    status='CONFIRMED'
                )
                
                return booking
        except AvailabilitySlot.DoesNotExist:
            raise ValidationError("Slot not found")
        except IntegrityError:
            raise ValidationError("Failed to create booking due to database error")
    
    def __str__(self):
        return f"Booking: {self.patient} with {self.slot.doctor} on {self.slot.date}"
