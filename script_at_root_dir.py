from tests.module_imports.script_at_root_dir_imports import get_dict


list_to_convert = list(map(lambda x: str(x), range(0,14)))
my_dict = get_dict(list_to_convert)
print(my_dict)