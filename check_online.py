import os
import asyncio
import sys
import logging
import requests

from utils.secrets import get_oauth, get_client_id, get_client_secret
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


ONLINE_SIGNAL_FILE_NAME = "online_signal.txt"
CHANNEL_ONLINE_CHECK_NAME = "hasanabi"
CHANNEL_ONLINE_CHECK_INTERVAL = 40  # changed from 20 to 40 to see if it fixes the "max retries exceeded for url" error


# async def print_every_5_seconds():
#     # global STREAM_ONLINE
#     while True:
#         print('STREAM IS OFFLINE')
#         try:
#             os.remove(ONLINE_SIGNAL_FILE_NAME)
#         except:
#             pass
#         await asyncio.sleep(20)
#         # STREAM_ONLINE = True
#         open(ONLINE_SIGNAL_FILE_NAME, 'w').close()
#         print('STREAM IS ONLINE')
#         await asyncio.sleep(20)


def get_signal_file_name() -> str:
    """Get the name of the online signal file

    Returns:
        str: name of the online signal file
    """
    return ONLINE_SIGNAL_FILE_NAME


def get_channel_name() -> str:
    """Get the name of the channel to check if online

    Returns:
        str: name of the channel to check if online
    """
    return CHANNEL_ONLINE_CHECK_NAME


def get_check_interval() -> int:
    """Get the interval at which to check if the channel is online

    Returns:
        int: interval at which to check if the channel is online
    """
    return CHANNEL_ONLINE_CHECK_INTERVAL


def check_stream_online(
    channel: str = CHANNEL_ONLINE_CHECK_NAME,
    verbose: bool = False,
):
    """Is the stream online?

    Args:
        channel (str, optional): channel to check. Defaults to 'hasanabi'.

    Returns:
        bool: True if stream is online, False if stream is offline
    """
    body = {
        "client_id": get_client_id(),
        "client_secret": get_client_secret(),
        "grant_type": "client_credentials",
    }
    r = requests.post("https://id.twitch.tv/oauth2/token", body)
    # data output
    keys = r.json()
    headers = {
        "Client-ID": get_client_id(),
        "Authorization": "Bearer " + keys["access_token"],
    }
    stream = requests.get(
        "https://api.twitch.tv/helix/streams?user_login=" + channel, headers=headers
    )
    stream_data = stream.json()
    logger.log(7, f"stream_data: {stream_data}")
    logger.log(7, f"type(stream_data): {type(stream_data)}")
    if len(stream_data["data"]) == 1:
        if verbose:
            print(
                channel
                + " is live: "
                + stream_data["data"][0]["title"]
                + " playing "
                + stream_data["data"][0]["game_name"]
            )
        logger.log(9, f"{channel} is live.")
        return True
    else:
        logger.log(9, f"{channel} is not live.")
        if verbose:
            print(channel + " is not live")
        return False


def online_signal_file_exists() -> bool:
    """Does the online signal file exist?

    Returns:
        bool: True if online signal file exists, False if it does not
    """
    try:
        status = os.path.isfile(ONLINE_SIGNAL_FILE_NAME)
    except Exception as e:
        logger.critical(f"Exception checking if online signal file exists: {e}")
        sys.exit(1)
    return status  # Is this correctly placed?


async def check_loop():
    while True:
        await asyncio.sleep(CHANNEL_ONLINE_CHECK_INTERVAL)
        attempts = 0
        MAX_ATTEMPTS = 3
        while attempts <= MAX_ATTEMPTS + 1:
            try:
                is_online = check_stream_online()
                break
            except Exception as e:
                attempts += 1
                if attempts >= MAX_ATTEMPTS + 1:
                    logger.critical(
                        f"Exception checking if stream is online: {e}. Cannot verify stream status, so exiting program."
                    )
                    sys.exit(1)
                else:
                    logger.warning(
                        f"Exception checking if stream is online: {e}. Retrying in 15 seconds. Attempt {attempts}/{MAX_ATTEMPTS}."
                    )
                    await asyncio.sleep(15)

        sig_file_exists = (
            online_signal_file_exists()
        )  # Does the "stream is online" signal file exist?

        if is_online and sig_file_exists:
            # Stream is online and online signal file exists. This is the expected state.
            logger.log(9, f"Stream is online and online signal file exists.")
        elif is_online and not sig_file_exists:
            # Stream is online but online signal file does not exist. Need to create signal file.
            logger.info(f"Stream now online. Sleeping bot.")
            try:
                open(ONLINE_SIGNAL_FILE_NAME, "w").close()
                logger.debug("Created online signal file.")
            except Exception as e:
                logger.critical(
                    f"Exception creating online signal file: {e}. Exiting program."
                )
                sys.exit(1)
        elif not is_online and sig_file_exists:
            # Stream is offline but online signal file exists. Need to remove signal file.
            logger.info(f"Stream now offline. Waking bot.")
            try:
                os.remove(ONLINE_SIGNAL_FILE_NAME)
                logger.debug("Removed online signal file.")
            except Exception as e:
                logger.critical(
                    f"Exception removing online signal file: {e}. Exiting program."
                )
                sys.exit(1)
        elif not is_online and not sig_file_exists:
            # Stream is offline and the online signal file does not exist. This is the expected state.
            logger.log(9, f"Stream is offline and online signal file does not exist.")
        else:
            # This should never happen.
            logger.critical(
                f"Unexpected state: is_online={is_online}, sig_file_exists={sig_file_exists}. Exiting program."
            )
            sys.exit(1)
