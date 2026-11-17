@echo off
title Push New Lucky Group to GitHub
echo ========================================================
echo   Push New Lucky Group to GitHub for Render Deployment
echo ========================================================
echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/username/new-lucky-sweets.git): "

if "%REPO_URL%"=="" (
    echo Error: No URL provided.
    pause
    exit /b
)

echo.
echo Adding remote origin...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo Pushing to GitHub (main branch)...
git push -u origin main

echo.
echo ========================================================
echo Code pushed successfully!
echo Now open https://dashboard.render.com and click:
echo   1. 'New +' -> 'Web Service'
echo   2. Select your repository
echo   3. Click 'Deploy Web Service'
echo ========================================================
pause
