import os
import sys
from pathlib import Path

from monkeytype.config import DefaultConfig

project_directory = sys.path[0]
os.environ['MT_DB_PATH'] = Path(project_directory).joinpath("monkeytype.sqlite3").as_posix()

class MyConfig(DefaultConfig):
    pass


CONFIG = MyConfig()
print("MonkeyType loaded configuration from monkeytype sandbox!")
