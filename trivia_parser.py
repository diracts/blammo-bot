# this script is meant to parse trivia questions from a CSV file of 
# trivia questions I found on Reddit and insert them into the csv of trivia
# questions that the bot uses (for now).

import pandas as pd
import random, time, logging, asyncio
import matplotlib.pyplot as plt

