import pandas as pd
import numpy as np

df = pd.read_csv('../blammo-bot-private/record_data.csv')
df = df[df['game_type'] == 'scramble']
df = df[df['outcome'] == 'solved']
freq = df['username'].value_counts()[:10].index.tolist()
print(freq)
# print('Most frequent player: ' + freq[0])
