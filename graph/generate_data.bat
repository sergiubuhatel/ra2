@echo off
setlocal EnableDelayedExpansion

REM Accept year as argument, default to 2017
set YEAR=%1
if "%YEAR%"=="" set YEAR=2017

REM Set data directory
set DATADIR=frontend\public\data\%YEAR%

REM Loop through Top50, Top100, Top200
for %%T in (50 100 200) do (
    echo -----------------------------------------
    echo Generating graph for Top%%T - Year %YEAR%
    
    set NODES=%DATADIR%\Top%%T_tickers.csv
    set EDGES=%DATADIR%\edgesBtwTop%%T_%YEAR%.csv
    set OUTPUT=%DATADIR%\graph_top_%%T.json

    python generate_data.py --nodes !NODES! --edges !EDGES! --output !OUTPUT!
)

echo -----------------------------------------
echo ✅ All graphs generated for year: %YEAR%

endlocal
