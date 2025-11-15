# MyLegalAdvisor

A Django-based web application for connecting clients with legal professionals.

## Features

- **Three User Types:**
  - Admin (Superuser - created via Django admin)
  - Lawyer (Can register and create profile)
  - User (Can register and request appointments)

- **User Features:**
  - Register and login
  - Browse available lawyers
  - View lawyer profiles and details
  - Request appointments with lawyers
  - View appointment status (pending/accepted/rejected)
  - Manage user profile

- **Lawyer Features:**
  - Register and login
  - Create and update professional profile
  - View appointment requests
  - Accept or reject appointments
  - Manage lawyer profile

- **Admin Features:**
  - Access Django admin panel
  - Manage all users, lawyers, and appointments

- **Email Notifications:**
  - Users receive email when appointment is accepted
  - Includes welcome message, date, and time

## Installation

1. Install Django:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Create superuser (Admin):
```bash
python manage.py createsuperuser
```

4. Run the development server:
```bash
python manage.py runserver
```

5. Access the application:
   - Home page: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Usage

### For Users:
1. Register as a "User"
2. Login to your account
3. Browse lawyers from the "Lawyers" menu
4. Click on a lawyer to view details
5. Request an appointment by filling the form
6. View your appointments and their status

### For Lawyers:
1. Register as a "Lawyer"
2. Login to your account
3. Complete your profile (lawyer type, bio, experience, etc.)
4. View appointment requests in "Appointments" menu
5. Accept or reject appointment requests

### For Admin:
1. Use the superuser account created via `createsuperuser`
2. Access Django admin panel at `/admin/`
3. Manage all users, lawyers, profiles, and appointments

## Email Configuration

By default, emails are sent to the console (for development). To configure real email sending:

1. Edit `legaladvisor/settings.py`
2. Uncomment and configure the SMTP settings:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

## Database

The project uses SQLite by default (configured in `settings.py`). The database file `db.sqlite3` will be created automatically after running migrations.

## Project Structure

```
MyLegalAdvisor/
├── legaladvisor/          # Main project settings
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL configuration
│   └── ...
├── accounts/             # Main application
│   ├── models.py         # User, LawyerProfile, UserProfile, Appointment models
│   ├── views.py          # All views
│   ├── forms.py          # Forms for registration and appointments
│   ├── admin.py          # Admin configuration
│   └── urls.py           # App URL routes
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   └── accounts/         # App-specific templates
├── manage.py
└── requirements.txt
```

## Notes

- Admin users are created via Django's `createsuperuser` command
- Lawyers and Users can register through the registration page
- Email notifications are sent when appointments are accepted
- All user types have different profiles and permissions

