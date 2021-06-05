from tests.module_imports.regular_module_imports import add

a = add(1, 2)

if __name__ == "__main__":
    print(f"MonkeyType ran {__file__} as main")
else:
    print("MonkeyType didn't call as main")
