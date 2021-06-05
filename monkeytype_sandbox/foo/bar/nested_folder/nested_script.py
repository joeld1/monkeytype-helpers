from tests.module_imports.nested_script_imports import hello

a = hello("nested script")
print(a)

if __name__ == "__main__":
    print(f"Replace this with callables for Monkeytype ")
else:
    print("MonkeyType didn't call this")
