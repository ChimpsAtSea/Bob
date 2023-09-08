
import os
import subprocess
from task_manager import VisualCPPBuildTask
import library_util as util

class DetoursBuildTask(VisualCPPBuildTask):
    def __init__(self, _parent_tasks = []):
        super().__init__('DetoursBuildTask', "x64", _parent_tasks)

    def build(self):
        super().build()
        
        source_directory = os.path.join(util.get_thirdparty_dir(), f'detours/detours/src')
        build_directory = os.path.join(util.get_thirdparty_dir(), f'detours/detours')
        #build_directory = os.path.join(util.get_thirdparty_dir(), f'detours/detours_build')

        if os.path.exists(os.path.join(build_directory, 'lib.X64/detours.lib')):
            return # Don't rebuild

        paths = [
            
        ]
        self.environment['PATH'] = ';'.join([self.environment['PATH']] + paths)

        if not os.path.exists(build_directory):
            os.makedirs(build_directory)

        nmake = self.get_nmake()
        process = subprocess.Popen([nmake], env=self.environment, cwd=source_directory)
        process.wait()
