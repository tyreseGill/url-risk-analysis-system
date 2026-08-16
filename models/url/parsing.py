from urllib.parse import urlparse, parse_qs
from models.risk_context import RiskContext
import re
import tldextract


SUSPICIOUS_KEYWORDS = ["redirect", "redirect_url", "return", "return_url",
                        "next", "continue", "url", "target",
                        "login", "signin", "auth", "token",
                        "session", "sessionid", "sid", "password",
                        "passwd", "pwd", "verify", "confirm",
                        "secure", "script", "cmd", "exec"]

SAFE_TLDS = ["com", "edu", "gov", "org", "net", "co"]

URL_SHORTENERS = ["bit.ly", "tinyurl.com", "t.co"]


# Extraction functions

def extract_url_components(url: str):
    """Retrieves the subdomain, domain, and top-level domain of a URL."""
    ext = tldextract.extract(url)
    subdomain = ext.subdomain
    domain = ext.domain
    suffix = ext.suffix
    return subdomain, domain, suffix


def extract_hostname(url: str, strict: bool = False) -> str | None:
    """Retrieves the hostname from a URL."""
    sub, dom, tld = extract_url_components(url)

    if strict:
        hostname = f"{dom}.{tld}"
    else:
        hostname = f"{sub}.{dom}.{tld}" if sub else f"{dom}.{tld}"

    # If top-level domain couldn't be extracted, must be an IP address
    if not tld:
        ip_addresses = fetch_ip_addresses(url)

        if ip_addresses:
            start, end = ip_addresses[0]
            return url[start:end]

    # Valid hostnames must consist of at least a domain and top-level domain
    if hostname.startswith(".") or hostname.endswith("."):
        return None
    
    return hostname


def extract_suspicious_params(url: str):
    """Retrieves list of URL parameters that match phishing-related keywords."""
    url_params = [ url[start:end] for start, end in fetch_url_params(url) ]
    suspicious_params = [ param for param in url_params if param in SUSPICIOUS_KEYWORDS ]
    return suspicious_params


# Span Location

def get_span_locations(pattern: re.Pattern, target_str: str, include_group: bool=False) -> list:
    """
    Retrieves the index spans for all regex matches within a target string.

    Args:
        pattern: Compiled regular expression.
        target_str: String to be parsed for matches.
        include_group: Flag to determine whether to return matched group text

    Returns:
        list: Either a list of (start, end) or ((start, end), group) tuples based on value of include_group.
    """
    matches = []
    list_matches = list(pattern.finditer(target_str))

    if include_group:
        for match in list_matches:
            matches.append(
                (match.span(), match.group())
            )
    else:
        for match in list_matches:
            matches.append(match.span())
    
    return matches


def get_span_locations_for_list(list_to_parse: list, target_str: str) -> list:
    """
    Retrieves the first index span for a provided of patterns to match within a target string.

    Args:
        list_to_parse: List of strings to search for.
        target_str: String to be searched.

    Returns:
        list: List of (start, end) spans for each match.
    """
    matches = []
    for match in list_to_parse:
        pattern = re.compile(fr"{match}")
        match_loc = get_span_locations(pattern, target_str)
        if match_loc:
            matches.append(match_loc[0])
    
    return matches
    

# Span-returning pattern matching functions

def fetch_suspicious_keywords(url: str) -> list:
    """
    Locates any suspicious keywords within URL subdomains.

    Args:
        url: The full URL to be analyze.

    Returns:
        list: List of (start, end) index spans in the URL where suspicious keyword exists.
    """
    subdomain, _, _ = extract_url_components(url)
    spans = []

    if not subdomain:
        return []

    for sub in fetch_subdomains(subdomain):
        matches = get_span_locations_for_list(SUSPICIOUS_KEYWORDS, sub)
        subdomain_idx = url.find(sub)
        if subdomain_idx == -1:
            continue
        for start, end in matches:
            start += subdomain_idx
            end += subdomain_idx
            spans.append(
                (start, end)
            )

    return spans


def fetch_uncommon_tlds(url: str) -> list:
    """
    Locates any uncommon top-level domains within a URL.

    Args:
        url: URL to inspect.

    Returns:
        list: Span locations for uncommon TLDs.
    """
    _, _, tld = extract_url_components(url)

    if not tld:
        return []
    if tld in SAFE_TLDS:
        return []
    
    pattern = re.compile(rf"{tld}")
    return get_span_locations(pattern, url) or []


def fetch_digits(url: str) -> list:
    """
    Locates any digits within a URL, excluding those that are part of an IP address.

    Args:
        url: URL to inspect.

    Returns:
        list: Span locations for individual digits.
    """
    pattern = re.compile(r"\d")
    matches = get_span_locations(pattern, url)

    if contains_ip_address(url):
        ip_address_spans = fetch_ip_addresses(url)
    
        for span in ip_address_spans:
            start, end = span
            matches = [ m for m in matches if not m[0] >= start and m[1] < end ]

    return matches


def fetch_special_chars(url: str) -> list:
    """Returns span locations for all special characters within a URL."""
    matches = [
        (pos, pos + 1) for (pos, char) in enumerate(url)
        if ord(char) > 127
    ]

    return matches


def fetch_url_params(url: str) -> list:
    """Returns span locations for any parameters within a URL."""
    # Gets URL parameters
    parsed_url = urlparse(url)
    params = list(
        parse_qs(parsed_url.query).keys()
    )

    return get_span_locations_for_list(params, url)


def fetch_ip_addresses(url: str) -> list:
    """Returns span locations for IPv4 addresses within a URL."""
    pattern = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    return get_span_locations(pattern, url)


def fetch_subdomains(subdomain: str) -> list:
    """Returns span locations for all subdomains in URL."""
    subdomains = subdomain.split(".") if subdomain else []
    return subdomains


def fetch_schemes(url: str) -> list:
    """Returns span locations for all URL schemes (http/https), if any."""
    pattern = re.compile(r"https?://")
    return get_span_locations(pattern, url, include_group=True)


def fetch_hyphens(url: str) -> list:
    """Returns span locations for all "-" symbols in URL."""
    pattern = re.compile(r"-")
    return get_span_locations(pattern, url)


def fetch_at_symbols(url: str) -> list:
    """Returns span locations for all "@" symbols in URL."""
    pattern = re.compile(r"@")
    return get_span_locations(pattern, url)


# Boolean-returning pattern matching functions

def contains_suspicious_keywords(list_strings: list, ctx: RiskContext = None) -> bool:
    """Determines if a list contains any suspicious keywords associated with phishing."""
    if not list_strings:
        return False
    sus_keywords_found = any(str.lower() in SUSPICIOUS_KEYWORDS for str in list_strings)
    if sus_keywords_found and ctx:
        ctx.add("sus_keywords")
    return sus_keywords_found


def contains_scheme(target_str: str) -> bool:
    """Determines if a URL specifies a scheme (http/https)."""
    pattern = re.compile(r"https?://")
    scheme_found = bool(
        list(pattern.finditer(target_str))
    )
    return scheme_found


def contains_multiple_subdomains(subdomain: str, ctx: RiskContext = None) -> bool:
    """Determines if a subdomain consists of more than one subdomain."""
    subdomains = fetch_subdomains(subdomain)
    multiple_subdomains_found = len(subdomains) > 1
    if multiple_subdomains_found and ctx:
        ctx.add("multiple_subdomains")
    return multiple_subdomains_found
    

def contains_ip_address(url: str, ctx: RiskContext = None) -> bool:
    """Determines if a URL contains an IPv4 address."""
    pattern = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    ip_address_found = bool(pattern.search(url))
    if ip_address_found and ctx:
        ctx.add("ip_address")
    return ip_address_found


def contains_at_symbols(target_str: str, ctx: RiskContext = None) -> bool:
    """Determines if a URL contains any "@" symbols."""
    at_symbols_found = "@" in target_str
    if at_symbols_found and ctx:
        ctx.add("at_symbol_in_url")
    return True if "@" in target_str else False


def contains_hyphens(target_str: str, ctx: RiskContext = None) -> bool:
    """Determines if a URL contains any "-" symbols."""
    hyphens_found = "-" in target_str
    if hyphens_found and ctx:
        ctx.add("hyphens_in_url")
    return hyphens_found


def contains_digits(target_str: str, ctx: RiskContext = None) -> bool:
    """Determines if a URL contains any digits."""
    digits_found = any(char.isdigit() for char in target_str) and not contains_ip_address(target_str)
    if digits_found and ctx:
        ctx.add("digits_in_url")
    return digits_found


def contains_special_chars(target_str: str, ctx: RiskContext = None) -> bool:
    """Determines if a URL contains any special characters."""
    special_char_found = any(ord(char) > 127 for char in target_str)
    if special_char_found and ctx:
        ctx.add("special_chars")


def contains_uncommon_tld(url: str, ctx: RiskContext = None) -> bool:
    """Determines if the top-level domain of a URL is common or not."""
    _, _, tld = extract_url_components(url)
    uncommon_tld_found = tld not in SAFE_TLDS
    if uncommon_tld_found and ctx:
        ctx.add("uncommon_tld")
    return uncommon_tld_found


def is_url_long(url: str, ctx: RiskContext = None) -> bool:
    """Determines if a URL is unusually long according to SEO benchmarks."""
    URL_STANDARD_LENGTH = 75
    is_long = len(url) > URL_STANDARD_LENGTH
    if is_long and ctx:
        ctx.add("long_url")
    return is_long


def is_url_shortener(registered_domain: str, ctx: RiskContext = None) -> bool:
    """Determines if a URL is associated with a common URL-shorter service."""
    is_shortner = registered_domain in URL_SHORTENERS
    if is_shortner and ctx:
        ctx.add("url_shortner")
    return is_shortner


def is_tld_common(top_level_domain: str) -> bool:
    """Determines if a top-level domain is common."""
    return True if top_level_domain in SAFE_TLDS else False
