import os
import sys
import subprocess
import shlex
from task_manager import BuildTask
import library_util as util
import library_project_setup as project_setup

class PipTOMLBuildTask(BuildTask):
    def __init__(self, _parent_tasks = []):
        super().__init__('PipTOMLBuildTask', _parent_tasks)
        
    def build(self):
        super().build()

        py_path = os.path.join(util.get_python_dir(), 'Lib/site-packages/toml/__init__.py')
        if os.path.exists(py_path):
            return # nothing to do

        args = [ util.get_python(), util.get_pip(), 'install', '-U', 'toml==0.10.2' ]
        util.dprint(' '.join(args))

        process = subprocess.Popen(args)
        process.wait()
