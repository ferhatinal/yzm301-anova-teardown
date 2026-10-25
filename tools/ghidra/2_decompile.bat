@echo off
rem Kullanim: 2_decompile.bat 00401000,00402000   (virgulle ayrilmis adresler, bosluk yok)
setlocal
if "%GHIDRA_INSTALL_DIR%"=="" set "GHIDRA_INSTALL_DIR=C:\Users\ferha\Downloads\ghidra_12.1.4_PUBLIC_20260921\ghidra_12.1.4_PUBLIC"
set "PROJ=%USERPROFILE%\gpower_ghidra"
set "OUT=%USERPROFILE%\gpower_dump"
call "%GHIDRA_INSTALL_DIR%\support\analyzeHeadless.bat" "%PROJ%" GPower -process GPowerNT.exe -noanalysis -scriptPath "%~dp0" -postScript DumpAnova.java decomp "%OUT%" "%~1"
echo.
echo BITTI. dec_*.c dosyalari: %OUT%
