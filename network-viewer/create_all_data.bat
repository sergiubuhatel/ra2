@echo off
setlocal enabledelayedexpansion

REM Base data directory
set DATADIR=.\frontend\public\data

REM Loop over directories (years) in the data folder
for /D %%Y in (%DATADIR%\*) do (
    set YEAR=%%~nY
    echo === Running scripts for year !YEAR! ===

    call prepare_nodes.bat !YEAR!
    call prepare_edges.bat !YEAR!
    call generate_data.bat !YEAR!

    echo.
)

echo All years processed.
endlocal

