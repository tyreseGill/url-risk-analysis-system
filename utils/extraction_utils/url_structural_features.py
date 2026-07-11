from models.url.parsing import extract_hostname, contains_ip_address, extract_url_components
import re

# BOOLEAN functions

def has_http_in_path(url: str) -> bool:
    pass

def has_https_token(url: str) -> bool:
    pass

def contains_punycode(url: str) -> bool:
    pass

def contains_port(url: str) -> bool:
    pass

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
    pass

def get_ratio_digits_host(url: str) -> float:
    pass

def get_avg_words_raw(url: str) -> float:
    pass

def get_avg_word_host(url: str) -> float:
    pass

def get_avg_word_path(url: str) -> float:
    pass
    

# INTEGER functions

def get_url_length(url: str) -> int:
    pass

def get_hostname_length(url: str) -> int:
    pass

def get_nb_symbol(url: str, symbol: str) -> int:
    pass

def get_nb_redirection(url: str) -> int:
    pass

def get_nb_subdomains(url: str) -> int:
    pass

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
    pass
    
def get_longest_word_path(url: str) -> int:
    pass

def get_phish_hints(url: str) -> int:
    pass
