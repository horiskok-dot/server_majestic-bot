@echo off
setlocal enabledelayedexpansion

echo Finding Visual Studio installation...

set "VS_PATH="

:: Common Visual Studio installation folders (2022, 2019, 2017)
for %%y in (2022, 2019, 2017) do (
    for %%e in (Community, Professional, Enterprise, BuildTools) do (
        set "test_path=C:\Program Files\Microsoft Visual Studio\%%y\%%e\VC\Auxiliary\Build\vcvars64.bat"
        if exist "!test_path!" (
            set "VS_PATH=!test_path!"
            goto :found
        )
        set "test_path=C:\Program Files (x86)\Microsoft Visual Studio\%%y\%%e\VC\Auxiliary\Build\vcvars64.bat"
        if exist "!test_path!" (
            set "VS_PATH=!test_path!"
            goto :found
        )
    )
)

:found
if "%VS_PATH%"=="" (
    echo [ERROR] Visual Studio vcvars64.bat not found! Install MSVC Build Tools first.
    exit /b 1
)

echo [OK] Found Visual Studio variables script at: "%VS_PATH%"

:: Call the VS environment variables script
call "%VS_PATH%"

echo Compiling resources (icon)...
rc.exe /nologo resource.rc

echo Compiling Native C++ PCManager Agent...
cl.exe /O2 /EHsc /DUNICODE /D_UNICODE main.cpp win_utils.cpp http_client.cpp gui.cpp websocket_client.cpp resource.res /link /OUT:PCManager_Agent.exe /SUBSYSTEM:WINDOWS shell32.lib advapi32.lib gdi32.lib gdiplus.lib psapi.lib ole32.lib user32.lib

if %errorlevel% neq 0 (
    echo [ERROR] Compilation failed!
    exit /b %errorlevel%
)

echo [SUCCESS] PCManager_Agent.exe built successfully!
dir PCManager_Agent.exe


