#! /opt/homebrew/anaconda3/envs/monkeytype_sandbox/bin/python
import os
import sys
from pathlib import Path

from pyment import PyComment

if __name__ == "__main__":
    old_dir = os.getcwd()
    wrapper_path = sys.argv[0]
    proj_path_to_add = Path(sys.argv[1])
    input_style = sys.argv[3]
    output_style = sys.argv[5]
    filepath_to_apply_pyment_on_to = Path(sys.argv[6])

    print(f"cur project path is{proj_path_to_add}")
    sys.path.append(proj_path_to_add.as_posix())
    new_dir = os.chdir(proj_path_to_add)

    c = PyComment(filepath_to_apply_pyment_on_to,
                  input_style=input_style,
                  output_style=output_style)
    c.proceed()
    patch = c.diff()
    path_filename = filepath_to_apply_pyment_on_to.with_suffix(".patch").name
    patch_location = proj_path_to_add.joinpath(f"patches/{path_filename}")
    patch_location.parent.mkdir(exist_ok=True, parents=True)
    with open(patch_location, 'w', encoding='utf-8') as f:
        f.writelines(patch)
    print(f"Successfully created patch for {filepath_to_apply_pyment_on_to.name} and saved it into:\n{patch_location}")
    sys.exit()
