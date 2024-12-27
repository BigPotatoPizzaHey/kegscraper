from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import requests
from dataclasses import dataclass, field
from datetime import datetime

from bs4 import BeautifulSoup, Comment

from ..util import commons, exceptions


@dataclass(init=True, repr=True)
class Category:
    id: int
    name: str


@dataclass(init=True, repr=True)
class NewsItem:
    id: int

    author: str = None
    title: str = None
    content: str = field(repr=False, default=None)

    date: datetime = None
    category: Category = None


def get_news_page(page: int = 1, category: int | Category = 7) -> NewsItem:
    """
    Get the news item at the specified page index
    :param category: Category of news
    :param page: Page index
    :return: The news item
    """
    if isinstance(category, Category):
        category = category.id

    # Find the page corresponding to the category & post
    response = requests.get(f"https://it.kegs.org.uk/",
                        params={
                            "cat": category,
                            "paged": page
                        })

    if response.status_code == 404:
        raise exceptions.NotFound(f"Could not find news page. Content: {response.content}")

    text = response.text
    soup = BeautifulSoup(text, "html.parser")

    anchor = soup.find("a", {"rel": "bookmark"})

    url = anchor.attrs.get("href")
    qparse = parse_qs(urlparse(url).query)

    news_id = int(qparse["p"][0])

    # Actually scrape the main page for this news item
    text = requests.get("https://it.kegs.org.uk/",
                        params={
                            "p": news_id
                        }).text
    soup = BeautifulSoup(text, "html.parser")

    title = soup.find("div", {"class": "singlepage"}).text

    date_elem = soup.find("abbr")
    date = datetime.fromisoformat(date_elem.attrs.get("title"))

    # There is a cheeky comment above the date element that we can try to webscrape
    comment = date_elem.parent.find(string=lambda _text: isinstance(_text, Comment)).extract()
    # It's actually in HTML format
    comment_text = BeautifulSoup(comment, "html.parser").text

    author = commons.webscrape_value(comment_text, "Written by ", " on")

    # Contents and category
    contents_div = soup.find("div", {"id": "content"})

    post_wrapper = contents_div.find("div", {"id": "singlepostwrapper"})
    category_anchor = post_wrapper.find("a", {"rel": "category"})

    # url = category_anchor.attrs.get("href")  # We already know the category index so we don't need to parse the link
    category_name = category_anchor.text
    category_obj = Category(category, category_name)

    # Get content
    content = contents_div.find("div", {"class": "entry"}).text.strip()


    return NewsItem(
        news_id,
        author,

        title,
        content,

        date,
        category_obj
    )

def load_news_category(category: int | Category = 7, *, limit: int=10, offset: int=0):
    pages = []
    for page, _ in zip(*commons.generate_page_range(limit, offset, 1, 1)):
        print(page)
        try:
            pages.append(get_news_page(page, category))

        except exceptions.NotFound:
            break

    return pages
