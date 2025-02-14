import os
import sys
import time
import asyncio
import platform
import fnmatch
import argparse
import inspect
from typing import Union, Callable, Iterable, Any, TypeVar, TypeAlias, NewType
import multiprocessing
import subprocess

ignore_missing_subdirectories = 0
ignore_missing_filepaths = 0

def argparse_is_directory(argument, directory):
    directory = os.path.abspath(directory)
    if not os.path.exists(directory):
        raise Exception(f'Directory for argument {argument} does not exist', directory)
    return directory

class BobArgumentParser(argparse.ArgumentParser):
    _T = TypeVar("_T")
    _ActionStr: TypeAlias = str
    _NArgsStr: TypeAlias = str
    _SUPPRESS_T = NewType("_SUPPRESS_T", str)

    def add_dir_argument(
        self,
        name: str,
        required: bool = False
    ) -> argparse.Action:
        return argparse.ArgumentParser.add_argument(self, name, type=lambda d : argparse_is_directory(name, d), required = required)

parser = BobArgumentParser()

cmd_bob_root_directory = '--bob-root-directory'
parser.add_dir_argument(cmd_bob_root_directory, required=True)

cmd_bob_download_cache_directory = '--bob-download-cache-directory'
parser.add_dir_argument(cmd_bob_download_cache_directory, required=True)

cmd_bob_thirdparty_directory = '--bob-thirdparty-directory'
parser.add_dir_argument(cmd_bob_thirdparty_directory, required=True)

cmd_bob_project_root_directory = '--bob-project-root-directory'
parser.add_dir_argument(cmd_bob_project_root_directory, required=True)

cmd_bob_solution_pretty_name = '--bob-solution-pretty-name'
parser.add_argument(cmd_bob_solution_pretty_name)

cmd_bob_solution_namespace = '--bob-solution-namespace'
parser.add_argument(cmd_bob_solution_namespace)

cmd_bob_use_clang_frontend = '--bob-use-clang-frontend'
parser.add_argument(cmd_bob_use_clang_frontend)

cmd_bob_build_arch = '--bob-build-arch'
parser.add_argument(cmd_bob_build_arch, type=str, choices=['x86', 'x64', 'arm', 'arm64', 'webassembly'])

cmd_bob_build_target = '--bob-build-target'
parser.add_argument(cmd_bob_build_target, type=str, choices=['all', 'windows', 'linux', 'webassembly'])

cmd_bob_enable_profile = '--bob-enable-profile'
parser.add_argument(cmd_bob_enable_profile, type=str)

cmd_bob_prebuild_force = '--bob-prebuild-force'
parser.add_argument(cmd_bob_prebuild_force, type=str)

cmd_bob_prebuild_max_threads = '--bob-prebuild-max-threads'
parser.add_argument(cmd_bob_prebuild_max_threads, type=int)

cmd_bob_prebuild_use_lto = '--bob-prebuild-use-lto'
parser.add_argument(cmd_bob_prebuild_use_lto, type=str)

cmd_bob_required_modules = '--bob-required-modules'
parser.add_argument(cmd_bob_required_modules, type=str)

cmd_bob_use_invalid_files = '--bob-use-invalid-files'
parser.add_argument(cmd_bob_use_invalid_files, type=str)

cmd_llvm_build_configs = '--llvm-build-configs'
parser.add_argument(cmd_llvm_build_configs, type=str)

cmd_gn_target_os = '--gn-target-os'
parser.add_argument(cmd_gn_target_os, type=str)

cmd_gn_target_config = '--gn-target-config'
parser.add_argument(cmd_gn_target_config, type=str)

cmd_gn_target_link_config = '--gn-target-link-config'
parser.add_argument(cmd_gn_target_link_config, type=str)

cmd_gn_target_cpu = '--gn-target-cpu'
parser.add_argument(cmd_gn_target_cpu, type=str)

cmd_gn_root_build_dir = '--gn-root-build-dir'
parser.add_dir_argument(cmd_gn_root_build_dir)

cmd_gn_root_gen_dir = '--gn-root-gen-dir'
parser.add_dir_argument(cmd_gn_root_gen_dir)

cmd_gn_root_out_dir = '--gn-root-out-dir'
parser.add_dir_argument(cmd_gn_root_out_dir)

cmd_gn_target_gen_dir = '--gn-target-gen-dir'
parser.add_dir_argument(cmd_gn_target_gen_dir)

cmd_gn_target_out_dir = '--gn-target-out-dir'
parser.add_dir_argument(cmd_gn_target_out_dir)

cmd_gn_target_src_dir = '--gn-target-src-dir'
parser.add_dir_argument(cmd_gn_target_src_dir)

cmd_tool_engine = '--tool-engine'
parser.add_argument(cmd_tool_engine, type=str)

cmd_tool_platform = '--tool-platform'
parser.add_argument(cmd_tool_platform, type=str)

cmd_tool_build = '--tool-build'
parser.add_argument(cmd_tool_build, type=str)

cmd_tool_dxc_passthrough = '--tool-dxc-passthrough'
parser.add_argument(cmd_tool_dxc_passthrough, type=str)

cmd_tool_inputs = '--tool-inputs'
parser.add_argument(cmd_tool_inputs, type=str)

cmd_tool_outputs = '--tool-outputs'
parser.add_argument(cmd_tool_outputs, type=str)

cmd_tool_sources = '--tool-sources'
parser.add_argument(cmd_tool_sources, type=str)

cmd_tool_output_subdirectory = '--tool-output-subdirectory'
parser.add_argument(cmd_tool_output_subdirectory, type=str)

cmd_debug = '--debug'
parser.add_argument(cmd_debug, action='store_true')

cmd_build_gn = '--build-gn'
parser.add_argument(cmd_build_gn, action='store_true')

args, unknown = parser.parse_known_args()

def get_argument(argument_name : str, default = None) -> str:
    argument = getattr(args, argument_name, default)
    if (default is None) and (argument is None):
        raise Exception(f'{argument_name} was not found')
    return argument or default

def parse_argument_bool(argument : str):
    if not argument:
        return False
    return any(argument.lower() == s for s in ['true', 'yes', '1'])

build_gn : bool = get_argument('build_gn', False)
debug = get_argument('debug', False)
bob_prebuild_use_lto = parse_argument_bool(get_argument('bob_prebuild_use_lto', 'false'))
bob_use_clang_frontend = parse_argument_bool(get_argument('bob_use_clang_frontend', 'false'))
bob_use_invalid_files = parse_argument_bool(get_argument('bob_use_invalid_files', 'false'))


def dprint(*args):
    if debug:
        print(*args)

if unknown:
    print("Unknown arguments", unknown)


build_target = args.bob_build_target
build_all = bool((build_target == 'all'))
build_windows = bool(build_all or (build_target == 'windows'))
build_linux = bool(build_all or (build_target == 'linux'))
build_webassembly = bool(build_all or (build_target == 'webassembly'))

is_host_windows = platform.system() == 'Windows'
is_host_linux = platform.system() == 'Linux'
host_executable_suffix = '.exe' if is_host_windows else ''

if not any([build_all, build_windows, build_linux, build_webassembly]):
    if is_host_windows:
        build_windows = True
        build_target = 'windows'
    elif is_host_linux:
        build_linux = True
        build_target = 'linux'

def get_directory_argument(argument_name : str, subdirectory : str):
    base_directory = get_argument(argument_name)
    if not os.path.exists(base_directory):
        raise Exception(f'Base directory for argument {argument_name} does not exist', argument_name, base_directory)
    if not subdirectory:
        return base_directory
    directory = os.path.join(base_directory, subdirectory)
    if ignore_missing_subdirectories == 0 and not os.path.exists(directory):
        raise Exception(f'Subdirectory for argument {argument_name} does not exist', argument_name, base_directory, subdirectory, directory)
    return directory


def get_root_dir(subdirectory : str = None) -> str:
    return get_directory_argument('bob_root_directory', subdirectory)
def get_thirdparty_dir(subdirectory : str = None) -> str:
    return get_directory_argument('bob_thirdparty_directory', subdirectory)
def get_download_cache_dir(subdirectory : str = None) -> str:
    return get_directory_argument('bob_download_cache_directory', subdirectory)
def get_project_root_dir(subdirectory : str = None) -> str:
    return get_directory_argument('bob_project_root_directory', subdirectory)
def get_solution_pretty_name() -> str:
    return get_argument('bob_solution_pretty_name')
def get_solution_namespace() -> str:
    return get_argument('bob_solution_namespace')
def get_build_target() -> tuple[str, None]:
    return get_argument('bob_build_target', build_target)
def get_build_arch() -> tuple[str, None]:
    return get_argument('bob_build_arch', '') or None
def get_enable_profile() -> bool:
    return parse_argument_bool(get_argument('bob_enable_profile', 'false'))
def get_gn_target_os() -> str:
    return get_argument('gn_target_os')
def get_gn_target_config() -> str:
    return get_argument('gn_target_config')
def get_gn_target_link_config() -> str:
    return get_argument('gn_target_link_config')
def get_gn_target_cpu() -> str:
    return get_argument('gn_target_cpu')
def get_gn_root_build_dir(subdirectory : str = None):
    return get_directory_argument('gn_root_build_dir', subdirectory)
def get_gn_root_gen_dir(subdirectory : str = None):
    return get_directory_argument('gn_root_gen_dir', subdirectory)
def get_gn_root_out_dir(subdirectory : str = None):
    return get_directory_argument('gn_root_out_dir', subdirectory)
def get_gn_target_gen_dir(subdirectory : str = None):
    return get_directory_argument('gn_target_gen_dir', subdirectory)
def get_gn_target_out_dir(subdirectory : str = None):
    return get_directory_argument('gn_target_out_dir', subdirectory)
def get_gn_target_src_dir(subdirectory : str = None):
    return get_directory_argument('gn_target_src_dir', subdirectory)
def get_tool_engine():
    return get_argument('tool_engine')
def get_tool_platform():
    return get_argument('tool_platform')
def get_tool_build():
    return get_argument('tool_build')
def get_tool_dxc_passthrough():
    return get_argument('tool_dxc_passthrough')
def get_tool_inputs():
    return get_argument('tool_inputs')
def get_tool_outputs():
    return get_argument('tool_outputs')
def get_tool_sources():
    return get_argument('tool_sources')
def get_tool_output_subdirectory():
    return get_argument('tool_output_subdirectory')

#TODO: Move this out to a better home?

def _get_thirdparty_subdir(name, subdirectory, subpath):
    if not subdirectory:
        raise Exception(f'Requested thirdparty directory is invalid', name, subdirectory)
    directory = os.path.join(get_thirdparty_dir(), subdirectory)
    directory = os.path.abspath(directory)
    if ignore_missing_subdirectories == 0 and not os.path.exists(directory):
        raise Exception(f'Requested thirdparty directory doesn\'t exist', name, subdirectory, directory)
    if subpath is not None:
        directory = os.path.join(directory, subpath)
        if ignore_missing_subdirectories == 0 and not os.path.exists(directory):
            raise Exception(f'Requested thirdparty subdirectory doesn\'t exist', name, subdirectory, subpath, directory)
    return directory

#TODO: Find a better way to get these variables
#llvm_version = None

#TODO: Programatically get these rather than hard code them

def _parse_string_array_argument(argument_name):
    argument_str = get_argument(argument_name, '')
    if not argument_str:
        return []
    argument = argument_str.split(';')
    argument = [a for a in argument if a] # filter
    return argument

def get_llvm_build_configs():
    return _parse_string_array_argument('llvm_build_configs')
def get_force_rebuild_names() -> list[str]:
    return _parse_string_array_argument('bob_prebuild_force')
def get_bob_required_modules():
    return _parse_string_array_argument('bob_required_modules')

def get_gn_dir(subpath : str = None):
    return _get_thirdparty_subdir('gn', 'gn/gn_build', subpath)
def get_ninja_dir(subpath : str = None):
    return _get_thirdparty_subdir('ninja', 'ninja/ninja_build', subpath)
def get_python_dir(subpath : str = None):
    return _get_thirdparty_subdir('python', 'python/python-3.11.1', subpath)
def get_pip_dir(subpath : str = None):
    return _get_thirdparty_subdir('python', 'python/pip', subpath)
def get_ewdk_dir(subpath : str = None):
    return _get_thirdparty_subdir('ewdk', 'EWDK/EWDK_ni_release_svc_prod1_22621_220804-1759', subpath)
def get_msys2_dir(subpath : str = None):
    #TODO: Move this into a configuration file
    msys2_version = 'msys2-base-x86_64-20230127'
    msys2_subdirectory = f'msys2/{msys2_version}/msys64'
    return _get_thirdparty_subdir('msys2', msys2_subdirectory, subpath)
def get_cmake_dir(subpath : str = None):
    return _get_thirdparty_subdir('cmake', 'cmake/cmake-3.25.2-windows-x86_64/bin', subpath)
def get_7z_dir(subpath : str = None):
    return _get_thirdparty_subdir('7z', '7-Zip/7z2201-x64/Files/7-Zip', subpath)
def get_yasm_dir(subpath : str = None):
    return _get_thirdparty_subdir('yasm', None, subpath)
def get_winpix3_dir(subpath : str = None):
    return _get_thirdparty_subdir('winpix3', None, subpath)
def get_ida_sdk_dir(subpath : str = None):
    return _get_thirdparty_subdir('idasdk', 'idasdk/idasdk77', subpath)
def get_rpmalloc_dir(subpath : str = None):
    return _get_thirdparty_subdir('rpmalloc', 'rpmalloc/rpmalloc', subpath)

#TODO Your Ass, My Size-24 Hoof
def get_llvm_root_dir(subpath : str = None):
    return _get_thirdparty_subdir('llvm', 'llvm', subpath)
def get_llvm_project_dir(subpath : str = None):
    return _get_thirdparty_subdir('llvm', 'llvm/llvm-project', subpath)

def get_llvm_build_root_dir(subpath : str = None):
    return _get_thirdparty_subdir('llvm', 'llvm/llvm-build', subpath)
def get_llvm_build_dir(target_config : str, llvm_runtime_library : str, subpath : str = None):
    return _get_thirdparty_subdir('llvm_build', f'llvm/llvm-build/llvm_build_{target_config}_x64_{llvm_runtime_library.lower()}', subpath) 
def get_llvm_build_bin_dir(target_config : str, llvm_runtime_library : str, subpath : str = None):
    return _get_thirdparty_subdir('llvm_build_bin', f'llvm/llvm-build/llvm_build_{target_config}_x64_{llvm_runtime_library.lower()}/bin', subpath)
def get_llvm_build_lib_dir(target_config : str, llvm_runtime_library : str, subpath : str = None):
    return _get_thirdparty_subdir('llvm_build_lib', f'llvm/llvm-build/llvm_build_{target_config}_x64_{llvm_runtime_library.lower()}/lib', subpath)
def get_llvm_build_include_dir(target_config : str, llvm_runtime_library : str, subpath : str = None):
    return _get_thirdparty_subdir('llvm_build_include', f'llvm/llvm-build/llvm_build_{target_config}_x64_{llvm_runtime_library.lower()}/include', subpath)

def _get_thirdparty_executable_exists(directory, filename):
    filepath = os.path.join(directory, filename)
    filepath = os.path.abspath(filepath)
    if ignore_missing_filepaths == 0 and not os.path.exists(filepath):
        raise Exception(f'Requested thirdparty filepath doesn\'t exist', filepath, directory, filename)
    return filepath

default_llvm_config = 'release'
defualt_llvm_msvc_runtime_library = 'MT'

def get_llvm_clang():
    return _get_thirdparty_executable_exists(get_llvm_build_bin_dir(default_llvm_config, defualt_llvm_msvc_runtime_library), f'clang{host_executable_suffix}')
def get_llvm_ar():
    return _get_thirdparty_executable_exists(get_llvm_build_bin_dir(default_llvm_config, defualt_llvm_msvc_runtime_library), f'llvm-ar{host_executable_suffix}')
def get_llvm_ld():
    return _get_thirdparty_executable_exists(get_llvm_build_bin_dir(default_llvm_config, defualt_llvm_msvc_runtime_library), f'lld{host_executable_suffix}')
def get_llvm_lld_link():
    return _get_thirdparty_executable_exists(get_llvm_build_bin_dir(default_llvm_config, defualt_llvm_msvc_runtime_library), f'lld-link{host_executable_suffix}')
def get_llvm_wasm_ld():
    return _get_thirdparty_executable_exists(get_llvm_build_bin_dir(default_llvm_config, defualt_llvm_msvc_runtime_library), f'wasm-ld{host_executable_suffix}')
def get_llvm_ld_lld():
    return _get_thirdparty_executable_exists(get_llvm_build_bin_dir(default_llvm_config, defualt_llvm_msvc_runtime_library), f'ld.lld{host_executable_suffix}')

def get_gn():
    return _get_thirdparty_executable_exists(get_gn_dir(), f'gn{host_executable_suffix}')
def get_ninja():
    return _get_thirdparty_executable_exists(get_ninja_dir(), f'ninja{host_executable_suffix}')
def get_python():
    return _get_thirdparty_executable_exists(get_python_dir(), f'python{host_executable_suffix}')
def get_pip():
    return _get_thirdparty_executable_exists(get_pip_dir(), f'pip.pyz')
def get_cmake():
    return _get_thirdparty_executable_exists(get_cmake_dir(), f'cmake{host_executable_suffix}')
def get_7z():
    return _get_thirdparty_executable_exists(get_7z_dir(), f'7z{host_executable_suffix}')

def force_ninja_rebuild():
    force_rebuild_names = get_force_rebuild_names()
    return 'ninja' in force_rebuild_names

class BobFileInvalidSize(Exception):
    def __init__(self, message : str, expected : int, got : int):
        super().__init__(f'\n'.join([message, f'expected:{expected}', f'     got:{got}', f'add {cmd_bob_use_invalid_files} to override']))

class BobFileInvalidHash(Exception):
    def __init__(self, message : str, expected : str, got : str):
        super().__init__(f'\n'.join([message, f'expected:{expected}', f'     got:{got}', f'add {cmd_bob_use_invalid_files} to override']))

#TODO: This is terrible, but everything I've tried from os/multiprocessing returns the local count
def _get_physical_core_count():
    if is_host_windows:
        command = 'wmic cpu get NumberOfCores'
        result = subprocess.run(command, stdout=subprocess.PIPE, shell=True, text=True)
        output_lines = result.stdout.strip().split('\n')
        if len(output_lines) == 3:
            return max(1, int(output_lines[2]))
    return multiprocessing.cpu_count()
physical_core_count = _get_physical_core_count()
def get_physical_core_count():
    return max(1, physical_core_count)
def get_restricted_thread_count():
    bob_prebuild_max_threads = getattr(args, 'bob_prebuild_max_threads')
    return max(1, min(bob_prebuild_max_threads or physical_core_count, physical_core_count))

def pretty_print_dict(
        input_dictionary,
        indent=1,
        depth=0
):
    # Bool flag to add comma's after first item in dict.
    needs_comma = False
    # String for any dict will start with a '{'
    return_string = '\t' * depth + '{\n'
    # Iterate over keys and values, building the full string out.
    for key, value in input_dictionary.items():
        # Start with key. If key follows a previous item, add comma.
        if needs_comma:
            return_string = return_string + ',\n' + '\t' * (depth + 1) + str(key) + ': '
        else:
            return_string = return_string + '\t' * (depth + 1) + str(key) + ': '
        # If the value is a dict, recursively call function.
        if isinstance(value, dict):
            return_string = return_string + '\n' + pretty_print_dict(value, depth=depth+2)
        else:
            return_string = return_string + '\t' * indent + str(value).replace('\n', '\n' + '\t' * (depth + 1))
        # After first line, flip bool to True to make sure commas make it.
        needs_comma = True
    # Complete the dict with a '}'
    return_string = return_string + '\n' + '\t' * depth + '}'
    # Return dict string.
    return return_string

def timer_func(func):
    def function_timer(*args, **kwargs):
        start = time.time()
        value = func(*args, **kwargs)
        end = time.time()
        runtime = end - start
        msg = '{func} {time}ms'
        print(msg.format(func = func.__name__,time = runtime * 1000))
        return value
    return function_timer

def execute_async_task(function, result_count = 0):
    loop = asyncio.get_event_loop()
    if result_count:
        result_wrapper = []
        for index in range(result_count):
            result_wrapper.append(None)
        loop.run_until_complete(function(result_wrapper))
        return result_wrapper
    else:
        loop.run_until_complete(function())

def async_start():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

def async_end():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        loop.close()

def write_file_if_changed(file_path, lines):
    new_content = '\n'.join(lines)
    try:
        with open(file_path, 'r') as existing_file:
            current_content = existing_file.read()
            if current_content == new_content:
                return False
    except FileNotFoundError:
        pass
    
    with open(file_path, 'w') as new_file:
        new_file.write(new_content)
        return True

def filesystem_get_files_recursive(dir_path : str, file_types : list[str] = []) -> list[str]:
    files = []
    #if not os.path.isabs(dir_path):
    #    dir_path = os.path.abspath(dir_path)
    if file_types:
        for root, dirnames, filenames in os.walk(dir_path):
            for file_type in file_types:
                for filename in fnmatch.filter(filenames, file_type):
                    files.append(os.path.join(root, filename))
    else:
        for root, dirnames, filenames in os.walk(dir_path):
            for filename in filenames:
                files.append(os.path.join(root, filename))

    return files

def filesystem_rebase(paths : Union[str, list[str]], base : str):
    if isinstance(paths, str):
        return os.path.relpath(paths, base)
    else:
        rel_paths = []
        for path in paths:
            rel_paths.append(os.path.relpath(path, base))
        return rel_paths

def filesystem_rebase_root(paths : Union[str, list[str]]):
    return filesystem_rebase(paths, get_project_root_dir())
