from django.contrib import admin
from .models import AvailabilitySlot, Booking

@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'date', 'start_time', 'end_time', 'is_booked']
    list_filter = ['is_booked', 'date']
    search_fields = ['doctor__user__username', 'doctor__specialization']
    date_hierarchy = 'date'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['slot', 'patient', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['patient__user__username', 'slot__doctor__user__username']
    date_hierarchy = 'created_at'
