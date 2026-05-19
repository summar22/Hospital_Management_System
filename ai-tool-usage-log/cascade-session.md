# Cascade AI Assistant Session

**Date**: May 19, 2026
**Task**: Build Hospital Management System (HMS) - Shortlisting Task

## Summary

This session involved building a complete Hospital Management System with Django backend and serverless email service according to the detailed requirements provided.

## Work Completed

### 1. Project Structure Setup
- Created directory structure: `hms/`, `email-service/`, `ai-tool-usage-log/`
- Initialized Django project in `hms/` directory
- Created Python virtual environment
- Installed required dependencies (Django, psycopg2-binary, google-auth, etc.)

### 2. Django Configuration
- Configured PostgreSQL database connection using python-decouple
- Added custom user model with roles (DOCTOR, PATIENT)
- Configured Google Calendar OAuth2 settings
- Configured email service URL
- Set up login/logout redirect URLs

### 3. Models Implementation
- **accounts/models.py**:
  - Custom User model with role field, phone, and google_calendar_token
  - DoctorProfile model (specialization, qualification, experience_years)
  - PatientProfile model (date_of_birth, address)
  
- **appointments/models.py**:
  - AvailabilitySlot model with unique constraint on (doctor, date, start_time)
  - Booking model with status tracking
  - Implemented `create_booking()` class method with race condition handling using `select_for_update()` and database transactions

### 4. Admin Configuration
- Registered User, DoctorProfile, PatientProfile in accounts admin
- Registered AvailabilitySlot, Booking in appointments admin
- Configured list displays, filters, and search fields

### 5. Authentication System
- Created CustomUserCreationForm with role selection
- Created DoctorProfileForm and PatientProfileForm
- Implemented signup view with SIGNUP_WELCOME email trigger
- Implemented profile creation views for both roles
- Role-based access control in all views

### 6. Dashboard Implementation
- **Doctor Dashboard**:
  - View availability slots
  - Create new availability slots
  - Delete unbooked slots
  - View all bookings
  
- **Patient Dashboard**:
  - View own bookings
  - View all available doctors
  - View available slots
  - Book slots with race condition protection

### 7. Google Calendar Integration
- Created `dashboard/calendar_utils.py` with `create_event()` function
- Handles OAuth2 credentials and token refresh
- Creates calendar events for both doctor and patient on booking confirmation
- Integrated into booking workflow

### 8. Serverless Email Service
- Created `email-service/serverless.yml` with AWS Lambda configuration
- Created `email-service/handler.py` with email sending logic
- Implemented two triggers: SIGNUP_WELCOME and BOOKING_CONFIRMATION
- Configured to run locally with serverless-offline on port 3000
- Uses SMTP for email delivery (configurable via environment variables)

### 9. Templates
- Created base template with Bootstrap 5 and navigation
- Authentication templates: login, signup, profile creation
- Dashboard templates: doctor dashboard, patient dashboard, slot creation, booking confirmation

### 10. URL Configuration
- Configured main project URLs with accounts and dashboard includes
- Created accounts URLs for authentication
- Created dashboard URLs for doctor and patient actions

### 11. Documentation
- Created comprehensive README.md with all required sections:
  - Setup and Run
  - System Architecture
  - The Design Decision (race condition handling)
  - Limitations
- Created .env.example with configuration template
- Created requirements.txt for both Django and email service

## Key Design Decisions

### Race Condition Handling
Chose database-level locking with `select_for_update()` over Redis-based locking for:
- Simplicity and no additional infrastructure
- Sufficient for local demo system
- ACID guarantees within transaction
- Django native support

### Email Service Architecture
Separated email functionality into serverless function for:
- Clear separation of concerns
- Easy local testing with serverless-offline
- Scalable to AWS Lambda if needed
- HTTP-based integration with Django backend

### Google Calendar Integration
Stored OAuth2 tokens as JSON in user model for:
- Simple implementation for demo
- Easy token refresh handling
- Per-user calendar access
- No additional database tables needed

## Files Created/Modified

### Django Application (hms/)
- config/settings.py - PostgreSQL, Google Calendar, email service config
- config/urls.py - Main URL routing
- accounts/models.py - User, DoctorProfile, PatientProfile
- accounts/admin.py - Admin registration
- accounts/forms.py - Authentication forms
- accounts/views.py - Signup, login, profile creation
- accounts/urls.py - Account URLs
- appointments/models.py - AvailabilitySlot, Booking with race condition handling
- appointments/admin.py - Admin registration
- appointments/forms.py - AvailabilitySlot form
- dashboard/views.py - Doctor and patient dashboards
- dashboard/urls.py - Dashboard URLs
- dashboard/calendar_utils.py - Google Calendar integration
- templates/base.html - Base template
- templates/accounts/*.html - Authentication templates
- templates/dashboard/*.html - Dashboard templates
- .env.example - Configuration template

### Email Service (email-service/)
- serverless.yml - Serverless Framework configuration
- handler.py - Email sending logic with two triggers
- requirements.txt - Python dependencies

### Root Directory
- README.md - Comprehensive documentation
- requirements.txt - Django dependencies
- ai-tool-usage-log/cascade-session.md - This file

## Integration Points

1. **Django → Email Service**: HTTP POST to `EMAIL_SERVICE_URL/send-email`
2. **Booking → Calendar Events**: Calls `create_calendar_events()` after successful booking
3. **Signup → Email**: Triggers SIGNUP_WELCOME email via HTTP request
4. **Booking → Email**: Triggers BOOKING_CONFIRMATION email via HTTP request

## Testing Status

System is ready for local testing. To test:
1. Set up PostgreSQL database
2. Configure .env files
3. Run Django server on port 8000
4. Run serverless-offline on port 3000
5. Test doctor signup, slot creation
6. Test patient signup, slot booking
7. Verify email triggers
8. Verify Google Calendar events (with valid OAuth2 credentials)

## Notes

- All email service failures are caught and logged without blocking main functionality
- Google Calendar integration is optional for basic functionality
- Race condition protection is implemented at database level
- Role-based access is enforced at view, template, and URL levels
