@echo off
REM Usage: run_prepare_nodes.bat [YEAR]

SETLOCAL ENABLEDELAYEDEXPANSION

IF "%~1"=="" (
    echo Usage: %0 [YEAR]
    exit /b 1
)

SET YEAR=%~1
SET BASEDIR=./frontend/public/data/%YEAR%

REM Run the generate_tickers.py script
python generate_tickers.py %BASEDIR%

REM Run Top50 and Top100 only if YEAR is NOT 2023
IF NOT "%YEAR%"=="2023" (
    python prepare_nodes.py ^
      --industries %BASEDIR%/%YEAR%_industries.csv ^
      --top %BASEDIR%/Top50_%YEAR%.csv ^
      --output %BASEDIR%/Top50_tickers.csv

    python prepare_nodes.py ^
      --industries %BASEDIR%/%YEAR%_industries.csv ^
      --top %BASEDIR%/Top100_%YEAR%.csv ^
      --output %BASEDIR%/Top100_tickers.csv
)

REM Always run Top200
python prepare_nodes.py ^
  --industries %BASEDIR%/%YEAR%_industries.csv ^
  --top %BASEDIR%/Top200_%YEAR%.csv ^
  --output %BASEDIR%/Top200_tickers.csv    

REM === Loop through ticker_<industry>.csv files and generate industry_tickers_<industry>.csv
echo ---------------------------------------------
echo Generating industry-specific ticker files...

for %%F in (%BASEDIR%\ticker_*.csv) do (
    set "FILENAME=%%~nF"
    set "INDUSTRY=!FILENAME:~7!"
    echo Processing industry: !INDUSTRY!
    python prepare_nodes.py ^
        --industries %BASEDIR%/%YEAR%_industries.csv ^
        --top %%F ^
        --output %BASEDIR%/industry_tickers_!INDUSTRY!.csv
    echo ✅ Saved: %BASEDIR%/industry_tickers_!INDUSTRY!.csv
)

ENDLOCAL
