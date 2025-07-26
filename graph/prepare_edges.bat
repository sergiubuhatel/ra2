@echo off
REM =============================================
REM Usage: run_all_edges.bat [YEAR]
REM Example: run_all_edges.bat 2017
REM This script will run prepare_edges.py for:
REM   - Top50
REM   - Top100
REM   - Top200
REM =============================================

SETLOCAL

IF "%~1"=="" (
    echo Usage: %0 [YEAR]
    exit /b 1
)

SET YEAR=%~1
SET BASEDIR=./frontend/public/data/%YEAR%

echo Running edge generation for year: %YEAR%
echo ------------------------------------------

REM Process Top50
echo Generating edges for Top50...
python prepare_edges.py ^
  --network %BASEDIR%/%YEAR%_Network.csv ^
  --top %BASEDIR%/Top50_%YEAR%.csv ^
  --output %BASEDIR%/edgesBtwTop50_%YEAR%.csv

REM Process Top100
echo Generating edges for Top100...
python prepare_edges.py ^
  --network %BASEDIR%/%YEAR%_Network.csv ^
  --top %BASEDIR%/Top100_%YEAR%.csv ^
  --output %BASEDIR%/edgesBtwTop100_%YEAR%.csv

REM Process Top200
echo Generating edges for Top200...
python prepare_edges.py ^
  --network %BASEDIR%/%YEAR%_Network.csv ^
  --top %BASEDIR%/Top200_%YEAR%.csv ^
  --output %BASEDIR%/edgesBtwTop200_%YEAR%.csv

echo ------------------------------------------
echo ✅ All edge files generated for %YEAR%.
ENDLOCAL
