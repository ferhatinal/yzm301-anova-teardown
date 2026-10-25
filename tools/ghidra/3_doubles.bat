@echo off
rem Kullanim: 3_doubles.bat "005c4970,005c3f38,005c48c8"
setlocal
if "%GHIDRA_INSTALL_DIR%"=="" set "GHIDRA_INSTALL_DIR=C:\Users\ferha\Downloads\ghidra_12.1.4_PUBLIC_20260921\ghidra_12.1.4_PUBLIC"
set "PROJ=%USERPROFILE%\gpower_ghidra"
set "OUT=%USERPROFILE%\gpower_dump"
call "%GHIDRA_INSTALL_DIR%\support\analyzeHeadless.bat" "%PROJ%" GPower -process GPowerNT.exe -noanalysis -scriptPath "%~dp0." -postScript DumpAnova.java doubles "%OUT%" "%~1"
type "%OUT%\doubles.txt"
