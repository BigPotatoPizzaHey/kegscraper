"""
Session class and login function. (most bromcom functionality)
"""

from __future__ import annotations

from base64 import b64decode

import dateparser
import requests
import mimetypes
from datetime import datetime, timedelta

from bs4 import BeautifulSoup, SoupStrainer

from ..util import exceptions, commons

import atexit

from .timetable import WeekDate, Lesson


class Session:
    def __init__(self, _sess: requests.Session):
        self._sess: requests.Session = _sess

        self._name: str | None = None

        self._timetable_weeks: list[WeekDate] | None = None

        atexit.register(self.logout)

    def __repr__(self):
        return f"Session for {self.name}"

    def logout(self) -> requests.Response:
        """
        Send a logout request to bromcom. After this is called, the session will no longer function.
        :return: The response from bromcom
        """
        resp = self._sess.get("https://www.bromcomvle.com/Auth/Logout")
        print(f"Logged out with status code: {resp.status_code}")
        self._sess = None

        return resp

    # --- Account settings ---
    def set_color_preference(self, *, name: str = "Theme", value: str = "default"):
        """
        Set a color preference request to bromcom. Might not work yet
        """
        return self._sess.post("https://www.bromcomvle.com/AccountSettings/SaveColorPreference",
                               json={
                                   "Name": name,
                                   "Value": value
                               })

    @property
    def email(self):
        """
        Fetch the user email from the account settings page
        """
        text = self._sess.get("https://www.bromcomvle.com/AccountSettings").text
        soup = BeautifulSoup(text, "html.parser")

        email_inp = soup.find("input", {
            "class": "form-control",
            "id": "EmailAddress",
            "name": "EmailAddress"
        })

        return email_inp["value"]

    @property
    def school_contact_details(self) -> dict:
        """
        Fetch the school contact details as a key:value table from the hidden drop-down menu
        """
        text = self._sess.get("https://www.bromcomvle.com/Home/Dashboard").text
        soup = BeautifulSoup(text, "html.parser")

        conn_anchor = soup.find("a", {"title": "Contact School"})
        table = conn_anchor.parent.find("table")

        data = {}
        for tr in table.find_all("tr"):
            tr_data = []
            for i, td in enumerate(tr.find_all("td")):
                text: str = td.text
                if i == 0:
                    continue

                elif text.endswith(':'):
                    # Trim off colon
                    text = text[:-1]

                tr_data.append(text)

            if len(tr_data) == 2:
                # Only add stuff that can be made into a dict
                data[tr_data[0]] = tr_data[1]

        return data

    @property
    def name(self):
        """
        Fetch the student name (not username) from the deshboard page
        """
        if self._name is None:
            text = self._sess.get("https://www.bromcomvle.com/Home/Dashboard").text
            soup = BeautifulSoup(text, "html.parser", parse_only=SoupStrainer("span"))

            message = soup.find("span", {"id": "WelcomeMessage"})
            if message is None:
                raise exceptions.NotFound(f"Could not find welcome message! Response: {text}")

            self._name = commons.webscrape_section(message.text, "Hi ", ". Welcome Back!")

        return self._name

    @property
    def pfp(self) -> bytes:
        """
        Fetch the user's corresponding profile picture as bytes
        """
        return self._sess.get("https://www.bromcomvle.com/AccountSettings/GetPersonPhoto").content

    @property
    def school_photo(self) -> bytes:
        """
        Fetch the school's corresponding photo as bytes
        """
        return self._sess.get("https://www.bromcomvle.com/AccountSettings/GetSchoolPhoto").content

    @property
    def pfp_ext(self):
        """
        Fetch the image format of the profile picture
        """
        response = self._sess.get("https://www.bromcomvle.com/AccountSettings/GetPersonPhoto")
        return mimetypes.guess_extension(response.headers.get("Content-Type", "image/Jpeg"))

    @property
    def school_photo_ext(self):
        """
        Fetch the image format of the school picture
        """
        response = self._sess.get("https://www.bromcomvle.com/AccountSettings/GetSchoolPhoto")
        return mimetypes.guess_extension(response.headers.get("Content-Type", "image/Jpeg"))

    # --- Timetable methods ---
    def get_timetable_list(self, start_date: datetime | WeekDate = None, end_date: datetime | WeekDate = None) -> list[
        Lesson]:
        """
        Fetch the user's timetable starting at a corresponding week and ending on another, as a list of Lesson objects
        :param start_date: The start date given to bromcom. Can be a datetime or a WeekDate object. Defaults to the latest valid week.
        :param end_date: The end date fiven to bromcom. Defaults to a week ahead of the start date.
        :return: A list of lesson objects, each with a period #, subject name, class name, room name etc.
        """
        if isinstance(start_date, WeekDate):
            start_date = start_date.date
        if isinstance(end_date, WeekDate):
            end_date = end_date.date

        if start_date is None:
            start_date = self.current_week.date
        if end_date is None:
            end_date = start_date + timedelta(weeks=1)

        response = self._sess.get("https://www.bromcomvle.com/Timetable/GetTimeTable",
                                  params={
                                      "WeekStartDate": commons.to_dformat(start_date),
                                      "weekEndDate": commons.to_dformat(end_date),
                                      "type": 1
                                  })
        data = response.json()["table"]

        lessons = []
        for lesson_data in data:
            lesson_data: dict[str, str | int]
            lessons.append(
                Lesson(
                    lesson_data.get("periods"),
                    lesson_data.get("subject"),
                    lesson_data.get("class"),
                    lesson_data.get("room"),
                    lesson_data.get("teacherName"),
                    datetime.fromisoformat(
                        lesson_data.get("startDate")
                    ),
                    datetime.fromisoformat(
                        lesson_data.get("endDate")
                    ),
                    color=lesson_data.get("subjectColour")
                ))
        return lessons

    @property
    def timetable_weeks(self) -> list[WeekDate]:
        """
        Fetch a list of valid weeks in the user's timetable
        :return: A list of WeekDate objects, representing the start of each week, also containing a term and week index.
        """
        if self._timetable_weeks is None:
            self._timetable_weeks = []

            text = self._sess.get("https://www.bromcomvle.com/Timetable").text
            soup = BeautifulSoup(text, "html.parser")

            date_selector = soup.find("select", {"id": "WeekStartDate"})

            for option in date_selector.find_all("option"):
                value = dateparser.parse(option.attrs.get("value"))
                text = option.text

                term, week, _ = text.split(' - ')
                term = commons.webscrape_section(term, "Term ", '', cls=int)
                week = commons.webscrape_section(week, "Week ", '', cls=int)

                self._timetable_weeks.append(
                    WeekDate(term, week, value)
                )

        return self._timetable_weeks

    @property
    def current_week(self) -> WeekDate | None:
        """
        Gets the current existing timetable week (will go to last school week during holidays)
        """
        prev = None
        for wdate in self.timetable_weeks:
            if wdate.date > datetime.today():
                return prev
            prev = wdate

    @property
    def current_week_idx(self) -> int:
        for i, wdate in enumerate(self.timetable_weeks):
            if wdate.date > datetime.today():
                return i
        return -1

    # --- Attendance methods ---
    @property
    def present_late_ratio(self) -> dict[str, int]:
        """
        Webscrape JSON inside JS inside HTML to get the present, late and other attendance type counts. i.e.:
        Returns a dictionary e.g.: {
        "present": 176,
        "late": 21
        }
        :return: A dictionary of attendance statuses and their counts
        """
        # Parse JSON inside of JS inside of HTML. Yeah....
        text = self._sess.get("https://www.bromcomvle.com/Attendance").text
        soup = BeautifulSoup(text, "html.parser")

        script_prf = ('$(document).ready(function () {\r\n'
                      '        var AttendanceChart = c3.generate({\r\n'
                      '            bindto: \'#AttendanceChart\',\r\n'
                      '            data: {\r\n'
                      '                columns: ')

        for script in soup.find_all("script", {"type": "text/javascript"}):
            text = script.text.strip()

            if text.startswith(script_prf):
                # Found correct js script. Now webscrape.
                text = text[len(script_prf):]

                data = commons.consume_json(text)

                ret = {cat: count for cat, count in data}

                return ret

        return {}

    @property
    def attendance_status(self):
        """
        Get the Status for the current day. (Uses the widget api)
        """
        return self._sess.get("https://www.bromcomvle.com/Home/GetAttendanceWidgetData").json()

    # --- Reports data ---

    @property
    def reports_data(self) -> dict[str, list[dict[str, str]]]:
        """
        Fetch the report list (needs to be parsed)
        :return: A list of dictionaries representing reports. The filePath attribute can be used in the get_report method to fetch the report pdf as bytes
        """
        # Parse this later
        return self._sess.get("https://www.bromcomvle.com/Home/GetReportsWidgetData").json()

    def get_report(self, filepath: str) -> bytes:
        """
        Get the report with the given 'filepath' as bytes
        :param filepath: The filePath attribute in the report data
        :return: The report data as bytes
        """
        # Get the data encoded in b64 encoded in JSON. Weird.
        data = self._sess.get("https://www.bromcomvle.com/Report/GetReport",
                              params={
                                  "filePath": filepath
                              }).json()

        return b64decode(data)

    # --- Exam data ---

    @property
    def exam_data(self) -> list[dict[str, str]]:
        """
        Fetch the exam data from the widget api
        :return:
        """
        # Parse this
        return self._sess.get("https://www.bromcomvle.com/Home/GetExamResultsWidgetData").json()

    # --- Bookmarks data ---
    @property
    def bookmarks_data(self) -> list[dict]:
        """
        Get the bookmarks list as a list of dictionaries (needs to be parsed)
        :return: list of dictionaries, each is a bookmark
        """
        # Parse this
        return self._sess.get("https://www.bromcomvle.com/Home/GetBookmarksWidgetData").json()

    # --- Homework data ---
    @property
    def homework_data(self) -> list:
        """
        Fetch homework data using the widget api. I have no homework so I am unable to parse this
        :return: A list of something
        """
        return self._sess.get("https://www.bromcomvle.com/Home/GetHomeworkWidgetData").json()


def login(school_id: int, username: str, password: str, remember_me: bool = True) -> Session:
    """
    Login to bromcom with a school id, username and password.
    :param school_id: KEGS school id (you provide it)
    :param username: Your username
    :param password: Your password
    :param remember_me: Option to 'remember me.' Defaults to True
    :return: A session representing your login
    """
    _sess = requests.Session()
    _sess.headers = commons.headers.copy()

    text = _sess.get("https://www.bromcomvle.com/").text
    soup = BeautifulSoup(text, "html.parser", parse_only=SoupStrainer("input"))

    rvinp = soup.find("input", {"name": "__RequestVerificationToken"})
    if rvinp is None:
        ptfy = BeautifulSoup(text, "html.parser").prettify()
        raise exceptions.NotFound(f"Could not find rv token; response text: {ptfy}")

    rvtoken = rvinp.attrs.get("value")

    response = _sess.post("https://www.bromcomvle.com/",
                          data={
                              "SpaceID": '',

                              "schoolid": school_id,
                              "username": username,
                              "password": password,

                              "__RequestVerificationToken": rvtoken,
                              "rememberme": str(remember_me).lower()
                          })

    if response.status_code != 200:
        if response.status_code == 500:
            raise exceptions.ServerError(
                f"The bromcom server experienced some error when handling the login request (ERR 500). Response content: {response.content}")
        else:
            raise exceptions.Unauthorised(
                f"The provided details for {username} may be invalid. Status code: {response.status_code} "
                f"Response content: {response.content}")

    return Session(_sess)
