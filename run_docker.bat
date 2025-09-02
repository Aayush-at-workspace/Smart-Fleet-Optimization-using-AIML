@echo off
echo Starting Smart Fleet Optimization App with Docker...
echo.

echo Step 1: Building Docker image...
docker build -t smart-fleet-app .
if %errorlevel% neq 0 (
    echo Error building Docker image. Make sure Docker Desktop is running.
    pause
    exit /b 1
)

echo.
echo Step 2: Starting the application...
docker run -d -p 5000:5000 --name smart-fleet-container smart-fleet-app
if %errorlevel% neq 0 (
    echo Error starting container. Container might already be running.
    echo Stopping existing container and starting new one...
    docker stop smart-fleet-container 2>nul
    docker rm smart-fleet-container 2>nul
    docker run -d -p 5000:5000 --name smart-fleet-container smart-fleet-app
)

echo.
echo Step 3: Waiting for application to start...
timeout /t 10 /nobreak >nul

echo.
echo Application is now running!
echo Frontend and Backend are both accessible at: http://localhost:5000
echo.
echo API Endpoints:
echo - GET  /zones - Get all taxi zones
echo - POST /complete_ride - Complete a ride and get predictions
echo - GET  /health - Health check
echo.
echo To stop the application, run: docker stop smart-fleet-container
echo To view logs, run: docker logs smart-fleet-container
echo.
pause
