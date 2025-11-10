@echo off
echo Starting Streamlit app [as Chrome app] using venv Python...
call "%~dp0venv\Scripts\activate"
python "%~dp0launcher.py"
pause
