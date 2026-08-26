@echo off
TITLE STALWART Full Spectrum Audit Engine
cd /d "%~dp0"
echo [*] Launching STALWART Web Server...
streamlit run moralityengine.py
pause