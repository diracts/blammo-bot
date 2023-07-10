import logging

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

# The purpose of this module is to provide a basic function to allow
# the bot to announce a message to the channel periodically.
# We do not need or want this functionality right now, but it may be useful
# in the future. Check with mods before enabling this feature.


MESSAGE_0 = "peepoHas 🪄 ✨ Submit trivia questions and scramble words using the \
    #submit command. Use the #help command to learn more."

MESSAGES = [
    'peepoHas 🪄✨ Submit trivia questions and scramble words using the \
        #submit command. Use the "#submit help" command to learn more.',
    'peepoHas 🪄✨ Type "#commands to get a list of all available commands.',
    "peepoHas 🪄✨ ",
]
