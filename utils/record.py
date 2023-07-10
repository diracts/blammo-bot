import logging, random, os, sys, time, datetime
import pandas as pd

# from log.loggers.custom_logger import custom_logger
# logger = custom_logger()

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


# The purpose of this module is to allow the bot to record interesting data
# about how people are answering questions.

# 1) set qid
# 2) other main.py methods add data entries to

# For now, write this as if the runtime issue doesnt exist. Then, when one
# arises, look at how this behaves and fix it.

# TODO: if main.py tries to add an entry when it already exists in that row of
#       the buffer, then record.py should throw a warning


class Record:
    def __init__(
        self,
        path: str,
        allow_load: bool = True,
    ):
        print("Record class instantiated")
        self.path = path
        self.allow_load = allow_load

        # if self.allow_load:
        #     self.df = pd.read_csv(path, index_col=False, header=0, encoding='latin-1')
        # else:
        #     self.df = None

        self.loglevel = logging.INFO

        self.init_timestamp: float = -1  # unix timestamp
        self.init_qid: int = -1  # question id
        self.init_game_type: str = ""  # 'trivia' or 'scramble'
        self.init_outcome: str = ""  # 'solved' or 'unsolved'
        self.init_time_elapsed: int = -1  # seconds since start of round
        self.init_username: str = ""  # username of the user who answered
        self.init_points_awarded: int = -1  # points awarded to the user
        # self.init_user_balance: int          = -1    # user's balance after points are awarded
        # self.init_loss_total: int            = -1    # total gambling losses for the user
        self.init_guess_string: str = ""  # the user's actual guess
        self.init_guess_similarity: float = -1  # computed string similarity
        self.init_question_string: str = ""  # the question string
        self.init_answer_string: str = ""  # the answer string

        self.buffer = None

        self.cols = [
            "timestamp",
            "qid",
            "game_type",
            "outcome",
            "time_elapsed",
            "username",
            "points_awarded",
            "guess_string",
            "guess_similarity",
            "question_string",
            "answer_string",
        ]

    # def _set_log_level(self, loglevel) -> None:
    #     # set the log level
    #     logger.setLevel(loglevel)

    def _get_row_number(self, qid: str) -> int:
        # look in the buffer dataframe for the row with the given qid
        # return the row number of the row with the given qid

        # this function should take a qid and return an int that you can pass into
        #   self.buffer.iloc[N] to get that row

        # iloc finds the row number like a list
        # index returns the index number of the row

        # from index --> row number
        if self.buffer is None:
            raise ValueError("Buffer is empty")
        return self.buffer.loc[self.buffer["qid"] == qid, "qid"].index[0]

    def _write_to_buffer(self, df: pd.DataFrame) -> None:
        # append the given dataframe to the buffer dataframe
        if self.buffer is None:
            self.buffer = df
        else:
            self.buffer = pd.concat([self.buffer, df], ignore_index=True)

    def _pop_to_file(self, qid: str) -> None:
        # pop the row with the given qid from the buffer dataframe
        # write the popped row to the file
        if self.buffer is None:
            raise ValueError("Buffer is empty")
        with open(self.path, "a") as f:
            f.write("\n")

        n_attempts = 0
        while n_attempts < 2:
            n_attempts += 1
            try:
                logger.debug(f"n_attempts = {n_attempts}")
                row = self._get_row_number(qid)
                logger.debug(f"buffer row: {row}")
                logger.debug(f"type(row) = {type(row)}")
                logger.debug(f"buffer: {self.buffer}")
                logger.debug(f"type(self.buffer) = {type(self.buffer)}")
                buffer_row = self.buffer.iloc[row]
                logger.debug(f"Buffer row: \n{buffer_row}")
                df_row = pd.DataFrame(buffer_row).T
                logger.debug(f"Put buffer row in dataframe")
                df_row.to_csv(self.path, index=False, header=False, mode="a")
                logger.debug(f"Successfully saved buffer row {row} to csv.")
                self.buffer.drop(row, inplace=True)
                logger.debug(f"Successfully dropped buffer row {row}.")
                logger.debug(f"Finished _pop_to_file successfully.")
                break
            except Exception as e:
                logger.error(f"Could not writing to file: {e}")
                logger.error(f"qid: {qid}")
                logger.error(f"row: {row}")
                logger.error(f"buffer: {self.buffer}")
                logger.error(f"buffer shape: {self.buffer.shape}")
                logger.debug(f"Trying to write again.")
                self.buffer.reset_index(drop=True, inplace=True)
                logger.debug(f"Reset self.buffer indices.")

    def new(self, qid: str) -> None:
        new = pd.DataFrame(
            [
                [
                    self.init_timestamp,
                    self.init_qid,
                    self.init_game_type,
                    self.init_outcome,
                    self.init_time_elapsed,
                    self.init_username,
                    self.init_points_awarded,
                    self.init_guess_string,
                    self.init_guess_similarity,
                    self.init_question_string,
                    self.init_answer_string,
                ]
            ],
            columns=self.cols,
        )
        ts = datetime.datetime.timestamp(datetime.datetime.now())
        new.at[0, "qid"] = qid  # set the qid
        new.at[0, "timestamp"] = ts  # set the timestamp

        if qid[0] == "t":
            new.at[0, "game_type"] = "trivia"
        elif qid[0] == "s":
            new.at[0, "game_type"] = "scramble"
        else:
            raise ValueError("Invalid qid")

        # new.to_csv('test.csv', index=False, header=False, mode='a')
        self._write_to_buffer(new)

    def add_outcome(self, qid: str, outcome: str) -> None:
        if outcome not in ("solved", "timeout"):
            logger.error(
                f"Invalid outcome passed to add_outcome for qid {qid}: {outcome}"
            )
            raise ValueError("Invalid outcome")
        self.buffer.at[self._get_row_number(qid), "outcome"] = outcome

    def add_time_elapsed(self, qid: str, t: float) -> None:
        self.buffer.at[self._get_row_number(qid), "time_elapsed"] = t

    def add_username(self, qid: str, username: str) -> None:
        self.buffer.at[self._get_row_number(qid), "username"] = username

    def add_points_awarded(self, qid: str, points: int) -> None:
        self.buffer.at[self._get_row_number(qid), "points_awarded"] = points

    def add_guess_string(self, qid: str, guess: str) -> None:
        self.buffer.at[self._get_row_number(qid), "guess_string"] = guess

    def add_guess_similarity(self, qid: str, similarity: float) -> None:
        self.buffer.at[self._get_row_number(qid), "guess_similarity"] = similarity

    def add_question_string(self, qid: str, question: str) -> None:
        self.buffer.at[self._get_row_number(qid), "question_string"] = question

    def add_answer_string(self, qid: str, answer: str) -> None:
        self.buffer.at[self._get_row_number(qid), "answer_string"] = answer

    def write(self, qid: str) -> None:
        # write the row with the given qid to the file
        try:
            self._pop_to_file(qid)
        except Exception as e:
            logger.error(f"Error writing qid to file: {e}")

    def write_all(self, time_padding: int = 120):
        logger.info(f"Attempting to write all old record buffer to file.")
        now = datetime.datetime.timestamp(datetime.datetime.now())
        if self.buffer != None:
            logger.debug(f"buffer length: {len(self.buffer)}")
            old_rows = self.buffer[self.buffer["timestamp"] - now > time_padding]
            logger.debug(f"number of old rows to write: {len(old_rows)}")
            for qid in old_rows["qid"]:
                self.write(qid)
            logger.debug(f"Write all complete.")
        else:
            logger.debug(f"Write all stopped early since buffer is None.")

    def clear(self, qid: str) -> None:
        # try to clear the row with the given qid from the buffer dataframe
        # if the row is not in the buffer, do nothing
        if self.buffer is None:
            logger.warning(f"Tried to clear qid {qid} from buffer but buffer is empty.")
            raise ValueError("Buffer is empty")
        try:
            row = self._get_row_number(qid)
            self.buffer.drop(row, inplace=True)
            logger.debug(f"Dropped qid {qid} from buffer")
        except Exception as e:
            logger.error(f"Tried to clear qid {qid} from buffer, but failed: {e}")
            pass


# >>> USER GUESSED TRIVIA CORRECTLY <<<
# self.timestamp: float           = <timestamp>
# self.qid: int                   = t0123456789          1+10 digit question id
# self.game_type: str             = 'trivia'
# self.outcome: str               = 'solved'
# self.time_elapsed: int          = 17
# self.username: str              = 'diraction'
# self.points_awarded: int        = 8
# self.user_balance: int          = 780
# self.loss_total: int            = 351
# self.guess_string: str          = 'oaklahoma'
# self.guess_similarity: float    = 0.8712794
# self.question_string: str       = 'What musical was named after a u.s city'
# self.answer_string: str         = 'Oklahoma'


# >>> USER GUESSED SCRAMBLE CORRECTLY <<<
# self.timestamp: float           = <timestamp>
# self.qid: int                   = s0123456789          1+10 digit question id
# self.game_type: str             = 'scramble'
# self.outcome: str               = 'solved'
# self.time_elapsed: int          = 9
# self.username: str              = 'diraction'
# self.points_awarded: int        = 10
# self.user_balance: int          = 790                 balance
# self.loss_total: int            = 351
# self.guess_string: str          = 'gecko'             the user's actual guess
# self.guess_similarity: float    = 1                   1 for all correct scramble guesses
# self.question_string: str       = 'kogec'
# self.answer_string: str         = 'gecko'


# >>> TRIVIA ROUND ENDED <<<
# self.timestamp: float           = <timestamp>
# self.qid: int                   = t0123456789          1+10 digit question id
# self.game_type: str             = 'trivia'
# self.outcome: str               = 'timeout'
# self.time_elapsed: int          = -1
# self.username: str              = ''
# self.points_awarded: int        = -1
# self.user_balance: int          = -1
# self.loss_total: int            = -1
# self.guess_string: str          = ''
# self.guess_similarity: float    = ''
# self.question_string: str       = 'What musical was named after a u.s city'
# self.answer_string: str         = 'Oklahoma'


# >>> SCRAMBLE ROUND ENDED <<<
# self.timestamp: float           = <timestamp>
# self.qid: int                   = s0123456789          1+10 digit question id
# self.game_type: str             = 'trivia'
# self.outcome: str               = 'timeout'
# self.time_elapsed: int          = -1
# self.username: str              = ''
# self.points_awarded: int        = -1
# self.user_balance: int          = -1
# self.loss_total: int            = -1
# self.guess_string: str          = ''
# self.guess_similarity: float    = ''
# self.question_string: str       = 'What musical was named after a u.s city'
# self.answer_string: str         = 'Oklahoma'
