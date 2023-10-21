import random
from typing import TypedDict
from .third_party_emotes import (
    ThirdPartyEmoteProvider,
    BetterTTVEmoteProvider,
    FrankerFaceZEmoteProvider,
    FailedToFetchEmotesException,
)
from .string_utils import (
    safe_scramble_word,
    AttemptedToScrambleWordWithLessThanTwoChars,
    ScrambleAttemptsExceededException,
)

# START: Logging

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

# END: Logging


class FailedToGetEmoteScrambleWord(Exception):
    pass


class EmoteScrambleWord(TypedDict):
    scrambled_emote_code_lower: str
    scrambled_emote_code: str
    unscrambled_emote_code: str


class EmoteScrambleData:
    user_id: int
    third_party_emote_providers: list[ThirdPartyEmoteProvider] = []

    BANNED_EMOTE_CODES = [  # TODO: Make this configurable externally
        "haHAA",
        "PepeLa",
        "dankHug",
    ]

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        self.third_party_emote_providers = [
            BetterTTVEmoteProvider(user_id=user_id),
            FrankerFaceZEmoteProvider(user_id=user_id),
        ]

    def get_emote_scramble_word(self) -> EmoteScrambleWord:
        last_exception = None

        MAX_ATTEMPTS = 100

        for _ in range(MAX_ATTEMPTS):
            third_party_emote_provider = random.choice(self.third_party_emote_providers)

            try:
                random_emote_code = third_party_emote_provider.get_random_emote_code()
            except FailedToFetchEmotesException as e:
                last_exception = e
                continue

            # Prevent two-character emotes (e.g. BetterTTV's emote modifiers like `w!`)
            # from being returned
            if len(random_emote_code) <= 2:
                logger.debug(
                    f"Skipping {random_emote_code} because it has 2 or less characters."
                )
                continue

            # Prevent banned emotes from being returned
            elif random_emote_code in self.BANNED_EMOTE_CODES:
                logger.debug(
                    f"Skipping {random_emote_code} because it is a banned emote."
                )
                continue

            try:
                scrambled_random_emote_code_lower = safe_scramble_word(
                    random_emote_code
                ).lower()
                scrambled_random_emote_code = safe_scramble_word(random_emote_code)
            except (
                AttemptedToScrambleWordWithLessThanTwoChars,
                ScrambleAttemptsExceededException,
            ) as e:
                last_exception = e
                logger.warn(f"Failed to scramble word: {random_emote_code} ({e})")
                continue

            logger.debug(f"Emote scramble answer: {random_emote_code}")

            return {
                "scrambled_emote_code_lower": scrambled_random_emote_code_lower,
                "scrambled_emote_code": scrambled_random_emote_code,
                "unscrambled_emote_code": random_emote_code,
            }

        if last_exception:
            raise FailedToGetEmoteScrambleWord from last_exception
        raise FailedToGetEmoteScrambleWord

    def reload_emotes(self) -> None:
        for emote_provider in self.third_party_emote_providers:
            try:
                emote_provider.fetch_and_cache_emote_codes()
            except FailedToFetchEmotesException as e:
                raise e

    def get_cached_emote_counts(self) -> dict:
        return {
            emote_provider.__class__.__name__: emote_provider.get_cached_emote_count()
            for emote_provider in self.third_party_emote_providers
        }
