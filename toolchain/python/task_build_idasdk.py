import os, hashlib
from task_manager import BuildTask
from task_build_extract import ExtractBuildTask
from task_build_download import DownloadBuildTask
from task_build_download import download_extract_task
import library_util as util

class IDASDKBuildTask(BuildTask):
    def __init__(self, _parent_tasks = []):
        super().__init__('IDASDKBuildTask', _parent_tasks)

    def build(self):
        super().build()

        ida_sdk_sha256 = "0c1febfae3b322dc9769a8cdbc8d90347cca2ee154a63b95b46a9f321c45cee5"
        ida_sdk_size = 21758636
        ida_sdk_version = "7.7"
        ida_sdk_version_numbers = "".join([c for c in ida_sdk_version if c.isnumeric()])
        ida_sdk_filename = f"idasdk{ida_sdk_version_numbers}.7z"
        ida_sdk_source_filepath = os.path.join(util.get_download_cache_dir(), ida_sdk_filename)

        if not os.path.exists(ida_sdk_source_filepath):
            if 'idasdk' in util.get_bob_required_modules():
                raise Exception(f"{ida_sdk_filename} is missing from the download cache")
            return # Can't install what doesn't exist
        
        if not util.bob_use_invalid_files:
            file_size = os.path.getsize(ida_sdk_source_filepath)

            if file_size != ida_sdk_size:
                raise util.BobFileInvalidSize(f"idasdk file is invalid", ida_sdk_size, file_size)

            hasher = hashlib.new("sha256")
            with open(ida_sdk_source_filepath, 'rb') as file:
                while True:
                    data = file.read(65536)  # Read in 64k chunks
                    if not data: break
                    hasher.update(data)  # Update the hash with the chunk's data
            # Calculate the final hash value as a hexadecimal string
            file_hash = hasher.hexdigest()

            if file_hash != ida_sdk_sha256:
                raise util.BobFileInvalidHash(f"idasdk file is invalid", ida_sdk_sha256, file_hash)
        
        ida_sdk_extract_directory = os.path.join(util.get_thirdparty_dir(), 'idasdk')
        ida_sdk_directory = os.path.join(ida_sdk_extract_directory, f'idasdk77')

        extract_task = ExtractBuildTask(ida_sdk_source_filepath, ida_sdk_extract_directory, [])

        extract_task.build()
