from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from typing import Any, Self

import dateparser
from bs4 import PageElement, BeautifulSoup

from . import session, user, tag
from ..util import commons, exceptions


@dataclass
class External:
    """Represents an external blog or an external blog entry"""
    url: str
    name: str

    _session: session.Session = field(repr=False, default=None)


@dataclass
class Comment:
    id: int = None
    content: BeautifulSoup = field(repr=False, default=None)
    format: str = '0'  # Idk what this is
    created: datetime = None
    author: user.User = None
    deletable: bool = False

    _entry: Entry = field(repr=False, default=None)
    _session: session.Session = field(repr=False, default=None)

    @classmethod
    def from_json(cls, data: dict[str, str | bool], _entry: Entry, _session: session.Session) -> Self:
        return cls(
            data.get("id"),
            BeautifulSoup(data.get("content", ''), "html.parser"),
            data.get("format"),
            datetime.fromtimestamp(int(data.get("timecreated"))),
            _session.connect_partial_user(
                id=int(data.get("userid")),
                name=data.get("fullname")
            ),
            data.get("delete"),
            _entry,
            _session
        )

    @property
    def text(self):
        return self.content.text

    def delete(self):
        response =  self._session.rq.post("https://vle.kegs.org.uk/comment/comment_ajax.php",
                              data={
                                  "sesskey": self._session.sesskey,
                                  "action": "delete",
                                  "client_id": self._session.file_client_id,
                                  "itemid": self._entry.id,
                                  "area": "format_blog",
                                  "courseid": 1,
                                  "contextid": self._entry.context_id,
                                  "component": "blog",
                                  "commentid": self.id
                              })
        if response:
            data = response.json()
            if data.get("error") == "Invalid comment ID":
                raise exceptions.NotFound("Invalud comment ID")
            else:
                return data
        else:
            extra = f" This may be because you are not {self.author.name} ({self.author.id})" if self._session.user_id != self.author.id else ''
            warnings.warn(f"Possibly couldn't delete {self}.{extra}")


@dataclass
class Entry:
    id: int = None
    subject: str = None
    author: user.User = None
    date: datetime = None
    audience: str = None
    content: PageElement | Any = field(repr=False, default=None)
    images: PageElement | Any = field(repr=False, default=None)
    tags: list[tag.Tag] = None

    external_blog: External = None
    external_blog_entry: External = None

    context_id: int = None

    _session: session.Session = field(repr=False, default=None)

    @property
    def url(self):
        return f"https://vle.kegs.org.uk/blog/index.php?entryid={self.id}"

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
        if div is None:
            raise exceptions.NotFound(
                f"BlogEntry #{self.id}, ({self}) does not seem to exist. It may have been deleted, or may never have existed, or you may be logged out.")

        header = div.find("div", {"class": "row header clearfix"})
        main = div.find("div", {"class": "row maincontent clearfix"})

        if header is None and main is None:
            raise exceptions.NotFound(
                f"BlogEntry #{self.id}, ({self}) does not seem to exist. It may have been deleted, or may never have existed, or you may be logged out.")

        self.id = int(div["id"][1:])

        self.subject = header.find("div", {"class": "subject"}).text

        author_anchor = header.find("div", {"class": "author"}).find("a")
        parse = urlparse(author_anchor["href"])
        qparse = parse_qs(parse.query)

        author_id = int(qparse["id"][0])

        self.author = self._session.connect_partial_user(id=author_id, name=author_anchor.text)

        date_str = author_anchor.next.next.text
        self.date = dateparser.parse(date_str)

        external_div = header.find("div", {"class": "externalblog"})
        if external_div:
            external_anchor = external_div.find("a")
            if external_anchor:
                self.external_blog = External(
                    external_anchor["href"],
                    external_anchor.text,
                    _session=self._session
                )

        # Get actual blog content
        self.audience = main.find("div", {"class": "audience"}).text

        # Parse this maybe
        self.images = main.find("div", {"class": "attachedimages"})

        self.content = main.find("div", {"class": "no-overflow"}) \
            .find("div", {"class": "no-overflow"})

        external_div = main.find("div", {"class": "externalblog"})
        if external_div:
            external_anchor = external_div.find("a")
            if external_anchor:
                self.external_blog_entry = External(
                    external_anchor["href"],
                    external_anchor.text,
                    _session=self._session
                )

        tag_list = main.find("div", {"class": "tag_list"})
        if tag_list:
            tag_list = tag_list.find_all("li")

        self.tags = []
        if tag_list:
            for tag_data in tag_list:
                tag_a = tag_data.find("a")

                # We could probably also get the anchor text, but this is more robust
                parse = urlparse(tag_a["href"])
                qparse = parse_qs(parse.query)

                self.tags.append(tag.Tag(qparse["tag"][0], _session=self._session))

        mdl = main.find("div", {"class": "mdl-left"})
        njs_url = mdl.find("a", {"class": "showcommentsnonjs"})["href"]
        parse = urlparse(njs_url)
        qparse = parse_qs(parse.query)
        self.context_id = int(qparse["comment_context"][0])

    def get_comments(self, *, limit: int = 1, offset: int = 0) -> list[Comment]:
        if self.context_id is None:
            self.update_from_id()

        data_lst = []
        for page, _ in zip(*commons.generate_page_range(limit, offset, items_per_page=999, starting_page=0)):
            data_lst += (self._session.rq.post("https://vle.kegs.org.uk/comment/comment_ajax.php",
                                               data={
                                                   "sesskey": self._session.sesskey,
                                                   "action": "get",
                                                   "client_id": self._session.file_client_id,
                                                   "itemid": self.id,
                                                   "area": "format_blog",
                                                   "courseid": "1",
                                                   "contextid": self.context_id,
                                                   "component": "blog",
                                                   "page": page
                                               }).json()["list"])

        return [Comment.from_json(data, self, self._session) for data in data_lst]

    def post_comment(self, content: str) -> Comment:
        if self.context_id is None:
            self.update_from_id()

        response = self._session.rq.post("https://vle.kegs.org.uk/comment/comment_ajax.php",
                                         data={
                                             "sesskey": self._session.sesskey,
                                             "action": "add",
                                             "client_id": self._session.file_client_id,
                                             "itemid": self.id,
                                             "area": "format_blog",
                                             "courseid": 1,
                                             "contextid": self.context_id,
                                             "component": "blog",
                                             "content": content
                                         })

        ret = Comment.from_json(response.json(), self, self._session)
        return ret
