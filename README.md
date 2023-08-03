# blammo-bot

Major work in progress. The code is extremely messy right now and there are core parts of the bot that have not been pushed to this repo yet. There is also certain pieces of the bot that will *never* be included in the public repo. These are: 
- Trivia database
- Scramble database
- Security features
- Certain config files (an example or default version will be provided if possible)
- User data (points, gamble loss, etc.)
- Logs
- Anything the sickos could abuse

Again, the code is extremely messy right now and if you roast me, then L nerd get rekt ur a bigger nerd than i am ICANT


## To-Do Items

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
- quick: create smart cooldown function and apply it to #roulette, #points, #submit, etc. to prevent intentional spamming
-       smart cooldown should keep track of how many commands a user has run in the recent past and prevent them from running the command again if they exceed some N number within a fixed T time window
- ISSUE: in database health utils, make functions to detect the following bad conditions:
    - failed git merge artifacts (<<<<<<<, >>>>>>>, HEAD, =======, etc.) (do not attempt to resolve, just provide warning and let a human fix it)
    - duplicate questions, duplicate users in user_data, duplicate scramble questions
- ISSUE: modify database utils to prevent a qid from ever being assigned if it is non-unique. The current strategy relies on "assign -> check unique -> reassign if non-unique". This causes issues when git failed merge creates duplicate rows in the file, and then dbutils tries to resolve duplicate qid by reassigning qid
- for all databases, add more dates. also decide on a standardized date string format (mm-dd-yyyy hh:mm:ss.{.3milliseconds} example 08-03-2023 08:34:21.704)  
    - for trivia database, add columns "date added", "date modified" (will need to create hash row and hash checker function for this)
    - for scramble databse, add colums "date added", "date modified" (similar situation as trivia)
    - for user_data, add columns "date added", "date modified"
    - add date time info for submission and event logs


## Contributing

Yes! If you would like to contribute anything to this project, please do so. 
