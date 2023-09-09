
import os
import subprocess
import shutil
from task_manager import VisualCPPBuildTask
import library_util as util

class DetoursBuildTask(VisualCPPBuildTask):
    def __init__(self, msvc_target, msvc_configuration, _parent_tasks = []):
        super().__init__('DetoursBuildTask', msvc_target, _parent_tasks)

        self.msvc_target = msvc_target
        self.msvc_configuration = msvc_configuration

    def build(self):
        super().build()

        is_debug = self.msvc_configuration == 'debug'
        suffix = 'Debug' if is_debug else ''
        lib_folder = f'lib.{self.msvc_target.upper()}{suffix}'
        bin_folder = f'bin.{self.msvc_target.upper()}{suffix}'
        
        source_directory = os.path.join(util.get_thirdparty_dir(), f'detours/detours/src')
        build_directory = os.path.join(util.get_thirdparty_dir(), f'detours/detours')
        build_lib_directory = os.path.join(build_directory, lib_folder)
        build_bin_directory = os.path.join(build_directory, bin_folder)
        output_directory = os.path.join(util.get_thirdparty_dir(), f'detours/detours_build')
        output_lib_directory = os.path.join(output_directory, lib_folder)
        output_bin_directory = os.path.join(output_directory, bin_folder)
        output_lib_file = os.path.join(output_lib_directory, f'detours.lib')
        
        if os.path.exists(output_lib_file):
            return # Don't rebuild

        paths = [
            
        ]
        self.environment['PATH'] = ';'.join([self.environment['PATH']] + paths)

        if not os.path.exists(build_directory):
            os.makedirs(build_directory)

        nmake = self.get_nmake()

        args = [nmake]
        if is_debug:
            args += [ 'DETOURS_CONFIG=Debug' ]
        args += [ 'clean' ]
        process = subprocess.Popen(args, env=self.environment, cwd=source_directory)
        process.wait()
        
        args = [nmake]
        if is_debug:
            args += [ 'DETOURS_CONFIG=Debug' ]
        args += [ 'all' ]
        process = subprocess.Popen(args, env=self.environment, cwd=source_directory)
        process.wait()
        
        util.dprint('    source_directory a>', os.path.exists(source_directory), source_directory)
        util.dprint('     build_directory a>', os.path.exists(build_directory), build_directory)
        util.dprint(' build_lib_directory a>', os.path.exists(build_lib_directory), build_lib_directory)
        util.dprint('    output_directory a>', os.path.exists(output_directory), output_directory)
        util.dprint('     output_lib_file a>', os.path.exists(output_lib_file), output_lib_file)
        util.dprint('output_lib_directory a>', os.path.exists(output_lib_directory), output_lib_directory)
        util.dprint('output_bin_directory a>', os.path.exists(output_bin_directory), output_bin_directory)

        if os.path.exists(output_lib_directory):
            shutil.rmtree(output_lib_directory)
        if os.path.exists(output_bin_directory):
            shutil.rmtree(output_bin_directory)

        util.dprint('output_lib_directory b>', os.path.exists(output_lib_directory), output_lib_directory)
        util.dprint('output_bin_directory b>', os.path.exists(output_bin_directory), output_bin_directory)

        shutil.move(build_lib_directory, output_directory)
        shutil.move(build_bin_directory, output_directory)

        util.dprint('output_lib_directory c>', os.path.exists(output_lib_directory), output_lib_directory)
        util.dprint('output_bin_directory c>', os.path.exists(output_bin_directory), output_bin_directory)

        args = [nmake]
        if is_debug:
            args += [ 'DETOURS_CONFIG=Debug' ]
        args += [ 'realclean' ]
        process = subprocess.Popen(args, env=self.environment, cwd=source_directory)
        process.wait()
