import json

def get_oauth():
    """Returns the oauth token.

    Returns:
        str: oauth token
    """
    with open(f'configs/config.json', 'r') as f:
        return json.load(f)['oauth']
    

def get_client_id():
    """Returns the client id.

    Returns:
        str: client id
    """
    with open(f'configs/config.json', 'r') as f:
        return json.load(f)['client_id']
    

def get_client_secret():
    """Returns the client secret.

    Returns:
        str: client secret
    """
    with open(f'configs/config.json', 'r') as f:
        return json.load(f)['client_secret']