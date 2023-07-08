import logging, inspect


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s : %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%m/%d/%Y %I:%M:%S %p')
        return formatter.format(record)




# class CustomLogger:
#     def __init__(
#             self,
            
#         ):
#         self.loglevel = loglevel
#         self.logfile = logfile
        

#     def setLevel(self, loglevel):
#         self.loglevel = loglevel


def custom_logger(
        loglevel=logging.DEBUG,
        logfile='logs.log',
    ):
    logger_name = inspect.stack()[1][3]

    # create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(loglevel)
    # create console handler and file handler
    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(logfile)

    # create formatter
    formatter1 = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    # add formatter to console and file handlers
    stream_handler.setFormatter(CustomFormatter())
    file_handler.setFormatter(formatter1)

    # add console and file handlers to logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger

# class CustomLogger:
#     def __init__(
#             self,
#             loglevel=logging.DEBUG,
#             logfile='logs.log',
#         ):
#         self.loglevel = loglevel
#         self.logfile = logfile
        

#     def setLevel(self, loglevel):
#         self.loglevel = loglevel


#     def custom_logger(self):
#         logger_name = inspect.stack()[1][3]
#         # create logger
#         logger = logging.getLogger(logger_name)
#         logger.setLevel(self.loglevel)
#         # create console handler and file handler
#         stream_handler = logging.StreamHandler()
#         file_handler = logging.FileHandler(self.logfile)

#         # create formatter
#         formatter1 = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

#         # add formatter to console and file handlers
#         stream_handler.setFormatter(CustomFormatter())
#         file_handler.setFormatter(formatter1)

#         # add console and file handlers to logger
#         logger.addHandler(stream_handler)
#         logger.addHandler(file_handler)

#         return logger