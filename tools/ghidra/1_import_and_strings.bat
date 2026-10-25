@echo off
setlocal
if "%GHIDRA_INSTALL_DIR%"=="" set "GHIDRA_INSTALL_DIR=C:\Users\ferha\Downloads\ghidra_12.1.4_PUBLIC_20260921\ghidra_12.1.4_PUBLIC"
set "EXE=C:\Users\ferha\Desktop\GPowerWin_3.1.9.7\GPower_3.1.9.7_143\GPowerNT.exe"
set "PROJ=%USERPROFILE%\gpower_ghidra"
set "OUT=%USERPROFILE%\gpower_dump"
mkdir "%PROJ%" 2>nul
mkdir "%OUT%" 2>nul
call "%GHIDRA_INSTALL_DIR%\support\analyzeHeadless.bat" "%PROJ%" GPower -import "%EXE%" -overwrite -scriptPath "%~dp0." -postScript DumpAnova.java strings "%OUT%"
echo.
echo BITTI. Dosya: %OUT%\strings_xrefs.tsv
