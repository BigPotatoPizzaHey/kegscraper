from __future__ import annotations

import atexit
import base64
import logging
import re
import time
import warnings
from dataclasses import dataclass
from typing import Optional

# noinspection PyProtectedMember
from playwright.sync_api import sync_playwright, PlaywrightContextManager, Playwright, Browser, Page, Request, \
    FilePayload
# noinspection PyProtectedMember
from playwright._impl import _errors as pw_errors

@dataclass
class Session:
    pw_ctx: PlaywrightContextManager
    playwright: Playwright
    browser: Browser
    page: Page

    def set_pfp(self, fp: str, *, return_screenshot: bool = True) -> Optional[bytes]:
        # depending on your theme, fetching the pfp seems to be inconsistent

        self.page.wait_for_load_state("networkidle", timeout=120_000)
        self.page.goto("https://myaccount.microsoft.com/")

        img_btn = self.page.locator("div[role='presentation'][class='ms-Persona-imageArea imageArea-307']")
        img_btn.wait_for()

        # maybe change this to a locator: https://playwright.dev/python/docs/other-locators
        div = self.page.locator('div[role=heading]:has-text("Give feedback to Microsoft")')
        try:
            div.wait_for(timeout=10_000)
        except pw_errors.TimeoutError as e:
            warnings.warn(f"{e.__class__}: {e}")
            div = None

        if div:
            frame_parent = div.locator("../..")
            cancel_btn = frame_parent.locator('button:not([aria-disabled]):has-text("Cancel")')

            cancel_btn.click()

        img = img_btn.locator("img[src][alt='Profile photo']")
        img.wait_for()

        img_btn.click()
        change_photo_btn = self.page.wait_for_selector("span[role=presentation].CloudUpload")

        with self.page.expect_file_chooser() as fc_info:
            change_photo_btn.click()

        file_chooser = fc_info.value
        file_chooser.set_files(fp)

        self.page.wait_for_selector("button[aria-label=Save]").click()

        if return_screenshot:
            return self.page.screenshot()


def login(username: str, password: str, *, headless: bool=True, **kwargs):
    if username.endswith("@kegs.org.uk"):
        username = username[:-len("@kegs.org.uk")]

    pw_ctx = sync_playwright()
    playwright = pw_ctx.__enter__()
    atexit.register(pw_ctx.__exit__)

    browser = playwright.chromium.launch(headless=headless, **kwargs)
    page = browser.new_page()

    page.goto("https://www.outlook.com/kegs.org.uk")

    username_input = page.wait_for_selector("input[id=userNameInput]")
    password_input = page.wait_for_selector("input[id=passwordInput]")
    sign_in_button = page.wait_for_selector("span[id=submitButton]")

    username_input.type(username)
    password_input.type(password)
    sign_in_button.click()

    page.wait_for_url("https://login.microsoftonline.com/login.srf")
    page.wait_for_selector("input[type=submit]").click()

    page.wait_for_url("https://login.microsoftonline.com/appverify")
    try:
        page.wait_for_selector("input[type=submit]").click()
    except Exception as e:
        warnings.warn(str(e))

    page.wait_for_load_state("networkidle", timeout=120_000)

    if page.url.startswith("https://login.microsoftonline.com/common/oauth2/v2.0/authorize"):
        table = page.wait_for_selector("div[class=table tole=button]")
        table.query_selector("div[class=table-row]").click()

    page.wait_for_url("https://outlook.office365.com/mail/")

    return Session(
        pw_ctx=pw_ctx, playwright=playwright, browser=browser, page=page
    )
