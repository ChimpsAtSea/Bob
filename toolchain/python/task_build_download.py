
import os
import subprocess
import shutil
from task_manager import BuildTask
from task_build_copy import CopyBuildTask
import library_util as util

class DownloadBuildTask(BuildTask):
    def __init__(self, url : str, filepath : str, _parent_tasks = []):
        super().__init__('DownloadBuildTask', _parent_tasks)
        self.url = url
        self.filepath = filepath

    def build(self):
        super().build()

        if os.path.exists(self.filepath):
            return # Don't download
        
        destination_directory = os.path.dirname(self.filepath)
        
        if not os.path.exists(destination_directory):
            os.makedirs(destination_directory)

        process = subprocess.Popen(['curl', '-L', self.url, '-o', f'{self.filepath}.temp'])
        process.wait()
        shutil.move(f'{self.filepath}.temp', self.filepath)

def download_extract_task(ExtractTask, url, cache_filename, output_directory, force = False):
    download_filepath = os.path.join(util.get_download_cache_dir(), cache_filename)
    download_task = DownloadBuildTask(url, download_filepath)
    extract_task = ExtractTask(download_filepath, output_directory, [download_task], force)
    return extract_task

def download_copy_task(url, cache_filename, output_directory, force = False):
    download_filepath = os.path.join(util.get_download_cache_dir(), cache_filename)
    download_task = DownloadBuildTask(url, download_filepath)
    output_filepath = os.path.join(output_directory, cache_filename)
    copy_task = CopyBuildTask(download_filepath, output_filepath, [download_task], force)
    return copy_task
