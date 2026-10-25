@echo off
rem Ghidra analizi zaten bitti; yalnizca dize dokumunu yeniden uretir. Gunluk: %USERPROFILE%\gpower_dump_log.txt
setlocal
if "%GHIDRA_INSTALL_DIR%"=="" set "GHIDRA_INSTALL_DIR=C:\Users\ferha\Downloads\ghidra_12.1.4_PUBLIC_20260921\ghidra_12.1.4_PUBLIC"
set "PROJ=%USERPROFILE%\gpower_ghidra"
set "OUT=%USERPROFILE%\gpower_dump"
mkdir "%OUT%" 2>nul
call "%GHIDRA_INSTALL_DIR%\support\analyzeHeadless.bat" "%PROJ%" GPower -process GPowerNT.exe -noanalysis -scriptPath "%~dp0." -postScript DumpAnova.java strings "%OUT%" > "%USERPROFILE%\gpower_dump_log.txt" 2>&1
findstr /i "DumpAnova ERROR strings written Exception" "%USERPROFILE%\gpower_dump_log.txt"
echo.
dir "%OUT%"
