@echo off
REM AI News Aggregator - Deploy Script (Windows)
REM Usage: deploy.bat [command]
REM Commands: deploy, build, start, stop, restart, logs, migrate

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
cd /d "%PROJECT_ROOT%"

set "COMMAND=%1"
if "%COMMAND%"=="" set "COMMAND=deploy"

echo ======================================
echo   AI News Aggregator Deploy Script
echo ======================================
echo Command: %COMMAND%
echo Project Root: %PROJECT_ROOT%
echo.

if "%COMMAND%"=="deploy" goto deploy
if "%COMMAND%"=="build" goto build
if "%COMMAND%"=="start" goto start
if "%COMMAND%"=="stop" goto stop
if "%COMMAND%"=="restart" goto restart
if "%COMMAND%"=="logs" goto logs
if "%COMMAND%"=="migrate" goto migrate

:deploy
echo [1/5] Checking prerequisites...
where docker >nul 2>nul
if errorlevel 1 (
    echo Error: Docker is not installed.
    exit /b 1
)
where docker-compose >nul 2>nul
if errorlevel 1 (
    docker compose version >nul 2>nul
    if errorlevel 1 (
        echo Error: Docker Compose is not installed.
        exit /b 1
    )
)
echo Prerequisites OK.
echo.

echo [2/5] Building Docker images...
docker-compose build
if errorlevel 1 (
    echo Error: Build failed.
    exit /b 1
)
echo.

echo [3/5] Starting services...
docker-compose up -d
if errorlevel 1 (
    echo Error: Failed to start services.
    exit /b 1
)
echo.

echo [4/5] Waiting for services to be healthy...
call :wait_for_service "ai-news-db" "pg_isready"
call :wait_for_backend
call :wait_for_frontend
echo.

echo [5/5] Deployment complete!
goto show_status

:build
echo Building Docker images...
docker-compose build
goto :eof

:start
echo Starting services...
docker-compose up -d
goto wait_and_show

:stop
echo Stopping services...
docker-compose down
goto :eof

:restart
echo Restarting services...
docker-compose restart
goto wait_and_show

:logs
echo Showing logs (Ctrl+C to exit)...
if "%2"=="" (
    docker-compose logs -f
) else (
    docker-compose logs -f %2
)
goto :eof

:migrate
echo Running database migrations...
docker-compose exec backend python -m alembic upgrade head
goto :eof

:wait_and_show
echo Waiting for services...
call :wait_for_backend
call :wait_for_frontend
:show_status
echo.
echo ======================================
echo   Deployment Status
echo ======================================
echo.
docker-compose ps
echo.
echo URLs:
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
goto :eof

:wait_for_service
set "SERVICE=%1"
set "CHECK_CMD=%2"
echo Waiting for %SERVICE%...
for /L %%i in (1,1,30) do (
    docker exec %SERVICE% %CHECK_CMD% >nul 2>nul
    if not errorlevel 1 (
        echo %SERVICE% is ready.
        exit /b 0
    )
    timeout /t 2 /nobreak >nul
)
echo Warning: %SERVICE% may not be ready.
exit /b 0

:wait_for_backend
echo Waiting for backend...
for /L %%i in (1,1,30) do (
    curl -s http://localhost:8000/api/health >nul 2>nul
    if not errorlevel 1 (
        echo Backend is ready.
        exit /b 0
    )
    timeout /t 2 /nobreak >nul
)
echo Warning: Backend may not be ready.
exit /b 0

:wait_for_frontend
echo Waiting for frontend...
for /L %%i in (1,1,30) do (
    curl -s http://localhost:3000 >nul 2>nul
    if not errorlevel 1 (
        echo Frontend is ready.
        exit /b 0
    )
    timeout /t 2 /nobreak >nul
)
echo Warning: Frontend may not be ready.
exit /b 0

endlocal
