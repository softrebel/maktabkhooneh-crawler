import pickle
import lxml.html
from lxml.html import Element
import re
import execjs
import httpx

CDN_REGEX: str = r"<\/script><script type=\"text\/javascript\">(var.+\n)"


def send_hash(hash: str) -> str:
    url = "https://api.pydia.ir/eval-hash"
    headers = {"Content-Type": "application/json"}
    payload = {"content": hash}
    response = httpx.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def get_hash(content: str) -> str:
    func = "(function() {return hash})();"
    matches = re.findall(CDN_REGEX, content)
    if len(matches) == 0:
        return None
    js = matches[0]

    # js_code = f"{js}\n{func}"
    # res = execjs.exec_(js_code)
    response = send_hash(js)
    res = response["hash"]
    return res


def extract_arc_js(content: str):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(content, "html.parser")
    script_tags = soup.find_all("script")
    tag = next(x for x in script_tags if "window.AR_SiteKey =" in x.text)
    hash = tag.text.split("window.AR_SiteKey = '")[-1].split("';")[0]
    return hash


def save_cookies(client, filepath):
    # Convert cookies to a dictionary
    cookies_dict = {cookie.name: cookie.value for cookie in client.cookies.jar}
    with open(filepath, "wb") as file:
        pickle.dump(cookies_dict, file)


# Load cookies from a file
def load_cookies(client, filepath):
    with open(filepath, "rb") as file:
        cookies_dict = pickle.load(file)
    # Load cookies into the client
    for name, value in cookies_dict.items():
        client.cookies.set(name, value)


def get_xpath_first_element(node: Element, xpath: str) -> str | None:
    tags = node.xpath(xpath)
    if tags and len(tags) > 0:
        output = tags[0]
        if isinstance(output, str):
            return output.strip()
        return output


def remove_extra_spaces(text: str) -> str:
    return " ".join(text.split())
