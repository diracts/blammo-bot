import random, logging, asyncio

from twitchbot.message import Message
from utils.points import PointData

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

# Let's do this another way.
# If we keep the responses separate from main.py and import them whenever the
# secretcommand function is called, we can add and remote potential load_responses
# in real time without having to restart the bot to apply changes.
# Each response should have 3 parts:
#   1. A unique index/key
#   2. A response string
#   3. A relative weight
#
# How should we weigh questions?
# If all are weight 1, then probability of each is 1/len(responses) = 1/n


def load_responses(msg: Message) -> list:
    responses = [
        [0, "https://youtu.be/hycF9IH55Lk", 1],
        [1, f"🫵 ICANT @{msg.author}", 1],
        [2, f"Susge @{msg.author}", 1],
        [3, f"FeelsDankMan TeaTime hold on ...", 3],
        [4, f"...", 1],
        [5, "", 1],
        [6, "", 1],
        [7, "", 1],
        [8, "", 1],
        [9, "", 1],
        [10, "", 1],
        [11, "", 1],
        [12, "", 1],
        [13, "", 1],
        [14, "", 1],
        [15, "", 1],
        [16, f"ReallyMad Don't try the secret command! You won't find anything.", 1],
        [17, f"ReallyMad Don't try the secret command! You won't find anything.", 1],
        [18, f"ReallyMad Stop trying the secret command! You won't find anything.", 1],
        [19, f"https://youtu.be/vOvfXCGKXbI", 1],
        [20, f"KEKW https://youtu.be/WDiB4rtp1qw", 1],
        [21, "!betel", 1],
        [22, "!quote", 1],
        [23, "!cock", 1],
        [24, "!sus", 1],
        [25, "!pog", 1],
        [27, "!dadjoke", 1],
        [28, "!fight @Fossabot", 1],
        [29, f"!fight @{msg.author}", 1],
        [30, "!fursona", 1],
        [31, f"widepeepoHappy", 3],
        [32, f"DinoFrogDisco https://youtu.be/XMCVCJ8ZuPs", 1],
        [33, f"Awkward hey", 1],
        [34, f"Salute https://youtu.be/YYEAmK4NCd8", 1],
        [35, f"Jamgie https://youtu.be/0_04Z-7kZ9E", 1],
        [36, f"LookUp", 1],
        [37, f"LookUp", 1],
        [38, f"@{msg.author} ReallyMad Stop trying the secret command!", 1],
        [39, f"@{msg.author} Grrr Stop trying the secret command!", 1],
        [40, f"KEKL https://youtu.be/Fkk9DI-8el4", 1],
        [41, f"PauseChamp 🎁", 5],
        [42, f"Joel https://youtu.be/YAgJ9XugGBo", 1],
        # [43, f"https://youtu.be/aNMKigmGreI", 1],
        [44, f"Peeporun https://youtu.be/6sLSArQ8Pvw", 1],
        [45, f"MEOW https://youtu.be/0fekTeVXMCM", 1],
        [46, f"HYPERNODDERS https://youtu.be/xbPwaAFHDG8", 1],
        [47, f"https://youtu.be/l_XxcTJGWtM", 1],
        [48, f"https://youtu.be/Sd4Qpf8Y6DE", 1],
        [49, f"https://youtu.be/vLe_BZ1mo3I", 1],
        [50, f"https://youtu.be/UtaH0wVm6H4", 1],
        [51, f"WAYTOODANK https://youtu.be/pVQqEQ68FR8", 1],
        [52, f"Concerned https://youtu.be/idi524Ni3qA", 1],
        [53, f"https://youtu.be/KCzwyFHSMdY", 1],
        [54, f"https://youtu.be/TCm9788Tb5g", 1],
        [55, f"https://youtu.be/N-7gbWKbXbQ", 1],
        [56, f"SHIVERMETIMBERS https://youtu.be/tw4CPZZkzTU", 1],
        [57, f"spongePls https://youtu.be/39UDZMgPg5k", 1],
        [58, f"https://youtu.be/b9ZxXwwxRvc", 1],
        [59, f"https://youtu.be/TOeQS7P9c5Q", 1],
        [60, f"Jamgie https://youtu.be/fIxuMIf0pJ8", 1],
        [61, f"🤙 https://youtu.be/jYHkBCrAzPs", 1],
        [62, f"hasBee https://youtu.be/Uae8qOr6Myw", 1],
        [63, f"ICANT https://youtu.be/L8XbI9aJOXk", 1],
        [64, f"AAAA https://youtu.be/-qz6-2FASlY", 1],
        [65, f"https://youtu.be/N-dxAXIwAv8", 1],
        [66, f"veryCat https://youtu.be/73Y_0TKFqmg", 1],
        [67, f"FeelsStrongMan Clap https://youtu.be/YFEYb_ay8mo", 1],
        [68, f"Jupijej https://youtu.be/kWVFEVWJMz8", 1],
        [69, f"SHIVERMETIMBERS https://youtu.be/fKhAeIm6ins", 1],
        [70, f"Jamgie https://youtu.be/9oQcqZOcs0Q", 2],
        [71, f"https://youtu.be/emJsHKINn-s", 1],
    ]
    return responses


def get_response(index: int, responses: list) -> list:
    for r in responses:
        if r[0] == index:
            return r


def normalize_responses(responses: list):
    # Normalize the weights of the responses
    # so that the sum of all weights is 1
    total_weight = sum([r[2] for r in responses])
    for r in responses:
        r[2] /= total_weight
    return responses


# responses = normalize_responses(responses)


# def first_loop(msg: Message, responses: list):
#     time1 = random.randint(15, 200)
#     time2 = random.randint(3, 15)
#     chosen_response = random.randint(0, len(responses)-1)

#     return time1, time2, chosen_response


# rewrite this in OOP

# async def loop(msg: Message, n: int):
#     # This function will loop and provide a sequence of output messages
#     # msg: The message that triggered the secret command
#     # n: The loop number (starting at 0)
#     global responses

#     if n == 0:
#         time1, time2, chosen_response = first_loop(msg)

#     if responses[chosen_response] == '':
#         out = False
#         return out, n+1

#     # WAIT BEFORE FIRST RESPONSE
#     if chosen_response in (4, 16, 17, 23, 24, 25):
#         await asyncio.sleep(time1)
#     if chosen_response in (18, 32, 33, 35):
#         await asyncio.sleep(time2)

#     # SEND FIRST RESPONSE
#     out = responses[chosen_response][1]
#     return out, n+1


async def run(msg: Message, points: PointData):
    responses = load_responses(msg)
    responses = normalize_responses(responses)

    time1 = random.randint(15, 200)
    time2 = random.randint(3, 15)
    chosen_response = random.randint(0, len(responses) - 1)
    response_text = responses[chosen_response][1]

    logger.info(
        f"{msg.author} ran #secretcommand and got response {chosen_response}: {response_text}"
    )

    if response_text == "":
        return

    if chosen_response in (4, 16, 17, 23, 24, 25):
        await asyncio.sleep(time1)

    if chosen_response in (18, 32, 33, 35):
        await asyncio.sleep(time2)

    await msg.reply(response_text, as_twitch_reply=True)

    if chosen_response not in (3, 31, 41):
        return
    else:
        await asyncio.sleep(time1)
        random_gift = random.randint(2, 100)
        points.add_points(msg.author, random_gift)
        await msg.reply(
            f"peepoHas FBCatch 🎁 Here's {random_gift} points for you",
            as_twitch_reply=True,
        )
