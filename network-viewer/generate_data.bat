@echo off
setlocal EnableDelayedExpansion

REM Accept year as argument, default to 2017
set YEAR=%1
if "%YEAR%"=="" set YEAR=2017

REM Set data directory
set DATADIR=frontend\public\data\%YEAR%

REM Loop through Top50, Top100, Top200
for %%T in (50 100 200) do (
    REM Skip Top50 and Top100 for year 2023
    if "%YEAR%"=="2023" (
        if "%%T"=="50" (
            echo Skipping Top50 for %YEAR% (no data file)
            goto :continueLoop
        )
        if "%%T"=="100" (
            echo Skipping Top100 for %YEAR% (no data file)
            goto :continueLoop
        )
    )

    echo -----------------------------------------
    echo Generating graph for Top%%T - Year %YEAR%
    
    set NODES=%DATADIR%\Top%%T_tickers.csv
    set EDGES=%DATADIR%\edgesBtwTop%%T_%YEAR%.csv
    set OUTPUT=%DATADIR%\graph_top_%%T.json

    python generate_data.py --nodes !NODES! --edges !EDGES! --output !OUTPUT!

    :continueLoop
)

REM ===== NEW SECTION: Generate graph per industry =====
echo -----------------------------------------
echo Generating per-industry graphs - Year %YEAR%

for %%F in (%DATADIR%\industry_tickers_*.csv) do (
    set "FILENAME=%%~nxF"
    set "INDUSTRY=!FILENAME:~17,-4!"

    set NODES=%%F
    set EDGES=%DATADIR%\edgesBtwAllTickers.csv
    set OUTPUT=%DATADIR%\graph_industry_!INDUSTRY!.json

    echo Generating graph for industry !INDUSTRY!
    python generate_data.py --nodes !NODES! --edges !EDGES! --output !OUTPUT!
)

echo -----------------------------------------
echo ✅ All graphs generated for year: %YEAR%

endlocal
