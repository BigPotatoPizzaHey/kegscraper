from . import utils


def get_news():
    data = utils.api_fetch("news")
    # Parse this...
    return data
