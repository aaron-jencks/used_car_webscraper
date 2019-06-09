from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

from display_util.string_display_util import print_exception


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def simple_get(url: str):
    """Retrieves the contents of a given url"""

    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return BeautifulSoup(resp.content, 'html.parser')
            else:
                return None
    except RequestException as e:
        print_exception()
