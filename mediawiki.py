import requests
import time
from datetime import datetime
from email.utils import parsedate_to_datetime
from tenacity import retry, retry_if_result, stop_after_attempt

def is_none_p(value):
    """Return True if value is None"""
    return value is None

def get_retry_after_delay(response: requests.Response) -> int:
    """
    Parses the Retry-After header from an HTTP response and returns the
    delay in seconds.
    """
    retry_after = response.headers.get("Retry-After")
    if not retry_after:
        return 0

    try:
        # Attempt to parse as an integer (delay in seconds)
        delay_seconds = int(retry_after)
        return delay_seconds
    except ValueError:
        # If not an integer, attempt to parse as an HTTP date
        try:
            retry_date = parsedate_to_datetime(retry_after)
            now = datetime.now(retry_date.tzinfo)
            delay_seconds = (retry_date - now).total_seconds()
            return max(0, int(delay_seconds))
        except (ValueError, TypeError):
            raise

def init_session():
    # https://wikitech.wikimedia.org/wiki/Robot_policy
    global session
    session = requests.Session()
    headers = {
        "User-Agent": f"User-Agent: FcitxZhwikiDictBot/1.0 (https://github.com/felixonmars/fcitx5-pinyin-zhwiki) python-requests/{requests.__version__}",
        "Accept-Encoding": "gzip, deflate, br, zstd",
    }
    session.headers.update(headers)

@retry(stop=stop_after_attempt(10), retry=retry_if_result(is_none_p))
def do_request(url: str, params=None) -> requests.Response:
    r = session.get(url, params=params)
    if r.status_code == 200:
        return r
    elif r.status_code == 429:
        delay = get_retry_after_delay(r)
        time.sleep(delay)
        return None
    else:
        r.raise_for_status()
        return None
