# How to Run Django Correctly with Virtual Environment

## The Problem

You were getting `ModuleNotFoundError: No module named 'google.oauth2'` because:
- Python packages were installed in the **virtual environment** 
- But Django was running with the **Microsoft Store Python** (system-wide)
- The system Python doesn't have the Google packages installed

## The Solution

### Option 1: Use the Batch File (Easiest for Windows)

Simply double-click this file to run Django:
```
run_django.bat
```

This automatically:
1. Activates your virtual environment
2. Navigates to the project directory
3. Starts the Django development server

### Option 2: Use PowerShell Script

Right-click `run_django.ps1` in your file explorer and select "Run with PowerShell"

### Option 3: Manual Terminal Command

Open PowerShell and run:
```powershell
& C:/Users/Masrol/.virtualenvs/Django-qD6mFPwX/Scripts/Activate.ps1
cd C:\CSE391\MyLegalAdvisor
python manage.py runserver
```

### Option 4: Use VS Code Task (Recommended)

In VS Code, press `Ctrl+Shift+B` to run the Django server if you've set up tasks.

---

## Important

**Never run Django with the default `python` command** - always activate the virtual environment first!

The packages are installed here:
```
C:\Users\Masrol\.virtualenvs\Django-qD6mFPwX\Lib\site-packages\
```

---

## Verification

To verify the virtual environment has all packages:

```powershell
& C:/Users/Masrol/.virtualenvs/Django-qD6mFPwX/Scripts/Activate.ps1
pip list
```

You should see:
- google-api-python-client
- google-auth
- google-auth-httplib2
- google-auth-oauthlib

---

## For Future Reference

When you add new packages, always do it like this:

```powershell
& C:/Users/Masrol/.virtualenvs/Django-qD6mFPwX/Scripts/Activate.ps1
pip install package-name
```

Then update `requirements.txt`:
```powershell
pip freeze > requirements.txt
```
