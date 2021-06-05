from tests.module_imports.nested_script_imports import hello

a = hello("nested script")
print(a)

if __name__ == "__main__":
    print(f"MonkeyType ran {__file__} as main")
else:
    print("MonkeyType didn't call as main")
