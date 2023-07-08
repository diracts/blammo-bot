from trivia import trivia
import asyncio

#To use outside of an async function
loop = asyncio.get_event_loop()
questions = loop.run_until_complete(trivia.question(amount=1, category=2, difficulty='easy', quizType='multiple'))

#To use within an aysnc function
async def main():
    questions = await trivia.question(amount=1, category=2, difficulty='easy', quizType='multiple')
    print(questions)


if __name__ == '__main__':
    asyncio.run(main())