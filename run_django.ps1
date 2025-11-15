# PowerShell script to run Django with the virtual environment
# Right-click on this file in VS Code and select "Run in PowerShell"

$env:Path = "C:\Users\Masrol\.virtualenvs\Django-qD6mFPwX\Scripts;" + $env:Path
cd "C:\CSE391\MyLegalAdvisor"

Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host "Running Django development server..." -ForegroundColor Cyan
Write-Host ""

python manage.py runserver

# Keep window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host "Press Enter to close..." -ForegroundColor Red
    Read-Host
}
