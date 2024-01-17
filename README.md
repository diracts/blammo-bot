# blammo-bot

Major work in progress. The code is extremely messy right now and there are core parts of the bot that have not been pushed to this repo yet. There is also certain pieces of the bot that will *never* be included in the public repo. These are: 
- Trivia database
- Scramble database
- Security features
- Certain config files (an example or default version will be provided if possible)
- User data (points, gamble loss, etc.)
- Logs
- Anything the sickos could abuse


## To-Do Items

- Rebuild the question id system to use alphanumeric id strings (make them shorter)
- Add #report command (report either question id or question ask number that is unique every question run)
- Add example trivia and scramble datasets so people know how to interact with them correctly
- Add documentation for all current functions
- Fix the latin-1 vs. UTF-8 encoding issue with the trivia database
- Auto trivia/scramble validation and format checking
- Refactor original twitch bot framework to allow class self variable to be used (so we can stop using global all the time)
- make timestamps system more comprehensive and robust
- general: integrate custom functions with original framework better
- general: remove or disable unused functionality from original bot framework
- add test cases like i was supposed to a long time ago lmao
- general: plan out and follow a better structure for the entire project
- quick: create smart cooldown function and apply it to #roulette, #points, #submit, etc. to prevent intentional spamming (smart cooldown should keep track of how many commands a user has run in the recent past and prevent them from running the command again if they exceed some N number within a fixed T time window)
- ISSUE: in database health utils, make functions to detect the following bad conditions:
    - failed git merge artifacts (<<<<<<<, >>>>>>>, HEAD, =======, etc.) (do not attempt to resolve, just provide warning and let a human fix it)
    - duplicate questions, duplicate users in user_data, duplicate scramble questions
- ISSUE: modify database utils to prevent a qid from ever being assigned if it is non-unique. The current strategy relies on "assign -> check unique -> reassign if non-unique". This causes issues when git failed merge creates duplicate rows in the file, and then dbutils tries to resolve duplicate qid by reassigning qid
- for all databases, add more dates. also decide on a standardized date string format (mm-dd-yyyy hh:mm:ss.{.3milliseconds} example 08-03-2023 08:34:21.704)  
    - for trivia database, add columns "date added", "date modified" (will need to create hash row and hash checker function for this)
    - for scramble databse, add colums "date added", "date modified" (similar situation as trivia)
    - for user_data, add columns "date added", "date modified"
    - add date time info for submission and event logs
- TODO: Figure out some way to interact with supervisorctl and trigger a restart from chat command
    - hacky idea: restart.sh; thru python launch shell to run restart.sh with supervisorctl restart blammobot after 1 second delay
- TODO: fix issue with no log file while running (ex: log file was moved for archive) and no new log file is created (specifically for logs.log, but may also be happening with other log files)
- TODO: set up auto log file archiving

## Trivia Editing

### Numbers in answers

In general, numbers should be given in their numerical form (ex. "8") instead of their word form (ex. "eight") in answers. This should be the default format most of the time, but there are many exceptions. 

### Former Names

Questions involving the former name of a person are allowed in most cases (ex. Q: "What was Bruno Mars named at birth?", A: "Peter Hernandez"). However, questions involving the former name of people who have transitioned (i.e. their dead name) are never allowed.

### Questions Involving Some Aspect of the Current Date

Careful treatment must be given to questions involving some detail that is attached to the current date. For example, the question "To the nearest million, what is the current population of China?" is bad because we do not know what "current" means here. Does it mean this year? Last year? Five years ago? Who knows. This question can be fixed by adding mention to a specific date. Now, the question might read "To the nearest million, what _was_ the population of China _in 2023_?" This is much better. It is also good practice to keep these kinds of questions in past tense. 

### British Spelling

U.S. English spelling is to be used over British spelling except in proper nouns, titles of works, or instances where distinction is needed. No aluminium, colour, and massacre. 

## FAQs

### Where are the trivia questions? 
You aren't going to find them here! The trivia database is in a separate private repository that will not be made public. The same is true for the scramble database. This is the only part of the bot that is not available publicly.

### Can I use this code? 
Yes of course! If you decide to use this code, I would appreciate a reference back to this repository somewhere in your documentation, but other than that, go wild. 

### Roulette is rigged! Stop it! 
Roulette is always 50-50 chance of success or failure. 

### Why isn't this project written in Go?
stfu nerd (i don't know go)


## Contributing

Yes! If you would like to contribute anything to this project, please do so. 
