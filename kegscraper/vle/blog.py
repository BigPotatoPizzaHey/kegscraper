from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from typing import Any

import dateparser
from bs4 import PageElement, BeautifulSoup

from . import session, user
from ..util import commons


@dataclass
class External:
    """Represents an external blog or an external blog entry"""
    url: str
    name: str


@dataclass
class Tag:
    name: str


@dataclass
class Entry:
    id: int = None
    subject: str = None
    author: user.User = None
    date: datetime = None
    audience: str = None
    content: PageElement | Any = field(repr=False, default=None)
    tags: list[Tag] = None

    external_blog: External = None
    external_blog_entry: External = None

    _context_id: int = None

    _session: session.Session = field(repr=False, default=None)

    def update_from_id(self):
        text = self._session.rq.get("https://vle.kegs.org.uk/blog/index.php",
                                    params={
                                        "entryid": self.id
                                    }).text
        soup = BeautifulSoup(text, "html.parser")

        self.update_from_div(
            soup.find("div", {"id": f"b{self.id}"})
        )

    def update_from_div(self, div: PageElement):
        header = div.find("div", {"class": "row header clearfix"})
        main = div.find("div", {"class": "row maincontent clearfix"})

        self.id = int(div["id"][1:])

        self.subject = header.find("div", {"class": "subject"}).text

        author_anchor = header.find("div", {"class": "author"}).find("a")
        parse = urlparse(author_anchor["href"])
        qparse = parse_qs(parse.query)

        author_id = int(qparse["id"][0])

        self.author = user.User(id=author_id, name=author_anchor.text)

        date_str = author_anchor.next.next.text
        self.date = dateparser.parse(date_str)

        external_div = header.find("div", {"class": "externalblog"})
        if external_div:
            external_anchor = external_div.find("a")
            if external_anchor:
                self.external_blog = External(
                    external_anchor["href"],
                    external_anchor.text
                )

        # Get actual blog content
        self.audience = main.find("div", {"class": "audience"}).text

        self.content = main.find("div", {"class": "text_to_html"})

        external_div = main.find("div", {"class": "externalblog"})
        if external_div:
            external_anchor = external_div.find("a")
            if external_anchor:
                self.external_blog_entry = External(
                    external_anchor["href"],
                    external_anchor.text
                )

        tag_list = main.find("div", {"class": "tag_list"}).find_all("li")
        self.tags = []
        for tag_data in tag_list:
            tag_a = tag_data.find("a")

            # We could probably also get the anchor text, but this is more robust
            parse = urlparse(tag_a["href"])
            qparse = parse_qs(parse.query)

            self.tags.append(Tag(qparse["tag"][0]))

        mdl = main.find("div", {"class": "mdl-left"})
        njs_url = mdl.find("a", {"class": "showcommentsnonjs"})["href"]
        parse = urlparse(njs_url)
        qparse = parse_qs(parse.query)
        self._context_id = int(qparse["comment_context"][0])

    def get_comments(self, *, limit: int = 1, offset: int = 0):
        data_lst = []
        for page, start_idx in zip(*commons.generate_page_range(limit, offset, items_per_page=999, starting_page=0)):
            data_lst += (self._session.rq.post("https://vle.kegs.org.uk/comment/comment_ajax.php",
                                               data={
                                                   "sesskey": self._session.sesskey,
                                                   "action": "get",
                                                   "client_id": self._session.file_client_id,
                                                   "itemid": self.id,
                                                   "area": "format_blog",
                                                   "courseid": "1",
                                                   "contextid": self._context_id,
                                                   "component": "blog",
                                                   "page": page
                                               }).json()["list"])

        return data_lst # Parse this
