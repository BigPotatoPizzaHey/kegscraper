"""
Session class and login/login by moodle function
"""
from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

from . import file, user, forum, blog
from ..util import commons


class Session:
    """
    Represents a login session
    """

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
        """Get the sesskey query parameter used in various functions. Webscraped from JS..."""
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

    def connect_notifications(self, *, limit: int = 20, offset: int = 0, user_id: int = None) -> tuple[list, int]:
        if user_id is None:
            user_id = self.user_id

        data: dict = self.rq.post("https://vle.kegs.org.uk/lib/ajax/service.php",
                                  params={
                                      "sesskey": self.sesskey,
                                      "info": "message_popup_get_popup_notifications"
                                  },
                                  json=[{"index": 0,  # idk what this is for
                                         "methodname": "message_popup_get_popup_notifications",
                                         "args": {
                                             "limit": limit,
                                             "offset": offset,
                                             "useridto": str(user_id)}
                                         }]
                                  ).json()["data"]


        return data["notifications"], data["unreadcount"]

    @property
    def file_client_id(self):
        """Get the client id value used for file management"""
        if self._file_client_id is None:
            response = self.rq.get("https://vle.kegs.org.uk/user/files.php")
            soup = BeautifulSoup(response.text, "html.parser")

            for div in soup.find_all("div", {"class": "filemanager w-100 fm-loading"}):
                self._file_client_id = div.attrs["id"].split("filemanager-")[1]

        return self._file_client_id

    @property
    def connected_user(self) -> user.User:
        """Fetch the connected user to this session"""
        if not self._user:
            self._user = self.connect_user(self.user_id)

        return self._user

    @property
    def file_item_id(self):
        """Fetch the item id value used for file management"""
        if self._file_item_id is None:
            response = self.rq.get("https://vle.kegs.org.uk/user/files.php")
            soup = BeautifulSoup(response.text, "html.parser")
            self._file_item_id = soup.find("input", {"id": "id_files_filemanager"}).attrs.get("value")

        return self._file_item_id

    @property
    def username(self):
        """Fetch the connected user's username"""
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
        """Fetch the connected user's user id"""
        if self._user_id is None:
            response = self.rq.get("https://vle.kegs.org.uk/")
            soup = BeautifulSoup(response.text, "html.parser")

            url = soup.find("a", {"title": "View profile"}) \
                .attrs["href"]

            parsed = parse_qs(urlparse(url).query)
            self._user_id = int(parsed.get("id")[0])

        return self._user_id

    def assert_login(self):
        """Raise an error if there is no connected user"""
        assert self.username

    # --- Connecting ---
    def connect_user(self, _id: int) -> user.User:
        """Get a user by ID and attach this session object to it"""
        ret = user.User(_id, _session=self)
        ret.update_from_id()
        return ret

    def connect_partial_user(self, **kwargs):
        """
        Connect to a user with given kwargs without any updating
        """
        return user.User(_session=self, **kwargs)

    def connect_forum(self, _id: int) -> forum.Forum:
        """Get a forum by ID and attach this session object to it"""
        ret = forum.Forum(_id, _session=self)
        ret.update_by_id()
        return ret

    # --- Private Files ---
    def _file_data(self, fp: str) -> dict:
        """Fetch the JSON response for private files in a given directory"""

        # Believe or not, KegsNet does actually have some JSON endpoints!
        return self.rq.post("https://vle.kegs.org.uk/repository/draftfiles_ajax.php",
                            params={"action": "list"},
                            data={
                                "sesskey": self.sesskey,

                                "clientid": self.file_client_id,
                                "itemid": self.file_item_id,
                                "filepath": fp
                            }).json()

    def files_in_dir(self, fp: str) -> list[file.File]:
        """Fetch files in a given directory"""
        data = self._file_data(fp)["list"]
        files = []
        for file_data in data:
            files.append(file.File.from_json(file_data, self))
        return files

    @property
    def files(self):
        """Fetch the files in the root directory"""
        return self.files_in_dir('/')

    def add_file(self, title: str, data: bytes, author: str = '', _license: str = "unknown", fp: str = '/',
                 save_changes: bool = True):
        """
        Make a POST request to add a new file to the given filepath
        :param title: file title
        :param data: file content (bytes)
        :param author: Author metadata. Defaults to ''
        :param _license: Given license. Defaults to 'unknown'
        :param fp: Directory path to add the file. Defaults to the root directory
        :param save_changes: Whether to save the change. Defaults to True
        """
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
        if save_changes:
            self.file_save_changes()

    def file_save_changes(self):
        """
        Tell kegsnet to save our changes to our files
        """
        self.rq.post("https://vle.kegs.org.uk/user/files.php",
                     data={"returnurl": "https://vle.kegs.org.uk/user/files.php",

                           "sesskey": self.sesskey,
                           "files_filemanager": self.file_item_id,
                           "_qf__user_files_form": 1,
                           "submitbutton": "Save changes"})

    @property
    def file_zip(self) -> bytes:
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

    # --- Blogs ---
    def _find_blog_entires(self, soup: BeautifulSoup) -> list[blog.Entry]:
        entries = []
        for div in soup.find("div", {"role": "main"}).find_all("div"):
            raw_id = div.attrs.get("id", '')

            if re.match(r"b\d*", raw_id):
                entries.append(blog.Entry(_session=self))
                entries[-1].update_from_div(div)

        return entries

    def connect_user_blog_entries(self, userid: int = None, *, limit: int = 10, offset: int = 0) -> list[blog.Entry]:
        if userid is None:
            userid = self.user_id

        entries = []
        for page, _ in zip(*commons.generate_page_range(limit, offset, 10, 0)):
            text = self.rq.get("https://vle.kegs.org.uk/blog/index.php",
                               params={
                                   "blogpage": page,
                                   "userid": userid
                               }).text
            soup = BeautifulSoup(text, "html.parser")
            entries += self._find_blog_entires(soup)

        return entries

    def connect_site_blog_entries(self, *, limit: int = 10, offset: int = 0) -> list[blog.Entry]:
        entries = []
        for page, _ in zip(*commons.generate_page_range(limit, offset, 10, 0)):
            text = self.rq.get("https://vle.kegs.org.uk/blog/index.php",
                               params={
                                   "blogpage": page
                               }).text
            soup = BeautifulSoup(text, "html.parser")
            entries += self._find_blog_entires(soup)

        return entries

    def connect_blog_entry_by_id(self, _id: int):
        entry = blog.Entry(id=_id, _session=self)
        entry.update_from_id()
        return entry


# --- * ---

def login(username: str, password: str) -> Session:
    """
    Login to kegsnet with a username and password
    :param username: Your username. Same as your email without '@kegs.org.uk'
    :param password: Your email password
    :return: a new session
    """

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


def login_by_moodle(moodle_cookie: str) -> Session:
    """
    Login to kegsnet with just a moodle cookie (basically a session id)
    :param moodle_cookie: The MoodleSession cookie (see in the application/storage tab of your browser devtools when you log in)
    :return: A new session
    """
    session = requests.Session()
    session.cookies.set("MoodleSession", moodle_cookie)

    return Session(session)
