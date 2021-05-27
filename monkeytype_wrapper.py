#! /opt/homebrew/anaconda3/envs/monkeytype_sandbox/bin/python
import os
import subprocess
import sys
import shutil
from pathlib import Path

from monkeytype.cli import entry_point_main

if __name__ == "__main__":
    old_dir = os.getcwd()
    wrapper_path = sys.argv[0]
    proj_path_to_add = sys.argv[1]
    # print(f"cur project path is{proj_path_to_add}")
    sys.path.append(proj_path_to_add)
    new_dir = os.chdir(proj_path_to_add)
    # print("Adding project root to path!")
    remaining_argvs = sys.argv[2::].copy()

    sys.argv = [wrapper_path] + remaining_argvs
    sys.exit(entry_point_main())
