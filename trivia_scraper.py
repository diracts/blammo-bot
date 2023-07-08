import sys, asyncio, time, random
from datetime import datetime
import pandas as pd
from trivia import trivia
import matplotlib.pyplot as plt

def remove_duplicates(df):
    df = df.drop_duplicates(subset=['question'])
    return df

def plot_length_history(counter, length):
    plt.plot(counter, length)
    plt.xlabel('Loop')
    plt.ylabel('Length')
    plt.savefig('length_history.png')
    plt.close()

async def main():
    print('SCRAPING DONE, DO NOT RUN THIS SCRIPT AGAIN')
    sys.exit(0)
    loops = 1000

    x, y = [], []
    counter = 0
    while True:
        print(f'Loop {counter}')
        diff_ratios = {
            'easy': 0.5,
            'medium': 0.3,
            'hard': 0.1,
        }
        diff = random.choices(list(diff_ratios.keys()), weights=list(diff_ratios.values()))[0]
        questions = await trivia.question(
            amount=20, 
            category=0, 
            difficulty=diff, 
            quizType='multiple',
        )
        # print(questions)
        # for question in questions:
        #     print(question, '\n')
        
        

        df = pd.DataFrame(questions)
        df.to_csv('trivia.csv', mode='a', header=False, index=False)

        if counter % 10 == 0:
            print('Removing duplicates...')
            df = pd.read_csv('trivia.csv')
            initial_len = len(df)
            df = remove_duplicates(df)
            final_len = len(df)
            print(f'Removed {initial_len - final_len} duplicates')
            print(f'Current length: {final_len}')
            df.to_csv('trivia.csv', index=False)
            x.append(counter)
            y.append(len(df))
            plot_length_history(x, y)

        counter += 1
        time.sleep(1)
        if counter == loops:
            sys.exit(0)

if __name__ == '__main__':
    asyncio.run(main())
