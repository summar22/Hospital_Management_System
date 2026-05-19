from django import forms
from .models import AvailabilitySlot
from django.utils import timezone

class AvailabilitySlotForm(forms.ModelForm):
    class Meta:
        model = AvailabilitySlot
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        date = cleaned_data.get('date')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("Start time must be before end time.")
        
        if date and start_time:
            from datetime import datetime
            slot_datetime = timezone.make_aware(datetime.combine(date, start_time))
            if slot_datetime < timezone.now():
                raise forms.ValidationError("Cannot create slots in the past.")
        
        return cleaned_data
