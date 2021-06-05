import difflib
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from functools import reduce
from pathlib import Path
from tkinter import filedialog, Tk, StringVar, OptionMenu, Button, Label
from typing import Iterable, List, Optional

import isort
import pyment
from black import format_str, FileMode
from monkeytype.cli import main


def _extra_tagstyle_elements(self, data):
    ret = {}
    style_param = self.opt['param'][self.style['in']]['name']
    style_type = self.opt['type'][self.style['in']]['name']
    # fixme for return and raise, ignore last char as there's an optional 's' at the end and they are not managed in this function
    style_return = self.opt['return'][self.style['in']]['name'][:-1]
    style_raise = self.opt['raise'][self.style['in']]['name'][:-1]
    last_element = {'nature': None, 'name': None}
    for line in data.splitlines():
        param_name = None
        param_type = None
        param_description = None
        param_part = None
        # parameter statement
        if line.strip().startswith(style_param):
            last_element['nature'] = 'param'
            last_element['name'] = None
            line = line.strip().replace(style_param, '', 1).strip()
            if ':' in line:
                param_part, param_description = line.split(':', 1)
            else:
                print("WARNING: malformed docstring parameter")
            res = re.split(r'\s+', param_part.strip())
            if len(res) == 1:
                param_name = res[0].strip()
            elif len(res) == 2:
                param_type, param_name = res[0].strip(), res[1].strip()
            else:
                print("WARNING: malformed docstring parameter")
            if param_name:
                # keep track in case of multiline
                last_element['nature'] = 'param'
                last_element['name'] = param_name
                if param_name not in ret:
                    ret[param_name] = {'type': None, 'type_in_param': None, 'description': None}
                if param_type:
                    ret[param_name]['type_in_param'] = param_type
                if param_description:
                    ret[param_name]['description'] = param_description.strip()
            else:
                print("WARNING: malformed docstring parameter: unable to extract name")
        # type statement
        elif line.strip().startswith(style_type):
            last_element['nature'] = 'type'
            last_element['name'] = None
            line = line.strip().replace(style_type, '', 1).strip()
            if ':' in line:
                param_name, param_type = line.split(':', 1)
                param_name = param_name.strip()
                param_type = param_type.strip()
            else:
                print("WARNING: malformed docstring parameter")
            if param_name:
                # keep track in case of multiline
                last_element['nature'] = 'type'
                last_element['name'] = param_name
                if param_name not in ret:
                    ret[param_name] = {'type': None, 'type_in_param': None, 'description': None}
                if param_type:
                    ret[param_name]['type'] = param_type.strip()
        elif line.strip().startswith(style_raise) or line.startswith(style_return):
            # fixme not managed in this function
            last_element['nature'] = 'raise-return'
            last_element['name'] = None
        else:
            # suppose to be line of a multiline element
            if last_element['nature'] == 'param':
                cur_name = last_element['name']
                cur_desc = ret[cur_name]['description']
                if cur_desc is None:
                    ret[cur_name]['description'] = ""
                else:
                    ret[cur_name]['description'] += f"\n{line}"
            elif last_element['nature'] == 'type':
                cur_name = last_element['name']
                cur_desc = ret[cur_name]['description']
                if cur_desc is None:
                    ret[cur_name]['description'] = ""
                else:
                    ret[cur_name]['description'] += f"\n{line}"
    return ret


pyment.docstring.DocsTools._extra_tagstyle_elements = _extra_tagstyle_elements
PyComment = pyment.pyment.PyComment


def relate_paths_using_dot_notation(first_path: os.PathLike, second_path: os.PathLike) -> str:
    """
    Get the first path relative to second path using dot notation

    :param first_path:
    :param second_path:
    :return:
    """
    abs_path_1 = Path(first_path).resolve()
    if abs_path_1.is_file() and (
            abs_path_1.name == "__init__.py"):  # have to point to dir containing file if this is True
        abs_path_1 = abs_path_1.parent
    abs_path_2 = Path(second_path).resolve()
    if abs_path_2.name == "__init__.py":
        abs_path_2 = abs_path_2.parent  # Don't care if its a file or dir, unless __init__.py
    try:
        relative_path = abs_path_1.relative_to(abs_path_2)
        return relative_path.as_posix()
    except ValueError as e:
        print("Relating directories using dot notation from first_path -> second_path")
        common_path = Path(os.path.commonpath([abs_path_1, abs_path_2]))
        path_to_abs_path_1_from_common = abs_path_1.relative_to(common_path)
        path_to_abs_path_2_from_common = abs_path_2.relative_to(common_path)
        relative_dots = [Path(os.pardir) for _ in path_to_abs_path_1_from_common.parts]
        if relative_dots:
            dots_to_common_path_from_path_1 = reduce(lambda x, y: x.joinpath(y), relative_dots)
            dots_from_path_1_to_path_2 = dots_to_common_path_from_path_1.joinpath(
                path_to_abs_path_2_from_common).as_posix()
        else:
            dots_from_path_1_to_path_2 = path_to_abs_path_2_from_common.as_posix()
        return dots_from_path_1_to_path_2


def get_filepath(prompt=""):
    try:
        root = Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(title=prompt, initialdir=Path(__file__).parent.as_posix())
    except Exception as e:
        print(e)
        filepath = ""
    return filepath


def get_directory_path(prompt="",init_dir=Path(__file__).parent.as_posix()):
    try:
        root = Tk()
        root.withdraw()
        dir_path = filedialog.askdirectory(title=prompt, initialdir=init_dir)
    except Exception as e:
        print(e)
        dir_path = ""
    return dir_path


MONKEYTYPE_CONFIG_FILE = """
import os
from pathlib import Path

from monkeytype.config import DefaultConfig

project_directory = Path(__file__).parent
os.environ['MT_DB_PATH'] = Path(project_directory).joinpath("monkeytype.sqlite3").as_posix()


class MyConfig(DefaultConfig):
    pass


CONFIG = MyConfig()

"""


class MonkeytypeAssistant:

    def __init__(self, root_dir=None,init_dir:str=Path(__file__).parent.as_posix()):
        if root_dir is None:
            root_dir = self.get_root_dir(init_dir=init_dir)
        self.root_dir = Path(root_dir)
        self.cwd_into_root(root_dir)
        path_to_config = root_dir.joinpath("monkeytype_config.py").resolve()
        if not path_to_config.exists():
            with open(path_to_config,'w',encoding='utf8') as f:
                f.write(MONKEYTYPE_CONFIG_FILE)
        parents_dict, paths_to_modules = self.recursively_add_py_files_to_path(root_dir)
        self.parents_dict = parents_dict.copy()
        self.paths_to_modules = paths_to_modules.copy()
        for k in self.parents_dict.keys():
            sys.path.insert(0, k)

    def get_rel_path_to_module(self):
        file_to_apply_monkeytype_onto = self.get_relative_path_to_py_file_or_package()
        rel_path_to_file = self.paths_to_modules[file_to_apply_monkeytype_onto]
        return rel_path_to_file

    @staticmethod
    def get_root_dir(init_dir:Optional[str]):
        prompt = "Select root dir that will contain monkeytype.sqlite3! This will be the pwd and the path to get relative roots from!"
        root_dir = get_directory_path(prompt=prompt,init_dir=init_dir)
        if root_dir:
            return Path(root_dir)
        else:
            return Path(".").resolve()

    @staticmethod
    def cwd_into_root(root_dir: Path):
        if Path(os.getcwd()) != root_dir:
            os.chdir(root_dir)

    @staticmethod
    def get_nearest_unknown_parent(filepath: Path, folder_paths: Iterable[Path]):
        """

        This recursively finds a parent of the filepath that is not found in the list of paths supplied

        folder_containing_package/outer_package/__init__.py
        folder_containing_package/outer_package/sub_package/__init__.py
        folder_containing_package/outer_package/sub_package/sub_package_2/__init__.py
        folder_containing_package/some_other_package/sub_package/sub_package_2/__init__.py

        folder_containing_package/outer_package
        folder_containing_package/outer_package/sub_package
        folder_containing_package/outer_package/sub_package/sub_package_2
        folder_containing_package/some_other_package/sub_package/sub_package_2

        filepath is any init_file found in the first list
        folder_paths is the second_list above

        If we pass in the 1st -> 3rd init_file, we expect to return the Path 'folder_containing_package' for the first file

        If we pass in the last init_file, we expect to return
        'folder_containing_package/some_other_package/sub_package'

        :param filepath:
        :param folder_paths:
        :return:
        """
        if filepath.parent not in folder_paths:
            return filepath.parent
        else:
            return MonkeytypeAssistant.get_nearest_unknown_parent(filepath.parent, folder_paths)

    @staticmethod
    def recursively_add_py_files_to_path(root_dir: Path):
        root_dir = Path(".").resolve()
        all_py_files = list(root_dir.rglob("**/*py"))
        all_init_py_files = list(root_dir.rglob("**/*__init__.py"))
        packages_dict = defaultdict(list)
        for p in all_init_py_files:
            cur_path = Path(p)
            cur_parent = cur_path.parent
            packages_dict[cur_parent.as_posix()].append(cur_path)

        known_packages = [Path(p) for p in packages_dict.keys()]

        init_files_parent_to_add_to_path_dict = {}

        for p in all_init_py_files:
            cur_path = Path(p)
            nearest_unknown_parent = MonkeytypeAssistant.get_nearest_unknown_parent(cur_path, known_packages)
            init_files_parent_to_add_to_path_dict[p.as_posix()] = nearest_unknown_parent

        parents_dict = defaultdict(list)
        paths_to_modules = {}
        for p in all_py_files:
            cur_path = Path(p)
            cur_parent = cur_path.parent
            is_part_of_module = len(list(cur_parent.glob("__init__.py")))
            rel_path = relate_paths_using_dot_notation(cur_path, root_dir)
            if is_part_of_module:
                path_to_module_in_pkg = cur_parent.joinpath("__init__.py")
                cur_parent = init_files_parent_to_add_to_path_dict[path_to_module_in_pkg.as_posix()]
                if cur_path.name == "__init__.py":
                    rel_path = relate_paths_using_dot_notation(path_to_module_in_pkg.parent, cur_parent)
                else:
                    rel_path = relate_paths_using_dot_notation(cur_path, cur_parent)

                rel_path_to_module = rel_path.replace(os.sep, ".").replace(".py", "")
                parents_dict[cur_parent.as_posix()].append(rel_path_to_module)
                paths_to_modules[cur_path.as_posix()] = rel_path_to_module

            else:
                rel_path = p.relative_to(root_dir)
                num_parents = len(rel_path.parents)
                if num_parents == 1:
                    rel_path_to_module = rel_path.stem
                else:
                    rel_path_to_module = rel_path.as_posix()
                parents_dict[cur_parent.as_posix()].append(rel_path_to_module)
                paths_to_modules[cur_path.as_posix()] = rel_path_to_module
        return parents_dict, paths_to_modules

    @staticmethod
    def get_relative_path_to_py_file_or_package():
        prompt = "Select file to apply monkeytype onto"
        filepath = get_filepath(prompt=prompt)
        return filepath

    @staticmethod
    def select_file_to_run_monkeytype_on():
        print("Select file to run monkeytype on!")


# Change the label text
def show(label, clicked):
    label.config(text=clicked.get())


def tkinter_options(options):
    # Import module
    # Create object
    root = Tk()
    # Adjust size
    root.geometry("200x200")
    root.withdraw()

    # datatype of menu text
    clicked = StringVar()
    # initial menu text
    clicked.set(options[0])
    # Create Dropdown menu
    drop = OptionMenu(root, clicked, *options)
    drop.pack()
    # Create button, it will change label text
    button = Button(root, text="click Me", command=lambda x, y: show(x, y)).pack()
    # Create Label
    label = Label(root, text=" ")
    label.pack()


def get_path_to_backup(filepath_to_apply_pyment_on_to: Path):
    prev_file_name = filepath_to_apply_pyment_on_to.stem
    new_name = prev_file_name + "_temp.bk"
    file_being_modified_backup = filepath_to_apply_pyment_on_to.parent.joinpath(new_name)
    return file_being_modified_backup


def create_backup(file_being_modified: Path):
    file_being_modified_backup = get_path_to_backup(file_being_modified)
    shutil.copy2(file_being_modified, file_being_modified_backup)
    return file_being_modified_backup


def monkeytype_apply(root_dir: Path, file_being_modified_backup: Path, file_being_modified: Path):
    r = main(sys.argv[1:], sys.stdout, sys.stderr)
    patch_lines = get_patch_lines(file_a=file_being_modified, file_b=file_being_modified_backup)
    patch = "".join(patch_lines)
    if patch:
        export_patch(root_dir=root_dir, filepath_being_patched=file_being_modified, patch=patch)


def get_patch_lines(file_a: Path, file_b: Path):
    fromfile = 'a/' + file_a.name
    tofile = 'b/' + file_a.name
    with open(file_a, 'r', encoding='utf8') as f:
        source_lines = f.readlines()
    with open(file_b, 'r', encoding='utf8') as f:
        target_lines = f.readlines()
    diff_list = difflib.unified_diff(source_lines, target_lines, fromfile, tofile)
    patch_lines = [d for d in diff_list]
    return patch_lines


def create_pyment_patch(root_dir: Path, filepath_to_apply_pyment_on_to: Path):
    file_being_modified_backup = get_path_to_backup(filepath_to_apply_pyment_on_to)

    file_a = Path(file_being_modified_backup).name
    file_b = filepath_to_apply_pyment_on_to.name
    dir_path = Path(filepath_to_apply_pyment_on_to).parent
    patch = call_git_diff_no_index(file_a, file_b, dir_path)
    export_patch(root_dir, filepath_to_apply_pyment_on_to, patch)


def apply_pyment_inplace(filepath_to_apply_pyment_on_to: Path, input_style: str,
                         output_style: str, first_line: bool = True):
    try:
        c = PyComment(filepath_to_apply_pyment_on_to,
                      input_style=input_style,
                      output_style=output_style,
                      convert_only=True, write=True, first_line=first_line)
        apply_pyment_to_file_inplace(c)
    except Exception as e:
        print(e)
    try:
        d = PyComment(filepath_to_apply_pyment_on_to, input_style=input_style, output_style=output_style,
                      first_line=first_line, write=True)
        apply_pyment_to_file_inplace(d)
    except Exception as e:
        print(e)


def apply_pyment_to_file_inplace(pycomment_obj: PyComment):
    pycomment_obj.proceed()
    before_conv, after_conv = pycomment_obj.compute_before_after()
    file_contents = apply_black_to_lines(after_conv)
    pycomment_obj.overwrite_source_file(lines_to_write=file_contents.splitlines(True))


def apply_black_to_lines(after_conv: List[str]):
    file_contents = format_str("".join(after_conv), mode=FileMode())
    return file_contents


def export_patch(root_dir: Path, filepath_being_patched: Path, patch: str):
    if filepath_being_patched.name == "__init__.py":
        patch_filename = filepath_being_patched.relative_to(root_dir).parent.joinpath(
            filepath_being_patched.name).with_suffix('.patch').as_posix().replace(os.sep, '_')
    else:
        patch_filename = filepath_being_patched.with_suffix(".patch").name
    patch_location = root_dir.joinpath(f"patches/{patch_filename}")
    patch_location.parent.mkdir(exist_ok=True, parents=True)
    with open(patch_location, 'w', encoding='utf-8') as f:
        f.write(patch)


def call_git_diff_no_index(file_a, file_b, dir_path):
    git_cmd = f"git diff --no-index -- {file_a} {file_b}"
    git_cmds = git_cmd.split()
    with subprocess.Popen(git_cmds, stdout=subprocess.PIPE, text=True, cwd=dir_path) as p:
        output, errors = p.communicate()
    patch = output.replace(f"a/{file_a}", f"a/{file_b}")
    new_lines = [l for l in patch.splitlines(1) if not (l.startswith('index'))]
    new_patch = "".join(new_lines)
    return new_patch


def create_monkeytype_pyment_black_isort_patch(root_dir: Optional[Path], script_ran_on: Path, module_path: str,
                                               input_style: str, output_style: str,
                                               first_line: bool = True, profile: str = "black"):
    assert not ('.py' in module_path)
    sys.argv = ["monkeytype"] + ['apply', '--ignore-existing-annotations'] + [module_path]
    file_being_modified = script_ran_on
    file_being_modified_backup = create_backup(file_being_modified)
    try:
        monkeytype_apply(root_dir=root_dir, file_being_modified=file_being_modified,
                         file_being_modified_backup=file_being_modified_backup)
        apply_pyment_inplace(filepath_to_apply_pyment_on_to=file_being_modified, input_style=input_style,
                             output_style=output_style,
                             first_line=first_line)
        isort.file(filename=file_being_modified, profile=profile)
        create_pyment_patch(root_dir=root_dir, filepath_to_apply_pyment_on_to=file_being_modified)
    except Exception as e:
        print(e)
    shutil.move(src=file_being_modified_backup, dst=file_being_modified)


def get_module_path(monkeytype_assistant: MonkeytypeAssistant, script_ran_on: Path):
    root_dir = monkeytype_assistant.root_dir
    for k, v in monkeytype_assistant.paths_to_modules.items():
        if k == script_ran_on.as_posix():
            path_to_get = v
    return root_dir, path_to_get


def monkeytype_run(module_path: str):
    cur_option = "run"
    if module_path.endswith(".py"):
        is_script = True
    else:
        is_script = False
    if is_script:
        sys.argv = ["monkeytype"] + [cur_option] + [module_path]
    else:
        sys.argv = ["monkeytype"] + [cur_option, '-m'] + [module_path]
    main(sys.argv[1:], sys.stdout, sys.stderr)


def monkeytype_list_modules():
    sys.argv = ["monkeytype"] + ['list-modules']
    main(sys.argv[1:], sys.stdout, sys.stderr)


if __name__ == "__main__":
    script_ran_on = Path(sys.argv[1])
    input_style = "reST"
    output_style = "reST"
    first_line = False
    profile = "black"
    root_dir = None
    monkeytype_assistant = MonkeytypeAssistant(root_dir=root_dir,init_dir=script_ran_on.parent.as_posix())

    root_dir, module_path = get_module_path(monkeytype_assistant, script_ran_on)
    create_monkeytype_pyment_black_isort_patch(root_dir=root_dir, script_ran_on=script_ran_on, module_path=module_path,
                                               input_style=input_style,
                                               output_style=output_style, first_line=first_line, profile=profile)
