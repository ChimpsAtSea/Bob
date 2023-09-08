@echo off
cls

IF NOT DEFINED bob_root set bob_root=%~dp0
IF NOT DEFINED bob_project_root set bob_project_root=%~dp0

IF DEFINED BOB_DOWNLOAD_CACHE set bob_download_cache_dir=%BOB_DOWNLOAD_CACHE%
IF NOT DEFINED bob_download_cache_dir set bob_download_cache_dir=%bob_root%downloadcache
IF NOT EXIST %bob_download_cache_dir% mkdir %bob_download_cache_dir%

call setup.bat --bob-solution-pretty-name "Test" --bob-solution-namespace "test" %*
