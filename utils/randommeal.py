import logging
from urllib import parse
import urllib.request
import json

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

# Response format:
#   <@Username>, <Name of Dish> - Ingredients: <comma separated ingredients>,
#   <youtube link>

url = "https://www.themealdb.com/api/json/v1/1/random.php"


def _request() -> dict:
    global url

    print(url)

    with urllib.request.urlopen(url) as response:
        j = json.loads(response.read())
        meal = j["meals"][0]  # strip unnecessary typing

    return meal


def _parse_ingredients(raw_response: dict) -> str:
    """
    Parse raw meal response dict, find the ingredients, and return
    a string of the ingredients separated by commas.
    """
    ingredients = ""
    print(type(raw_response))
    for key, value in raw_response.items():
        if "ingredient" not in key.lower():
            continue
        if len(value) == 0:
            continue
        ingredients = ingredients + value.lower() + ", "

    ingredients = ingredients.strip(", ")

    return ingredients


def get_meal() -> str:
    """
    Returns a string of the formatted recipe response.
    """
    raw = _request()
    name = raw["strMeal"]
    category = raw["strCategory"]
    area = raw["strArea"]
    youtube = raw["strYoutube"]
    ingredients = _parse_ingredients(raw)

    formatted_response = (
        f"{name} ({category}, {area}) - Ingredients: {ingredients}, {youtube}"
    )

    return formatted_response
