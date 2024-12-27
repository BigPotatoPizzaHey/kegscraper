from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

from . import file, user, forum
from ..util import commons


class Session:
    def __init__(self, _sess: requests.Session):
        self.rq: requests.Session = _sess
        """Request handler (requests session object)"""

        self._sesskey: str | None = None
        self._file_client_id: str | None = None
        self._file_item_id: str | None = None
        self._user_id: int | None = None
        self._user: user.User | None = None

        self.assert_login()

    # --- Session/auth related methods ---
    @property
    def sesskey(self):
        """Get the sesskey query parameter used in various functions"""
        if self._sesskey is None:
            pfx = "var M = {}; M.yui = {};\nM.pageloadstarttime = new Date();\nM.cfg = "

            response = self.rq.get("https://vle.kegs.org.uk/")
            soup = BeautifulSoup(response.text, "html.parser")

            self._sesskey = None
            for script in soup.find_all("script"):
                text = script.text
                if "\"sesskey\":" in text:
                    i = text.find(pfx)
                    if i > -1:
                        i += len(pfx) - 1
                        data = commons.consume_json(text, i)

                        if isinstance(data, dict):
                            self._sesskey = data.get("sesskey")

        return self._sesskey

    @property
    def file_client_id(self):
        if self._file_client_id is None:
            response = self.rq.get("https://vle.kegs.org.uk/user/files.php")
            soup = BeautifulSoup(response.text, "html.parser")

            for div in soup.find_all("div", {"class": "filemanager w-100 fm-loading"}):
                self._file_client_id = div.attrs["id"].split("filemanager-")[1]

        return self._file_client_id

    @property
    def connected_user(self) -> user.User:
        if not self._user:
            self._user = self.connect_user(self.user_id)

        return self._user

    @property
    def file_item_id(self):
        if self._file_item_id is None:
            response = self.rq.get("https://vle.kegs.org.uk/user/files.php")
            soup = BeautifulSoup(response.text, "html.parser")
            self._file_item_id = soup.find("input", {"id": "id_files_filemanager"}).attrs.get("value")

        return self._file_item_id

    @property
    def username(self):
        response = self.rq.get("https://vle.kegs.org.uk/login/index.php")
        soup = BeautifulSoup(response.text, "html.parser")
        for alert_elem in soup.find_all(attrs={"role": "alert"}):
            alert = alert_elem.text

            username = commons.webscrape_value(alert, "You are already logged in as ",
                                               ", you need to log out before logging in as different user.")
            if username:
                return username
        return None

    @property
    def user_id(self):
        if self._user_id is None:
            response = self.rq.get("https://vle.kegs.org.uk/")
            soup = BeautifulSoup(response.text, "html.parser")

            url = soup.find("a", {"title": "View profile"}) \
                .attrs["href"]

            parsed = parse_qs(urlparse(url).query)
            self._user_id = int(parsed.get("id")[0])

        return self._user_id

    def assert_login(self):
        assert self.username

    # --- Connecting ---
    def connect_user(self, _id: int) -> user.User:
        ret = user.User(_id, _session=self)
        ret.update_from_id()
        return ret

    def connect_forum(self, _id: int) -> forum.Forum:
        ret = forum.Forum(_id, _session=self)
        ret.update_by_id()
        return ret

    # --- Private Files ---
    def _file_data(self, fp: str) -> dict:
        # Believe or not, KegsNet does actually have some JSON endpoints!
        return self.rq.post("https://vle.kegs.org.uk/repository/draftfiles_ajax.php",
                            params={"action": "list"},
                            data={
                                     "sesskey": self.sesskey,

                                     "clientid": self.file_client_id,
                                     "itemid": self.file_item_id,
                                     "filepath": fp
                                 }).json()

    def files_in_dir(self, fp: str):
        data = self._file_data(fp)["list"]
        files = []
        for file_data in data:
            files.append(file.File.from_json(file_data, self))
        return files

    @property
    def files(self):
        return self.files_in_dir('/')

    def add_file(self, title: str, data: bytes, author: str = '', _license: str = "unknown", fp: str = '/'):
        # Perhaps this method should take in a File object instead of title/data/author etc

        self.rq.post("https://vle.kegs.org.uk/repository/repository_ajax.php",
                     params={"action": "upload"},
                     data={
                              "sesskey": self.sesskey,
                              "repo_id": 3,  # I'm not sure if it has to be 3

                              "title": title,
                              "author": author,
                              "license": _license,

                              "clientid": self.file_client_id,
                              "itemid": self.file_item_id,
                              "savepath": fp
                          },
                     files={"repo_upload_file": data})

        # Save changes
        self.file_save_changes()

    def file_save_changes(self):
        self.rq.post("https://vle.kegs.org.uk/user/files.php",
                     data={"returnurl": "https://vle.kegs.org.uk/user/files.php",

                                "sesskey": self.sesskey,
                                "files_filemanager": self.file_item_id,
                                "_qf__user_files_form": 1,
                                "submitbutton": "Save changes"})

    @property
    def file_zip(self):
        """
        Returns bytes of your files as a zip archive
        """
        url = self.rq.post("https://vle.kegs.org.uk/repository/draftfiles_ajax.php",
                           params={"action": "downloaddir"},
                           data={
                                    "sesskey": self.sesskey,
                                    "client_id": self.file_client_id,
                                    "filepath": '/',
                                    "itemid": self.file_item_id
                                }).json()["fileurl"]

        return self.rq.get(url).content


# --- * ---

def login(username: str, password: str):
    session = requests.Session()
    session.headers = commons.headers.copy()

    response = session.get("https://vle.kegs.org.uk/login/index.php")

    soup = BeautifulSoup(response.text, "html.parser")
    login_token = soup.find("input", {"name": "logintoken"})["value"]

    session.post("https://vle.kegs.org.uk/login/index.php",
                 data={"logintoken": login_token,
                       "anchor": None,
                       "username": username,
                       "password": password
                       })

    return Session(session)


def login_by_moodle(moodle_cookie: str):
    session = requests.Session()
    session.cookies.set("MoodleSession", moodle_cookie)

    return Session(session)
