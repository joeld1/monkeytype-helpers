from tests.module_imports.nested_regular_module_imports import hello

a = hello("world")
print(a)

if __name__ == "__main__":
    print(f"MonkeyType ran {__file__} as main")
else:
    print("MonkeyType didn't call as main")
