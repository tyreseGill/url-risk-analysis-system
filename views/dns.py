import dns.resolver
import requests

from models.risk_context import RiskContext
from views.helpers import print_header, print_kv
from views.style import highlight_green, highlight_red, highlight_yellow

USER_COUNTRY = "US"


def get_ipv4_address(url: str) -> str:
    """
    Get the IPv4 address(es) associated with the given URL.

    Args:
        url: The URL to query for IPv4 addresses.

    Returns:
        A comma-separated list of IPv4 addresses.
    """
    try:
        answers = dns.resolver.resolve(
            url,
            "A"
        )
    except dns.resolver.LifetimeTimeout:
        return []

    ipv4_addresses = [
        str(address) for address in answers
    ]
    return ipv4_addresses


def get_ipv6_address(url: str) -> str:
    """
    Get the IPv6 address(es) associated with the given URL.

    Args:
        url: The URL to query for IPv6 addresses.

    Returns:
        A comma-separated list of IPv6 addresses.
    """
    try:
        answers = dns.resolver.resolve(
            url,
            "AAAA"
        )
    except dns.resolver.LifetimeTimeout:
        return []

    ipv6_addresses = [
        str(address) for address in answers
    ]
    return ", ".join(ipv6_addresses)


def get_mail_servers(url: str) -> str:
    """
    Get the mail server(s) associated with the given URL.

    Args:
        url: The URL to query for mail servers.

    Returns:
        A comma-separated list of mail servers.
    """
    try:
        servers = dns.resolver.resolve(
            url,
            "MX"
        )
    except dns.resolver.LifetimeTimeout:
        return None

    mail_servers = [
        str(server.exchange) for server in servers
    ]
    return ", ".join(mail_servers)


def get_geoip_info(ip_address: str) -> str:
    """
    Get the GeoIP information for the given IP address.

    Args:
        ip_address: The IP address to query for GeoIP information.

    Returns:
        A string containing GeoIP information.
    """
    response = requests.get(f"https://ipinfo.io/{ip_address}/json")
    return response.json()


def get_geolocation(ipv4_addresses: list) -> str:
    """
    Fetches the geolocation information for the given IPv4 addresses.

    Args:
        ipv4_addresses: A list of IPv4 addresses to query for geolocation information.

    Returns:
        A string containing the geolocation information.
    """
    if len(ipv4_addresses) == 0:
        return None, None

    ip_address = ipv4_addresses[0]
    geo_ip_info = get_geoip_info(ip_address)
    
    # Extract state and country from the GeoIP information
    if "error" in geo_ip_info:
        print_kv("Status", f"{geo_ip_info["status"]} Error ({geo_ip_info["error"]["title"]} - {geo_ip_info["error"]["message"]})")
        return None, None
    else:
        state = geo_ip_info["region"]
        country = geo_ip_info["country"]
    
    return state, country


def print_geolocation(ipv4_addresses: list, ctx: RiskContext):
    """
    Print the geolocation information for the given IPv4 addresses.

    Args:
        ipv4_addresses: A list of IPv4 addresses to query for geolocation information.
        ctx: The risk context to update based on the geolocation analysis.
    """
    state, country = get_geolocation(ipv4_addresses)

    # Check if the country of the IP address matches the expected user country
    if state is None or country is None:
        origin = highlight_yellow("Unknown")
    else:
        origin = f"{state}, {country}"

    if country != USER_COUNTRY and country != None:
        ctx.add("country_mismatch")

    print_kv("GeoIP Information", origin)


def print_email_infrastructure_support(hostname: str, ctx: RiskContext):
    """
    Print the mail servers associated with the given hostname.

    Args:
        hostname: The hostname to query for mail servers.
        ctx: The risk context to update based on the email infrastructure analysis.
    """
    response = get_mail_servers(hostname)

    # Check if the hostname has any MX records
    if response is None:
        has_mx_records = highlight_yellow("Unknown")
    if response == ".":
        has_mx_records = highlight_red("No")
        ctx.add("no_mx_records")
    else:
        has_mx_records = highlight_green("Yes")

    print_kv("Supports Email Infrastructure", has_mx_records)


def print_ipv4_addresses(ipv4_addresses: list):
    """
    Print the associated IPv4 addresses.

    Args:
        ipv4_addresses: A list of IPv4 addresses to print.
    """
    if len(ipv4_addresses) == 0:
        print_kv("Associated IPv4 Addresses", highlight_yellow("Unknown"))
    else:
        print_kv("Associated IPv4 Addresses", ", ".join(ipv4_addresses))


def print_dns_analysis(hostname: str, ctx: RiskContext):
    """
    Perform a DNS analysis for the given hostname, including IPv4, IPv6, and mail server information.

    Args:
        hostname: The hostname to analyze.
        ctx: The risk context to update based on the DNS analysis.
    """
    print_header("DNS Analysis")

    ipv4_addresses = get_ipv4_address(hostname)

    print_geolocation(ipv4_addresses, ctx)
    print_email_infrastructure_support(hostname, ctx)
    print_ipv4_addresses(ipv4_addresses)
    
    