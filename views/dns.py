from views.helpers import print_header, print_kv
import dns.resolver
import geoip2.database
import requests


def get_ipv4_address(url: str) -> str:
    """
    Get the IPv4 address(es) associated with the given URL.

    Args:
        url (str): The URL to query for IPv4 addresses.

    Returns:
        str: A comma-separated list of IPv4 addresses.
    """
    answers = dns.resolver.resolve(
        url,
        "A"
    )
    ipv4_addresses = [
        str(address) for address in answers
    ]
    return ipv4_addresses


def get_ipv6_address(url: str) -> str:
    """
    Get the IPv6 address(es) associated with the given URL.

    Args:
        url (str): The URL to query for IPv6 addresses.

    Returns:
        str: A comma-separated list of IPv6 addresses.
    """
    answers = dns.resolver.resolve(
        url,
        "AAAA"
    )
    ipv6_addresses = [
        str(address) for address in answers
    ]
    return ", ".join(ipv6_addresses)


def get_mail_servers(url: str) -> str:
    """
    Get the mail server(s) associated with the given URL.

    Args:
        url (str): The URL to query for mail servers.

    Returns:
        str: A comma-separated list of mail servers.
    """
    answers = dns.resolver.resolve(
        url,
        "MX"
    )
    mail_servers = [
        str(server) for server in answers
    ]
    return ", ".join(mail_servers)


def get_geoip_info(ip_address: str) -> str:
    """
    Get the GeoIP information for the given IP address.

    Args:
        ip_address (str): The IP address to query for GeoIP information.

    Returns:
        str: A string containing GeoIP information.
    """
    response = requests.get(f"https://ipinfo.io/{ip_address}/json")
    return response.json()

def print_dns_analysis(hostname: str):
    """
    Perform a DNS analysis for the given hostname, including IPv4, IPv6, and mail server information.

    Args:
        hostname (str): The hostname to analyze.
    """
    print_header("DNS Analysis")

    ipv4_addresses = get_ipv4_address(hostname) or "Unknown"
    ipv6_addresses = str(get_ipv6_address(hostname)) or "Unknown"

    origins = set()
    state = None
    country = None

    # Gather GeoIP information for each IPv4 address
    for ip_address in ipv4_addresses:
        geo_ip_info = get_geoip_info(ip_address)
        
        if "error" in geo_ip_info:
            print_kv("Status", f"{geo_ip_info["status"]} Error ({geo_ip_info["error"]["title"]} - {geo_ip_info["error"]["message"]})")
        
        state = geo_ip_info["region"]
        country = geo_ip_info["country"]
        origins.add(f"{state}, {country}")

    origins = ", ".join(list(origins))

    print_kv("GeoIP Information", f"{origins}")
    print_kv("Associated IPv4 Addresses", ", ".join(ipv4_addresses))
    print_kv("Associated IPv6 Addresses", ipv6_addresses)
    
    