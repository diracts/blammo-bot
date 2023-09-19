import pandas as pd

# The purpose of this script is to take a csv and convert it into a utf-8 encoded csv.

pd.read_csv("../../blammo-bot-private/scramble.csv", encoding="utf-8")
