#! /opt/homebrew/anaconda3/envs/monkeytype_sandbox/bin/python
import difflib
import os
import shutil
import sys
from pathlib import Path

from monkeytype.cli import main

if __name__ == "__main__":
    old_dir = os.getcwd()
    wrapper_path = sys.argv[0]
    proj_path_to_add = sys.argv[1]
    py_file_ran_on = sys.argv[2]
    sys.path.append(proj_path_to_add)
    new_dir = os.chdir(proj_path_to_add)
    remaining_argvs = sys.argv[3::].copy()

    file_being_modified = py_file_ran_on
    file_being_modified_backup = Path(file_being_modified).with_suffix('.bk').as_posix()
    shutil.copy2(file_being_modified, file_being_modified_backup)
    sys.argv = [wrapper_path] + remaining_argvs

    sys.path.insert(0, os.getcwd())
    r = main(sys.argv[1:], sys.stdout, sys.stderr)
    source_path = file_being_modified_backup
    target_path = file_being_modified
    fromfile = 'a/' + Path(target_path).name
    tofile = 'b/' + Path(target_path).name
    with open(source_path, 'r', encoding='utf8') as f:
        source_lines = f.readlines(1)

    with open(target_path, 'r', encoding='utf8') as f:
        target_lines = f.readlines(1)
    print("source and dest read".split())
    diff_list = difflib.unified_diff(source_lines, target_lines, fromfile, tofile)
    patch_lines = [d for d in diff_list]
    filepath_to_apply_pyment_on_to = Path(source_path)
    path_filename = filepath_to_apply_pyment_on_to.with_suffix(".patch").name
    proj_path_to_add = Path(proj_path_to_add)
    patch_location = proj_path_to_add.joinpath(f"patches/{path_filename}")
    patch_location.parent.mkdir(exist_ok=True, parents=True)
    with open(patch_location, 'w', encoding='utf-8') as f:
        f.writelines(patch_lines)
    os.rename(src=source_path, dst=target_path)
    sys.exit()
