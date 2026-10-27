@echo off
echo =======================================================================
echo ABC AUTOMOTIVE COMPONENTS PVT. LTD.
echo Predictive Maintenance & Machine Health Intelligence System
echo =======================================================================
echo.
echo Starting FastAPI application server on http://localhost:8000 ...
cd /d "%~dp0"
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
pause
