
import re

from models.url.parsing import (
    extract_hostname,
    extract_url_components,
    fetch_ip_addresses,
)

# BOOLEAN functions

def has_http_in_path(url: str) -> bool:
    pass

def has_https_token(url: str) -> bool:
    pass

def contains_punycode(url: str) -> bool:
    pass

def contains_port(url: str) -> bool:
    port_num = re.search(r":\d+", url)

    if not port_num:
        return False

    port_num = int(
        port_num.group(0)[1:]
    )
    
    # Checks if URL has a valid port
    if not (0 <= port_num <= 65_535):
        return False 

    hostname = extract_hostname(url)

    # Checks if a number is indeed a port given a hostname
    if hostname:
        return bool(
            re.match(rf"https?://{hostname}:{port_num}", url)
        )
    
    return False

# NOTE: nb_external_redirection
def has_external_redirection(url: str) -> bool:
    pass

def is_tld_in_path(url: str) -> bool:
    pass

def is_tld_in_subdomain(url: str) -> bool:
    pass

def has_abnormal_subdomain(url: str) -> bool:
    pass

def has_prefix_suffix(url: str) -> bool:
    pass

def is_domain_random(url: str) -> bool:
    pass

def is_domain_in_brand(url: str) -> bool:
    pass


# FLOAT functions

def get_ratio_digits_url(url: str) -> float:
    num_digits = sum(
        1 for char in url if char.isdigit()
    )
    return num_digits / len(url)

def get_ratio_digits_host(url: str) -> float:
    hostname = extract_hostname(url)
    
    num_digits = sum(
        1 for char in hostname if char.isdigit()
    )
    
    return num_digits / len(hostname)

def get_avg_words_raw(url: str) -> float:
    pass

def get_avg_word_host(url: str) -> float:
    pass

def get_avg_word_path(url: str) -> float:
    pass
    

# INTEGER functions

def get_url_length(url: str) -> int:
    return len(url)

def get_hostname_length(url: str) -> int:
    subdomain, domain, tld = extract_url_components(url)
    hostname = ".".join(
        part for part in (subdomain, domain, tld)
        if part
    )
    return len(hostname)

def get_nb_symbol(url: str, symbol: str) -> int:
    return url.count(symbol)

def get_nb_redirection(url: str) -> int:
    pass

def get_nb_subdomains(url: str) -> int:
    nb_subdomains = get_nb_symbol(url, '.')

    if nb_subdomains > 3:
        return 3
    else:
        return get_nb_symbol(url, '.')

def get_length_words_raw(url: str) -> int:
    pass

def get_char_repeat(url: str) -> int:
    pass

def get_shortest_words_raw(url: str) -> int:
    pass

def get_shortest_word_host(url: str) -> int:
    pass

def get_shortest_word_path(url: str) -> int:
    pass

def get_longest_words_raw(url: str) -> int:
    pass

def get_longest_word_host(url: str) -> int:
    subdomain, _, tld = extract_url_components(url)
    hostname = extract_hostname(url)
    if hostname:
        # _, hostname, _ = extract_url_components(url)
        words = re.split(r'[.-]', hostname)

        try:
            words.remove(tld)
        except ValueError:
            pass

        longest_word = max(words, key=len)
        return len(longest_word)
    else:
        ip_address_span = fetch_ip_addresses(url)[0]
        start, end = ip_address_span
        ip_address = url[start:end]
        
        if re.match(rf"https?://{ip_address}", url):
            words = ip_address.split('.')
            longest_octet = max(words, key=len)
            return len(longest_octet)
    
def get_longest_word_path(url: str) -> int:
    pass

def get_phish_hints(url: str) -> int:
    pass

# print(get_longest_word_host("https://www.todayshomeowner.com/how-to-make-homemade-insecticidal-soap-for-plants/"))