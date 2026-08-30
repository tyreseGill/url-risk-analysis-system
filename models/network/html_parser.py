from bs4 import BeautifulSoup


def fetch_external_css(soup: BeautifulSoup) -> list:
    """
    Retrieves the links to all CSS files referenced and used to style a given URL.

    Args:
        soup: Parsed HTML to be inspected.

    Returns:
        list: List of links to CSS files.
    """
    stylesheet_tags = soup.find_all('link', rel="stylesheet")
    stylesheet_links = [
        tag.get("href") for tag in stylesheet_tags if tag.get("href")
    ]
    return stylesheet_links


def fetch_internal_css(soup: BeautifulSoup) -> list:
    styles = [
        style.get_text() for style in soup.find_all("style")
    ]
    inline_styles = [
        tag.get("style") for tag in soup.find_all(style=True)
    ]
    return styles + inline_styles


def fetch_js(soup: BeautifulSoup):
    """
    Retrieves all JS scripts embedded in an HTML page.

    Args:
        soup: Parsed HTML to be inspected.

    Returns:
        _SomeTags: List of script elements.
    """
    scripts = soup.find_all('script')
    return scripts


def fetch_absolute_links(soup: BeautifulSoup) -> list:
    """
    Retrieves all absolute links listed on the HTML page for the given URL.

    Args:
        soup: Parsed HTML to be inspected.

    Returns:
        list: List of absolute links.
    """
    links = soup.find_all('a')
    links = [
        link for link in links
        if link.get('href')                      # Ensures collection of links with a destination URL
        and link.get('href').startswith('http')  # Prevents collection of relative links on same domain
    ]
    return links


def convert_html_to_soup(html_file: str) -> BeautifulSoup:
    """
    Takes in an HTML file, reads it, and obtain a BeautifulSoup object.

    Args:
        html_file (str): The path to the HTML file.

    Returns:
        BeautifulSoup: Parsed HTML.
    """
    with open(html_file, "r") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")
    return soup
