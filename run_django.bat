@echo off
REM Activate the virtual environment and run Django development server
cd /d "%~dp0"
call C:/Users/Masrol/.virtualenvs/Django-qD6mFPwX/Scripts/activate.bat
python manage.py runserver
pause
