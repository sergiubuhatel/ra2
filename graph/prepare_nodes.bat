@echo off
REM Usage: run_prepare_nodes.bat [YEAR]

SETLOCAL

REM Check if a year is provided
IF "%~1"=="" (
    echo Usage: %0 [YEAR]
    exit /b 1
)

SET YEAR=%~1

REM Run Top50 and Top100 only if YEAR is NOT 2023
IF NOT "%YEAR%"=="2023" (
    python prepare_nodes.py ^
      --industries ./frontend/public/data/%YEAR%/%YEAR%_industries.csv ^
      --top ./frontend/public/data/%YEAR%/Top50_%YEAR%.csv ^
      --output ./frontend/public/data/%YEAR%/Top50_tickers.csv

    python prepare_nodes.py ^
      --industries ./frontend/public/data/%YEAR%/%YEAR%_industries.csv ^
      --top ./frontend/public/data/%YEAR%/Top100_%YEAR%.csv ^
      --output ./frontend/public/data/%YEAR%/Top100_tickers.csv
)

REM Always run Top200
python prepare_nodes.py ^
  --industries ./frontend/public/data/%YEAR%/%YEAR%_industries.csv ^
  --top ./frontend/public/data/%YEAR%/Top200_%YEAR%.csv ^
  --output ./frontend/public/data/%YEAR%/Top200_tickers.csv    

REM Always run ticker extraction
generate_tickers.bat %YEAR%

ENDLOCAL
