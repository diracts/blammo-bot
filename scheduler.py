import subprocess, datetime, time, asyncio, os, sys, requests, logging

from utils.secrets import get_client_id, get_oauth, get_client_secret
from main import BlammoBot as bot

# from log.loggers.custom_format import CustomFormatter   # for level colors

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

# formatter1 = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
# file_handler = logging.FileHandler('logs.log')
# file_handler.setFormatter(formatter1)

# stream_handler = logging.StreamHandler()
# stream_handler.setFormatter(CustomFormatter())

# logger.addHandler(file_handler)
# logger.addHandler(stream_handler)


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


from log.loggers.custom_format import CustomFormatter   # for level colors

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter1 = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s : %(message)s', 
    datefmt='%m/%d/%Y %I:%M:%S %p'
)
file_handler = logging.FileHandler('logs.log')
file_handler.setFormatter(formatter1)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(CustomFormatter())

logger.addHandler(file_handler)
logger.addHandler(stream_handler)



CLIENT_ID = get_client_id()
OATH_TOKEN = get_oauth()
CLIENT_SECRET = get_client_secret()


# !!! SCHEDULER AND MAIN MUST BE IN SAME DIRECTORY FOR SHUTDOWN TO WORK !!!
if os.path.exists('shutdown.txt'):
    os.remove('shutdown.txt')

def check_stream_online(
        channel: str = 'hasanabi', 
        verbose: bool = False,
    ):
    """Is the stream online?

    Args:
        channel (str, optional): channel to check. Defaults to 'hasanabi'.

    Returns:
        bool: True if stream is online, False if stream is offline
    """    
    body = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        "grant_type": 'client_credentials'
    }
    r = requests.post('https://id.twitch.tv/oauth2/token', body)
    #data output
    keys = r.json()
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': 'Bearer ' + keys['access_token']
    }
    stream = requests.get('https://api.twitch.tv/helix/streams?user_login=' + channel, headers=headers)
    stream_data = stream.json()
    if len(stream_data['data']) == 1:
        if verbose:
            print(
                channel + ' is live: ' + stream_data['data'][0]['title'] + 
                ' playing ' + stream_data['data'][0]['game_name']
            )
        logger.debug(f'{channel} is live.')
        return True
    else:
        logger.debug(f'{channel} is not live.')
        if verbose:
            print(channel + ' is not live')
        return False

def check_command_shutdown():
    if os.path.exists('shutdown.txt'):
        os.remove('shutdown.txt')
        print('COMMAND SHUTDOWN')
        logger.info('Shutting down from #shutdown command.')
        subproc.kill()
        sys.exit(0)

subproc = subprocess.Popen(["python", "main.py"])
while True:
    # print(f'COMMAND_SHUTDOWN: {COMMAND_SHUTDOWN}')
    stream_live = check_stream_online()
    bot_running = subproc.poll() is None

    logger.debug(f'Stream Live: {stream_live}')
    logger.debug(f'Bot Running: {bot_running}')

    check_command_shutdown()
    if stream_live and bot_running:
        # stream live and bot running --> kill bot
        logger.debug('Stream is live and bot is running. Attempt kill.')
        subproc.kill()
        logger.info('Killed bot since stream is online.')
    elif not stream_live and not bot_running:
        # stream offline and bot not running --> start bot
        logger.debug('Stream is offline and bot is not running. Attempt start.')
        subproc = subprocess.Popen(["python", "main.py"])
        logger.info('Started bot since stream is offline.')

    elif stream_live and not bot_running:
        # this is what we want if the stream is live
        logger.debug('Stream is live and bot is not running.')
        pass
    elif not stream_live and bot_running:
        # this is what we want if the stream is offline
        logger.debug('Stream is offline and bot is running.')
        pass

    for i in range(5):
        check_command_shutdown()
        time.sleep(4)