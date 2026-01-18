@echo off
REM This is for Windows
echo ================================
echo  Valant PDF Bill Splitter
echo ================================

call venv\Scripts\activate
python split_bills.py %*
call venv\Scripts\deactivate
