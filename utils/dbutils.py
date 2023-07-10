import pandas as pd
import logging, datetime, random, os, sys, time
import numpy as np

# The purpose of this module is to provide basic function to manimpulate the
# databases.

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
#     datefmt='%m/%d/%Y %I:%M:%S %p',
#     handlers=[
#         logging.FileHandler('logs.log'),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger(__name__)


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


def rand_with_N_digits(n: int):
    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return random.randint(range_start, range_end)


def _load_csv(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File {path} does not exist")
    df = pd.read_csv(path, index_col=False, header=0, encoding="latin-1")
    return df


def _save_csv(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False)


def _replace_duplicates(df: pd.DataFrame, game_type: str):
    while df["qid"].duplicated().sum() > 0:
        for i, qid in enumerate(df["qid"]):
            if df["qid"].duplicated()[i]:
                new_qid = game_type[0] + str(rand_with_N_digits(10))
                df.at[i, "qid"] = new_qid
                logger.warning(f"qid {qid} is duplicated, replacing with {new_qid}")
    return df


def clean_qid(fname: str, game_type: str):
    # find any duplicate qids and replace them with new ones
    logger.debug(f"Running clean_qid on {fname}")
    if game_type not in ("trivia", "scramble"):
        raise ValueError(f"Invalid game type: {game_type}")
    df = _load_csv(fname)
    df = _replace_duplicates(df, game_type)
    _save_csv(df, fname)


def add_qid(fname: str, game_type: str):
    logger.debug(f"Running add_qid on {fname}")
    if game_type not in ("trivia", "scramble"):
        raise ValueError(f"Invalid game type: {game_type}")

    # load scramble or trivia csv
    df = _load_csv(fname)
    if "qid" not in df.columns:
        df["qid"] = ["" for _ in range(len(df))]

    # set game prefix
    if game_type == "trivia":
        game_prefix = "t"
    elif game_type == "scramble":
        game_prefix = "s"
    else:
        raise ValueError(f"Invalid game type: {game_type}")

    for i, qid in enumerate(df["qid"]):
        if qid == "":
            df.at[i, "qid"] = game_prefix + str(rand_with_N_digits(10))

    df = _replace_duplicates(df, game_type)
    _save_csv(df, fname)
