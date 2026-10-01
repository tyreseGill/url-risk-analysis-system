from datetime import datetime as dt, timezone as tz
from models.network.requests import supports_https
from models.network.whois import normalize_expiration_date
from models.risk_context import RiskContext
from models.url.parsing import *
from utils.text_utils import find_literal, find_literals
from views.span import Span, make_spans, collect_spans
from views.style import *
import argparse



DAYS_IN_YEAR = 365
DAYS_IN_MONTH = 30


def classify_risk(params: argparse.Namespace, ctx: RiskContext, query: dict | None = None) -> dict:
    """
    Classifies severity of individual domain attributes.

    Returns:
        dict: Provides risk summary for each domain attribute.
    """
    domain_name = extract_hostname(params.url)

    result = {}

    if params.url_structure:
        url = params.url
        result |= classify_url_structure(url, ctx)

    if params.domain_identity:
        result |= classify_domain_identity(query, ctx)

    if params.dns:
        pass

    if params.transport_security:
        result |= classify_transport_security(domain_name, ctx)
        
    if params.tls:
        pass

    if params.html:
        pass

    return result


def classify_domain_identity(query: dict, ctx: RiskContext):
    valid_domain_flag = is_domain_registration_valid(query)
    creation_date = normalize_expiration_date(query.creation_date)
    exp_date = normalize_expiration_date(query.expiration_date)
    age = dt.now(tz.utc) - creation_date

    age_num, age_unit, age_color = classify_domain_age(age)
    expiration_date_color = classify_expiration_risk(exp_date, age)
    domain_reg_color, domain_reg_status = classify_domain_registration(valid_domain_flag)

    if age_color == RED:
        ctx.add("young_domain")
    if expiration_date_color == RED:
        ctx.add("expires_shortly")
    if domain_reg_color == RED:
        ctx.add("expired_domain")

    return {
        "age": {
            "value": age_num,
            "unit": age_unit,
            "color": age_color
        },
        "exp_date": {
            "color": expiration_date_color
        },
        "domain_reg": {
            "color": domain_reg_color,
            "status": domain_reg_status
        }
    }


def classify_transport_security(domain_name: str, ctx: RiskContext):
    https_supp_color, https_supp_status = classify_https_status(domain_name)

    if https_supp_color == RED:
        ctx.add("no_https")

    return {
        "https_support": {
            "color": https_supp_color,
            "status": https_supp_status
        }
    }


def classify_expiration_date(days: int):
    EXPIRY_OK_DAYS = 30
    EXPIRY_WARN_DAYS = 7

    if days > EXPIRY_OK_DAYS:
        days_colored = highlight_green(days)
    elif days > EXPIRY_WARN_DAYS:
        days_colored = highlight_yellow(days)
    else:
        days_colored = highlight_red(days)

    return days_colored


def classify_domain_age(domain_age: dt) -> tuple:
    """
    Classifies risk of domain age.

    Returns:
        int: Numerical value showcasing age of domain in days/years.
        str: Unit of measurement representing either "days" or "years".
        str: Color indicating level of severity of age.
    """
    domain_age_days = domain_age.days

    # CASE 1: Trusted if domain has been registered for over a year
    if domain_age_days > DAYS_IN_YEAR:
        val = domain_age_days // DAYS_IN_YEAR
        unit = "years"
        color = GREEN
    # CASE 2: Suspicious if domain has been registered for less than a year
    else:
        val = domain_age_days
        unit = "days"
        color = YELLOW if domain_age_days > DAYS_IN_MONTH else RED

    return val, unit, color


def classify_expiration_risk(exp_date: dt, domain_age: dt) -> str:
    """
    Classifies risk based on domain expiration timing relative to age.

    Returns:
        str: Color indicating level of severity of domain's expiration date. 
    """
    days_until_expiration = (exp_date - dt.now(tz.utc)).days

    # Suspicious only if short-lived AND newly registered
    if days_until_expiration < DAYS_IN_YEAR and domain_age.days < DAYS_IN_YEAR:
        return RED

    return GREEN


def classify_domain_registration(valid_domain_flag: bool) -> tuple:
    """
    Outputs status of domain registration.

    Returns:
        str: Color indicating whether a site's domain has expired or not. 
        str: Current status of the site's domain.
    """
    color = GREEN if valid_domain_flag else RED
    status = "Active" if valid_domain_flag else "Expired"
    return color, status


def classify_https_status(domain_name: str) -> tuple:
    """
    Outputs HTTPS status of a provided domain name.

    Returns:
        str: Color indicating whether site is HTTPS-supported or not. 
        str: Current HTTPS status of the site's domain.
    """
    has_https = supports_https(domain_name)
    color = GREEN if has_https else RED
    status = "Yes" if has_https else "No"

    return color, status


def is_domain_registration_valid(query: dict) -> bool:
    """
    Verifies if the domain has not expired and is still valid.

    Returns:
        bool: True if the domain has not yet expired. Otherwise, false.
    """
    # Initializes date variables with global timezone standard
    domain_expiration_date = query.expiration_date
    current_date = dt.now(tz.utc)
    
    domain_expiration_date = normalize_expiration_date(domain_expiration_date)

    # Determines if domain is expired or not
    if domain_expiration_date < current_date:
        return False
    else:
        return True


def detect_url_spans(url: str, ctx: RiskContext) -> list:
    """
    Runs detection phase to aggregate raw Span objects.

    Returns:
        list[Span]: List of Span objects to be processed and resolved of conflicts.
    """
    subdomain, domain, tld = extract_url_components(url)
    sus_params = extract_suspicious_params(url)

    spans = []
    domain_name = f"{domain}.{tld}"

    if contains_scheme(url):
        for (start, end), scheme in fetch_schemes(url):
            color = GREEN if scheme == "https://" else RED
            spans.append(
                Span(start, end, color)
            )

    if is_url_shortener(domain_name):
        start, end = find_literal(url, domain)
        spans.append(
            Span(start, end, RED)
        )

    if contains_suspicious_keywords(sus_params):
        list_spans = find_literals(url, sus_params)
        spans.extend(
            make_spans(list_spans, YELLOW)
        )
    
    if contains_multiple_subdomains(subdomain):
        subdomains = fetch_subdomains(subdomain)
        for subdomain in subdomains:
            start, end = find_literal(url, subdomain)
            spans.append(
                Span(start, end, YELLOW)
            )
    
    domain_checks = {
        fetch_digits: YELLOW,
        fetch_hyphens: YELLOW
    }

    misc_checks = {
        fetch_at_symbols: YELLOW,
        fetch_suspicious_keywords: YELLOW,
        fetch_special_chars: RED,
        fetch_uncommon_tlds: RED,
        fetch_ip_addresses: RED
    }

    spans.extend(
        collect_spans(domain_checks, url, domain)
    )
    spans.extend(
        collect_spans(misc_checks, url)
    )

    return spans


def resolve_spans(spans: Span) -> list:
    """
    Resolves overlap conflicts between spans to prevent corruption of URL during render.

    Returns:
        list[Span]: Processed list of Spans with low-priority, conflicting spans filtered out.
    """
    resolved = []

    PRIORITY = {
        RED: 3,
        YELLOW: 2,
        GREEN: 1
    }

    def overlaps(a: Span, b: Span) -> bool:
        return a.start < b.end and b.start < a.end
    
    # sort spans by start, then by priority in descending order
    spans = sorted(
        spans,
        key=lambda s: (s.start, -PRIORITY[s.color])
    )

    for span in spans:
        # Accepts first span when resolved list empty
        if not resolved:
            resolved.append(span)
            continue

        # Grabs previous resolved span to prevent overlap
        last = resolved[-1] 

        if overlaps(last, span):  # Two spans overlap, one must be chosen
            # Replaces previous resolved span if new span is higher‑priority
            if PRIORITY[span.color] > PRIORITY[last.color]:
                resolved[-1] = span
            # Otherwise, new span is discarded
        else:  # No overlap, prior and new spans can coexist
            resolved.append(span)

    return resolved


def color_code_url(url, span) -> str:
    """Returns URL with color-coding from ANSI code."""
    start = span.start
    end = span.end
    color = span.color
    colored_segment = f"{highlight(url[start:end], color)}"
    return url[:start] + colored_segment + url[end:]


def render_url(url: str, spans: list) -> str:
    """Apply ANSI code to URL using resolved spans."""
    offset = 0
    rendered_url = url

    # Applies color coding with resolved spans
    for span in spans:
        span.start += offset
        span.end += offset
        color = span.color
        rendered_url = color_code_url(rendered_url, span)
        offset += len(color) + len(RESET)
    
    return rendered_url


def classify_url_structure(url: str, ctx: RiskContext) -> str:
    """
    Classifies and highlights URL risk indicators.

    Returns:
        str: ANSI-highlighted URL.
    """
    spans = detect_url_spans(url, ctx)
    spans = resolve_spans(spans)
    color_coded_url = render_url(url, spans)
    generate_url_risk_context(url, ctx)

    return {
        "url_structure": {
            "rendered_url": color_coded_url
        }
    }


def generate_url_risk_context(url: str, ctx: RiskContext, domain: str=None):
    """
    Runs multiple span-returning detection functions along with their expected color.

    Attributes:
        check_list: Dictionary of function-color pairs determining the color for the spans returned from each function.
        url: URL to inspect.
        domain: Optional, determines whether scope is confined to domain or the full URL.

    Returns:
        list: Aggregated spans from all detection functions.
    """
    check_url = {
        contains_ip_address,
        contains_suspicious_keywords,
        contains_uncommon_tld,
        is_url_long,
        contains_special_chars
    }

    check_domain = {
        contains_at_symbols,
        contains_digits,
        contains_hyphens,
    }

    subdomain, domain, _ = extract_url_components(url)

    contains_multiple_subdomains(subdomain, ctx)

    for check_func in check_url:
        check_func(url, ctx)

    for check_func in check_domain:
        check_func(domain, ctx)
    