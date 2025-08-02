@echo off
REM Usage: generate_tickers.bat [YEAR]

SETLOCAL

REM Check if a year is provided
IF "%~1"=="" (
    echo Usage: %0 [YEAR]
    exit /b 1
)

SET YEAR=%~1

REM Construct paths
SET INPUT=./frontend/public/data/%YEAR%/%YEAR%_industries.csv
SET OUTPUT=./frontend/public/data/%YEAR%/tickers.csv

REM Run the generate_tickers.py script
python generate_tickers.py %INPUT% %OUTPUT%

ENDLOCAL
