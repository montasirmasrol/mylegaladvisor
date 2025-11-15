# Email Configuration Guide

To enable email notifications when lawyers accept appointments, you need to configure SMTP settings in Django.

## Gmail Setup (Recommended)

### Step 1: Enable 2-Step Verification
1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security**
3. Enable **2-Step Verification** if not already enabled

### Step 2: Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select **Mail** as the app
3. Select **Other (Custom name)** as device, enter "MyLegalAdvisor"
4. Click **Generate**
5. Copy the 16-character password (it will look like: `abcd efgh ijkl mnop`)

### Step 3: Configure Django Settings
Open `legaladvisor/settings.py` and update:

```python
EMAIL_HOST_USER = 'your-email@gmail.com'  # Your Gmail address
EMAIL_HOST_PASSWORD = 'abcd efgh ijkl mnop'  # The app password (remove spaces or keep them)
```

### Step 4: Restart Server
After updating settings, restart your Django development server:
```bash
python manage.py runserver
```

## Other Email Providers

### Outlook/Hotmail
```python
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@outlook.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

### Yahoo Mail
```python
EMAIL_HOST = 'smtp.mail.yahoo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@yahoo.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## Testing Email Configuration

1. Start your Django server
2. Login as a lawyer
3. Accept an appointment request
4. Check the user's email inbox
5. If errors occur, check the server console for error messages

## Troubleshooting

### "Email not sent" error
- Verify `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are set correctly
- For Gmail, make sure you're using an App Password, not your regular password
- Check that 2-Step Verification is enabled

### "Authentication failed" error
- Verify your email credentials are correct
- For Gmail, ensure you're using an App Password
- Check if "Less secure app access" is needed (older Gmail accounts)

### Emails going to spam
- This is normal for transactional emails
- Users should check their spam folder
- Consider using a professional email service (SendGrid, Mailgun) for production

## Fallback: Console Backend (Testing Only)

If you want to test without sending actual emails, you can use the console backend:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

This will print emails to your console instead of sending them.

