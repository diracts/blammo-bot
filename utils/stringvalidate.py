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

# TODO: Add logging

# The purpose of this file is to provide a fast function that can be used to
# make sure a string is safe to chat (i.e. won't get automodded or be cause for
# concern). This is done by checking the string against a list of banned words
# and phrases, and taking the appropriate action if a match is found.

# Example: 1488 --> 1,488
