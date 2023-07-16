import sys
import os
import random
import time
import logging
import urllib3
import json
import requests
import datetime
import signal
import re
from pathlib import Path
from twitchbot import BaseBot
from twitchbot import event_handler, Event, Command, Message, Channel, PollData, get_bot
from twitchbot.config import get_nick, get_oauth, get_client_id, get_client_secret

# from trivia import trivia
import asyncio
from difflib import SequenceMatcher as SM

from twitchbot.command import Command
from twitchbot.message import Message

from utils.dbutils import clean_qid, add_qid
from utils.timestamps import Timestamps
from utils.record import Record
from utils.points import PointData
from utils.trivia import TriviaData
from utils.scramble import ScrambleData
from utils.secrets import get_oauth, get_client_id, get_client_secret
from utils import submit
from utils import secretcommand
import check_online

# from validate import get_alt_answer, check_string_safety
# 10 - DEBUG + level 11
# 11 - all chat messages + level 12
# 12 - all Bot messages

from log.loggers.custom_format import CustomFormatter  # for level colors

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter1 = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s : %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
file_handler = logging.FileHandler("logs.log")
file_handler.setFormatter(formatter1)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(CustomFormatter())

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

ONLINE_SIGNAL_FILE_NAME = check_online.get_signal_file_name()
CHANNEL_ONLINE_CHECK_NAME = check_online.get_channel_name()
CHANNEL_ONLINE_CHECK_INTERVAL = check_online.get_check_interval()


class BlammoBot(BaseBot):
    logger.debug("BlammoBot class instantiated")

    global points
    global timestamps_dict  # used to track when the last time a command was used
    global timestamps
    global restart_scheduled  # used to track if a restart is scheduled
    global shutdown_scheduled  # used to track if a shutdown is scheduled
    global silent_cooldown  # used to allow silent cooldowns
    global record
    global TRIVIA_QID
    global SCRAMBLE_QID
    global STREAM_ONLINE
    global REPLY_NEXT

    global trivia
    global questions
    global trivia_started
    global _generate_hint
    global _find_chars
    global _set_char_in_string
    global _check_all_alphanumeric
    global _reload_trivia
    global _reload_scramble
    global _reload_secretcommand

    global scramble  # trivia equivalent: trivia
    global scramble_word  # trivia equivalent: questions  (scrambled, unscrambled)
    global scramble_started  # trivia equivalent: trivia_started

    questions = None
    trivia_started = False
    scramble_started = False
    COMMAND_SHUTDOWN = False
    restart_scheduled = False
    shutdown_scheduled = False
    TRIVIA_QID = ""
    SCRAMBLE_QID = ""
    silent_cooldown = {
        "trivia": 10,
        "scramble": 10,
    }
    REPLY_NEXT = ""

    timestamps = Timestamps()
    record = Record("../blammo-bot-private/record_data.csv")
    points = PointData()
    trivia = TriviaData()
    scramble = ScrambleData()

    def logmsg(self, msg: str):
        now = datetime.datetime.now()
        ts = now.strftime("%Y-%m-%d %H:%M:%S")
        print("\x1B[3m" + ts + " " + msg + "\x1B[0m")
        # logger.log(11, msg)

    def _drop_stop(self):
        pass

    def _check_all_alphanumeric(string: str):
        """Check if string is alphanumeric

        Args:
            string (str): string to check

        Returns:
            bool: True if string is alphanumeric, False otherwise
        """
        pattern = re.compile(r"^\w+$")
        return bool(pattern.fullmatch(string))

    def _check_trivia_guess(self, msg: Message, questions: list | tuple):
        question, answer, qid = questions

        # msg.content = msg.content.lower().strip('smadge').strip(' ')

        # fix year exploit: guess of 198 will be accepted for 1980, 1981, 1982, etc.
        if len(answer) < 5 and answer.isdigit():
            if answer == msg.content:
                return 1
            else:
                return 0.0

        # answer: Jeremy        This combination should be counted as correct
        # msg.content: Jeremy Elbertson
        if answer.lower() in msg.content.lower():
            return 1  # if guess is in answer, return 0.99
        else:
            similarity_ratio = SM(
                None, msg.content.lower(), questions[1].lower()
            ).ratio()
            return similarity_ratio

    def _check_scramble_guess(self, msg: Message) -> bool:
        global scramble_word

        answer = scramble_word[1].lower()  # work in lowerspace chars

        words = str(msg.content.lower()).split(" ")
        words = [w.lower() for w in words if w != ""]
        logger.log(7, f"[Scramble] word in chat message being checked: {words}")
        if len(words) >= 5:  # change to 4 the function takes too long
            return False  # any message with more 5 or more words cannot be the correct answer
        out = answer in words
        logger.log(7, f"[Scramble] answer ({answer}) in word list: {out}")
        return out

    def _find_chars(string: str, char: str):
        """Find indices of character in string. string[ind[0]] == char

        Args:
            string (str): string to search
            char (str): character to find

        Returns:
            list: indices of char in string
        """
        # TODO: make this a generator if needed
        return [i for i, letter in enumerate(string) if letter == char]

    def _set_char_in_string(string: str, char: str, ind: (list | str)):
        """Set character at index in string to char

        Args:
            string (str): string to modify
            char (str): character to set
            ind (list | str): index to set char at

        Returns:
            str: modified string
        """
        if isinstance(ind, str):
            ind = [ind]
        for i in ind:
            string = string[:i] + char + string[i + 1 :]
        return string

    def _generate_hint(answer: str):
        # for multi-word answers, we should consider hinting the first letter of
        # each word after the first word

        # 1) set all characters to underscores
        # 2) add spaces back in
        # 3) add first 3 characters back in if longer than 4 characters
        # 4) add first 2 chars if len(answer) == 4
        # 5) add first char if len(answer) == 3
        # 6) add nothing if len(answer) == 2 or 1
        # 7) if len(answer) > 10, cut off characters after 10 and add '...' to end
        global _find_chars
        global _set_char_in_string

        hint = "_" * len(answer)
        space_inds = _find_chars(answer, " ")
        hint = _set_char_in_string(hint, " ", space_inds)
        if len(answer) == 1:
            hint = "_"
        elif len(answer) == 2:
            hint = answer[0] + "_"
        elif len(answer) == 3:
            hint = answer[:2] + "_"
        elif len(answer) == 4:
            # hint = answer[:2] + hint[2:]
            hint = answer[:3] + hint[3:]
        elif len(answer) < 10:
            hint = answer[:3] + hint[3:]
        elif len(answer) >= 10:
            hint = answer[:6] + hint[6:]
            hint = hint[:10] + "..."

        return hint

    def check_online_signal_file(self) -> bool:
        """Check if the online signal file exists

        Returns:
            bool: True if file exists, False otherwise
        """
        return os.path.isfile(ONLINE_SIGNAL_FILE_NAME)

    async def on_privmsg_received(self, msg: Message):
        global points
        global timestamps
        global record
        global TRIVIA_QID
        global SCRAMBLE_QID
        global STREAM_ONLINE
        global REPLY_NEXT

        global trivia_started
        global questions

        global scramble_started
        global scramble_word
        # TODO: understand whether it reloads these global vars every chat message
        # i.e., if we add 10 more chat games, will it ~10x the timing of on_privmsg_received?
        # If so, this could cause serious global timing issues.

        # # every 5 seconds change the value of self.stream_online to simulate a stream going online/offline
        # if self.stream_online and 'toggletimetest' in msg.content and msg.author == 'diraction':
        #     self.stream_online = False
        # if not self.stream_online and 'toggletimetest' in msg.content and msg.author == 'diraction':
        #     self.stream_online = True

        self.stream_online = self.check_online_signal_file()
        if self.stream_online == True and self.stream_online_prev == False:
            await msg.reply(f"Bedge 💤 honk shoo Bedge 💤 mimimimi")
            logger.info(
                f"Stream went online at {datetime.datetime.now().isoformat()}. Bot sleeping."
            )
        if self.stream_online == False and self.stream_online_prev == True:
            await msg.reply(f"Wokege")
            logger.info(
                f"Stream went offline at {datetime.datetime.now().isoformat()}. Bot awake."
            )
        self.stream_online_prev = self.stream_online

        if not self.stream_online or not self.stream_online_prev:
            self.logmsg(f"Chat #{msg.channel.name} ({msg.author}) {msg.content}")

        if "lekw" in msg.content.lower():
            await msg.reply("LEKW ✊")
            logger.info(
                f"{msg.author} triggered LEKW response with message: {msg.content}"
            )

        if REPLY_NEXT != "":
            reply_next_copy = REPLY_NEXT
            REPLY_NEXT = ""
            logger.info(
                f"{msg.author} triggered REPLY_NEXT, delivered the message: {reply_next_copy}"
            )
            await msg.reply(reply_next_copy)
            reply_next_copy = ""

        bot_names = [
            "blammobot",
            "blammo",
            "blamobot",  # for spelling mistakes
            "blamo",  # for spelling mistakes
        ]
        if any(substr in msg.content.lower() for substr in bot_names):
            logger.info(f"{msg.author} mentioned BlammoBot: {msg.content}")

        if trivia_started:
            # # TODO: Is this "already running" reminder doing anything? Is it redundant? Or is it being used somehow???
            # if msg.content.lower()[1:] == 'trivia':
            #     await msg.reply(f'[Trivia] @{msg.author} Trivia already running.')
            #     await msg.reply(f'DinkDonk @Diraction')     # ??? why is this here?

            similarity = self._check_trivia_guess(msg, questions)
            if (
                similarity >= 0.92 and len(msg.content) < 250
            ):  # allow 8% error for spelling, punctuation, etc.
                trivia_started = False
                await msg.reply(
                    f'[Trivia] @{msg.author} You answered the question correctly and got 10 points. FeelsGoodMan The answer was: "{questions[1]}"'
                )
                points.add_points(msg.author, 10)
                logger.info(f"[Trivia] {msg.author} answered trivia correctly.")
                logger.debug(f"[Trivia] Similarity: {similarity}")

                # >>> record section <<<
                logger.debug(f"[Trivia] Writing trivia record for {TRIVIA_QID}")
                trivia_delta = datetime.datetime.now() - timestamps.read(
                    "trivia_started"
                )
                record.add_time_elapsed(TRIVIA_QID, trivia_delta.total_seconds())
                record.add_outcome(TRIVIA_QID, "solved")
                record.add_username(TRIVIA_QID, msg.author)
                record.add_points_awarded(TRIVIA_QID, 10)
                record.add_guess_string(TRIVIA_QID, msg.content)
                record.add_guess_similarity(TRIVIA_QID, similarity)
                record.write(TRIVIA_QID)
                TRIVIA_QID = ""

            elif similarity >= 0.85 and len(msg.content) < 250:
                trivia_started = False
                await msg.reply(
                    f'[Trivia] @{msg.author} You answered the question correctly and got 8 points. FeelsGoodMan The answer was: "{questions[1]}"'
                )
                points.add_points(msg.author, 8)
                logger.info(f"[Trivia] {msg.author} answered trivia correctly.")
                logger.debug(f"[Trivia] Similarity: {similarity}")

                # >>> record section <<<
                logger.debug(f"[Trivia] Writing trivia record for {TRIVIA_QID}")
                trivia_delta = datetime.datetime.now() - timestamps.read(
                    "trivia_started"
                )
                record.add_time_elapsed(TRIVIA_QID, trivia_delta.total_seconds())
                record.add_outcome(TRIVIA_QID, "solved")
                record.add_username(TRIVIA_QID, msg.author)
                record.add_points_awarded(TRIVIA_QID, 8)
                record.add_guess_string(TRIVIA_QID, msg.content)
                record.add_guess_similarity(TRIVIA_QID, similarity)
                record.write(TRIVIA_QID)
                TRIVIA_QID = ""

            elif similarity >= 0.75 and len(msg.content) < 250:
                await msg.reply(
                    f"[Trivia] @{msg.author} {msg.content} is close. [Similarity {100*similarity:.0f}%]"
                )
                logger.debug(f"[Trivia] Similarity: {similarity}")
                logger.info(f"[Trivia] {msg.author} is close ({100*similarity:.0f}%).")
            else:
                pass

        if scramble_started:
            if self._check_scramble_guess(msg):
                # if msg.content.lower() == scramble_word[1].lower():
                scramble_started = False
                # logger.debug(f'scramble solution found from {msg.author}')
                # logger.debug(f'scramble solution: {scramble_word[1]}')
                await msg.reply(
                    f'[Scramble] @{msg.author} You answered the question correctly and got 10 points. FeelsGoodMan The word was " {scramble_word[1]} "'
                )
                points.add_points(msg.author, 10)

                # >>> record section <<<
                scramble_delta = datetime.datetime.now() - timestamps.read(
                    "scramble_started"
                )
                record.add_time_elapsed(SCRAMBLE_QID, scramble_delta.total_seconds())
                record.add_outcome(SCRAMBLE_QID, "solved")
                record.add_username(SCRAMBLE_QID, msg.author)
                record.add_points_awarded(SCRAMBLE_QID, 10)  #
                record.add_guess_string(
                    SCRAMBLE_QID, msg.content
                )  # TODO: make sure msg.content is type string
                record.add_guess_similarity(
                    SCRAMBLE_QID, 1
                )  # similarity always 1 for correct scramble
                record.write(SCRAMBLE_QID)
                SCRAMBLE_QID = ""

    @Command(
        "echo",
        permission="mod",
        help="say something",
        syntax="",
    )
    async def cmd_echo(msg: Message, *args):
        if not args:
            await msg.reply("echo what?")
            return
        await msg.reply(" ".join(args))

    @Command("trivia", help="Tricia came back FeelsStrongMan")
    async def cmd_trivia(msg: Message):
        # trivia database: https://opentdb.com/browse.php
        # trivia documentation: https://pypi.org/project/trivia.py/
        global trivia
        global trivia_started
        global timestamps
        global questions
        global _generate_hint
        global silent_cooldown
        global record
        global TRIVIA_QID
        global restart_scheduled
        global shutdown_scheduled

        TRIVIA_COOLDOWN: int = silent_cooldown["trivia"]
        TRIVIA_HINT_TIME: int = 20
        TRIVIA_TIMEOUT: int = 30

        if restart_scheduled:
            logger.debug(f"Trivia command blocked -- restart scheduled.")
            return

        if shutdown_scheduled:
            logger.debug(f"Trivia command blocked -- shutdown scheduled.")
            return

        delta = datetime.datetime.now() - timestamps.read("trivia_started")
        # do not reply if since since command activated is less than 5 seconds
        if trivia_started and delta > datetime.timedelta(seconds=5):
            await msg.reply(f"[Trivia] @{msg.author} Trivia already running.")
            return
        elif trivia_started and delta <= datetime.timedelta(seconds=5):
            return

        # delta is time since last trivia question
        in_cooldown = delta < datetime.timedelta(seconds=TRIVIA_COOLDOWN)
        if in_cooldown:
            logger.debug(f"Trivia command blocked -- in silent cooldown.")
            return

        # delta_auto_write = datetime.datetime.now() - timestamps.read('last_auto_record_write')
        # if delta_auto_write.total_seconds() > 120:
        #     record.write_all(time_padding=120)
        #     timestamps.update('last_auto_record_write')

        trivia_started = True

        questions = trivia.question()
        question, answer, TRIVIA_QID = questions
        question_stylized = f"Chatting [Trivia] {question} Frenchge WineTime"

        # >>> record section <<<
        record.new(TRIVIA_QID)
        record.add_question_string(TRIVIA_QID, question)
        record.add_answer_string(TRIVIA_QID, answer)

        await msg.reply(question_stylized)
        timestamps.update("trivia_started")
        logger.info(f"Trivia Question: {question}")
        logger.info(f"Trivia Answer: {answer}")
        logger.debug(f"Trivia QID: {TRIVIA_QID}")

        t = 0
        while trivia_started is True:
            await asyncio.sleep(1)
            if t == TRIVIA_HINT_TIME and trivia_started is True:
                hint = _generate_hint(answer)
                hint = f"[Trivia] Hint: {hint}"
                await msg.reply(hint)

            if t == TRIVIA_TIMEOUT and trivia_started is True:
                trivia_started = False
                await msg.reply(
                    f"[Trivia] No one answered correctly. FeelsBadMan The answer was: {questions[1]}"
                )
                # >>> record section <<<
                record.add_outcome(TRIVIA_QID, "timeout")
                record.add_time_elapsed(TRIVIA_QID, t)
                record.write(TRIVIA_QID)
                logger.debug("Wrote trivia record")
                logger.debug(f"TRIVIA_QID: {TRIVIA_QID}")
                logger.debug(f"t: {t}")
                TRIVIA_QID = ""
                logger.debug("Reset TRIVIA_QID")

                return

            t += 1

    @Command(
        "scramble",
        help="Play scramble.",
    )
    async def cmd_scramble(msg: Message):
        global points
        global timestamps
        global restart_scheduled
        global shutdown_scheduled
        global silent_cooldown
        global record
        global SCRAMBLE_QID

        global scramble
        global scramble_word
        global scramble_started
        global scramble_question

        # Do not remind that a scramble is going if it's been less than
        #   QUIET_REMIND_TIME seconds since the scramble started
        QUIET_REMIND_TIME: int = 5
        # Time since the START of the last scramble before another scramble
        #   can be started
        SCRAMBLE_COOLDOWN: int = silent_cooldown["scramble"]
        SCRAMBLE_HINT_TIME: int = 20
        SCRAMBLE_TIMEOUT: int = 30

        if restart_scheduled:
            logger.debug(f"Scramble command blocked -- restart scheduled.")
            return

        if shutdown_scheduled:
            logger.debug(f"Scramble command blocked -- shutdown scheduled.")
            return

        # delta is time since last scramble
        delta = datetime.datetime.now() - timestamps.read("scramble_started")
        # if scramble started and it's been long enough after it's started, remind.
        if scramble_started and delta > datetime.timedelta(seconds=QUIET_REMIND_TIME):
            await msg.reply(f"[Scramble] @{msg.author} Scramble already running.")
            logger.debug(
                f"Scramble command blocked -- scramble already running. Reminded {msg.author}."
            )
            return
        elif scramble_started and delta <= datetime.timedelta(
            seconds=QUIET_REMIND_TIME
        ):
            logger.debug(
                f"Scramble command blocked -- scramble already running. \
Did not remind {msg.author} since it has been {delta.total_seconds()} second \
since new scramble round started."
            )
            return

        in_cooldown = delta < datetime.timedelta(seconds=SCRAMBLE_COOLDOWN)
        if in_cooldown:
            logger.debug(f"Scramble command blocked -- in silent cooldown.")
            return

        # delta_auto_write = datetime.datetime.now() - timestamps.read('last_auto_record_write')
        # if delta_auto_write.total_seconds() > 120:
        #     record.write_all(time_padding=120)
        #     timestamps.update('last_auto_record_write')

        scramble_started = True
        scramble_word = (
            scramble.get_word()
        )  # tuple of (scrambled word, UNscrambled word)
        scramble_puzzle, scramble_answer, SCRAMBLE_QID = scramble_word
        puzzle_stylized = f"[Scramble] A scramble game has started. Unscramble the following word to win: {scramble_puzzle} FeelsDankMan TeaTime"

        scramble_question = scramble_puzzle

        # >>> record section <<<
        record.new(SCRAMBLE_QID)
        record.add_question_string(SCRAMBLE_QID, scramble_question)
        record.add_answer_string(SCRAMBLE_QID, scramble_answer)

        await msg.reply(puzzle_stylized)
        timestamps.update("scramble_started")
        logger.info(f"Scramble answer: {scramble_answer}")
        logger.info(f"Scramble question: {scramble_question}")
        logger.debug(f"Scramble QID: {SCRAMBLE_QID}")
        t = 0
        while scramble_started is True:
            await asyncio.sleep(1)
            if t == SCRAMBLE_HINT_TIME and scramble_started is True:
                hint = scramble_answer[:3] + "_" * (len(scramble_answer) - 3)
                await msg.reply(f"[Scramble] Hint: {hint}")
            if t == SCRAMBLE_TIMEOUT and scramble_started is True:
                await msg.reply(
                    f'[Scramble] No one answered correctly. FeelsBadMan The word was: " {scramble_answer} "'
                )
                # >>> record section <<<
                record.add_outcome(SCRAMBLE_QID, "timeout")
                record.write(SCRAMBLE_QID)
                SCRAMBLE_QID = ""
                scramble_started = False
                return  # TODO: is break or return better here?
            t += 1

    @Command(
        "stoptrivia",
        help="Stop the trivia game",
        permission="mod",
    )
    async def cmd_stoptrivia(msg: Message):
        global trivia_started
        if trivia_started == True:
            trivia_started = False
            logger.debug(f"stoptrivia command run, set trivia_started = False")
            await msg.reply(f"[Trivia] MrDestructoid Trivia stopped.")
            # >>> record section <<<
            record.clear(TRIVIA_QID)
        else:
            logger.debug(
                f"Command stoptrivia run, but no trivia round is active (trivia_started is False)"
            )

    @Command(
        "top",
        help="Shows the top 5 users with the most points",
        cooldown=60 * 5,  # 5 second cooldown
        aliases=["top5"],
    )
    async def cmd_top(msg: Message):
        # return the top 10 users with the most points
        global points

        logger.debug(f"{msg.author} ran command {msg.content}")
        top_usernames, top_points = points.get_top_points()
        await msg.reply(
            f"Corpa WineTime Top 5: {top_usernames[0]} ({top_points[0]}), {top_usernames[1]} ({top_points[1]}), {top_usernames[2]} ({top_points[2]}), {top_usernames[3]} ({top_points[3]}), {top_usernames[4]} ({top_points[4]})"
        )
        # await msg.reply('no ping top response placeholder')

    @Command(
        "losers",
        help="Shows the top 5 users with the most total accumulated gambling loss",
        cooldown=60 * 5,  # 5 second cooldown
    )
    async def cmd_losers(msg: Message):
        # return the top 10 users with the most points
        global points

        logger.debug(f"{msg.author} ran command {msg.content}")
        top_usernames, top_points = points.get_top_gamble_loss()
        await msg.reply(
            f"GAMBA 📉: {top_usernames[0]} ({top_points[0]}), {top_usernames[1]} ({top_points[1]}), {top_usernames[2]} ({top_points[2]}), {top_usernames[3]} ({top_points[3]}), {top_usernames[4]} ({top_points[4]})"
        )

    @Command(
        "roulette",
        help="Play roulette",
        # cooldown=5,    # 5 second cooldown
    )
    async def cmd_roulette(msg: Message):
        global points
        global timestamps

        ROULETTE_COOLDOWN: int = 5

        # time since roulette cmd last run
        delta = datetime.datetime.now() - timestamps.read("roulette_cmd")
        if delta <= datetime.timedelta(seconds=ROULETTE_COOLDOWN):
            logger.debug(f"Roulette command blocked -- in silent cooldown.")
            return

        # TODO: double spaces cause error at wager[-1] --> fix this
        msg_arg = msg.content.split(" ")
        if len(msg_arg) < 2:
            await msg.reply(f"[Roulette] @{msg.author} Awkward Please specify a wager.")
            return
        # elif len(msg_arg) > 2:  # TODO: Remove this if statement
        #     await msg.reply(f'[Roulette] @{msg.author} WAYTOODANK Too many arguments. Examples: #roulette 20% or #roulette 35')
        #     return

        if msg.author == "wannabe_mailman":
            await msg.reply("@wannabe_mailman FeelsOkayMan No.")
            return

        wager = msg_arg[1].strip(" ")
        try:
            if wager[-1] == "%":
                fmt = "percent"
                wager = wager[:-1]
                wager = int(wager)
            elif wager[-1] != "%" and wager.isdigit():
                fmt = "points"
                wager = int(wager)
            elif wager == "all":
                fmt = "all"
            else:
                logger.warning(f"Invalid wager format: {wager}")
                logger.debug(f"wager: {wager}")
                logger.debug(f"len(wager): {len(wager)}")
                logger.debug(f"type(wager): {type(wager)}")
                return
        except:
            logger.warning(f"Invalid wager format: {wager}")
            logger.debug(f"wager: {wager}")
            logger.debug(f"len(wager): {len(wager)}")
            logger.debug(f"type(wager): {type(wager)}")
            return

        if fmt == "percent" and wager > 100:
            await msg.reply(
                f"[Roulette] @{msg.author} Weirdge You cannot wager more than 100% of your points."
            )
            return

        if fmt in ("percent", "points"):
            if wager < 0:
                await msg.reply(
                    f"[Roulette] @{msg.author} Weirdge Wager must be positive."
                )
                return
            if wager == 0:
                await msg.reply(
                    f"[Roulette] 🫵 ICANT @{msg.author} just tried to wager 0 points"
                )
                return
        try:
            out, new_bal, delta = points.gamble(msg.author, wager, fmt)
        except:
            logger.warning("Error in points.gamble()")
            logger.debug(f"wager: {wager}")
            logger.debug(f"[DEBUG] fmt: {fmt}")
            logger.debug(f"[DEBUG] msg.author: {msg.author}")
            return
        if out == "win":
            await msg.reply(
                f"[Roulette] @{msg.author} HYPERPOGGER You won {delta} points and now have {new_bal} points."
            )
            return
        elif out == "lose":
            await msg.reply(
                f"[Roulette] @{msg.author} FeelsBadMan You lost {delta} points and now have {new_bal} points."
            )
            return
        elif out == "not enough points":
            await msg.reply(
                f"[Roulette] @{msg.author} Weirdge You don't have enough points for that. Get your money up."
            )
            return
        elif out == "no points":
            await msg.reply(
                f"[Roulette] @{msg.author} Sadge You don't have any points."
            )

    @Command(
        "give",
        help="Give some of your points to another user",
        syntax="#give <user> <amount>",
        aliases=["donate", "send"],
    )
    async def cmd_give(msg: Message):
        global points
        global timestamps

        split_msg = msg.content.split(" ")
        if len(split_msg) != 3:
            logger.warning(f"Invalid #give syntax from message: {msg.content}")
            return

        # Example: #give Diraction 10
        [_, arg1, arg2] = split_msg

        sender = msg.author
        receiver = arg1.split("@")[-1]  # recipient
        transfer_amount = arg2

        if _check_all_alphanumeric(receiver) == False:
            logger.warning("Invalid recipient: alphanumeric")
            return

        if receiver.isdigit():
            logger.warning("Invalid recipient: digit")
            return

        initial_amount = points.get_points(sender) + points.get_points(receiver)
        if not transfer_amount.isdigit():
            logger.warning("Invalid amount to give")
            return

        transfer_amount = int(transfer_amount)

        # check if the msg.author has enough points
        if points.get_points(sender) < transfer_amount:
            await msg.reply(
                f"@{msg.author} Weirdge You can't give more points than you have."
            )
            return

        outcome = points.transfer(sender, receiver, transfer_amount)
        if outcome == "success":
            logger.debug("Successfully transferred points")
            logger.debug(f"transfered {transfer_amount} from {sender} to {receiver}")
            await msg.reply(f"peepoHas FBCatch {transfer_amount} pts to @{receiver}")
            return
        elif outcome == "not enough points":
            await msg.reply(
                f"@{msg.author} Weirdge You can't give more points than you have."
            )
            return
        elif outcome == "invalid amount":
            logger.warning(f"Invalid amount to give: {transfer_amount}]")
            logger.debug(f"sender: {sender}")
            logger.debug(f"receiver: {receiver}")
            return
        elif outcome == "cannot transfer to self":
            logger.warning(f"{sender} tried to transfer points to self")
            return
        elif outcome == "negative points":
            logger.warning(f"{sender} or {receiver} has negative point balance")
            return
        elif outcome == "balance mismatch":
            logger.warning(f"Balance mismatch, but reverted successfully")
            return
        elif outcome == "balance mismatch and could not revert":
            msg.reply(f"DinkDonk @Diraction check console logs monkaW")
            logger.warning(f"Balance mismatch and could not revert")
            logger.debug(f"transfered {transfer_amount} from {sender} to {receiver}")
            logger.debug(f"initial amount: {initial_amount}")
            logger.debug(
                f"final amount: {points.get_points(sender) + points.get_points(receiver)}"
            )
            return
        else:
            logger.warning(f"Unknown outcome: {outcome}")
            return

    @Command(
        "submit",
        help="Submit a trivia question+answer or a scramble word. Do #submit help for more.",
    )
    async def cmd_submit(msg: Message):
        global timestamps
        global restart_scheduled
        global shutdown_scheduled

        logger.info(f"{msg.author} ran #submit")

        if restart_scheduled or shutdown_scheduled:
            logger.warning(
                f"Blocked #submit. Cannot submit question while restart or shutdown is scheduled"
            )
            return

        out = await submit.submit(msg)
        if isinstance(out, str):
            await msg.reply(f"@{msg.author} {out}")
        if isinstance(out, bool):
            logger.debug(f"out: {out}")
            return

    @Command(
        "points",
        help="Shows your current points",
    )
    async def cmd_points(msg: Message):
        # return the user's current points
        global points
        global timestamps

        msg_content = msg.content.strip(" ")
        if "  " in msg_content:
            while "  " in msg_content:
                msg_content = msg_content.replace("  ", " ")

        if msg_content == "#points":
            response = f"@{msg.author} you have {points.get_points(msg.author)} points."
            await msg.reply(response, as_twitch_reply=True)
            return

        if len(msg_content.split(" ")) == 2:
            [cmd, user] = msg_content.split(" ")

            if user.startswith("@"):
                user = user.split("@")[-1]

            if _check_all_alphanumeric(user) == False:
                logger.warning(f"Invalid recipient: alphanumeric")
                return

            response = f"@{user} has {points.get_points(user)} points."
            if user == "BlammoBot":
                response = f"I have {points.get_points(user)} points."
            await msg.reply(response)
            return

    async def _reload_trivia(msg: Message, verbose=True, save_timestamps=True):
        global trivia
        global timestamps

        logger.info(f"{msg.author} called reload trivia command")
        trivia.reload()
        add_qid("../blammo-bot-private/trivia.csv", "trivia")
        if save_timestamps:
            try:
                timestamps.save()
            except Exception as e:
                logger.error(f"Could not save timestamps: {e}")
        if verbose:
            await msg.reply("MrDestructoid Reloaded trivia database")

    async def _reload_scramble(msg: Message, verbose=True, save_timestamps=True):
        global scramble
        global timestamps

        logger.info(f"{msg.author} called reload scramble command")
        scramble.reload()
        add_qid("../blammo-bot-private/scramble.csv", "scramble")
        if save_timestamps:
            try:
                timestamps.save()
            except Exception as e:
                logger.error(f"Could not save timestamps: {e}")
        if verbose:
            await msg.reply("MrDestructoid Reloaded scramble database")

    async def _reload_secretcommand(msg: Message, verbose=True, save_timestamps=True):
        global timestamps

        logger.info(f"{msg.author} called reload secretcommand command")
        from utils import secretcommand

        if save_timestamps:
            try:
                timestamps.save()
            except Exception as e:
                logger.error(f"Could not save timestamps: {e}")
        if verbose:
            await msg.reply("MrDestructoid Reloaded secretcommand")

    @Command(
        "reload",
        help="Reload a database or functionality.",
        permission="admin",
        syntax="#reload <subcommand>",
    )
    async def cmd_reload(msg: Message):
        global trivia
        global scramble
        global timestamps
        global _reload_trivia
        global _reload_scramble
        global _reload_secretcommand

        subcommand = msg.content.split(" ")
        subcommand = [x for x in subcommand if x != ""]
        if len(subcommand) != 2:
            logger.error(f"Invalid syntax: {msg.content}")
            return

        subcommand = subcommand[1].lower()

        allowed_subcommands = [
            "all",
            "trivia",
            "scramble",
            "secretcommand",
        ]

        if subcommand not in allowed_subcommands:
            logger.error(f"Invalid subcommand: {subcommand}")
            return

        logger.info(f"{msg.author} called reload command with subcommand: {subcommand}")

        if subcommand == "trivia":
            logger.debug(f"Reloading trivia database")
            await _reload_trivia(msg)

        elif subcommand == "scramble":
            logger.debug(f"Reloading scramble database")
            await _reload_scramble(msg)

        elif subcommand == "secretcommand":
            logger.debug(f"Reloading secretcommand")
            await _reload_secretcommand(msg)

        elif subcommand == "all":
            logger.debug(f"Reloading all databases")
            try:
                timestamps.save()
            except Exception as e:
                logger.error(f"Could not save timestamps: {e}")
            await _reload_trivia(msg, verbose=False, save_timestamps=False)
            await _reload_scramble(msg, verbose=False, save_timestamps=False)
            await _reload_secretcommand(msg, verbose=False, save_timestamps=False)
            await msg.reply("MrDestructoid Reloaded all databases")

        else:
            logger.error(f"Invalid subcommand not caught: {subcommand}")
            return

    @Command(
        "logger",
        help="Interact with the logger system.",
        permission="admin",
        syntax="#logger <subcommand> [args]",
    )
    async def cmd_logger(msg: Message):
        subcommands = [
            "help"  # display help message of subcommands, args
            "level",  # return current log level
            "set",  # set log level
            "archive",  # move logs.log to /root/logs-old (or )
            "",
        ]

        old_logs_archive_path: str = "/root/logs-old"
        # get the timestamp in the format MM-DD-YYYY

        pass

    @Command("setloglevel", help="Sets the log level", permission="admin")
    async def cmd_setloglevel(msg: Message):
        logger.info("Called setloglevel command")
        if len(msg.content.split(" ")) != 2:
            logger.warning(f"Invalid number of arguments for setloglevel command.")
            return
        [cmd, loglevel] = msg.content.split(" ")
        loglevel = loglevel.upper()
        if loglevel not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            logger.warning(f"Invalid log level: {loglevel}")
            return

        # loggers_list = [logging.getLogger(name) for name in logging.root.manager.loggerDict]

        logger_names = [
            __name__,
            "record",
            "points",
            "trivia",
            "scramble",
            "dbutils",
            "scheduler",
            "timestamps",
            "check_online",
        ]

        if loglevel == "DEBUG":
            for l in logger_names:
                logging.getLogger(l).setLevel(logging.DEBUG)
            # logging.getLogger(__name__).setLevel(logging.DEBUG)
            # logging.getLogger('record').setLevel(logging.DEBUG)
        elif loglevel == "INFO":
            for l in logger_names:
                logging.getLogger(l).setLevel(logging.INFO)
            # logging.getLogger(__name__).setLevel(logging.INFO)
            # logging.getLogger('record').setLevel(logging.INFO)
        elif loglevel == "WARNING":
            for l in logger_names:
                logging.getLogger(l).setLevel(logging.WARNING)
            # logging.getLogger(__name__).setLevel(logging.WARNING)
            # logging.getLogger('record').setLevel(logging.WARNING)
        elif loglevel == "ERROR":
            for l in logger_names:
                logging.getLogger(l).setLevel(logging.ERROR)
            # logging.getLogger(__name__).setLevel(logging.ERROR)
            # logging.getLogger('record').setLevel(logging.ERROR)
        elif loglevel == "CRITICAL":
            for l in logger_names:
                logging.getLogger(l).setLevel(logging.CRITICAL)
            # logging.getLogger(__name__).setLevel(logging.CRITICAL)
            # logging.getLogger('record').setLevel(logging.CRITICAL)

        # logger = custom_logger(loglevel=logging.getLevelName(loglevel))
        # logger.info(f'Log level set to {loglevel}')

    @Command("silentcooldown", help="Set silent status", permission="mod")
    async def cmd_silentcooldown(msg: Message):
        global silent_cooldown

        # TODO:
        # 1) make #silentcooldown trivia default a thing that pulls from defaults
        # 2) make silentcooldown defaults a global variable
        # 3) make a response for #silentcooldown in chat
        # 4) will there be an issue if silentcooldown is set to be less than the no-remind time?

        msg_split = msg.content.split(" ")
        if len(msg_split) != 3:
            logger.warning(f"Invalid number of arguments for silentcooldown command.")
            return

        # We might decide to add a silent cooldown to a non-game cmd in the future.
        #   If so, the variable name below should change.
        [cmd, game, cooldown] = msg_split
        if game not in ["trivia", "scramble"]:
            logger.warning(f"Invalid game: {game}")
            return

        if cooldown.lower() in ("false", "off"):
            silent_cooldown[game] = 0
            logger.info(f"Silent cooldown for {game} set to 0.")
            return
        elif cooldown.isdigit():
            silent_cooldown[game] = int(cooldown)
            logger.info(f"Silent cooldown for {game} set to {cooldown}.")
            return
        else:
            logger.warning(f"Invalid cooldown: {cooldown}")
            return

    # TODO: Verify the shutdown command still works even if timestamp throws an error.
    # @Command('shutdown', permission='mod')
    # async def cmd_shutdown(msg: Message):
    #     global timestamps

    #     try:
    #         timestamps.save()
    #     except Exception as e:
    #         logger.error(f'Could not save timestamps: {e}')

    #     await msg.reply('MrDestructoid shutting down...')
    #     open('shutdown.txt', 'w').close()       # creates signal file

    # @Command('schedulerestart', permission='mod', help='Restarts the bot whenever there are no games running.')
    # async def cmd_schedulerestart(msg: Message):
    #     global restart_scheduled
    #     global timestamps

    #     # toggle restart_scheduled (cancel the scheduled restart)
    #     if restart_scheduled:
    #         restart_scheduled = False
    #         logger.info('Scheduled restart cancelled.')
    #         return

    #     restart_scheduled = True
    #     await msg.reply('MrDestructoid Restart scheduled. Will restart when no games are running.')
    #     logger.info('Scheduled restart initiated.')
    #     # Keep looping while either trivia or scramble is running
    #     #   AND if a restart is scheduled.
    #     # If schedulerestart is called again, it will change restart_scheduled to False
    #     #   and the loop will break.
    #     while any((trivia_started, scramble_started)) and restart_scheduled:
    #         await asyncio.sleep(1)
    #         logger.debug('Waiting for games to end...')
    #         logger.debug(f'trivia_started: {trivia_started}')
    #         logger.debug(f'scramble_started: {scramble_started}')
    #         logger.debug(f'restart_scheduled: {restart_scheduled}')

    #     logger.debug('Exited scheduled restart loop.')
    #     # The loop is broken and if a restart is scheduled, restart the bot.
    #     if restart_scheduled:
    #         try:
    #             timestamps.save()
    #         except Exception as e:
    #             logger.error(f'Could not save timestamps: {e}')

    #         await msg.reply('MrDestructoid Restarting...')
    #         logger.info('Restarting...')
    #         await get_bot().shutdown()

    @Command(
        "shutdown",
        permission="mod",
        aliases=["stop", "exit", "quit"],
        help="Shuts down the bot.",
    )
    async def cmd_shutdown(msg: Message, *args):
        try:
            timestamps.save()
            logger.debug("Saved timestamps")
        except Exception as e:
            logger.error(f"Could not save timestamps: {e}")

        try:
            # remove online_signal.txt file if it exists
            os.remove(ONLINE_SIGNAL_FILE_NAME)
            logger.debug(f"Removed {ONLINE_SIGNAL_FILE_NAME}")
        except FileNotFoundError:
            logger.debug(f"{ONLINE_SIGNAL_FILE_NAME} does not exist.")

        await msg.reply("MrDestructoid shutting down...")
        await get_bot().shutdown()

    @Command(
        "scheduleshutdown",
        permission="mod",
        help="Shuts down the bot whenever there are no games running.",
    )
    async def cmd_scheduleshutdown(msg: Message):
        global shutdown_scheduled
        global timestamps

        if shutdown_scheduled:
            shutdown_scheduled = False
            logger.info("Scheduled shutdown cancelled.")
            return

        shutdown_scheduled = True
        await msg.reply(
            "MrDestructoid Shutdown scheduled. Will shutdown when no games are running."
        )
        logger.info("Scheduled shutdown initiated.")
        if any((trivia_started, scramble_started)) and shutdown_scheduled:
            await asyncio.sleep(1)
            logger.debug("Waiting for games to end...")
            logger.debug(f"trivia_started: {trivia_started}")
            logger.debug(f"scramble_started: {scramble_started}")
            logger.debug(f"shutdown_scheduled: {shutdown_scheduled}")

        if shutdown_scheduled:
            try:
                timestamps.save()
                logger.debug("Saved timestamps")
            except Exception as e:
                logger.error(f"Could not save timestamps: {e}")

            try:
                os.remove(ONLINE_SIGNAL_FILE_NAME)
                logger.debug(f"Removed {ONLINE_SIGNAL_FILE_NAME}")
            except FileNotFoundError:
                logger.debug(f"{ONLINE_SIGNAL_FILE_NAME} does not exist.")

            await msg.reply("MrDestructoid Shutting down...")
            logger.info("Shutting down...")
            await get_bot().shutdown()

    @Command(
        "logs",
        help="Shows the logs of this bot in this channel",
    )
    async def cmd_logs(msg: Message):
        BOT_USERNAME = "blammobot"
        logs_url = f"https://logs.ivr.fi/?channel=hasanabi&username={BOT_USERNAME}"
        await msg.reply(f"@{msg.author} {logs_url}", as_twitch_reply=True)

    @Command("fridge", help="It's a fridge")
    async def cmd_fridge(msg: Message):
        await msg.reply("Fridge brrrrrr")

    @Command("tricia")
    async def cmd_tricia(msg: Message):
        await msg.reply("Life tricia is back")

    @Command("blammo")
    async def cmd_blammo(msg: Message):
        await msg.reply("peepoHas 🪄 blammo")

    @Command("joel", help="Joel")
    async def cmd_joel(msg: Message):
        i = random.randint(1, 15)
        if i == 1:
            await msg.reply("Joel Looking look at him go")
        elif i == 2:
            await msg.reply("Joel Looking")
        elif i == 3:
            await msg.reply("Joel")
        elif i == 4:
            await msg.reply("Joel Looking wow")
        elif i == 5:
            await msg.reply("Joel Looking damn damn damn")
        elif i == 6:
            await msg.reply("Joel Looking superb")
        elif i == 7:
            await msg.reply("Joel Looking look at him go")
        elif i == 8:
            await msg.reply("Joel Looking")
        elif i == 9:
            await msg.reply("Joel Looking they added joel")
        elif i == 10:
            await msg.reply("Joel Looking fantastic")
        elif i == 11:
            await msg.reply("Joel Looking look at him go")
        elif i == 12:
            await msg.reply("Joel Looking")
        elif i == 13:
            await msg.reply("Joel Looking")
        elif i == 14:
            await msg.reply("Joel Looking superb")
        elif i == 15:
            await msg.reply("Joel Looking brilliant")

    @Command("hasan", help="Hasan")
    async def cmd_hasan(msg: Message):
        responses = [
            "peepoHas",
            "peepoHas get nukes",
            "peepoHas BLAMMO",
            "peepoHas like ive been saying",
            "peepoHas ive said it a million times",
            "peepoHas friend of the show",
            "peepoHas paul pelosi is sexy",
            "peepoHas wut",
            "peepoHas 🤘 make it quick",
            "peepoHas 🤘 gotta go",
            "peepoHas 🤘",
            "peepoHas 🤘 yo",
            "peepoHas yo",
            "peepoHas so uh...",
            "peepoHas nani?",
            "peepoHas uh",
            "peepoHas *racism*",
            "peepoHas *homophobia*",
            "peepoHas italians are poc",
            "peepoHas offliners are nerds",
            "peepoHas *Turkish swearing*",
            "peepoHas amk",
            "peepoHas america deserved 9/11",
            "peepoHas america deserved 7/11",
            "peepoHas blammo",
            "peepoHas 2 genders: italian and mexican",
            "peepoHas im not a weeb",
            "peepoHas maybe i am a weeb",
            "peepoHas lole",
            "peepoHas gaming?",
            "peepoHas what",
            "peepoHas shingles",
            "peepoHas anyways chat...",
            "peepoHas top of the hour",
            "peepoHas donnie is gone",
            "peepoHas in the cars cinematic universe...",
            "peepoHas sounds like chicken tendies",
            "peepoHas *bans chatter*",
            "peepoHas",
            "peepoHas",
            "peepoHas",
            "peepoHas",
            "peepoHas",
            "peepoHas",
            "peepoHas",
            "peepoHas",
            "peepoHas",
            "peepoHas",
            "peepoHas i had a brown out",
            "widepeepoHas can u do this steven",
            "peepoHas gorillion",
            "peepoHas nuke hascord",
            "peepoHas 30% of Americans will agree with anything",
            "peepoHas it's like a muscle",
            "peepoHas no shot",
            "peepoHas don't tap the glass",
            "peepoHas women's rights and women's wrongs",
            "peepoHas meritocracy is a lie",
            "peepoHas Rule 1: Get nukes",
            "peepoHas Rule 2: Never give up the nukes",
            "peepoHas Rule 3: If America tells you you have nukes, drop everything and find nukes",
            "peepoHas kids are no content",
            "peepoHas let people be cringe",
            "peepoHas be normal",
            "peepoHas just be fucking normal",
            "peepoHas show me the paystubs",
            "peepoHas holy shit dude",
            "peepoHas every guy can be a 7",
            "peepoHas absolute bananas mode",
            "peepoHas bananas mode",
            "peepoHas what do I always say",
            "peepoHas decked out the wazoo",
            "peepoHas out the wazoo",
            "peepoHas balding",
            "peepoHas basketball",
            "peepoHas copskull",
            "peepoHas *malding*",
            "peepoHas im not a walmart streamer",
            "peepoHas kinda weird dude",
            "peepoHas stfu about the echo",
            "peepoHas i hate audiophiles",
            "peepoHas dont be cringe",
            "peepoHas we have a special guest later",
            "peepoHas you are not japanese",
            "peepoHas gaming later",
            "peepoHas gaming later (lie)",
            "peepoHas Belgium is a fake country",
            "peepoHas whatsgoingoneverybodyimhasanpikerandthisisthehasanabibroadcastcomingtoyoulivefromsunnycalifornalosangeles",
            "peepoHas 📣 ANNE",
            "peepoHas 📣 CLOSE THE DOOR",
            "peepoHas speak into the mic",
            "peepoHas woah kay gay",
            "peepoHas chat stop spamming PèpeLa",
            "peepoHas mawds nuke the chat",
            "peepoHas cucks",
            "peepoHas yall are nerds",
            "peepoHas mawds nuke jupijej",
            "peepoHas my head is not small",
            "peepoHas 1453 best year of my life",
            "peepoHas *Turkish yelling*",
            "peepoHas *Turkish swearing*",
            "peepoHas offliners are nerds",
            "peepoHas mawds nuke jupijej",
            "peepoHas 👉 this is a homosexual man",
            "peepoHas ive been saying this for years",
            "peepoHas every guy can be a 7",
            "peepoHas parasocial cringelords",
            "peepoHas *weeb noises*",
            "peepoHas offliners are the backbone of the community",
            "peepoHas gaming later *lies*",
            "peepoHas time and time again",
            "peepoHas I'm gonna keep this one as a pet",
            "peepoHas my offline chat is a whole bucnh of nerds",
            "peepoHas promises made promises kept",
            "peepoHas he's so back baby",
            "peepoHas I eat at the same time every day",
            "peepoHas 🤟 lets do it",
            "peepoHas 🤟 just a quick one",
            "peepoHas Clap hasBee",
            "peepoHas 📣 MOOROT",
            "peepoHas 📣 MURAT",
            "peepoHas the point of contention",
            "peepoHas *farts on dog* HEKW",
        ]
        await msg.reply(random.choice(responses))

    @Command("secretcommand", cooldown=20)
    async def on_secret_command(msg: Message):
        global points

        try:
            await secretcommand.run(msg, points)
        except Exception as e:
            logger.error(f"Error in secretcommand: {e}")
            await msg.reply(f"FeelsDankMan TeaTime something is broken...")
            return

    @Command(
        "silentecho",
        permission="admin",
        help="Echo but silent. Use from Diraction's chat.",
    )
    async def cmd_silentecho(msg: Message):
        global REPLY_NEXT

        content = msg.content.replace("#silentecho ", "")

        if REPLY_NEXT == "":
            REPLY_NEXT = content
            logger.info(f"Wrote to REPLY_NEXT: {content}")
        else:
            logger.warning(
                f"Command #silentecho command not completed since REPLY_NEXT already full."
            )
            logger.warning(f"Attempted to write message: {content}")
            logger.warning(f"REPLY_NEXT: {REPLY_NEXT}")

    @Command(
        "dumptologs",
        permission="admin",
        help="Dumps most variables to logs for debugging.",
    )
    async def cmd_dumptologs(msg: Message):
        global points
        # global timestamp_dict
        global timestamps
        global restart_scheduled
        global shutdown_scheduled
        global silent_cooldown
        global record
        global TRIVIA_QID

        global SCRAMBLE_QID
        # global STREAM_ONLINE
        global REPLY_NEXT

        global trivia
        global questions
        global trivia_started
        global _generate_hint
        global _find_chars
        global _set_char_in_string
        global _check_all_alphanumeric

        global scramble  # trivia equivalent: trivia
        global scramble_word  # trivia equivalent: questions  (scrambled, unscrambled)
        global scramble_started  # trivia equivalent: trivia_started

        logger.info(f"=== BEGIN DUMP TO LOGS ===")
        logger.debug(f"REPLY_NEXT = {REPLY_NEXT}")
        logger.debug(f"TRIVIA_QID = {TRIVIA_QID}")
        logger.debug(f"SCRAMBLE_QID = {SCRAMBLE_QID}")
        # logger.debug(f'STREAM_ONLINE = {STREAM_ONLINE}')
        logger.debug(f"silent_cooldown = {silent_cooldown}")
        logger.debug(f"shutdown_scheduled = {shutdown_scheduled}")
        logger.debug(f"restart_scheduled = {restart_scheduled}")
        # logger.debug(f'timestamps_dict = {timestamps_dict}')
        # logger.debug(f'timestamps = {timestamps}')

        logger.debug(f"trivia_started = {trivia_started}")
        logger.debug(f"questions = {questions}")
        logger.debug(f"scramble_started = {scramble_started}")
        logger.debug(f"scramble_word = {scramble_word}")

        logger.info(f"=== END DUMP TO LOGS ===")

    @Command("dvl", permission="admin", help="See README or contact dev for acronym.")
    async def cmd_dvl(msg: Message):
        # dumps viewer list
        pass

    async def on_whisper_received(self, msg: Message):
        global REPLY_NEXT

        logger.info(
            f"WhisperReceived: {msg.author} sent whisper {msg.content} to channel {msg.channel_name}"
        )
        # self.logmsg(f'WhisperRecv {msg.author}: {msg.content}')

        if msg.author == "diraction":
            REPLY_NEXT = msg.content
            logger.info(f"added message to REPLY_NEXT queue: {msg.content}")


if __name__ == "__main__":
    logger.info("Starting bot...")

    # BlammoBot().run()

    loop = asyncio.get_event_loop()
    loop.create_task(check_online.check_loop())
    loop.create_task(BlammoBot().run())
    loop.run_forever()
