import logging, os, sys, time, datetime, csv

from log.loggers.custom_format import CustomFormatter

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

# The purpose of this file is to provide a handler for timestamps. 
# There will be a timestamps.csv file in the root directory of the bot.
# This file will be used to store timestamps for various events.
# This file will allow main.py to interact with the timestamps.csv file.
# The timestamps file will store time data in UNIX time format (floats).
# It is important that this code is fast and efficient, as it will be used
# in the main loop of the bot very frequently.
# Should this be an async function? We want this module to be designed in such
# a way that we don't encounter runtime errors when who read and/or update 
# requests are made very close to each other. 

# Dicts are fast, so we will use them to store timestamps in memory.
# When possible, we will update the timestamps.csv file with the latest state of
# self.timestamps. This will be done when the bot is shutting down, or when
# the bot is updating the timestamps.csv file. 

class Timestamps:
    def __init__(
            self,
            fname: str = 'timestamps.csv',
            allowwrite: bool = True,         # allow write to timestamps.csv file
        ):
        self.fname = fname
        self.allowwrite = allowwrite
        self.timestamps: dict = self._init_timestamps() # dict of floats

        logger.info('Timestamps class instantiated')
        logger.info(f'fname: {self.fname}')
        logger.info(f'allowwrite: {self.allowwrite}')
        logger.info(f'timestamps: \n{self.timestamps}')


    def _float_to_timestamp(self, f: float) -> datetime.datetime:
        # converts a float to a datetime.datetime object
        return datetime.datetime.fromtimestamp(f)
    
    def _timestamp_to_float(self, dt: datetime.datetime) -> float:
        # converts a datetime.datetime object to a float
        return dt.timestamp()


    def _create_timestamps_file(self) -> None:
        # create new timestamps csv file with filename self.fname
        logger.warning(f'File {self.fname} does not exist, creating it now')
        logger.error(f'The function _create_timestamps_file() has not been implemented yet.')
        pass


    def _load_from_file(self) -> dict:
        # loads the timestamps.csv file into a pandas dataframe
        # This method of loading a csv to dictionary is meant to be fast, but 
        # this particular way does not work if the csv has more than 2 rows 
        # (header and data).
        with open(self.fname, 'r') as f:
            data = next(csv.DictReader(f))
        for key in data.keys():
            data[key] = float(data[key])
        return data


    def _init_timestamps(self) -> dict:
        # loads the timestamps.csv file into a dictionary
        # if the file does not exist, it creates it
        try:
            if not os.path.exists(self.fname):
                logger.info(f'File {self.fname} does not exist, creating it now')
                self._create_timestamps_file()
            # load the timestamps.csv file as a dictionary
            return self._load_from_file()
        except Exception as e:
            logger.error(f'Exception on initializing timestamps file: {e}')
            pass



    def _write_to_file(self, timestamps: dict) -> None:
        # writes the dictionary to the timestamps.csv file
        # this function is slow and should only be done when necessary.
        try:
            if not self.allowwrite:
                logger.warning(f'Writing to {self.fname} is not allowed.')
                return
            with open(self.fname, 'w') as f:
                writer = csv.DictWriter(f, fieldnames=timestamps.keys())
                writer.writeheader()
                writer.writerow(timestamps)
        except Exception as e:
            logger.error(f'Exception on writing to timestamps file: {e}')
            pass



    def read(self, event_name: str) -> datetime.datetime | float:
        # returns the timestamp of the event
        try:
            unix_time = self.timestamps[event_name]     # timestamp as a float in UNIX time
            return self._float_to_timestamp(unix_time)
        except Exception as e:
            logger.error(f'Exception on reading timestamp from timestamps dict: {e}')
            pass



    def update(self, event_name: str) -> None:
        # writes the current time datetime.datetime.now() to the timestamps.csv file
        try:
            self.timestamps[event_name] = datetime.datetime.now().timestamp()
        except Exception as e:
            logger.error(f'Exception on writing updated timestamp to timestamps dict: {e}')


    def save(self) -> None:
        # writes the current state of self.timestamps to the timestamps.csv file
        # this function is slow and should only be done when necessary.
        try:
            self._write_to_file(self.timestamps)
        except Exception as e:
            logger.error(f'Exception on saving timestamps dict to file: {e}')


    # def clear(self, event_name: str):
    #     # sets the timestamp of the event to datetime.datetime.min
    #     df = self._load_df()
    #     df[event_name] = datetime.datetime.min
    #     self._write_df(df)