import os
import sys

sys.path.append(os.path.realpath(os.path.dirname(__file__))) # Allow Local Imports

import library_util as util

util.ignore_missing_subdirectories += 1

from task_manager import BuildTaskManager
from task_build_download import DownloadBuildTask
from task_build_extract import ExtractBuildTask
from task_build_extract import ExtractMSIBuildTask
from task_build_extract import ExtractTarfileBuildTask
from task_build_ninja import NinjaBuildTask
from task_build_gn import GNBuildTask
from task_build_yasm import YasmBuildTask
from task_build_zlib import ZlibBuildTask
from task_build_ffmpeg import FFmpegBuildTask
from task_build_msys2 import MSYS2BuildTask
from task_build_winpix3 import WinPix3BuildTask
from task_build_assimp import AssimpBuildTask
from task_build_cmake import CMakeBuildTask
from task_build_detours import DetoursBuildTask
from task_build_iced_x86 import IcedX86BuildTask
from task_build_llvm import LLVMBuildTask
from task_build_download import download_extract_task
from task_build_download import download_copy_task
from task_build_copy import CopyBuildTask

util.async_start()

_7z_directory = os.path.join(util.get_thirdparty_dir(), '7-Zip/7z2201-x64/Files/7-Zip')
_7z_task = download_extract_task(ExtractMSIBuildTask,
    'https://www.7-zip.org/a/7z2201-x64.msi',
    '7z2201-x64.msi',
    _7z_directory)

bcs_ewdk_directory = os.path.join(util.get_thirdparty_dir(), 'EWDK/EWDK_ni_release_svc_prod1_22621_220804-1759')
ewdk_task = download_extract_task(ExtractBuildTask,
    'https://software-static.download.prss.microsoft.com/dbazure/988969d5-f34g-4e03-ac9d-1f9786c66749/EWDK_ni_release_svc_prod1_22621_220804-1759.iso',
    'EWDK_ni_release_svc_prod1_22621_220804-1759.iso',
    bcs_ewdk_directory)

#llvm_version = '15.0.6'
#util.llvm_version = llvm_version #TODO: Move this
#llvm_root_directory = util.get_llvm_root_dir()

#llvm_prebuilt_directory = os.path.join(llvm_root_directory, f'llvm-{llvm_version}.prebuilt')
#llvm_prebuilt_task = download_extract_task(ExtractBuildTask,
#    f'https://github.com/llvm/llvm-project/releases/download/llvmorg-{llvm_version}/LLVM-{llvm_version}-win64.exe',
#    f'LLVM-{llvm_version}-win64.exe',
#    llvm_prebuilt_directory,
#    force=not os.path.exists(llvm_prebuilt_directory))
#
#llvm_src_directory = os.path.join(llvm_root_directory, f'llvm-{llvm_version}.src')
#llvm_src_task = download_extract_task(ExtractTarfileBuildTask,
#    f'https://github.com/llvm/llvm-project/releases/download/llvmorg-15.0.6/llvm-{llvm_version}.src.tar.xz',
#    f'llvm-{llvm_version}.src.tar.xz',
#    llvm_root_directory,
#    force=not os.path.exists(llvm_src_directory))

#llvm_debug_task = LLVMBuildTask('debug', llvm_version, [llvm_prebuilt_task, llvm_src_task])
#llvm_release_task = LLVMBuildTask('release', llvm_version, [llvm_prebuilt_task, llvm_src_task])

llvm_configs = util.get_llvm_build_configs() or ['release']
llvm_tasks = [LLVMBuildTask(config, []) for config in llvm_configs]

llvm_directory = os.path.join(util.get_thirdparty_dir(), 'llvm')
llvm_bin_directory = os.path.join(llvm_directory, 'bin')



busybox_task = DownloadBuildTask(
    'https://frippery.org/files/busybox/busybox64.exe', 
    os.path.join(util.get_thirdparty_dir(), 'busybox/busybox64.exe'))

#winpix3_task = WinPix3BuildTask()

cmake_version = '3.25.2'
cmake_extract_directory = os.path.join(util.get_thirdparty_dir(), 'cmake')
cmake_directory = os.path.join(cmake_extract_directory, f'cmake-{cmake_version}-windows-x86_64/bin')
cmake_task = download_extract_task(ExtractBuildTask,
    f'https://github.com/Kitware/CMake/releases/download/v{cmake_version}/cmake-{cmake_version}-windows-x86_64.zip',
    f'cmake-{cmake_version}-windows-x86_64.zip',
    cmake_extract_directory)

cmake_task = CMakeBuildTask([_7z_task])

musl_untar_directory = os.path.join(util.get_thirdparty_dir(), f'musl')
musl_i686_download_extract_task = download_extract_task(ExtractTarfileBuildTask,
    f'https://musl.cc/i686-linux-musl-native.tgz',
    f'i686-linux-musl-native.tgz',
    musl_untar_directory,
    force=not os.path.exists(os.path.join(musl_untar_directory, 'i686-linux-musl-native')))
musl_x86_64_download_extract_task = download_extract_task(ExtractTarfileBuildTask,
    f'https://musl.cc/x86_64-linux-musl-native.tgz',
    f'x86_64-linux-musl-native.tgz',
    musl_untar_directory,
    force=not os.path.exists(os.path.join(musl_untar_directory, 'x86_64-linux-musl-native')))
musl_aarch64_download_extract_task = download_extract_task(ExtractTarfileBuildTask,
    f'https://musl.cc/aarch64-linux-musl-native.tgz',
    f'aarch64-linux-musl-native.tgz',
    musl_untar_directory,
    force=not os.path.exists(os.path.join(musl_untar_directory, 'aarch64-linux-musl-native')))
musl_arm_download_extract_task = download_extract_task(ExtractTarfileBuildTask,
    f'https://musl.cc/arm-linux-musleabi-native.tgz',
    f'arm-linux-musleabi-native.tgz',
    musl_untar_directory,
    force=not os.path.exists(os.path.join(musl_untar_directory, 'arm-linux-musleabi-native')))

wasi_untar_directory = os.path.join(util.get_thirdparty_dir(), f'wasi/wasi-sdk-17')
wasi_directory = os.path.join(wasi_untar_directory, 'wasi-sysroot')
wasi_download_extract_task = download_extract_task(ExtractTarfileBuildTask,
    f'https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-17/wasi-sysroot-17.0.tar.gz',
    f'wasi-sysroot-17.0.tar.gz',
    wasi_untar_directory,
    force=not os.path.exists(wasi_directory))
wasi_exceptions_untar_directory = os.path.join(util.get_thirdparty_dir(), f'wasi/wasi-sdk-17-exceptions')
wasi_exceptions_directory = os.path.join(wasi_exceptions_untar_directory, 'wasi-sysroot')
wasi_exceptions_download_extract_task = download_extract_task(ExtractTarfileBuildTask,
    f'https://github.com/ChimpsAtSea/wasi-sdk/releases/download/wasi-sdk-17-exceptions/wasi-sysroot-17.0.tar.gz',
    f'wasi-sysroot-17.0.tar.gz',
    wasi_exceptions_untar_directory,
    force=not os.path.exists(wasi_exceptions_directory))

directxshadercompiler_directory = os.path.join(util.get_thirdparty_dir(), f'directxshadercompiler/directxshadercompiler')
directxshadercompiler_task = download_extract_task(ExtractBuildTask,
    f'https://github.com/ChimpsAtSea/DirectXShaderCompiler/releases/download/1.0.2139/dxc-artifacts.zip',
    f'dxc-artifacts-1.0.2139.zip',
    directxshadercompiler_directory)

ninja_build_task = NinjaBuildTask([ewdk_task])
gn_build_task = GNBuildTask([ninja_build_task])
msys2_init_task = MSYS2BuildTask()
yasm_build_task = YasmBuildTask([cmake_task, ninja_build_task])

detours_build_tasks = [
    DetoursBuildTask('arm64', 'release', []),
    DetoursBuildTask('arm64', 'debug', []),
    DetoursBuildTask('x64', 'release', []),
    DetoursBuildTask('x64', 'debug', []),
    DetoursBuildTask('x86', 'release', []),
    DetoursBuildTask('x86', 'debug', []) ]

pip_directory = util.get_pip_dir()
pip_task = download_copy_task('https://bootstrap.pypa.io/pip/pip.pyz',
    'pip.pyz',
    pip_directory)

iced_x86_task = IcedX86BuildTask([pip_task])

#zlib_build_task = ZlibBuildTask([cmake_task, ninja_build_task])
#zlib_build_tasks = [
#    ZlibBuildTask('arm64', True, [cmake_task, ninja_build_task]),
#    ZlibBuildTask('arm64', False, [cmake_task, ninja_build_task]),
#    ZlibBuildTask('x64', True, [cmake_task, ninja_build_task]),
#    ZlibBuildTask('x64', False, [cmake_task, ninja_build_task]),
#    ZlibBuildTask('x86', True, [cmake_task, ninja_build_task]),
#    ZlibBuildTask('x86', False, [cmake_task, ninja_build_task]) ]

#TODO build all command
# Automatically Build by GN Loopback see action_build_ffmpeg.py
#ffmpeg_build_tasks = [
#    FFmpegBuildTask('win32', 'aarch64', 'msvc', 'arm64', 'shared', [yasm_build_task, msys2_init_task]),
#    FFmpegBuildTask('win32', 'aarch64', 'msvc', 'arm64', 'static', [yasm_build_task, msys2_init_task]),
#    FFmpegBuildTask('win32', 'x86_64', 'msvc', 'x64', 'shared', [yasm_build_task, msys2_init_task]),
#    FFmpegBuildTask('win32', 'x86_64', 'msvc', 'x64', 'static', [yasm_build_task, msys2_init_task]),
#    FFmpegBuildTask('win32', 'x86_32', 'msvc', 'x86', 'shared', [yasm_build_task, msys2_init_task]),
#    FFmpegBuildTask('win32', 'x86_32', 'msvc', 'x86', 'static', [yasm_build_task, msys2_init_task]) ]

#TODO build all command
# Automatically Build by GN Loopback see action_build_assimp.py
#assimp_build_tasks = [
#    AssimpBuildTask('arm64', True, [cmake_task, ninja_build_task]),
#    AssimpBuildTask('arm64', False, [cmake_task, ninja_build_task]),
#    AssimpBuildTask('x64', True, [cmake_task, ninja_build_task]),
#    AssimpBuildTask('x64', False, [cmake_task, ninja_build_task]),
#    AssimpBuildTask('x86', True, [cmake_task, ninja_build_task]),
#    AssimpBuildTask('x86', False, [cmake_task, ninja_build_task]) ]

BuildTaskManager.run_until_complete()

util.async_end()

util.ignore_missing_subdirectories -= 1
