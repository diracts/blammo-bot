import json


def get_oauth():
    """Returns the oauth token.

    Returns:
        str: oauth token
    """
    with open(f"configs/config.json", "r") as f:
        return json.load(f)["oauth"]


def get_client_id():
    """Returns the client id.

    Returns:
        str: client id
    """
    with open(f"configs/config.json", "r") as f:
        return json.load(f)["client_id"]


def get_client_secret():
    """Returns the client secret.

    Returns:
        str: client secret
    """
    with open(f"configs/config.json", "r") as f:
        return json.load(f)["client_secret"]


def get_news_api_key():
    """Returns the news api key.

    Returns:
        str: news api key
    """
    with open(f"configs/config.json", "r") as f:
        return json.load(f)["news_api_key"]


def get_wa_appid():
    """Returns the Wolfram Alpha appID.

    Returns:
        str: WA appID
    """
    with open(f"configs/config.json", "r") as f:
        return json.load(f)["wa_appid"]
