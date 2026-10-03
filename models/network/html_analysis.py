import re

from bs4 import BeautifulSoup, element

from models.network.html_parser import fetch_absolute_links, fetch_js
from models.network.requests import fetch_page_resource
from models.network.whois import query_exists, query_url
from models.risk.classifiers import classify_domain_identity, classify_url_structure
from models.risk_context import RiskContext
from models.url.parsing import contains_ip_address, extract_hostname
from views.style import RED, YELLOW


def remove_js_from_html(soup: BeautifulSoup) -> str:
    """
    Removes all JS scripts embedded in an HTML page.

    Args:
        soup: Parsed HTML to be inspected.

    Returns:
        str: HTML without executeable JavaScript.
    """
    for data in soup(['script']):
        data.decompose()
   
    return ' '.join(soup.stripped_strings)


def fetch_links_to_external_domains(url: str, soup: BeautifulSoup) -> set:
    """
    Retrieves all links listed on the HTML page for the given URL that point to an external domain. 

    Args:
        url: The URL to be parsed.
        soup: Parsed HTML to be inspected.
    
    Returns:
        set: List of external domains associated with the URL.
    """
    origin_hostname = extract_hostname(url)
    abs_links = fetch_absolute_links(soup)
    hrefs = [
        link.get('href') for link in abs_links
    ]
    external_domains = set()

    for href in hrefs:
        href_hostname = extract_hostname(href, strict=True)

        if not href_hostname:
            continue

        if href_hostname == origin_hostname:
            continue

        if origin_hostname == href_hostname:
            continue
        
        if href_hostname not in external_domains:
            external_domains.add(href_hostname)

    return external_domains


def href_text_mismatch(anchor: element.Tag) -> bool:
    """
    Compares the URLs of hyperlinked text and it's actual destination 
    according to the `href` attribute to determine if a hyperlink is 
    deceiving.

    Args:
        anchor: The HTML element to be parsed.

    Returns:
        bool: True, if a mismatch exists. Otherwise, False.
    """
    text = anchor.text
    href = anchor.get('href')
    
    text_hostname = extract_hostname(text, strict=True)
    href_hostname = extract_hostname(href, strict=True)

    # Case 1: Text looks like a URL but differs from href
    if (text_hostname and href_hostname) and (text_hostname != href_hostname):
        return True
    
    # Case 2: IP-based deception
    if contains_ip_address(href) and text != href:
        return True
    
    return False


def analyze_html(url: str, soup: BeautifulSoup, ctx: RiskContext) -> dict:
    """
    Parses HTML for the presence of JS scripts, links to external domains, 
    and any misleading hyperlinks.

    Args:
        url: The URL to be parsed.
        soup: Parsed HTML to be inspected.

    Returns:
        dict: Collection of key-value pairs representing HTML characteristics.
    """
    result = {}

    # Scripts
    js_scripts = fetch_js(soup)
    result["script_count"] = len(js_scripts) if js_scripts else 0

    if result["script_count"] > 10 and ctx:
        ctx.add("many_scripts")

    # External domains
    external_domains = fetch_links_to_external_domains(url, soup)
    result["external_domains"] = external_domains

    if external_domains and ctx:
        ctx.add("external_links")

    # Mismatched domains
    num_mismatches = sum(
        1 for hyperlink in fetch_absolute_links(soup)
        if href_text_mismatch(hyperlink)
    )
    result["mismatch_count"] = num_mismatches

    if num_mismatches > 0 and ctx:
        ctx.add("mismatched_links")

    return result


def has_sus_domain_info(link: str) -> bool:
    # Prevents spam of time out errors
    try:
        query = query_url(link)
    except Exception:
        return False

    if not query or not query_exists(link, query):
        return False

    domain_risk = classify_domain_identity(query)

    colors = [
        domain_risk['age']['color'],
        domain_risk['exp_date']['color'],
        domain_risk['domain_reg']['color']
    ]

    return any(color in (RED, YELLOW) for color in colors)


def has_sus_url_struct(link: str) -> bool:
    url_risk = classify_url_structure(link)
    rendered = url_risk["url_structure"]["rendered_url"]
    return any(color in rendered for color in (RED, YELLOW))


def analyze_external_domains(external_domains: list[str]):
    sus_links = set()
    
    for dom in external_domains:
        try:
            if has_sus_url_struct(dom):       # Limits number of Whois queries to suspicious-looking URLs
                if has_sus_domain_info(dom): 
                    sus_links.add(dom)
        except Exception:
            continue

    return list(sus_links)


def contains_hidden_elements(txt: str) -> bool:
    """
    Checks if HTML/CSS contains invisible elements.

    Args:
        txt: The text to be inspected.

    Return:
        bool: True, if a text contains "opacity: 0", "display: none", or "visibility: hidden".
        Otherwise, False.
    """
    patterns = [
        r"opacity:\s*0\b",
        r"display:\s*none\b",
        r"visibility:\s*hidden\b",
    ]

    # return True if match else False
    return any(re.search(pattern, txt) for pattern in patterns)


def contains_sus_hidden_elem(txt: str, ctx: RiskContext):
    hidden = contains_hidden_elements(txt)
    has_abs_pos = re.search(r"position:\s*(absolute|fixed)", txt)
    large_area = re.search(r"(width|height):\s*(100%|100vh|100vw)", txt)
    sus_hidden_elem_found = hidden and (has_abs_pos or large_area)

    if sus_hidden_elem_found and ctx:
        ctx.add("hidden_elements")
    
    return sus_hidden_elem_found


def contains_overlay(txt: str, ctx: RiskContext) -> bool:
    """
    Checks if HTML/CSS text contains overlays.

    Args:
        txt: The text to be inspected.
    
    Returns:
        bool: True, if a text contains both "position: absolute" and "z-index: 99".
        Otherwise, False.
    """
    has_abs_pos = re.search(r"position:\s*(absolute|fixed)", txt)
    has_high_z = re.search(r"z-index:\s*(\d{2,})", txt)
    overlay_found = bool(has_abs_pos and has_high_z)
    
    if overlay_found and ctx:
        ctx.add("overlay_detected")

    return overlay_found


def analyze_css(html: str, stylesheet_links: list[str], ctx: RiskContext) -> dict:
    """
    Parses HTML and CSS texts for the presence of CSS that can be used to 
    make invisible elements and overlays.

    Args:
        html: The text to be parsed.
        stylesheet_links: Links to external CSS files to be inspected.

    Returns:
        dict: Collection of key-value pairs representing CSS characteristics.
    """
    result = {}
    parseable_txt = []

    # Adds string of HTML code to be parsed for internal & inline CSS
    if html:
        parseable_txt.append(html)

    # Adds strings of external CSS code to be parsed 
    for link in stylesheet_links:
        pg_resource = fetch_page_resource(link)

        # Adds text to list if fetch was successful
        if pg_resource:
            parseable_txt.append(pg_resource)
    
    hidden_elements_found = False
    overlay_found = False

    # Early return
    if len(parseable_txt) == 0:
        result["hidden_elements_present"] = hidden_elements_found
        result["overlays_present"] = overlay_found
        return result

    for txt in parseable_txt:
        if hidden_elements_found and overlay_found:
            break
        if contains_sus_hidden_elem(txt, ctx):
            hidden_elements_found = True
        if contains_overlay(txt, ctx):
            overlay_found = True

    result["hidden_elements_present"] = hidden_elements_found
    result["overlays_present"] = overlay_found
    
    return result
