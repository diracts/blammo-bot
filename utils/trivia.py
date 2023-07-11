import pandas as pd
import logging, random

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

# TODO: Swich from using Pandas to using builtin dict functionality for
#       performance boost.
# TODO: use RegEx to look for features in these strings.


def _punctuation(s: str) -> str:
    pass


def fuzzy_check(row):
    # This function accepts a row from the trivia database and determines how
    # well the question matches the Bot's policy.

    # 0 levels:
    #   0. Question is valid and no action required.

    #   1. Question is valid but minor touch ups might be needed.
    #       - Improper capitalization, punctuation, etc. (e.g. "What Is The Capital Of France.")
    #       - Possible types or spelling mistakes in question string.   (e.g. "What is the captial of Franec?")
    #       - Possible unclear language.    (e.g. Q:"French capital main city?" A:"Paris")
    #       - Possible formatting errors. (e.g. Space before or after question/answer string.)
    #       - Answer string contains stop words or unwanted punctuation. (e.g. Q: "What fruit is commonly mistaken as a vegetable?" A: "The Tomato.")
    #           > Always include stop words that are a part of a proper noun. (e.g. "The Who", "The Beatles", "The Rolling Stones", etc.)
    #       - Answer string contains words that are really long. (e.g. "Anthropomorphism") (not always an issue)
    #       - Answer string contains a mix of numbers and unit names. (e.g. "5 feet", "5ft", "5 ft", "5'") (It is best to modify the question to make the answer be just a number.)

    #   2. Question is not good and might be annoying if asked in chat. Action required.
    #       - Question or answer is too long.
    #       - Answer appears to be multiple choice format.
    #       - Question is too similar to another question.
    #       - Likely unclear language in question or answer.
    #       - Bad characters in question/answer string. (e.g. Ê or ¬¬¬)
    #       - Question contains the name of numbers instead of the number. (e.g. "One", "Seven feet", "thirty", etc.)
    #       - Possible spelling mistake in the answer string.

    #   3. Serious problems. Question should be disabled until fixed.
    #       - Any slurs, banned phrases, automod flags, etc.\
    #       - Any repeated character more than 6 times. (eg. ååååååå)

    pass


class TriviaData:
    def __init__(
        self,
        path="../blammo-bot-private/trivia.csv",
        allow_load=True,  # use False when testing or anticipating unsafe behavior
    ):
        self.path = path
        self.allow_load = allow_load

        if self.allow_load:
            self.df = pd.read_csv(path, index_col=False, header=0, encoding="latin-1")
        else:
            self.df = None

        self.loglevel = logging.INFO

    # def _val_question(self, : str):
    #     # returns a string that is valid for the csv file
    #     if string

    def reload(self):
        if self.allow_load:
            # TODO: investigate non-UTF-8 encoding issues.
            #       Maybe add a validation function to catch and disable non-UTF-8 question?
            self.df = pd.read_csv(
                self.path, index_col=False, header=0, encoding="latin-1"
            )

    # try seeding the df.sample() function with utc time code
    def question(self):
        do_shuffle = random.choices([True, False], weights=[0.01, 0.99], k=1)[0]
        if do_shuffle:
            logger.info("Shuffling trivia questions...")
            # shuffle the dataframe
            self.df = self.df.sample(frac=1).reset_index(drop=True)
            logger.info("Done shuffling trivia questions.")

        if not self.allow_load:
            return
        # select a random row from the self.df object
        found_valid = False
        while not found_valid:
            q_df = self.df.sample(n=1)
            q = q_df.to_dict("records")[0]

            if (
                q["enabled"] == True
                or q["enabled"] == "TRUE"
                and str(q["question"]) != "nan"
                and str(q["correct_answer"]) != "nan"
            ):
                if "not" not in str(q["question"]):  # TEMPORARY FIX!
                    found_valid = True
            else:
                q_df.to_csv(
                    "../blammo-bot-private/rejected_questions.csv",
                    mode="a",
                    header=False,
                    index=False,
                )
                hbar = "=" * 81
                logger.info(f"{hbar}\nQuestion disabled, trying again...")
                logger.info(f'Question: {q["question"]}')
                logger.log(8, f'type(q["question"]): {type(q["question"])}')
                logger.info(f'Answer: {q["correct_answer"]}')
                logger.log(8, f'type(q["correct_answer"]): {type(q["correct_answer"])}')
                logger.info(f'qid: {q["qid"]}')
                logger.log(8, f'type(q["qid"]): {type(q["qid"])}')
                logger.info(f"")

        removed_char = False
        if str(q["question"])[-1] == "Ê":
            q["question"] = q["question"][:-1]
            logger.warning(f'Removed invalid character from question: {q["question"]}')
            removed_char = True
        if str(q["correct_answer"])[-1] == "Ê":
            q["correct_answer"] = q["correct_answer"][:-1]
            logger.warning(
                f'Removed invalid character from answer: {q["correct_answer"]}'
            )
            removed_char = True
        if removed_char:
            logger.info(f'Question: {q["question"]}')
            logger.info(f'Answer: {q["correct_answer"]}')

        return str(q["question"]), str(q["correct_answer"]), str(q["qid"])

    @classmethod
    def check_guess(guess: str, answer: str) -> bool:
        """Checks if the guess is correct.

        Args:
            guess (str): user guess to be checked
            answer (str): correct answer to be checked against

        Returns:
            bool: True if correct, False if incorrect
        """
        return
