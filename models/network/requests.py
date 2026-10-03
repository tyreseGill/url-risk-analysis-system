import requests
from bs4 import BeautifulSoup

from utils.animations import display_load_animation


def supports_https(domain_name: str) -> bool:
    """
    Attempts to connect to HTTPS-supporting site.

    Return:
        bool: True, if HTTPS-connection is established. Otherwise, false.
    """
    try:
        requests.head(f"https://{domain_name}",
                                 timeout=5,
                                 allow_redirects=True)
        return True
    except requests.exceptions.SSLError:
        return False
    except requests.exceptions.ReadTimeout:
        return False


def fetch_page_resource(url: str) -> str | None:
    """
    Attempts to obtain a string copy of HTML/CSS code from the given URL.

    Args:
        url: The URL to retrieve HTML/CSS text from.
    
    Returns:
        str: A string of HTML/CSS text. Otherwise, none.
    """
    def connect():
        try:
            resource = requests.get(url, timeout=5, headers={"User-Agent": "PreviewBot/1.0"})
            return resource.text
        except requests.RequestException:
            return None
    
    # Runs load animation as resource is being fetched
    page_resource = display_load_animation(
        connect,
        "[INFO] Attempting to fetch page resource",
    )

    return page_resource
    

def fetch_page_resource_soup(url: str) -> BeautifulSoup | None:
    """
    Attempts to obtain BeautifulSoup object from URL.
    """
    try:
        html = fetch_page_resource(url)
        soup = BeautifulSoup(html, 'html.parser')
        return soup
    except requests.RequestException:
        return None
