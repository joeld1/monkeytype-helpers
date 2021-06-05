import os
import sqlite3
import sys
from pathlib import Path
import pytest
from monkeytype.db.sqlite import SQLiteStore

from create_monkeytype_patch import MonkeytypeAssistant, get_module_path, monkeytype_run, monkeytype_list_modules, \
    create_monkeytype_pyment_black_isort_patch


@pytest.fixture()
def root_dir():
    root_dir = Path(__file__).parent.parent
    return root_dir


class TestMonkeytypePatch:

    @staticmethod
    def run_create_monkeytype_pyment_black_isort_patch(root_dir, script_ran_on):

        monkeytype_assistant = MonkeytypeAssistant(root_dir=root_dir)

        root_dir, module_path = get_module_path(monkeytype_assistant, script_ran_on)
        from monkeytype_config import MyConfig
        monkeytype_run(module_path)
        monkeytype_list_modules()
        db_path = os.environ.get(MyConfig.DB_PATH_VAR, "monkeytype.sqlite3")
        conn = sqlite3.connect(db_path)
        monkeytype_modules_ran = SQLiteStore(conn=conn)
        cur_modules = monkeytype_modules_ran.list_modules()
        for cur_module in cur_modules:
            script_ran_on_dict_temp = {v: k for k, v in monkeytype_assistant.paths_to_modules.items() if
                                       v == cur_module}
            script_ran_on_path = script_ran_on_dict_temp.get(cur_module, None)
            if script_ran_on_path:
                script_ran_on_path = Path(script_ran_on_path)
                input_style = "reST"
                output_style = "reST"
                first_line = False
                profile = "black"
                create_monkeytype_pyment_black_isort_patch(root_dir=root_dir, script_ran_on=script_ran_on_path,
                                                           module_path=cur_module, input_style=input_style,
                                                           output_style=output_style, first_line=first_line,
                                                           profile=profile)
            else:
                pass

    def test_regular_module(self, root_dir):
        path_to_script = "monkeytype_sandbox/regular_module.py"
        script_ran_on = root_dir.joinpath(path_to_script)
        self.run_create_monkeytype_pyment_black_isort_patch(root_dir, script_ran_on)
        assert root_dir.joinpath("patches/regular_module_imports.patch").exists()

    def test_nested_regular_module(self, root_dir):
        path_to_script = r"monkeytype_sandbox/foo/bar/nested_regular_module.py"
        script_ran_on = root_dir.joinpath(path_to_script)
        self.run_create_monkeytype_pyment_black_isort_patch(root_dir, script_ran_on)
        assert root_dir.joinpath("patches/nested_regular_module_imports.patch").exists()

    def test_nested_script(self, root_dir):
        path_to_script = r"monkeytype_sandbox/foo/bar/nested_folder/nested_script.py"
        script_ran_on = root_dir.joinpath(path_to_script)
        self.run_create_monkeytype_pyment_black_isort_patch(root_dir, script_ran_on)
        assert root_dir.joinpath("patches/nested_script_imports.patch").exists()

    def test_script_at_root_dir(self, root_dir):
        path_to_script = r"script_at_root_dir.py"
        script_ran_on = root_dir.joinpath(path_to_script)
        self.run_create_monkeytype_pyment_black_isort_patch(root_dir, script_ran_on)
        assert root_dir.joinpath("patches/script_at_root_dir_imports.patch").exists()

    def test_init_file_method(self, root_dir):
        path_to_script = r"tests/run_package_init_file.py"
        script_ran_on = root_dir.joinpath(path_to_script)
        self.run_create_monkeytype_pyment_black_isort_patch(root_dir, script_ran_on)
        assert root_dir.joinpath("patches/monkeytype_sandbox___init__.patch").exists()

