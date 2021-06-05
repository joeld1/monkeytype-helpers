import sys
from pathlib import Path

from monkeytype.cli import main

from create_monkeytype_patch import MonkeytypeAssistant, create_monkeytype_pyment_black_isort_patch
# TODO: Refactor or redact

if __name__ == "__main__":
    # script_ran_on = Path(sys.argv[1])
    script_ran_on = Path(__file__).parent.joinpath(r"tests/module_imports/regular_module_imports.py")
    monkeytype_assistant = MonkeytypeAssistant(root_dir=Path(".").resolve())
    for k, v in monkeytype_assistant.paths_to_modules.items():
        if k == script_ran_on.as_posix():
            path_to_get = v
        print(f"Original Path:\t\t{k}")
        print(f"Module Path:\t\t{v}")
        print()

    opts_to_run = ['run', 'apply', 'stub', 'list-modules', 'create patch']
    # cur_option = input(
    #     f"\nOptions:\n{opts_to_run}\nInput monkeytype option arguments to run on (2nd line):\n{script_ran_on}\n{path_to_get}\n")
    cur_option = "create patch"
    if path_to_get.endswith(".py"):
        is_script = True
    else:
        is_script = False
    if "list-modules" in cur_option:
        sys.argv = ["monkeytype"] + [cur_option]
        sys.exit(main(sys.argv[1:], sys.stdout, sys.stderr))
    elif cur_option.strip().lower() == "run":
        if is_script:
            sys.argv = ["monkeytype"] + [cur_option] + [path_to_get]
        else:
            sys.argv = ["monkeytype"] + [cur_option, '-m'] + [path_to_get]
        sys.exit(main(sys.argv[1:], sys.stdout, sys.stderr))
    elif cur_option.strip().lower() == "create patch":
        input_style = "reST"
        output_style = "reST"
        first_line = False
        profile = "black"
        script_ran_on = Path(__file__).parent.joinpath(r"tests/module_imports/regular_module_imports.py")
        root_dir = Path(".").resolve()

        create_monkeytype_pyment_black_isort_patch(root_dir=root_dir, script_ran_on=script_ran_on,
                                                   input_style=input_style, output_style=output_style,
                                                   first_line=first_line, profile="black")

    else:
        sys.argv = ["monkeytype"] + [cur_option] + [path_to_get]
        sys.exit(main(sys.argv[1:], sys.stdout, sys.stderr))
else:
    print("is not main!")
