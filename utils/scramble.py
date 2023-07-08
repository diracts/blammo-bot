import pandas as pd
import logging, random

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

formatter1 = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
file_handler = logging.FileHandler('logs.log')
file_handler.setFormatter(formatter1)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(CustomFormatter())

logger.addHandler(file_handler)
logger.addHandler(stream_handler)



class ScrambleData():
    def __init__(
            self,
            path='scramble.csv',
            allow_load=True,        # use False when testing or anticipating unsafe behavior
        ):
        self.path = path
        self.allow_load = allow_load

        if self.allow_load:
            self.df = pd.read_csv(
                path, 
                index_col=False, 
                header=0, 
                # encoding='latin-1'
            )
        else:
            self.df = None

        
    def reload(self):
        if self.allow_load:
            self.df = pd.read_csv(
                self.path,
                index_col=False,
                header=0,
                # encoding='latin-1'
            )
            logger.info(f'Reloaded scramble database: {self.path}')
            logger.debug(f'Scramble database length: {len(self.df)}')
            logger.debug(f'Scramble database columns: {self.df.columns}')   # string concat col names for appearance?
        else:
            logger.warning('Attempted to reload scramble database with allow_load=False. Ignoring...')
            pass
            

    def scramble_string(self, s: str):
        # scramble the string
        shuffled = s
        # while loop prevents non-scrambled words from being returned
        while shuffled == s:
            lst = list(s)
            random.shuffle(lst)
            shuffled = ''.join(lst)
        return shuffled
        
        


    def get_word(self):
        # return a tuple of (scrambled word, unscrambled word)
        if not self.allow_load:
            return
        
        found_valid = False   # bool to keep track of if we've found a valid word
        while not found_valid:
            w_df = self.df.sample(n=1)
            w = w_df.to_dict('records')[0]      # verify that 'records' is the correct arg for what we want
            # TODO: Add an actual word validation function.
            if w['enabled'] == True or w['enabled'] == 'TRUE':
                found_valid = True
            else:
                print('================================================================================================')
                print('Scramble word disabled, trying again...')
                print(f'Word: {w["word"]}')
                print('================================================================================================')

        scrambled_word = self.scramble_string(w['word'])

        return scrambled_word, w['word'], w['qid']