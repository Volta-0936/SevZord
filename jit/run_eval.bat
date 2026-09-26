@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
set PY=python
where python >nul 2>nul || set PY=py
%PY% -c "import numpy, sklearn" 2>nul
if errorlevel 1 (
  echo numpy / scikit-learn is missing. Run this once in PowerShell:
  echo     python -m pip install numpy scikit-learn
  pause
  exit /b 1
)
echo ===== r2 (reasons) on holdout3 =====
%PY% eval2.py
echo.
echo ===== faithfulness of reasons =====
%PY% probe_faith.py score
echo.
echo ===== r1 on holdout2 =====
%PY% auto_eval.py r1
%PY% spec_gaps.py r1 > nul
echo.
echo saved: holdout3\eval2.txt , probe_faith\score.txt , auto_runs\r1\eval.txt , auto_runs\r1\spec_gaps.txt
pause
