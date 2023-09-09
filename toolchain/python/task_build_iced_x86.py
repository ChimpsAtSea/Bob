import os
import sys
import subprocess
import shlex
from task_manager import BuildTask
import library_util as util
import library_project_setup as project_setup

class IcedX86BuildTask(BuildTask):
    def __init__(self, _parent_tasks = []):
        super().__init__('IcedX86BuildTask', _parent_tasks)
        
    def build(self):
        super().build()
        
        pyd_path = os.path.join(util.get_python_dir(), 'Lib/site-packages/iced_x86/_iced_x86_py.pyd')
        if os.path.exists(pyd_path):
            return # nothing to do

        args = [ util.get_python(), util.get_pip(), 'install', '-U', 'iced-x86==1.20.0' ]
        util.dprint(' '.join(args))

        process = subprocess.Popen(args)
        process.wait()
