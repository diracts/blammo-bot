import logging, sys, os

# from log.loggers.custom_format import CustomFormatter   # for level colors

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# formatter1 = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
# file_handler = logging.FileHandler('logs.log')
# file_handler.setFormatter(formatter1)

# stream_handler = logging.StreamHandler()
# stream_handler.setFormatter(CustomFormatter())

# logger.addHandler(file_handler)
# logger.addHandler(stream_handler)


# The purpose of this file is to take in a string and determine the appropriate
#   splash emote to be included with the message. 


DEFAULT = {
    'trivia question prefix':       'Chatting',             # for when question is asked
    'trivia question suffix':       'Gayge HYPERCLAP',
    'trivia correct prefix':        '',                     # for when correct answer is given
    'trivia correct suffix':        'FeelsGoodMan',
    'trivia timeout prefix':        '',                     # for when time runs out
    'trivia timeout suffix':        'FeelsBadMan',
    'scramble question prefix':     '',
    'scramble question suffix':     'FeelsDankMan TeaTime',
    'scramble correct prefix':      '',
    'scramble correct suffix':      'FeelsGoodMan',
    'scramble timeout prefix':      '',
    'scramble timeout suffix':      'FeelsBadMan',
}

def splash(s: str):
    if 'german' in s.lower():
        return 'DatSheffy HYPERCLAP'
    elif any(i in s.lower() for i in ['french', 'france']):
        return 'Madge 🥖'
    elif 'album' in s.lower():
        return 'pepeJAM 🎵'
    elif 'song' in s.lower():
        return 'pepeJAM 🎵'
    elif any(i in s.lower() for i in ['british', 'britain', 'england']):
        return '3Head TeaTime'
    elif any(i in s.lower() for i in ['look up', 'looking up']):
        return 'LookUp TeaTime'
    elif any(i in s.lower() for i in ['hasan minhaj']):
        return 'hasWut TeaTime'
    elif any(i in s.lower() for i in ['hasanabi', 'hasan']):
        return 'peepoHas TeaTime'
    elif any(i in s.lower() for i in ['turkey', 'turkish', 'ankara', 'istanbul', 'constantinople', '1453']):
        return 'KEKebab HYPERCLAP'
    else:
        return ''