# Google Calendar/Meet OAuth Implementation Guide

## Problem You Had

Your original code was **deleting the token file every time**, forcing re-authorization each time:

```python
# ❌ WRONG - This was forcing re-auth every time
if os.path.exists(TOKEN_FILE):
    try:
        os.remove(TOKEN_FILE)
        logger.info("Removed existing token file to force new authentication")
```

## What I Fixed

✅ **Removed the token deletion logic** so the saved credentials are reused instead of being deleted.

Now the flow is:
1. **First run**: User authorizes → Token is saved to `token.pickle`
2. **Subsequent runs**: Token is loaded and reused (no re-authorization needed)
3. **Token expiration**: If token expires, it's automatically refreshed using the refresh token

---

## How OAuth 2.0 Works with Google Calendar

### Current Implementation (Single Service Account)
```
Your Server → OAuth Credentials → Google Calendar API → Creates Meet Links
                 (shared token.pickle)
```

**Limitations:**
- Only ONE Google account can authorize the app
- All users' meetings are created under that ONE account

---

## For Production Deployment

When you deploy to hosting and other users need to create meetings, you have **3 options**:

### **Option 1: Service Account (RECOMMENDED for Production) ✅**

A service account is a special Google account that doesn't require user login.

**Pros:**
- No user authorization needed
- Can create meetings on behalf of users
- Works in production environments

**Setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Calendar API
4. Go to **Credentials** → **Create Credentials** → **Service Account**
5. Name it "MyLegalAdvisor Service Account"
6. Grant the role "Editor"
7. Create a key (JSON format) and save it as `service-account-key.json`
8. In your Django app, use this service account instead

**Code Example:**
```python
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = '/path/to/service-account-key.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

service = build('calendar', 'v3', credentials=creds)
```

---

### **Option 2: OAuth 2.0 Web Application Flow (For Multi-User Apps)**

If you want different users to create meetings under their own Google accounts:

**Current Flow (Development):**
- User clicks "Create Meeting"
- Redirected to Google login
- User authorizes
- Browser opens a local server to capture the token

**Production Flow:**
- Use OAuth 2.0 redirect URLs instead of `run_local_server()`
- Store credentials in your database (one token per user)
- Each user has their own Google credentials

**Modified Code Example:**
```python
from django.shortcuts import redirect
from django.urls import reverse
from google_auth_oauthlib.flow import Flow

def authorize_google(request):
    """Initiate Google OAuth flow"""
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=request.build_absolute_uri(reverse('google_callback'))
    )
    auth_url, state = flow.authorization_url()
    request.session['oauth_state'] = state
    return redirect(auth_url)

def google_callback(request):
    """Handle Google OAuth callback"""
    state = request.session['oauth_state']
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=request.build_absolute_uri(reverse('google_callback'))
    )
    
    # Get credentials from the authorization response
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    creds = flow.credentials
    
    # Store creds in database for this user
    user = request.user
    UserGoogleCredentials.objects.update_or_create(
        user=user,
        defaults={'token': creds.to_json()}
    )
    
    return redirect('home')
```

---

### **Option 3: Lawyer's Google Account (Current Approach)**

Keep the current approach but with improvements:

**How it works:**
1. Only the lawyer needs to authorize once
2. When a meeting is scheduled, it's created on the lawyer's Google Calendar
3. Invitation email goes to the client
4. Client receives a Meet link in the email

**This is suitable if:**
- Each lawyer manages their own calendar
- Clients just receive invitations (don't need to authorize)

---

## Current Implementation Status

Your app currently uses **Option 3** with a shared token. Here's what happens:

1. ✅ **Development**: Lawyer authorizes once, token saved
2. ✅ **The token is reused**: No need to re-authorize
3. ✅ **Email sent to client**: Client gets meeting link in email
4. ⚠️ **Production issue**: If deployed to hosting, the hosting server can't open a browser for OAuth

---

## For Deployment to Hosting

When you deploy to a hosting service (Heroku, AWS, Digital Ocean, etc.):

### **RECOMMENDED: Use Service Account**

Service accounts don't require a browser, so they work on servers:

1. Download the service account JSON file
2. Upload it to your server (or store in environment variable)
3. Modify `google_meet.py`:

```python
from google.oauth2 import service_account

def get_credentials():
    SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, 'service-account-key.json')
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return creds
```

---

## Checklist for Production

- [ ] Remove `token.pickle` from version control (add to `.gitignore`)
- [ ] Use Service Account instead of OAuth for server
- [ ] Store credentials securely (environment variables, not in code)
- [ ] Test meeting creation without browser login
- [ ] Verify email invitations are being sent
- [ ] Test with actual Google Meet links
- [ ] Add error handling for failed authentications
- [ ] Set up logging to track OAuth issues

---

## Current State

Your code is now:
- ✅ Reuses tokens (no forced re-authorization)
- ✅ Automatically refreshes expired tokens
- ✅ Works for development
- ⚠️ Still needs Service Account setup for production

The changes I made will prevent the **"authorize every time"** issue in development and testing!

---

## Testing

To test the fix:
1. Delete `token.pickle` if it exists
2. Run your app and create a meeting
3. You'll be asked to authorize once
4. Create another meeting
5. **It should work without asking for authorization again** ✅
