@echo off
rem Kullanim: 4_vtable.bat "004ba6b0"
setlocal
if "%GHIDRA_INSTALL_DIR%"=="" set "GHIDRA_INSTALL_DIR=C:\Users\ferha\Downloads\ghidra_12.1.4_PUBLIC_20260921\ghidra_12.1.4_PUBLIC"
set "PROJ=%USERPROFILE%\gpower_ghidra"
set "OUT=%USERPROFILE%\gpower_dump"
call "%GHIDRA_INSTALL_DIR%\support\analyzeHeadless.bat" "%PROJ%" GPower -process GPowerNT.exe -noanalysis -scriptPath "%~dp0." -postScript DumpAnova.java vtable "%OUT%" "%~1" > "%USERPROFILE%\gpower_vtable_log.txt" 2>&1
findstr /i "ERROR vtables Exception" "%USERPROFILE%\gpower_vtable_log.txt"
echo.
echo Dosya: %OUT%\vtables.txt
