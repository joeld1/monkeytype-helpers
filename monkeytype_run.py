import os
import sqlite3
import sys
from pathlib import Path

from monkeytype.db.sqlite import SQLiteStore

from create_monkeytype_patch import MonkeytypeAssistant, get_module_path, monkeytype_run, monkeytype_list_modules, \
    create_monkeytype_pyment_black_isort_patch

if __name__ == "__main__":
    script_ran_on = Path(sys.argv[1])
    root_dir = None

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
        script_ran_on_dict_temp = {v:k for k,v in monkeytype_assistant.paths_to_modules.items() if v==cur_module}
        script_ran_on_path = script_ran_on_dict_temp.get(cur_module,None)
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
    sys.exit()