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

:: التحقق من صلاحيات المدير
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  يفضل تشغيل هذا الملف كمسؤول (Run as Administrator)
    echo.
)

:: تحديد المسار الحالي
set "PROJECT_DIR=%CD%"
echo 📂 مسار المشروع: %PROJECT_DIR%
echo.

:: ================================================
:: الجزء 1: التحقق من وجود Python
:: ================================================
echo [1/7] 🔍 التحقق من وجود Python...
echo.

:: محاولة العثور على Python
set "PYTHON_CMD="
for %%X in (python.exe) do (set "PYTHON_CMD=%%~$PATH:X")
if defined PYTHON_CMD (
    echo ✅ تم العثور على Python في: !PYTHON_CMD!
) else (
    echo ❌ Python غير موجود في PATH!
    echo.
    echo ⬇️  جاري تحميل Python...
    
    :: تحميل Python إذا لم يكن موجوداً
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    set "PYTHON_INSTALLER=%TEMP%\python-installer.exe"
    
    echo ⏳ جاري التحميل من: !PYTHON_URL!
    
    :: استخدام PowerShell للتحميل
    powershell -Command "& { (New-Object System.Net.WebClient).DownloadFile('!PYTHON_URL!', '!PYTHON_INSTALLER!') }"
    
    if exist "!PYTHON_INSTALLER!" (
        echo ✅ تم تحميل Python بنجاح
        echo.
        echo 📦 جاري تثبيت Python (قد يستغرق دقيقة)...
        
        :: تثبيت Python بصمت مع إضافته إلى PATH
        start /wait "" "!PYTHON_INSTALLER!" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
        
        echo ✅ تم تثبيت Python
    ) else (
        echo ❌ فشل تحميل Python
        echo.
        echo يرجى تحميل Python يدوياً من: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

:: الحصول على مسار Python الفعلي
for /f "delims=" %%i in ('where python 2^>nul') do set "PYTHON_PATH=%%i"
if defined PYTHON_PATH (
    echo ✅ Python مثبت على: !PYTHON_PATH!
) else (
    echo ❌ لم نتمكن من العثور على Python بعد التثبيت
    echo يرجى إعادة تشغيل الجهاز والمحاولة مرة أخرى
    pause
    exit /b 1
)

:: عرض إصدار Python
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PY_VERSION=%%i"
echo 📊 !PY_VERSION!
echo.

:: ================================================
:: الجزء 2: إنشاء البيئة الافتراضية
:: ================================================
echo [2/7] 🌐 إنشاء بيئة افتراضية...

if exist "%PROJECT_DIR%\venv\" (
    echo ✅ البيئة الافتراضية موجودة مسبقاً
) else (
    echo ⏳ جاري إنشاء بيئة افتراضية...
    python -m venv "%PROJECT_DIR%\venv"
    if !errorlevel! equ 0 (
        echo ✅ تم إنشاء البيئة الافتراضية بنجاح
    ) else (
        echo ❌ فشل إنشاء البيئة الافتراضية
        pause
        exit /b 1
    )
)
echo.

:: ================================================
:: الجزء 3: تفعيل البيئة الافتراضية
:: ================================================
echo [3/7] 🔌 تفعيل البيئة الافتراضية...

call "%PROJECT_DIR%\venv\Scripts\activate.bat"
if defined VIRTUAL_ENV (
    echo ✅ البيئة مفعلة: !VIRTUAL_ENV!
) else (
    echo ❌ فشل تفعيل البيئة الافتراضية
    pause
    exit /b 1
)
echo.

:: ================================================
:: الجزء 4: تحديث pip وتثبيت المتطلبات
:: ================================================
echo [4/7] 📦 تحديث pip وتثبيت المكتبات...

echo ⏳ تحديث pip...
python -m pip install --upgrade pip >nul 2>&1
echo ✅ تم تحديث pip

echo.
echo 📚 تثبيت المكتبات المطلوبة...

:: قائمة المكتبات المطلوبة
set "LIBRARIES=PyQt6 rapidfuzz"

:: تثبيت كل مكتبة مع عرض التقدم
for %%L in (%LIBRARIES%) do (
    echo    ⏳ جاري تثبيت %%L...
    pip install %%L -q
    if !errorlevel! equ 0 (
        echo    ✅ تم تثبيت %%L
    ) else (
        echo    ❌ فشل تثبيت %%L
        echo.
        echo محاولة تثبيت %%L مع خيارات إضافية...
        pip install %%L --no-cache-dir -q
        if !errorlevel! equ 0 (
            echo    ✅ تم تثبيت %%L بعد المحاولة الثانية
        ) else (
            echo    ⚠️  تحذير: قد تكون هناك مشكلة في %%L
        )
    )
)

:: التحقق من التثبيت
echo.
echo ✅ تم تثبيت جميع المكتبات الأساسية
echo.

:: ================================================
:: الجزء 5: التحقق من بنية المجلدات
:: ================================================
echo [5/7] 📁 التحقق من بنية المجلدات...

:: إنشاء المجلدات المطلوبة إذا لم تكن موجودة
if not exist "%PROJECT_DIR%\Data\JSON\narrators" (
    echo ⏳ إنشاء مجلدات الرواة...
    mkdir "%PROJECT_DIR%\Data\JSON\narrators" 2>nul
    mkdir "%PROJECT_DIR%\Data\JSON\custom_narrators" 2>nul
    echo ✅ تم إنشاء مجلدات الرواة
)

if not exist "%PROJECT_DIR%\Data\BOOKS" (
    echo ⏳ إنشاء مجلدات الكتب...
    mkdir "%PROJECT_DIR%\Data\BOOKS" 2>nul
    mkdir "%PROJECT_DIR%\Data\BOOKS\the_9_books" 2>nul
    mkdir "%PROJECT_DIR%\Data\BOOKS\forties" 2>nul
    echo ✅ تم إنشاء مجلدات الكتب
)

if not exist "%PROJECT_DIR%\info" (
    echo ⏳ إنشاء مجلدات المعلومات...
    mkdir "%PROJECT_DIR%\info" 2>nul
    mkdir "%PROJECT_DIR%\info\APP" 2>nul
    mkdir "%PROJECT_DIR%\info\.amn" 2>nul
    echo ✅ تم إنشاء مجلدات المعلومات
)

echo ✅ بنية المجلدات جاهزة
echo.

:: ================================================
:: الجزء 6: إنشاء ملفات بيانات تجريبية (إذا كانت فارغة)
:: ================================================
echo [6/7] 📝 التحقق من وجود بيانات تجريبية...

:: التحقق مما إذا كان مجلد الرواة فارغاً
dir /b "%PROJECT_DIR%\Data\JSON\narrators\*.json" >nul 2>&1
if !errorlevel! neq 0 (
    echo ⏳ إنشاء ملفات رواة تجريبية...
    
    :: إنشاء ملف راوي تجريبي 1
    (
        echo { 
        echo   "id": 1, 
        echo   "name": "محمد بن إسماعيل البخاري", 
        echo   "basic_info": { 
        echo     "الاسم": "محمد بن إسماعيل البخاري", 
        echo     "الكنية": "أبو عبد الله", 
        echo     "النسب": "الجعفي", 
        echo     "اللقب": "أمير المؤمنين في الحديث", 
        echo     "تاريخ الوفاة": "256 هـ", 
        echo     "طبقة رواة التقريب": "العاشرة", 
        echo     "الرتبة عند ابن حجر": "إمام حافظ" 
        echo   }, 
        echo   "jarh_tadil": [ 
        echo     { 
        echo       "scholar": "ابن حجر العسقلاني", 
        echo       "comment": "إمام أهل الحديث بلا مدافع", 
        echo       "source": "تهذيب التهذيب" 
        echo     } 
        echo   ], 
        echo   "is_custom": false 
        echo }
    ) > "%PROJECT_DIR%\Data\JSON\narrators\1.json"

    :: إنشاء ملف راوي تجريبي 2
    (
        echo { 
        echo   "id": 2, 
        echo   "name": "مسلم بن الحجاج النيسابوري", 
        echo   "basic_info": { 
        echo     "الاسم": "مسلم بن الحجاج النيسابوري", 
        echo     "الكنية": "أبو الحسين", 
        echo     "النسب": "القشيري", 
        echo     "تاريخ الوفاة": "261 هـ", 
        echo     "طبقة رواة التقريب": "العاشرة", 
        echo     "الرتبة عند ابن حجر": "إمام حافظ" 
        echo   }, 
        echo   "jarh_tadil": [], 
        echo   "is_custom": false 
        echo }
    ) > "%PROJECT_DIR%\Data\JSON\narrators\2.json"

    echo ✅ تم إنشاء بيانات رواة تجريبية
)

:: التحقق من وجود صورة الشعار
if not exist "%PROJECT_DIR%\image_1.png" (
    echo ⏳ إنشاء صورة شعار تجريبية...
    :: إنشاء صورة فارغة (يمكن استبدالها لاحقاً)
    echo دالة مساعدة > "%PROJECT_DIR%\image_1.png"
    echo ✅ تم إنشاء ملف شعار تجريبي
)

echo ✅ البيانات جاهزة
echo.

:: ================================================
:: الجزء 7: تشغيل التطبيق
:: ================================================
echo [7/7] 🚀 تشغيل تطبيق سند...
echo.
echo ⏳ جاري تشغيل التطبيق...
echo.

:: تشغيل التطبيق
start /b python "%PROJECT_DIR%\src\main.py"

:: التحقق من نجاح التشغيل
timeout /t 2 /nobreak >nul
tasklist | findstr /i "python" >nul
if !errorlevel! equ 0 (
    echo ✅ تم تشغيل التطبيق بنجاح!
    echo.
    echo ================================================
    echo 📊 معلومات التشغيل:
    echo ================================================
    echo 📁 مسار المشروع: %PROJECT_DIR%
    echo 🐍 إصدار Python: %PY_VERSION%
    echo 🌐 البيئة الافتراضية: %VIRTUAL_ENV%
    echo 📦 المكتبات: PyQt6, rapidfuzz
    echo 📚 قاعدة البيانات: %PROJECT_DIR%\Data\JSON\narrators\
    echo.
    echo ✅ التطبيق يعمل الآن في نافذة منفصلة
) else (
    echo ❌ فشل تشغيل التطبيق
    echo.
    echo محاولة تشغيل مع وضع التصحيح...
    python "%PROJECT_DIR%\src\main.py" --debug
)

echo.
echo ================================================
echo 📋 خيارات إضافية:
echo ================================================
echo [1] 🔄 إعادة تشغيل التطبيق
echo [2] 🏗️  بناء ملف EXE مستقل
echo [3] 📁 فتح مجلد المشروع
echo [4] ❌ إغلاق
echo.

set /p "CHOICE=اختر رقم (1-4): "

if "%CHOICE%"=="1" (
    echo.
    echo 🔄 جاري إعادة التشغيل...
    taskkill /f /im python.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
    python "%PROJECT_DIR%\src\main.py"
    goto :EOF
)

if "%CHOICE%"=="2" (
    echo.
    echo 🏗️  بناء ملف EXE مستقل...
    pip install pyinstaller -q
    pyinstaller --name=Sanad --windowed --onefile ^
        --add-data "Data;Data" ^
        --add-data "info;info" ^
        --add-data "image_1.png;." ^
        "%PROJECT_DIR%\src\main.py"
    echo.
    echo ✅ تم بناء الملف: %PROJECT_DIR%\dist\Sanad.exe
    pause
    goto :EOF
)

if "%CHOICE%"=="3" (
    echo.
    echo 📁 فتح مجلد المشروع...
    explorer "%PROJECT_DIR%"
    goto :EOF
)

if "%CHOICE%"=="4" (
    echo.
    echo 👋 وداعاً!
    exit /b 0
)

echo.
pause