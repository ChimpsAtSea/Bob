import os
import sys

sys.path.append(os.path.realpath(os.path.dirname(__file__))) # Allow Local Imports

import library_project_setup as project_setup
import library_sln as sln
import library_gn as gn
import library_util as util
import library_engine_platform_build as epb

util.async_start()

target_os = util.get_gn_target_os()
target_config = util.get_gn_target_config()
target_link_config = util.get_gn_target_link_config()
target_cpu = util.get_gn_target_cpu()

gn.generate_build_configuration_files(target_os, target_config, target_link_config, target_cpu, epb.tag_configuration_triplets_concat, True)
global_targets = project_setup.parse_global_targets_list('//solution')

print("Setting up Visual Studio Projects")
solution = sln.Solution(util.get_solution_pretty_name(), f'solution/{util.get_solution_namespace()}.sln')
project_setup.setup_solution_project_structure(solution, global_targets)

for project in solution.projects:
    sln.write_project(solution, project)
sln.write_solution("solution/", solution)

util.async_end()
