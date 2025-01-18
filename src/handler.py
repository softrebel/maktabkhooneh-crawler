import httpx
from src._core.utils import (
    save_cookies,
    load_cookies,
    get_hash,
    extract_arc_js,
)
import logging
from src._core.schemas import LoginResponse, UserInfo


class MaktabkhoonehCrawler:
    name: str = "Maktabkhooneh"
    AUTH_API_URL: str = "https://maktabkhooneh.org/api/v1/auth"
    COURSE_API_URL: str = "https://maktabkhooneh.org/api/v1/courses"

    def __init__(
        self,
        username: str,
        password: str,
        client: httpx.Client | None = None,
        headers: dict | None = None,
        cookies_file: str | None = None,
        save_path: str = "data",
        proxy: str | None = None,
        *args,
        **kwargs,
    ):
        self.username: str = username
        self.password: str = password
        self.user_info: UserInfo | None = None
        self._client: httpx.Client | None = client
        self.headers: dict | None = headers or {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "cookie": "_gcl_au=1.1.1308024598.1737195183; analytics_token=3f57f4d8-7a39-f9c9-9d2a-fc3d95841c42; analytics_session_token=08941ace-5fea-453c-faa8-a7c22d8bc3f7; yektanet_session_last_activity=1/18/2025; _yngt_iframe=1; _ga=GA1.1.920167623.1737195183; _yngt=667edd59-ed92-4160-8d71-2568681a946c; _clck=1e7jteb%7C2%7Cfso%7C0%7C1844; _clsk=1wfctg2%7C1737195185820%7C1%7C1%7Cd.clarity.ms%2Fcollect; ribbon_expire=94; csrftoken=PnYeHUspterdSbgZRtwxDNU09rroqbzQIjJ2sQ1YYQGM71Z2AEWdMWCFSQK1XwFp; beta_tester_expiration=triceratops; _ga_53QNTVNLXS=GS1.1.1737195183.1.0.1737195210.33.0.2033333126",
            "origin": "https://maktabkhooneh.org",
            "priority": "u=1, i",
            "referer": "https://maktabkhooneh.org/",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "x-csrftoken": "v9UrAFRfZjcbrxOsFssTwcp3lPExJkQDo5FflBqOuVrKGnxvoDSzFl7I4eXagFWc",
            "x-requested-with": "XMLHttpRequest",
        }

        self.cookies_file: str = cookies_file or f"{self.name}.cookies"

        self.paginator_xpath = '//div[@class="paginator"]/ul/li[last()-1]/a/text()'  # xpath to get the last page number

        self.save_path = save_path
        self._crawled_links: list[str] = []

        self.proxy = proxy

        super().__init__(*args, **kwargs)

    @property
    def crawled_links(self) -> list[str]:
        return self._crawled_links

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(follow_redirects=True, proxy=self.proxy)
        return self._client

    @client.setter
    def client(self, value: httpx.Client):
        self._client = value

    def init_cookies(self):
        load_cookies(self.client, self.cookies_file)

    def request(
        self,
        method: str = "GET",
        url: str = "",
        headers: dict = {},
        params: dict | None = None,
        data: dict | None = None,
        files: list | None = None,
    ):
        for i in range(3):
            try:
                response = self.client.request(
                    method, url, headers=headers, params=params, data=data, files=files
                )
            except Exception as e:
                print(f"Error in url {url}")
                print(e)
                continue
        response.raise_for_status()
        return response

    def request_with_bypass_cdn(
        self,
        method: str = "GET",
        url: str = "",
        headers: dict = {},
        params: dict = {},
        data: dict = {},
    ):
        response = self.request(
            method=method, url=url, headers=headers, params=params, data=data
        )
        content = response.text

        if "redirect__captcha" in content:
            hash = extract_arc_js(content)
            if not hash:
                logging.error("hash error")
                return None
            # self.headers["cookie"] += f"__arcsjs={hash};"
            # headers = {**headers, "cookie": f"__arcsjs={hash};"}
            self.client.cookies.set("__arcsjs", hash)
            headers = self.headers
            response = self.request(
                method=method, url=url, headers=headers, params=params, data=data
            )
        if "error-section__title" in content:
            hash = get_hash(content)
            if not hash:
                logging.error("hash error")
                return None
            # self.headers["cookie"] += f"__arcsjs={hash};"
            self.client.cookies.set("__arcsjs", hash)
            # headers = {**headers, "cookie": f"__arcsjs={hash};"}
            headers = self.headers
            response = self.request(
                method=method, url=url, headers=headers, params=params, data=data
            )

        return response

    # other methods and attributes

    def login(self) -> UserInfo | None:
        url = f"{self.AUTH_API_URL}/check-active-user"
        payload = {"tessera": self.username, "g-recaptcha-response": "recaptcha-token"}
        response = self.client.request("POST", url, headers=self.headers, data=payload)
        response.raise_for_status()

        res = LoginResponse(**response.json())
        match res.message:
            case "get-pass":
                logging.info("success verify user")
            case "get-token":
                logging.error("user not exist. You must sign up first.")
                raise Exception(res.message)
            case "invalid-format":
                logging.error("Username is in ivalid format")
                raise Exception(res.message)
            case _:
                raise Exception(response.message)

        url = f"{self.AUTH_API_URL}/login-authentication"

        payload = {
            "csrfmiddlewaretoken": "wqau8ntdgDJtafOrHveANdwf17VO0NRwPa7VjxLra4LkxkaI4sTFLOIeCiOVqi5j",
            "tessera": self.username,
            "hidden_username": self.username,
            "password": self.password,
            "g-recaptcha-response": "recaptcha-token",
        }

        response = self.client.request("POST", url, headers=self.headers, data=payload)
        response.raise_for_status()
        res = LoginResponse(**response.json())

        match res.message:
            case "logined":
                self.user_info = UserInfo(**response.json())
            case _:
                logging.error(f"Error on login with password: {response.text}")
                raise Exception(res.message)
        save_cookies(self.client, self.cookies_file)
        return self.user_info

    def __del__(self):
        del self
