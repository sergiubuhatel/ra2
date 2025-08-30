@echo off
REM Usage: create_all_tickers.bat [YEAR]

SETLOCAL ENABLEDELAYEDEXPANSION

REM Default year
set YEAR=%1
if "%YEAR%"=="" set YEAR=2017

REM Set input and output paths
set INPUT_FILE=.\public\data\%YEAR%\%YEAR%_industries.csv
set OUTPUT_FILE=.\public\data\%YEAR%\All_%YEAR%.csv

REM If singular file doesn't exist, try plural
if not exist "%INPUT_FILE%" (
    set INPUT_FILE=.\public\data\%YEAR%\%YEAR%_industries.csv
    if not exist "%INPUT_FILE%" (
        echo ERROR: Input file not found: %YEAR%_industries.csv
        exit /b 1
    )
)

REM Run the Python script with flags
python create_all_tickers.py --input "%INPUT_FILE%" --output "%OUTPUT_FILE%"
