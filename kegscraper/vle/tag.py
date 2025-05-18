"""
Class representing tags accessible through here: https://vle.kegs.org.uk/tag/index.php?tag=woodlouse
"""
from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs

import dateparser
import requests
from bs4 import BeautifulSoup, PageElement
from . import session, user, blog
from ..util import commons


@dataclass
class Tag:
    name: str = None
    exists: bool = None

    description: PageElement = field(default=None, repr=False)
    related_tags: list[Tag] = field(default_factory=list)

    id: int = None

    _session: session.Session = field(repr=False, default=None)

    def _update_from_response(self, response: requests.Response):

        self.exists = response.url != "https://vle.kegs.org.uk/tag/search.php"
        if self.exists:
            soup = BeautifulSoup(response.text, "html.parser")
            main = soup.find("div", {"role": "main"})

            self.name = main.find("h2").text

            mng_box = main.find("div", {"class": "tag-management-box"})
            tedit = mng_box.find("a", {"class": "edittag"})
            href = tedit.attrs.get("href", '')
            q_parse = parse_qs(urlparse(href).query)
            self.id = int(q_parse.get("id")[0])

            # get desc
            self.description = main.find("div", {"class": "tag-description"})

            # get related tags
            self.related_tags.clear()
            related_tag_div = main.find("div", {"class": "tag-relatedtags"})
            for li in related_tag_div.find_all("li"):
                href = li.find("a").attrs["href"]
                if href == '#':
                    continue

                parsed = urlparse(href)
                q_parse = parse_qs(parsed.query)
                related_tag_name = q_parse["tag"][0]
                self.related_tags.append(
                    Tag(
                        related_tag_name,
                        _session=self._session
                    )
                )

    def update_from_name(self):
        response = self._session.rq.get("https://vle.kegs.org.uk/tag/index.php",
                                        params={
                                            "tag": self.name
                                        })
        self._update_from_response(response)

    def update_from_id(self):
        response = self._session.rq.get("https://vle.kegs.org.uk/tag/index.php",
                                        params={
                                            "id": self.id
                                        })
        self._update_from_response(response)

    def _req_get_tagindex(self, page: int | str, ta: int | str):
        json_data = [
            {
                "index": 0,
                "methodname": "core_tag_get_tagindex",
                "args": {
                    "tagindex": {"tc": "1",
                                 "tag": self.name,
                                 "ta": str(ta),  # 1 = users, 3 = courses, 7 = blog posts. todo: courses?
                                 "page": str(page)
                                 }
                }
            }]

        return self._session.rq.post("https://vle.kegs.org.uk/lib/ajax/service.php",
                                     params={
                                         "sesskey": self._session.sesskey,
                                         "info": "core_tag_get_tagindex"
                                     },
                                     json=json_data)

    def connect_interested_users(self, limit: int = 5, offset: int = 0):
        users = []

        for page in commons.generate_page_range(limit, offset, 5, 0)[0]:
            data = self._req_get_tagindex(page, 1).json()[0]["data"]["content"]
            soup = BeautifulSoup(data, "html.parser")

            for li in soup.find_all("li", {"class": "media"}):
                a = li.find("a")
                href = a.attrs["href"]
                q_parse = parse_qs(urlparse(href).query)

                uid = int(q_parse["id"][0])

                img = a.find("img")
                src = img.attrs["src"]

                body = li.find("div", {"class": "media-body"})
                name = body.text.strip()

                users.append(user.User(id=uid, name=name, image_url=src))

        return users

    def connect_tagged_blog_entries(self, limit: int = 5, offset: int = 0):
        entries = []

        for page in commons.generate_page_range(limit, offset, 5, 0)[0]:
            data = self._req_get_tagindex(page, 7).json()[0]["data"]["content"]
            soup = BeautifulSoup(data, "html.parser")

            for li in soup.find_all("li", {"class": "media"}):
                a = li.find("a")
                href = a.attrs["href"]
                q_parse = parse_qs(urlparse(href).query)

                uid = int(q_parse["id"][0])

                img = a.find("img")
                src = img.attrs["src"]

                body = li.find("div", {"class": "media-body"})

                entry_a = body.find("a")
                subject = entry_a.contents[0].strip()

                href = entry_a.attrs["href"]
                q_parse = parse_qs(urlparse(href).query)
                entry_id = int(q_parse["entryid"][0])

                muted = body.find("div", {"class": "muted"})
                split = muted.text.split(',')
                author_name = split[0].strip()
                date = dateparser.parse(','.join(split[1:]))

                author = user.User(id=uid, name=author_name, image_url=src)

                entries.append(
                    blog.Entry(
                        id=entry_id,
                        subject=subject,
                        date=date,
                        author=author,
                        _session=self._session
                    )
                )

        return entries
