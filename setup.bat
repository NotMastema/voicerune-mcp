@echo off
setlocal
title VoiceRune setup
set "APP=%LOCALAPPDATA%\voicerune-mcp"
set "PROFILE=%~1"
if "%PROFILE%"=="" set "PROFILE=default"

echo.
echo  ===  VoiceRune setup: Ruune for Claude  ===
echo.

rem --- Find Python, or install it ---
set "PYEXE="
for /f "delims=" %%i in ('py -3 -c "import sys;print(sys.executable)" 2^>nul') do set "PYEXE=%%i"
if not defined PYEXE (
  echo Python isn't installed yet. Installing it now ^(Windows may ask for permission^)...
  winget install -e --id Python.Python.3.13 --scope user --silent --accept-package-agreements --accept-source-agreements
  if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
)
if not defined PYEXE (
  echo.
  echo Couldn't install Python automatically.
  echo Install it from https://www.python.org/downloads/ ^(check "Add python.exe to PATH"^),
  echo then double-click this file again.
  pause
  exit /b 1
)

rem --- Download the latest version ---
echo Downloading the latest version...
set "ZIP=%TEMP%\voicerune.zip"
set "EXT=%TEMP%\voicerune-extract"
"%SystemRoot%\System32\curl.exe" -fsSL -o "%ZIP%" https://github.com/NotMastema/voicerune-mcp/archive/refs/heads/main.zip || goto :dlfail
if exist "%EXT%" rmdir /s /q "%EXT%"
mkdir "%EXT%"
"%SystemRoot%\System32\tar.exe" -xf "%ZIP%" -C "%EXT%" || goto :dlfail
if not exist "%APP%" mkdir "%APP%"
xcopy /e /y /q "%EXT%\voicerune-mcp-main\*" "%APP%\" >nul

rem --- Python does the rest ---
"%PYEXE%" "%APP%\setup.py" %PROFILE%
exit /b %errorlevel%

:dlfail
echo.
echo Couldn't download the files. Check your internet connection and try again.
pause
exit /b 1
