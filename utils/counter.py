import sys
import os
import asyncio

from log.loggers.custom_format import CustomFormatter  # for level colors

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter1 = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s : %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
file_handler = logging.FileHandler("logs.log")
file_handler.setFormatter(formatter1)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(CustomFormatter())

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# It would be a good idea to store these temp and state files in
# a /tmp/ or /state/ directory in the main project directory.
# Is this the right way to do this? Is it better to use the system
# /tmp/ directory?
STATE_DIR_NAME: str = "state"
COUNTER_FILE_NAME: str = "counter.json"

CWD = os.getcwd()
PATH = os.path.join(CWD, STATE_DIR_NAME, COUNTER_FILE_NAME)


def _check_state_dir_exists() -> int:
    global STATE_DIR_NAME
    pass


def _check_countfile_exists() -> int:
    """Checks that the counter file does exist in the right spot.

    Returns:
        int: 0 file does not exist, 1 file exists
    """
    global PATH

    # if countfile does not exist, check that state dir exists, if not, then create both
    return 0


def _write_counter(key: str, new_value: int) -> int:
    global PATH
    return 0


def read(key: str) -> int:
    global PATH
    return 0


def increment() -> int:
    global PATH
    return 0
