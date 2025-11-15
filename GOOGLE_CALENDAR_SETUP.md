# Setting up Google Calendar Integration

Follow these steps carefully to enable Google Calendar integration for online meetings:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)

2. Create a new project:
   - Click on the project dropdown at the top of the page
   - Click "New Project"
   - Name it "MyLegalAdvisor"
   - Click "Create"

3. Enable the Google Calendar API:
   - In the dashboard, click "Enable APIs and Services"
   - Search for "Google Calendar API"
   - Click "Enable"

4. Configure the OAuth consent screen:
   - In the left sidebar, go to "APIs & Services" > "OAuth consent screen"
   - Select "External" user type
   - Click "Create"
   - Fill in the required fields:
     * App name: "MyLegalAdvisor"
     * User support email: Your email
     * Developer contact email: Your email
   - Click "Save and Continue"
   - On "Scopes" page, click "Add or Remove Scopes"
   - Select "Google Calendar API ../auth/calendar" scope
   - Click "Save and Continue"
   - On "Test users" page, click "Add Users"
   - Add your Google email address that you'll use for testing
   - Click "Save and Continue"

5. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" and select "OAuth client ID"
   - Choose "Desktop application" as the application type
   - Name it "MyLegalAdvisor Desktop Client"
   - Click "Create"
   - Click "Download" to get the JSON file

6. Setup the credentials:
   - Rename the downloaded JSON file to `credentials.json`
   - Place it in your project's root directory (same level as manage.py)
   - Add these lines to .gitignore:
     ```
     credentials.json
     token.pickle
     ```

7. Delete any existing token.pickle file if it exists in your project directory.

8. First-time authentication:
   - When you first try to create a meeting, you'll see a browser window
   - Choose your Google account
   - You'll see "Google hasn't verified this app" warning
   - Click "Continue" (or "Advanced" > "Go to MyLegalAdvisor (unsafe)")
   - Click "Continue" to grant access
   - This is normal for development/testing

Important Notes:
- For development/testing, the app doesn't need to be verified by Google
- The warning about unverified app is normal in development
- Only the Google account you added as a test user can access the app
- Make sure you're using the same Google account that you added as a test user
- If you get errors, try deleting token.pickle and reauthorizing

Troubleshooting:
1. If you get "Access blocked" error:
   - Make sure you added your Google account as a test user
   - Use the same Google account you added as a test user
   - Delete token.pickle if it exists and try again

2. If authorization fails:
   - Check that credentials.json is in the correct location
   - Ensure you enabled Google Calendar API
   - Verify you added the correct scope (Google Calendar API)
   - Try deleting token.pickle and reauthorizing

3. If meetings aren't created:
   - Check the debug.log file for detailed error messages
   - Verify your Google account has calendar access
   - Ensure your system time is correctly set