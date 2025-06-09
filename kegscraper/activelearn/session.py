from __future__ import annotations

import atexit
import random
import string
import enum
from dataclasses import dataclass, field
from urllib.parse import quote_plus, ParseResult, urlunparse, urlencode

import requests
import requests.cookies
# noinspection PyProtectedMember
from playwright.sync_api import sync_playwright, PlaywrightContextManager, Playwright, Browser, Page, Request


class EventType(enum.Enum):
    library_update = "library_update"

@dataclass
class DebugSettings:
    print_on_req: bool = False

@dataclass
class Session:
    pw_ctx: PlaywrightContextManager = field(repr=False)
    playwright: Playwright = field(repr=False)
    browser: Browser = field(repr=False)
    page: Page = field(repr=False)

    events: dict[str, bool] = field(default_factory=dict) # special dict that logs if certain events occur - e.g. updating based on library data
    debug: DebugSettings = field(repr=False, default_factory=DebugSettings)

    def __post_init__(self):
        self.page.on("requestfinished", self.on_req)

        atexit.register(self.pw_ctx.__exit__)

    def _register_event(self, event_type: EventType, value = True):
        self.events[event_type.value] = value

    def _expect_event(self, event_type: EventType, *, pop: bool = True):
        ...

    def clear_events(self):
        self.events.clear()

    def on_req(self, req: Request):
        resp = req.response()

        if self.debug.print_on_req:
            print(f"Session.on_req.{req = }")

        match req.url:
            case "https://www.pearsonactivelearn.com/app/Execute/GetUserSeriesList":
                self._register_event(EventType.library_update, resp.json())


    @property
    def library(self):
        self.page.goto("https://www.pearsonactivelearn.com/app/library")
        self.page.expect_response("https://www.pearsonactivelearn.com/app/Execute/GetUserSeriesList")
        input()


def login(username: str, password: str, headless: bool = True, **kwargs):
    # we can generate a random ies code by ourselves. We can go directly to the pearson login page
    iescode = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    url = urlunparse(ParseResult(scheme='https',
                                 netloc='login.pearson.com',
                                 path='/v1/piapi/iesui/signin',
                                 params='',
                                 query=urlencode({
                                     # client id is always the same
                                     "client_id": "BRSIcPHr2Iq0NV8AQP99zDZau8IPUxgy",
                                     "redirect_uri": "https://www.pearsonactivelearn.com/app/login",
                                     "nonce": "123454321",
                                     "prompt": "login",
                                     "cookieConsentGroups": "100000",
                                     "login_success_url": f"https://www.pearsonactivelearn.com/app/login?iesCode={quote_plus(iescode)}"
                                 }),
                                 fragment=''))  # type:ignore

    pw_ctx = sync_playwright()
    playwright = pw_ctx.__enter__()

    browser = playwright.webkit.launch(headless=headless, **kwargs)
    page = browser.new_page()


    page.goto(str(url))

    username_inp = page.wait_for_selector("input[id=username]")
    password_inp = page.wait_for_selector("input[id=password]")
    submit_btn = page.wait_for_selector("button[id=submitBttn]")

    username_inp.type(username)
    password_inp.type(password)
    submit_btn.click()

    page.wait_for_url("https://www.pearsonactivelearn.com/app/library")

    return Session(
        pw_ctx=pw_ctx,
        playwright=playwright,
        browser=browser,
        page=page
    )
