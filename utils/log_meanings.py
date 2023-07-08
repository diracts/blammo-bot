# The purpose of this file is to define a dictionary of log levels and their 
#   corresponding meanings. This is primarily used in the #setloglevel command
#   to display the meaning of integer log levels in chat. 
# The function to 



# `levels` will be a dictionary of dict[int, str]
# There are 51 (50?) log levels, but we don't want to write them all out now.
# Instead, we will have the get_level_meaning function return the nlevel of the 

levels = {
    0: 'NOTSET',
    10: 'DEBUG',
    20: 'INFO',
    30: 'WARNING',
    40: 'ERROR',
    50: 'CRITICAL'
}

def get_level_meaning(level: int) -> str:
    """Returns the meaning of a given log level."""
    global levels

    return 