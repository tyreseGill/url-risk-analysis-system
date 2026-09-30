from views.helpers import print_header, print_kv
import dns.resolver


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
    return ", ".join(ipv4_addresses)


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


def print_dns_analysis(hostname: str):
    """
    Perform a DNS analysis for the given hostname, including IPv4, IPv6, and mail server information.

    Args:
        hostname (str): The hostname to analyze.
    """
    print_header("DNS Analysis")

    ipv4_address = str(get_ipv4_address(hostname)) or "None"
    ipv6_address = str(get_ipv6_address(hostname)) or "None"
    
    print_kv("Associated IPv4 Addresses", ipv4_address)
    print_kv("Associated IPv6 Addresses", ipv6_address)
    
    
    