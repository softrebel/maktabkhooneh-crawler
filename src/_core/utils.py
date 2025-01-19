import pickle
from lxml.html import Element
import re
import httpx
from pydantic import BaseModel
import json
from typing import Type, TypeVar
from pydantic import ValidationError
import re


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


def save_model_to_json(model: BaseModel, filename: str, indent: int = 4) -> None:
    """Saves a Pydantic model to a JSON file with UTF-8 encoding and indentation."""
    with open(filename, "w", encoding="utf-8") as f:
        # Option 1: Directly use the model's json() method with indent
        json_string = model.model_dump_json(indent=indent)
        f.write(json_string)


T = TypeVar("T", bound=BaseModel)


def load_model_from_json(model_type: Type[T], filename: str) -> T:
    """Loads a Pydantic model from a JSON file.

    Args:
        model_type: The Pydantic model class (e.g., MyModel).
        filename: The path to the JSON file.

    Returns:
        An instance of the Pydantic model if loading is successful.

    Raises:
        FileNotFoundError: If the JSON file does not exist.
        json.JSONDecodeError: If the JSON file is not valid JSON.
        ValidationError: If the JSON data doesn't match the model.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            json_data = json.load(f)
            model_instance = model_type(**json_data)
            return model_instance

    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found: {filename}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON format in {filename}: {e.msg}", e.doc, e.pos
        )
    except ValidationError as e:
        raise ValidationError(
            f"JSON data does not match the model: {e}", model=model_type
        )


def sanitize_filename(filename, replacement='_'):
    """Replaces or removes characters that are not allowed in filenames, while preserving UTF-8."""
    # # Replace spaces with underscores.
    # filename = re.sub(r'\s+', replacement, filename)

     # Remove or replace problematic characters.
    filename = re.sub(r'[\\/:*?"<>|]', replacement, filename)

    # remove leading and trailing underscores and points
    # filename = filename.strip('_').strip('.')

    # Limit to a maximum length for safety.
    max_length = 255  # Reasonable max for most file systems
    return filename[:max_length]
