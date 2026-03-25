@echo off
echo ========================================
echo   Stopping RAG Monitoring Stack
echo ========================================
echo.

echo Stopping all services...
docker-compose down

echo.
echo Removing unused containers and networks...
docker system prune -f

echo.
echo ✅ All services stopped successfully!
echo.
echo To start again, run: start_docker_monitoring.bat
echo ========================================

pause