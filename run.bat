@echo off
setlocal enabledelayedexpansion

echo ================================
echo  Valant PDF Bill Splitter
echo ================================

cd /d "%~dp0"

set LOCKFILE=%TEMP%\splitbills.lock
if exist "%LOCKFILE%" (
    echo Another instance is running. Exiting.
    exit /b 1
)
type nul > "%LOCKFILE%"

if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run: python -m venv venv
    del "%LOCKFILE%"
    exit /b 1
)
call venv\Scripts\activate.bat

python split_bills.py %*
set PYTHON_EXIT=%ERRORLEVEL%

call deactivate 2>nul
del "%LOCKFILE%"

exit /b %PYTHON_EXIT%
