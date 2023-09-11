
import os
import subprocess
from task_manager import VisualCPPBuildTask
import library_util as util

class NinjaBuildTask(VisualCPPBuildTask):
    def __init__(self, _parent_tasks = []):
        super().__init__('NinjaBuildTask', "x64", _parent_tasks)

    def build(self):
        super().build()

        util.ignore_missing_filepaths += 1
        ninja = util.get_ninja()
        util.ignore_missing_filepaths -= 1

        if not util.force_ninja_rebuild() and os.path.exists(ninja):
            return # Don't rebuild
        
        source_directory = os.path.join(util.get_thirdparty_dir(), f'ninja/ninja')
        build_directory = os.path.join(util.get_thirdparty_dir(), f'ninja/ninja_build')

        paths = [
            #os.path.join(util.get_thirdparty_dir(), 'ninja'),
        ]
        self.environment['PATH'] = ';'.join([self.environment['PATH']] + paths)

        self.environment['CL'] = ' '.join([self.environment['CL']] + ['/wd4005', '/wd4244', '/wd4267', '/wd4312'])

        self.environment['PYTHONWARNINGS'] = 'ignore::DeprecationWarning'

        if not os.path.exists(build_directory):
            os.makedirs(build_directory)

        python = util.get_python()
        args = [python, os.path.join(source_directory, 'configure.py'), '--bootstrap']
        process = subprocess.Popen(args, env=self.environment, cwd=build_directory)
        process.wait()
