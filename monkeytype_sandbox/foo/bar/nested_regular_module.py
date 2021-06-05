from tests.module_imports.nested_regular_module_imports import hello

a = hello("world")
print(a)

if __name__ == "__main__":
    print(f"Replace this with callables for Monkeytype ")
else:
    print("MonkeyType didn't call this")
