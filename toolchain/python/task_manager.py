
import os
import subprocess
import library_util as util
import platform 

class BuildTask:
    name : str
    is_built : bool
    parent_tasks : list
    
    def __init__(self, name, _parent_tasks = []):
        self.name = name
        self.is_built = False
        self.parent_tasks : list[BuildTask] = [] + _parent_tasks
        BuildTaskManager.register_task(self)

    def can_build(self):
        for wait_for_task in self.parent_tasks:
            if not wait_for_task.is_built:
                return False
        return True

    def build(self):
        for parent in self.parent_tasks:
            if not parent.is_built:
                parent.build()

class BuildTaskManager:
    tasks : list[BuildTask] = []

    def register_task(task : BuildTask):
        BuildTaskManager.tasks.append(task)
    
    def is_finished():
        for task in BuildTaskManager.tasks:
            if not task.is_built:
                return False
        return True

    def get_next_task():
        for task in BuildTaskManager.tasks:
            if not task.is_built and task.can_build():
                return task
        return None

    def log_tasks():
        for task in BuildTaskManager.tasks:
            if not task.is_built:
                task_pending_names = ' '
                for parent_task in task.parent_tasks:
                    task_pending_names += f'\'{parent_task.name}\' '
                print(f'\t{task.name} [{task_pending_names}]')

    def process_tasks():
        if BuildTaskManager.is_finished():
            return False
        
        next_task = BuildTaskManager.get_next_task()
        if next_task == None:
            print('Unable to execute next task')
            print('Pending Tasks:')
            BuildTaskManager.log_tasks()
            raise Exception('Unable to execute next task')
        #print(f'Processing task {next_task.name}')
        next_task.build()
        next_task.is_built = True

        return True
    
    def run_until_complete():
        while BuildTaskManager.process_tasks():
            pass

class VisualCPPBuildTask(BuildTask):
    def __init__(self, name, msvc_target : str, _parent_tasks = []):
        super().__init__(name, _parent_tasks)

        [architecture, *_] = platform.architecture()
        self.msvc_host = 'HostX64' if architecture == '64bit' else 'HostX86'
        self.msvc_host_short = 'x64' if architecture == '64bit' else 'x86'
        #self.msvc_host = 'HostX86'
        #self.msvc_host_short = 'x86'

        self.msvc_target = msvc_target

        environment = os.environ.copy()

        environment.clear()
        for variable in ['SYSTEMROOT', 'OS', 'TEMP']:
            if variable in os.environ:
                environment[variable] = os.environ[variable]

        environment['CL'] = ''
        environment['LINK'] = ''
        
        if self.msvc_target == 'x64':
            environment['PROCESSOR_ARCHITECTURE'] = 'AMD64'
        if self.msvc_target == 'x86':
            environment['PROCESSOR_ARCHITECTURE'] = 'X86'
        if self.msvc_target == 'arm':
            environment['PROCESSOR_ARCHITECTURE'] = 'ARM'
        if self.msvc_target == 'arm64':
            environment['PROCESSOR_ARCHITECTURE'] = 'ARM64'

        paths = [
            util.get_ewdk_dir(f''),
            util.get_ewdk_dir(f'Program Files/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.31.31103/bin/{self.msvc_host}/{msvc_target}'),
            util.get_ewdk_dir(f'Program Files/Microsoft Visual Studio/2022/BuildTools/Common7/IDE/VC/VCPackages'),
            util.get_ewdk_dir(f'Program Files/Microsoft Visual Studio/2022/BuildTools/Common7/IDE/CommonExtensions/Microsoft/TestWindow'),
            util.get_ewdk_dir(f'Program Files/Microsoft Visual Studio/2022/BuildTools/Common7/IDE/CommonExtensions/Microsoft/TeamFoundation/Team Explorer'),
            util.get_ewdk_dir(f'Program Files/Microsoft Visual Studio/2022/BuildTools/MSBuild/Current/bin/Roslyn'),
            util.get_ewdk_dir(f'Program Files/Windows Kits/10/bin/{self.msvc_host_short}'),
            util.get_ewdk_dir(f'Program Files/Microsoft Visual Studio/2022/BuildTools/MSBuild/Current/Bin/amd64'),
            util.get_ewdk_dir(f'Program Files/Microsoft Visual Studio/2022/BuildTools/Common7/IDE/'),
            util.get_ewdk_dir(f'Program Files/Microsoft Visual Studio/2022/BuildTools/Common7/Tools/'),
            util.get_ewdk_dir(f'Program Files/Microsoft Visual Studio/2022/BuildTools/Common7/IDE/VC/Linux/bin/ConnectionManagerExe'),
            util.get_ewdk_dir(f'Program Files/Windows Kits/10/bin/10.0.22621.0/{self.msvc_host_short}'),
            util.get_ewdk_dir(f'Program Files/Windows Kits/10/tools'),
            util.get_ewdk_dir(f'Program Files/Microsoft SDKs/Windows/v10.0A/bin/NETFX 4.8.1 Tools'),
            util.get_ewdk_dir(f'BuildEnv'),
            os.path.join(environment['SYSTEMROOT'], 'System32') #TODO: Can this be handled better?. Required for cmd.exe
        ]
        environment['PATH'] = ';'.join(paths)

        includes = [
            util.get_ewdk_dir('Program Files/Windows Kits/10/include/10.0.22621.0/ucrt'),
            util.get_ewdk_dir('Program Files/Windows Kits/10/include/10.0.22621.0/um'),
            util.get_ewdk_dir('Program Files/Windows Kits/10/include/10.0.22621.0/shared'),
            util.get_ewdk_dir('Program Files/Windows Kits/10/include/10.0.22621.0/winrt'),
            util.get_ewdk_dir('Program Files/Windows Kits/10/include/10.0.22621.0/cppwinrt'),
            util.get_ewdk_dir('Program Files/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.31.31103/include'),
            util.get_ewdk_dir('Program Files/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.31.31103/atlmfc/include'),
        ]
        environment['INCLUDE'] = ';'.join(includes)

        compiler_library = [
            util.get_ewdk_dir('Program Files/Windows Kits/10/UnionMetadata/10.0.22621.0'),
            util.get_ewdk_dir('Program Files/Windows Kits/10/References/10.0.22621.0'),
        ]
        environment['LIBPATH'] = ';'.join(compiler_library)

        linker_library = [
            util.get_ewdk_dir(f'Program Files/Windows Kits/NETFXSDK/4.8/lib/um/{msvc_target}'),
            util.get_ewdk_dir(f'Program Files/Windows Kits/10/lib/10.0.22621.0/ucrt/{msvc_target}'),
            util.get_ewdk_dir(f'Program Files/Windows Kits/10/lib/10.0.22621.0/um/{msvc_target}'),
            util.get_ewdk_dir(f'Program Files/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.31.31103/lib/{msvc_target}'),
            util.get_ewdk_dir(f'Program Files/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.31.31103/atlmfc/lib/{msvc_target}'),
        ]
        environment['LIB'] = ';'.join(linker_library)

        self.environment = environment

    def get_nmake(self):
        nmake = util.get_ewdk_dir(os.path.join(f'Program Files/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.31.31103/bin/{self.msvc_host}/{self.msvc_target}', 'nmake.exe'))
        if not os.path.exists(nmake):
            raise Exception(f"EWDK invalid. Can't find {nmake}")
        return nmake

    def build(self):
        super().build()
        
        cl = util.get_ewdk_dir(os.path.join(f'Program Files/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.31.31103/bin/{self.msvc_host}/{self.msvc_target}', 'cl.exe'))
        if not os.path.exists(cl):
            raise Exception(f"EWDK invalid. Can't find {cl}")

