import requests
from dataclasses import dataclass, field
from datetime import datetime
import dateparser
import mimetypes

from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup, SoupStrainer

from ..util import commons, exceptions

@dataclass(init=True, repr=True)
class Asset:
    """
    Represents an asset that can be downloaded with the 'force_download.cfm' endpoint
    """

    id: int=None
    content: bytes = field(repr=False, default=None)
    name: str = None
    mime: str = None
    last_modified: datetime = None

    @property
    def ext(self):
        """
        Guess the file extension of this asset
        """
        return mimetypes.guess_extension(self.mime)


def download_asset_by_id(_id: int) -> Asset:
    """
    Fetch an asset by id from the force_download.cfm endpoint, using headers to provide metadata
    :param _id: id of asset to fetch
    :return: The corresponding Asset object
    """

    url = "https://www.kegs.org.uk/force_download.cfm"
    response = requests.get(url,
                            params={"id": _id})

    if response.url == f"{url}?id={_id}":
        raise exceptions.NotFound(f"Asset id {_id!r} could not be found (no redirect)")

    fname = urlparse(response.url).path.split('/')[-1]

    return Asset(_id,
                 response.content,
                 fname,
                 response.headers.get("Content-Type"),
                 dateparser.parse(response.headers.get("Last-Modified", '')))

def find_asset_ids(url: str) -> list[int]:
    """
    Scrape any asset ids by looking for force_download.cfm links
    :param url: url of page to scrape
    :return: list of ids
    """
    ids = []

    global_netloc = urlparse(url).netloc

    links = commons.find_links(BeautifulSoup(
        requests.get(url).text, "html.parser", parse_only=SoupStrainer("a")
    ))

    for link in links:
        parse = urlparse(link)

        netloc = parse.netloc if parse.netloc else global_netloc

        if netloc == "www.kegs.org.uk" and parse.path == "/force_download.cfm":
            qparse = parse_qs(parse.query)
            ids.append(int(qparse.get("id")[0]))

    return ids
