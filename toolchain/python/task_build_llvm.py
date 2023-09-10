import os
import sys
import subprocess
import shlex
from task_manager import VisualCPPBuildTask
import library_util as util
import library_project_setup as project_setup
import pathlib

class LLVMBuildTask(VisualCPPBuildTask):
    def __init__(self, target_config : str, _parent_tasks = []):
        super().__init__('LLVMBuildTask', 'x64', _parent_tasks)
        self.target_config = target_config
        
        util.ignore_missing_subdirectories += 1
        util.ignore_missing_filepaths += 1

        self.source_directory = util.get_llvm_project_dir('llvm')
        self.build_folder_name = f'llvm_build_{self.target_config}_{self.msvc_target}'
        self.build_directory = util.get_llvm_build_dir(self.build_folder_name)
        self.llvm_build_stamp_filepath = os.path.join(self.build_directory, 'llvm_build_stamp.stamp')
        self.llvm_cmake_stamp_filepath = os.path.join(self.build_directory, 'llvm_cmake_stamp.stamp')
        
        self.configuration = project_setup.vs_configuration_to_cmake_configuration(target_config)
        
        util.ignore_missing_subdirectories -= 1
        util.ignore_missing_filepaths -= 1

    def build(self):
        super().build()

        is_llvm_built = os.path.exists(self.llvm_build_stamp_filepath)
        is_cmake_built = os.path.exists(self.llvm_cmake_stamp_filepath)
        is_all_built = all([is_llvm_built, is_cmake_built])
        
        if not is_all_built:

            paths = [
                #os.path.join(util.get_thirdparty_dir(), 'ninja'),
            ]
            self.environment['PATH'] = ';'.join([self.environment['PATH']] + paths)

            if not os.path.exists(self.build_directory):
                os.makedirs(self.build_directory)

            ninja = util.get_ninja()

            if not is_cmake_built:
                cmake = util.get_cmake()
                cmake_args = [
                    cmake,
                    '-S', self.source_directory,
                    '-B', self.build_directory,
                    '-G', 'Ninja',
                    '--log-level=NOTICE',
                    '-Wno-dev',
                    '-Wno-deprecated',

                    '-DCMAKE_C_COMPILER=cl',
                    '-DCMAKE_CXX_COMPILER=cl',
                    '-DCMAKE_DEBUG_POSTFIX:STRING=',
                    f'-DCMAKE_MAKE_PROGRAM={ninja}',
                    f'-DCMAKE_BUILD_TYPE:STRING={self.configuration}',

                    # Disable ASLR for Build Tools
                    '-DCMAKE_EXE_LINKER_FLAGS:STRING="/DYNAMICBASE:NO"',

                    '-DLLVM_ENABLE_PROJECTS=clang;lld',
                    '-DLLVM_ENABLE_OCAMLDOC:BOOL=0',
                    '-DLLVM_INCLUDE_BENCHMARKS:BOOL=0',
                    '-DLLVM_INCLUDE_DOCS:BOOL=0',
                    '-DLLVM_INCLUDE_EXAMPLES:BOOL=0',
                    #'-DLLVM_INCLUDE_RUNTIMES:BOOL=0',
                    '-DLLVM_INCLUDE_TESTS:BOOL=0',
                    #'-DLLVM_INCLUDE_TOOLS:BOOL=0',
                    #'-DLLVM_INCLUDE_UTILS:BOOL=0',
                    '-DLLVM_BUILD_LLVM_C_DYLIB:BOOL=0',
                    #'-DLLVM_BUILD_RUNTIME:BOOL=0',
                    #'-DLLVM_BUILD_RUNTIMES:BOOL=0',
                    '-DLLVM_BUILD_TESTS:BOOL=0',
                    #'-DLLVM_BUILD_TOOLS:BOOL=0',
                    #'-DLLVM_BUILD_UTILS:BOOL=0',

                    '-DBENCHMARK_INSTALL_DOCS:BOOL=0',
                    '-DBENCHMARK_USE_BUNDLED_GTEST:BOOL=0',

                    '-DCLANG_DEFAULT_CXX_STDLIB:STRING=',
                    '-DCLANG_DEFAULT_LINKER:STRING=',
                    '-DCLANG_DEFAULT_OBJCOPY:STRING=objcopy',
                    '-DCLANG_DEFAULT_OPENMP_RUNTIME:STRING=libomp',
                    '-DCLANG_DEFAULT_RTLIB:STRING=',
                    '-DCLANG_DEFAULT_UNWINDLIB:STRING=',
                    '-DCLANG_ENABLE_ARCMT:BOOL=0',
                    '-DCLANG_ENABLE_STATIC_ANALYZER:BOOL=0',
                    '-DCLANG_INCLUDE_DOCS:BOOL=0',
                    '-DCLANG_INCLUDE_TESTS:BOOL=0',
                    '-DCLANG_INSTALL_SCANBUILD:BOOL=0',
                    '-DCLANG_INSTALL_SCANVIEW:BOOL=0',

                    f'-DMSVC_DIA_SDK_DIR:PATH={util.get_ewdk_dir("Program Files/Microsoft Visual Studio/2022/BuildTools/DIA SDK")}',
                ]
                if util.bob_prebuild_use_lto:
                    cmake_args += [ '-DCMAKE_INTERPROCEDURAL_OPTIMIZATION:BOOL=1' ]

                print(f'CMake generating LLVM build files {self.build_folder_name}')
                sys.stdout.flush()
                process = subprocess.Popen(cmake_args, env=self.environment, cwd=self.build_directory)
                process.wait()
                if process.returncode:
                    print(cmake_args)
                    raise Exception("CMake Failed")
                else:
                    pathlib.Path(self.llvm_cmake_stamp_filepath).touch()

            #NOTE: We do this because there is very little speed advantage
            # to using hyperthreading to build LLVM and it cuts the ram
            # usage in half
            restricted_thread_count = util.get_restricted_thread_count()
            print(f"Using {restricted_thread_count} threads")

            ninja_args = [ninja, '-C', self.build_directory, '-j', str(restricted_thread_count)]
            process = subprocess.Popen(ninja_args, env=self.environment)
            process.wait()
            if process.returncode:
                print(ninja_args)
                raise Exception("Ninja Failed")
            else:
                pathlib.Path(self.llvm_build_stamp_filepath).touch()
