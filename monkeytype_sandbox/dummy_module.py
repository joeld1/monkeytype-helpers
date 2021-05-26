from tests.verify_overwrite_copy import add

a = add(1, 2)

if __name__ == "__main__":
    print(f"MonkeyType ran {__file__} as main\n__name__ == '__main__'")
else:
    print("MonkeyType didn't call as main")
