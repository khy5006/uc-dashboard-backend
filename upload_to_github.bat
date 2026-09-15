@echo off
echo Uploading backend to GitHub...
echo.

cd /d "C:\Users\Samsung\Cohort\UC\backend"

git init
git add .
git commit -m "Initial commit - UC Dashboard Backend"
git branch -M main
git remote add origin https://github.com/khy5006/uc-dashboard-backend.git
git push -u origin main

echo.
echo Done! Your code is now on GitHub.
pause
