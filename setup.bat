@echo off

IF DEFINED APPVEYOR echo Setup recognised AppVeyor

IF NOT DEFINED bob_root (
    echo Error bob_root not defined
    exit /b 1
)

IF NOT DEFINED bob_project_root (
    echo Error bob_project_root not defined
    exit /b 1
)

IF NOT DEFINED bob_download_cache_dir (
    echo Error bob_download_cache_dir not defined
    exit /b 1
)

IF NOT DEFINED bob_third_party_dir set bob_third_party_dir=%bob_root%\thirdparty

rem Install 7z
set bob_7z_dir=%bob_third_party_dir%\7-Zip\7z2201-x64
IF NOT EXIST %bob_download_cache_dir%\7z2201-x64.msi curl -L --show-error https://www.7-zip.org/a/7z2201-x64.msi -o %bob_download_cache_dir%\7z2201-x64.msi
IF NOT EXIST %bob_third_party_dir%\7z2201-x64\Files\7-Zip\7z.exe msiexec /a %bob_download_cache_dir%\7z2201-x64.msi /qn TARGETDIR=%bob_7z_dir%\

rem Download Python
IF NOT EXIST %bob_download_cache_dir%\python-3.11.1-embed-amd64.zip curl -L https://www.python.org/ftp/python/3.11.1/python-3.11.1-embed-amd64.zip -o %bob_download_cache_dir%\python-3.11.1-embed-amd64.zip
rem Extract Python
IF NOT EXIST %bob_third_party_dir%\python\python-3.11.1\ %bob_7z_dir%\Files\7-Zip\7z.exe x -y %bob_download_cache_dir%\python-3.11.1-embed-amd64.zip -o%bob_third_party_dir%\python\python-3.11.1\
set bob_python_dir=%bob_third_party_dir%\python\python-3.11.1

%bob_python_dir%/python %bob_root%/toolchain/python/setup_generate_solution.py --bob-root-directory "%bob_root%\"  --bob-project-root-directory "%bob_project_root%\" --bob-thirdparty-directory "%bob_third_party_dir%" --bob-download-cache-directory "%bob_download_cache_dir%" %*
