import os
from pathlib import Path

from monkeytype.config import DefaultConfig

project_directory = Path(__file__).parent
os.environ['MT_DB_PATH'] = Path(project_directory).joinpath("monkeytype.sqlite3").as_posix()


class MyConfig(DefaultConfig):
    pass


CONFIG = MyConfig()
