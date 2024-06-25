import logging, os, sys, asyncio, re, time, datetime, csv
from twitchbot.message import Message

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


# details to store in the database:
# - username of submitter
# - parsed question string (only question)
# - parsed answer string (only answer)
# - raw submission string (no q/a parsing)
# - timestamp of submission

# TODO: start using user_data to store info like this
BANNED_USERS = [
    "ghostwisperer1",
    "LimeTopPop",
    "kiri40324",
    "sen456",
    "mooncharnel",
]

SUBMISSION_FNAME = "../blammo-bot-private/submissions.csv"
SCRAMBLE_PATH = "../blammo-bot-private/scramble.csv"


async def _check_safety(content):
    # This function comes before all other steps in the main submit function.
    # It's purpose is to detect if the input is safe to deal with.

    # Check that input is a string:
    if not isinstance(content, str):
        logger.error(f"[ACTION REQUIRED] content is not a string: {content}")
        return False  # on a false output, the function in main script should then reply to message tagging dev(s)

    # TODO: make this function sensitive to special characters like \n.
    #       Adding it to the list below doesn't work for some reason.
    if any(
        i in content
        for i in [
            "__init__",
            "__class__",
            "__globals__",
            "__builtins__",
            "eval(",
            "exec(",
            "open(",
            # "..",
            "0x27",
            "0x3f",
            "0x5c",
            "0x07",
            "0x08",
            "0x0c",
            "0x22",
            "0x0a",
            "0x0d",
            "0x09",
            "0x0b",
            "\n",
            "\\n",
            "\r",
            "\\r",
            "\f",
            "\\f",
            "&#10;",
            "&#41;",
            "&#40;",
            "&#32;",
            "&#9;",
            "&Tab;",
        ]
    ):
        logger.error(f"[ACTION REQUIRED] content contains suspicious string: {content}")
        return False

    return True


async def _check_irregular_chars(content: str):
    # check for irregular characters in the message
    # return True if no irregular characters are found
    # return False if irregular characters are found
    # regular characters are defined as any that you can type on the standard keyboard (a-z, 0-9, etc.)
    # irregular characters are defined as any that you cannot type on the standard keyboard (e.g. invisible chars, double spaces, etc.)
    pass


async def _check_banned_users(username: str):
    global BANNED_USERS

    if username in BANNED_USERS:
        return False
    else:
        return True


async def _parse_formating(content: str):
    # check that the msg content adheres to the correct format
    # return (True, game) if the format is correct
    # return (False, game) if the format is incorrect
    # game is returned so that the main script can suggest appropriate help text to reply
    # trivia format: <question> | <answer>

    content = content.replace("#submit ", "")
    content = content.strip(" ")
    game = content.split(" ")[0]  # game is either 'trivia', 'scramble', or 'help'

    if game == "help":
        return True, "help"

    elif game == "trivia":
        # check that there is only one '|' character in content
        if content.count("|") != 1:
            return False, "trivia"
        else:
            return True, "trivia"

    elif game == "scramble":
        # check that there are no '|' characters in content
        if "|" in content:
            return False, "scramble"
        elif (
            len(content.split(" ")) != 2
        ):  # no spaces, only 1 word (other than game word)
            return False, "scramble"
        else:
            return True, "scramble"

    else:
        return False, "unknown"


async def _remove_braces(s: str):
    # The purpose of this function is to take a string like '<this is a string>', and return 'this is a string'
    # First, should check that the string starts with '<' and ends with '>'
    # If it does not, just return the original string as is.
    # If it does, remove the first and last characters, and return the string

    s = s.strip(" ")
    if s.startswith("<") and s.endswith(">"):
        s = s[1:-1]
        return s
    elif s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
        return s
    elif s.startswith("(") and s.endswith(")"):
        s = s[1:-1]
        return s
    elif s.startswith("{") and s.endswith("}"):
        s = s[1:-1]
        return s
    else:
        return s


async def _parse_question(content: str, game: str):
    # parse the question from the msg content
    # return the parsed question

    content = content.replace("”", '"')
    content = content.replace("“", '"')

    content = content.replace("#submit ", "")
    content = content.strip(" ")
    content = content.split(" ")[1:]  # remove the 'trivia' word from the content
    content = " ".join(content)  # join the list back into a string
    content = content.strip(" ")  # remove any trailing whitespace
    if game == "trivia":
        question = content.split("|")[0]
        question = question.strip(" ")
        question = await _remove_braces(question)
        answer = content.split("|")[1]
        answer = answer.strip(" ")
        answer = await _remove_braces(answer)
        # now we have the question and answer string separated and stripped of trailing whitespace
        return question, answer

    elif game == "scramble":
        content = await _remove_braces(content)
        return content  # just return the word

    else:
        return False


# async def _prep_for_csv(s: str) -> str:
#     # prepare a string to be written to a csv file

#     if any(i in s for i in ['"', '\n', ',', '\r']):
#         # if any of these characters are in the string, wrap the string in double quotes
#         return f'"{s}"'


async def _check_scrable_duplicate(word: str):
    """
    Checks current scramble list to see if word has already been used.

    Args:
        word (str): word to check

    Returns:
        bool: True if word has not been used, False if it has

    """
    global SCRAMBLE_PATH

    # open scramble.csv and read the first row
    with open(SCRAMBLE_PATH, "r") as f:
        reader = csv.reader(f)
        first_row = next(reader)
        words = first_row[0].split(" ")


async def _write_dict_to_csv(d: dict):
    # write a dictionary to a csv file
    # return True if successful
    # return False if unsuccessful

    global SUBMISSION_FNAME

    # first, check that the submissions.csv file exists
    if not os.path.isfile(SUBMISSION_FNAME):
        # if the file does not exist, create it and write the header
        with open(SUBMISSION_FNAME, "w") as f:
            f.write("username,question,answer,raw,timestamp\n")

    # now, write the dictionary to the csv file
    try:
        # with open(SUBMISSION_FNAME, 'a') as f:
        #     f.write(f'"{d["username"]}","{d["question"]}","{d["answer"]}","{d["raw"]}","{d["timestamp"]}"\n')
        # use csv module instead of writing to file directly
        with open(SUBMISSION_FNAME, "a", newline="") as f:
            writer = csv.writer(
                f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            writer.writerow(
                [
                    d["username"],
                    d["question"],
                    d["answer"],
                    d["word"],
                    "",
                    d["timestamp"],
                ]
            )
        return True
    except Exception as e:
        logger.error(f"Error writing to submissions.csv: {e}")
        logger.error(f'username: {d["username"]}')
        logger.error(f'author: {d["author"]}')
        logger.error(f'question: {d["question"]}')
        logger.error(f'answer: {d["answer"]}')
        logger.error(f'word: {d["word"]}')
        logger.error(f'raw: {d["raw"]}')
        logger.error(f'timestamp: {d["timestamp"]}')
        return False


async def submit(msg: Message) -> str | bool:
    # if output is a string, then the main script should reply to the message with the string
    # if output is False, then the main script should do nothing

    content = msg.content
    author = msg.author

    is_safe = await _check_safety(content)
    if not is_safe:
        return "@Diraction DinkDonk ⚠️"

    user_allowed_to_submit = await _check_banned_users(content)
    if not user_allowed_to_submit:
        return False

    is_format_correct, game = await _parse_formating(content)
    if is_format_correct == False and game == "help":
        logger.warning(
            f"User {author} tried to submit a question with incorrect formatting."
        )
        logger.warning(f"Message content: {content}")
        return "Please use the following format: #submit <game> <question> | <answer>. For more, type #submit help."
    elif is_format_correct == False and game == "trivia":
        logger.warning(
            f"User {author} tried to submit a trivia question with incorrect formatting."
        )
        logger.warning(f"Message content: {content}")
        return "Please use the following format: #submit trivia <question> | <answer>. (Don't include the < > symbols)"
    elif is_format_correct == False and game == "scramble":
        logger.warning(
            f"User {author} tried to submit a scramble question with incorrect formatting."
        )
        logger.warning(f"Message content: {content}")
        return "Please use the following format: #submit scramble <word>. Don't include the < > symbols and don't put multiple words."
    elif is_format_correct == False and game == "unknown":
        logger.warning(
            f"User {author} tried to submit a question with incorrect formatting."
        )
        logger.warning(f"Message content: {content}")
        return "Please specify what game you are submitting for (trivia or scramble). For more information, type #submit help."
    elif is_format_correct == True and game == "trivia":
        pass
    elif is_format_correct == True and game == "scramble":
        pass
    elif is_format_correct == True and game == "help":
        logger.debug(f"User {author} requested help with the submit command.")
        return "Trivia questions, use: #submit trivia <question> | <answer>. Scramble questions, use: #submit scramble <word>. Don't include the < > symbols. Scramble can only be 1 word."
    else:
        logger.error(f"Unknown error in submit.py. submit-submit-1")
        return "Unknown error. Please ping the developer(s). submit-submit-1"

    answer, question, word = "", "", ""
    parsed = await _parse_question(content, game)
    if game == "trivia":
        question = parsed[0]
        answer = parsed[1]
    elif game == "scramble":
        word = parsed
    else:
        logger.error(f"Unknown error in submit.py. submit-submit-2")
        return "Unknown error. Please ping the developer(s). submit-submit-2"

    submission = {
        "username": author,
        "question": question,
        "answer": answer,
        "word": word,
        "raw": content,
        "timestamp": datetime.datetime.now().timestamp(),
    }

    MAX_ANSWER_LENGTH: int = 50
    MAX_WORD_LENGTH: int = 25

    if game == "trivia" and len(answer) > 50:
        logger.warning(
            f"User {author} tried to submit a trivia question with an answer that is too long."
        )
        logger.warning(f"Message content: {content}")
        return f"That answer is too long. Please keep it under {MAX_ANSWER_LENGTH} characters."
    elif game == "trivia" and len(answer) == 0:
        logger.warning(
            f"User {author} tried to submit a trivia question with an answer that had 0 length."
        )
        logger.warning(f"Message content: {content}")
        return "You must specify an answer after the | symbol."
    elif game == "scramble" and len(word) > 30:
        logger.warning(
            f"User {author} tried to submit a scramble word that is too long."
        )
        logger.warning(f"Message content: {content}")
        return (
            f"That word is too long. Please keep it under {MAX_WORD_LENGTH} characters."
        )

    outcome: bool = await _write_dict_to_csv(submission)
    if outcome:
        logger.info(f"User {author} made a {game} submission.")
        if game == "trivia":
            logger.info(f"Question: {question}")
            logger.info(f"Answer: {answer}")
        elif game == "scramble":
            logger.info(f"Word: {word}")
        return "FeelsOkayMan 👍 Submission successful! Thanks!"
    else:
        logger.error(
            f"User {author} made a {game} submission, but it failed to write to the csv file. submit-submit-3"
        )
        return "Submission failed. Please ping the developer(s). submit-submit-3"
