__version__ = '0.1.0'


def print_something_from_init_file(my_str):
    """This is found in the __init__.py file for the monkeytype_sandbox package"""
    print([my_str] * 100)
    return [my_str] * 20, range(20)
