from __future__ import annotations

from typing import Any, Self
from dataclasses import dataclass, field
from datetime import datetime

import dateparser

from . import session, course

from ..util import commons


@dataclass
@commons.with_kwargs
class DigitalBook:
    id: int = None
    name: str = None

    published: bool = field(repr=False, default=None)
    is_new: bool = field(repr=False, default=None)
    is_updated: bool = field(repr=False, default=None)

    image_src: str = field(repr=False, default=None)
    content_object_link: str = field(repr=False, default=None)

    launcher: str = field(repr=False, default=None)
    # image_class: str

    purchase_url: dict[str, str] = field(repr=False, default=None)
    available: dict[str, str] = field(repr=False, default=None)
    purchased: dict[str, str] = field(repr=False, default=None)
    subs_end_date: datetime = field(repr=False, default=None)

    course: course.Course = field(repr=False, default=None)
    _sess: session.Session = field(repr=False, default=None)

    # engine: str
    # purchase_link: str

    # offline_content_link: Any
    # offline_content_version: int

    # url: dict[str, str]

    # purchase_link_text: dict[str, str]
    # purchase_instruction_text: dict[str, str]
    # purchase_popup_title: dict[str, str]

    def __post_init__(self):
        if not isinstance(self.subs_end_date, datetime) and self.subs_end_date is not None:
           self.subs_end_date = dateparser.parse(str(self.subs_end_date))

    @classmethod
    def from_kwargs(cls, **kwargs) -> Self: ...

    @property
    def _interactive_url(self):
        return f"https://www.kerboodle.com/api/courses/{self.course.id}/interactives/{self.id}.html"

