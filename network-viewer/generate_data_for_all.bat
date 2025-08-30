@echo off
setlocal EnableDelayedExpansion

REM === generate_data_for_all.bat ===
REM Usage:
REM   generate_data_for_all.bat [YEAR]
REM If YEAR is provided, only that year is processed.
REM If no YEAR is provided, all years 2018–2023 are processed.

set YEAR=%1

REM If no year is provided, loop through 2018–2023
if "%YEAR%"=="" (
    for %%Y in (2017 2018 2019 2020 2021 2022 2023) do (
        call :processYear %%Y
    )
    goto :eof
) else (
    call :processYear %YEAR%
    goto :eof
)

:processYear
set "YEAR=%1"
set "DATADIR=.\public\data\%YEAR%"
set "NODES=%DATADIR%\All_tickers.csv"
set "EDGES=%DATADIR%\edgesBtwAllTickers.csv"
set "OUTPUT=%DATADIR%\graph_all_%YEAR%.json"

echo ==============================
echo Processing year %YEAR%...
echo ==============================

REM Check if input files exist
if not exist "!NODES!" (
    echo WARNING: Nodes file not found: !NODES!
    goto :eof
)

if not exist "!EDGES!" (
    echo WARNING: Edges file not found: !EDGES!
    goto :eof
)

REM Run Python script
python generate_data.py --nodes "!NODES!" --edges "!EDGES!" --output "!OUTPUT!"

goto :eof
