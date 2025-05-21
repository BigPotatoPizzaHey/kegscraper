import dateparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from dataclasses import dataclass

from ..util import commons

from . import org


@dataclass
class Session:
    username: str = None

    balance: float = None
    pages: int = None
    jobs: int = None

    trees: float = None
    co2: int = None  # Grams of co2
    energy: float = None  # joules
    since: datetime = None

    pages_graph: list[int] = None  # idx -1 is this week, -2 is last week, etc. (reverse?)

    _organisation: org.Organisation = None

    rq: requests.Session = None

    @property
    def organisation(self):
        if not self._organisation:
            self.update_by_env()

        return self._organisation

    def update_by_env(self):
        response = self.rq.get(f"http://printing.kegs.local:9191/environment/dashboard/{self.username}")

        self.update_by_env_dash_html(BeautifulSoup(response.text, "html.parser"))

    def logout(self):
        self.rq.get("http://printing.kegs.local:9191/app?service=direct/1/UserSummary/$UserBorder.logoutLink")

    def update_from_dashboard(self):
        resp = self.rq.get("http://printing.kegs.local:9191/app?service=page/UserSummary")
        self.update_by_html(BeautifulSoup(resp.text, "html.parser"))

    def _gen_org(self):
        if not self._organisation:
            self._organisation = org.Organisation(sess=self)

    def update_by_env_dash_html(self, soup: BeautifulSoup):
        self._gen_org()

        # maybe scrape sheets (week/month), cost/month + trees/co2/energy

        # graph (canvas) - have to scrape js!
        for script in soup.find_all("script", {"type": "text/javascript"}):
            if script.contents:
                content = script.contents[0]
                find_str = "datasets : ["
                if find_str in content:
                    i = content.find(find_str)
                    content = content[i:]

                    find_str = "data : ["
                    f1 = content.find(find_str)
                    f2 = content[f1 + 8:].find(find_str) + f1 + 8

                    self._organisation.pages_graph = commons.consume_json(content, f1 + 6)  # num. pages
                    self.pages_graph = commons.consume_json(content, f2 + 6)  # num. pages

        for div in (soup.find("div", {"class": "box box50-100 medium"}),
                    soup.find("div", {"class": "box box50-100 darker"})):
            h2 = div.find("h2", {"class": "centered"})

            if h2.text.strip() == "Organization Impact":
                for stat in div.find_all("div", {"class": "env-stats-text"}) + \
                            div.find_all("div", {"class": "centered env-impact"}):
                    stat = stat.text.strip()
                    print(repr(stat))

                    if stat.endswith(" trees"):
                        self._organisation.trees = float(stat.split()[0])
                    elif stat.endswith(" kg of CO2"):
                        self._organisation.co2 = 1000 * int(stat.replace(',', '').split()[0])
                    elif stat.endswith(" bulb hours"):
                        self._organisation.energy = 60 * 60 * 60 * int(stat.replace(',', '').split()[0])
                    elif stat.startswith("Since\n"):
                        self._organisation.since = dateparser.parse(stat[len("Since\n"):])


    def update_by_html(self, soup: BeautifulSoup):
        self.username = soup.find("span", {"id": "username"}).text

        bal_div = soup.find("div", {"class": "widget stat-bal"})
        self.balance = float(bal_div.find("div", {"class": "val"}).text.strip()[1:])  # [1:] is to remove '£'

        pages_div = soup.find("div", {"class": "widget stat-pages"})
        self.pages = int(pages_div.find("div", {"class": "val"}).text)

        jobs_div = soup.find("div", {"class": "widget stat-jobs"})
        self.jobs = int(jobs_div.find("div", {"class": "val"}).text)

        env_div = soup.find("div", {"id": "enviro", "class": "col"})
        env_widget = env_div.find("div", {"class": "widget"})

        for li in env_widget.find_all("li"):
            key = li.get("class")[0]
            val = li.text.strip()

            match key:
                case "trees":
                    self.trees = float(val.split('%')[0]) / 100  # /100 because it's a percentage
                case "co2":
                    self.co2 = int(val.split('g')[0])
                case "energy":
                    val = float(val.split("hours")[0])  # hours running a 60W light bulb
                    val = val * 60 * 60  # seconds spent powering bulb
                    val *= 60  # 60W bulb
                    self.energy = val
                case "since-date":
                    val = val.replace("Since", '').strip()
                    self.since = dateparser.parse(val)


def login(username: str, password: str):
    sess = requests.Session()

    sess.get("http://printing.kegs.local:9191/user")

    sess.headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Length": "302",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "printing.kegs.local:9191",
        "Origin": "http://printing.kegs.local:9191",
        "Referer": "http://printing.kegs.local:9191/app",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    }

    resp = sess.post("http://printing.kegs.local:9191/app",
                     data={
                         "service": "direct/1/Home/$Form",
                         "sp": "S0",
                         "Form0": "$Hidden$0,$Hidden$1,inputUsername,inputPassword,$Submit$0,$PropertySelection",

                         "$Hidden$0": "true",
                         "$Hidden$1": "X",
                         "inputUsername": username,
                         "inputPassword": password,

                         "$Submit$0": "Log in",
                         "$PropertySelection": "en"
                     })

    ret = Session(rq=sess, username=username)
    ret.update_by_html(BeautifulSoup(resp.text, "html.parser"))

    return ret
