@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ================================================
:: سند - ملف التثبيت والتشغيل الآلي لنظام ويندوز
:: Sanad - All-in-One Setup and Run Script for Windows
:: ================================================

title 🚀 سند - برنامج رسم الأسانيد | Sanad Hadith App

:: تعيين الألوان
color 0F

:: الشعار
echo.
echo    ╔══════════════════════════════════════════════════════════════╗
echo    ║                                                              ║
echo    ║     ███████╗ █████╗ ███╗   ██╗ █████╗ ██████╗                ║
echo    ║     ██╔════╝██╔══██╗████╗  ██║██╔══██╗██╔══██╗               ║
echo    ║     ███████╗███████║██╔██╗ ██║███████║██║  ██║               ║
echo    ║     ╚════██║██╔══██║██║╚██╗██║██╔══██║██║  ██║               ║
echo    ║     ███████║██║  ██║██║ ╚████║██║  ██║██████╔╝               ║
echo    ║     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═════╝                ║
echo    ║                                                              ║
echo    ║                    📚 برنامج سند - رسم الأسانيد                      ║
echo    ║              Sanad - Hadith Chain Visualization              ║
echo    ║                                                              ║
echo    ╚══════════════════════════════════════════════════════════════╝
echo.

pip install pyinstaller PyQt6 rapidfuzz && pyinstaller --name=Sanad --onefile --windowed --add-data "Data;Data" --add-data "info;info" --add-data "image_1.png;." src/main.py && echo ✅ تم! الملف في dist\Sanad.exe && start dist