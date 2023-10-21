import random
import requests

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


class FailedToFetchEmotesException(Exception):
    pass


class ThirdPartyEmoteProvider:
    cached_emote_codes: list[str] = []

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def get_random_emote_code(self) -> str:
        if len(self.cached_emote_codes) < 1:
            self.fetch_and_cache_emote_codes()
        return random.choice(self.cached_emote_codes)

    def get_cached_emote_count(self) -> int:
        return len(self.cached_emote_codes)

    def fetch_and_cache_emote_codes(self) -> None:
        emote_codes = []
        emote_codes.extend(self.fetch_global_emote_codes())
        emote_codes.extend(self.fetch_channel_emote_codes())
        logger.debug(
            f"Caching {len(emote_codes)} emotes for {self.__class__.__name__}: "
            f"{emote_codes}"
        )
        self.cached_emote_codes = emote_codes

    def fetch_global_emote_codes(self) -> list[str]:
        raise NotImplementedError

    def fetch_channel_emote_codes(self) -> list[str]:
        raise NotImplementedError

    def get_global_emotes_api_url(self) -> str:
        raise NotImplementedError

    def get_channel_emotes_api_url(self) -> str:
        raise NotImplementedError

    def make_request(self, url) -> requests.Response:
        logger.debug("Fetching emotes from %s", url)

        resp = requests.get(url)
        if resp.ok:
            return resp

        logger.error(f"Failed to fetch emotes from {url}")
        raise FailedToFetchEmotesException


class BetterTTVEmoteProvider(ThirdPartyEmoteProvider):
    def fetch_global_emote_codes(self) -> list[str]:
        resp = self.make_request(self.get_global_emotes_api_url())
        return [emote["code"] for emote in resp.json()]

    def fetch_channel_emote_codes(self) -> list[str]:
        resp = self.make_request(self.get_channel_emotes_api_url())
        channel_emotes = [emote["code"] for emote in resp.json()["channelEmotes"]]
        shared_emotes = [emote["code"] for emote in resp.json()["sharedEmotes"]]
        return channel_emotes + shared_emotes

    def get_global_emotes_api_url(self) -> str:
        return "https://api.betterttv.net/3/cached/emotes/global"

    def get_channel_emotes_api_url(self) -> str:
        return f"https://api.betterttv.net/3/cached/users/twitch/{self.user_id}"


class FrankerFaceZEmoteProvider(ThirdPartyEmoteProvider):
    def fetch_global_emote_codes(self) -> list[str]:
        resp = self.make_request(self.get_global_emotes_api_url())
        global_emote_set = "3"
        return [
            emote["name"]
            for emote in resp.json()["sets"][global_emote_set]["emoticons"]
        ]

    def fetch_channel_emote_codes(self) -> list[str]:
        resp = self.make_request(self.get_channel_emotes_api_url())
        resp_json = resp.json()
        room_emote_set = str(resp_json["room"]["set"])
        return [
            emote["name"] for emote in resp_json["sets"][room_emote_set]["emoticons"]
        ]

    def get_global_emotes_api_url(self) -> str:
        return "https://api.frankerfacez.com/v1/set/global"

    def get_channel_emotes_api_url(self) -> str:
        return f"https://api.frankerfacez.com/v1/room/id/{self.user_id}"
