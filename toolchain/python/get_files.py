import sys, glob

arguments = sys.argv[1:]

recursive = False
include_hidden = False
for argument in arguments:
    if argument == 'recursive':
        recursive = True
        continue
    if argument == 'include_hidden':
        include_hidden = True
        continue

    for file in glob.glob(argument, recursive=recursive, include_hidden=include_hidden):
        print(file)

    # Reset Flags
    recursive = False
    include_hidden = False
