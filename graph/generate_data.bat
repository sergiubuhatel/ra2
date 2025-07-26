@echo off
REM Accept year as argument, default to 2017
set YEAR=%1
if "%YEAR%"=="" set YEAR=2017

REM Set data directory
set DATADIR=frontend\public\data\%YEAR%

REM Set input and output file paths
set NODES=%DATADIR%\Top50_tickers.csv
set EDGES=%DATADIR%\edgesBtwTop50_%YEAR%.csv
set OUTPUT=%DATADIR%\graph_with_centrality.json

REM Run the Python script
python generate_data.py --nodes %NODES% --edges %EDGES% --output %OUTPUT%


