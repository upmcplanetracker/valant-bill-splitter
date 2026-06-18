@echo off
setlocal enabledelayedexpansion

echo ================================
echo  Valant PDF Bill Splitter
echo ================================

REM Change to the script's directory
cd /d "%~dp0"

REM ---- File lock (prevents overlapping runs) ----
set LOCKFILE=%TEMP%\splitbills.lock
if exist "%LOCKFILE%" (
    echo Another instance is running. Exiting.
    exit /b 1
)
type nul > "%LOCKFILE%"

REM ---- Activate virtual environment ----
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run: python -m venv venv
    del "%LOCKFILE%"
    exit /b 1
)
call venv\Scripts\activate.bat

REM ---- Run the Python script with all arguments ----
python split_bills.py %*
set PYTHON_EXIT=%ERRORLEVEL%

REM ---- Cleanup ----
call deactivate 2>nul
del "%LOCKFILE%"

exit /b %PYTHON_EXIT%
