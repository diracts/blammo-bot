# BlammoBot Example Datasets

This directory contains example CSV files that demonstrate the structure and format of BlammoBot's database files.

## File Descriptions

### `trivia_example.csv`
Contains example trivia questions with their answers and unique question IDs.

**Format:**
- `question`: The trivia question text
- `correct_answer`: The correct answer
- `enabled`: Whether the question is active (TRUE/FALSE)
- `qid`: Unique question identifier (format: T#### for trivia)

### `scramble_example.csv` 
Contains example scramble words with their scrambled versions and unique question IDs.

**Format:**
- `word`: The original word to be unscrambled
- `enabled`: Whether the word is active (TRUE/FALSE)
- `qid`: Unique question identifier (format: S#### for scramble)

### `user_data_example.csv`
Contains example user data including points and gambling statistics.

**Format:**
- `username`: Twitch username (lowercase)
- `points`: Current point balance
- `gamble_loss`: Total points lost through gambling

### `timestamps_example.csv`
Contains example timestamp data for command cooldowns and game states.

**Format:**
- `trivia_started`: When the last trivia game started
- `scramble_started`: When the last scramble game started  
- `roulette_cmd`: When the last roulette command was used
- `last_auto_record_write`: When records were last written to file
- Values are UNIX timestamps (floats)
- Used for cooldown management and state tracking

### `record_data_example.csv`
Contains example game event records for statistics and logging.

**Format:**
- `timestamp`: When the record was created (UNIX timestamp)
- `qid`: Unique question identifier for the game
- `game_type`: Type of game (trivia, scramble)
- `outcome`: Result (solved, timeout)
- `time_elapsed`: Time taken to answer (seconds)
- `username`: Player who answered
- `points_awarded`: Points given for correct answer
- `guess_string`: Player's actual guess
- `guess_similarity`: Similarity score between guess and answer (0.0-1.0)
- `question_string`: The question that was asked
- `answer_string`: The correct answer

### `submissions_example.csv`
Contains example user submissions for trivia questions and scramble words.

**Format:**
- `username`: User who submitted the content
- `question`: Trivia question submitted (if applicable)
- `answer`: Answer for trivia question (if applicable)
- `word`: Scramble word submitted (if applicable)
- Empty column (reserved)
- `timestamp`: When the submission was made (UNIX timestamp)

## Usage

### For Development
Copy these files to `../blammo-bot-private/` and rename them:
```bash
cp trivia_example.csv ../blammo-bot-private/trivia.csv
cp scramble_example.csv ../blammo-bot-private/scramble.csv
cp user_data_example.csv ../blammo-bot-private/user_data.csv
cp timestamps_example.csv ../blammo-bot-private/timestamps.csv
cp record_data_example.csv ../blammo-bot-private/record_data.csv
cp submissions_example.csv ../blammo-bot-private/submissions.csv
```

### For New Installations
The bot will create empty versions of these files automatically, but you can use these examples as starting points.

## Important Notes

1. **Encoding**: The actual bot databases use `latin-1` encoding for compatibility with legacy data
2. **QID Format**: Question IDs should be unique and follow the T#### (trivia) or S#### (scramble) format
3. **Username Case**: All usernames are stored in lowercase
4. **Timestamps**: Use UNIX timestamp format (seconds since epoch) as floats

## Data Guidelines

### Trivia Questions
- Keep questions clear and concise
- Answers should be specific but not overly complex
- Avoid questions that become outdated quickly
- Follow the style guidelines in the main README

### Scramble Words
- Use common English words
- Avoid proper nouns unless very well-known
- Ensure words are not too easy or too difficult
- Keep reasonable word length (3-15 characters)

### Points System
- Default starting balance is 200 points (configurable)
- New users automatically get default balance
- Points cannot go negative (enforced by bot)

## Testing
These example files are used by the test suite to verify database functionality works correctly.