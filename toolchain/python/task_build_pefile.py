import os
import sys
import subprocess
import shlex
from task_manager import BuildTask
import library_util as util
import library_project_setup as project_setup

class PEFileBuildTask(BuildTask):
    def __init__(self, _parent_tasks = []):
        super().__init__('PEFileBuildTask', _parent_tasks)
        
    def build(self):
        super().build()
        
        pyd_path = os.path.join(util.get_python_dir(), 'Lib/site-packages/pefile.py')
        if os.path.exists(pyd_path):
            return # nothing to do

        args = [ util.get_python(), util.get_pip(), 'install', '-U', 'pefile==2023.2.7' ]
        util.dprint(' '.join(args))

        process = subprocess.Popen(args)
        process.wait()
