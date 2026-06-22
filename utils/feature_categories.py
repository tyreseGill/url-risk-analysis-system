URL_LENGTH_FEATURES = {
    'length_url', 'length_hostname'
}

URL_NUMERIC_FEATURES = {
    'nb_dots', 'nb_hyphens', 'nb_at', 'nb_qm', 'nb_and', 'nb_or', 'nb_eq', 'nb_underscore', 'nb_tilde', 'nb_percent', 'nb_slash', 'nb_star',
    'nb_colon', 'nb_comma', 'nb_semicolumn', 'nb_dollar', 'nb_space', 'nb_www', 'nb_com', 'nb_dslash'
}

URL_STRUCTURAL_FEATURES = {
    'ip', 'http_in_path', 'https_token', 'ratio_digits_url', 'ratio_digits_host', 'punycode', 'port', 'path_extension'
}

URL_BEHAVIOR_FEATURES = {
    'shortening_service', 'nb_redirection', 'nb_external_redirection'
}

DOMAIN_AND_SUBDOMAIN_FEATURES = {
    'tld_in_path', 'tld_in_subdomain', 'abnormal_subdomain', 'nb_subdomains', 'prefix_suffix', 'random_domain', 'domain_in_brand', 
    'brand_in_subdomain', 'brand_in_path', 'suspecious_tld'
}

WORD_STATS = {
    'length_words_raw', 'char_repeat', 'shortest_words_raw', 'shortest_word_host', 'shortest_word_path', 'longest_words_raw', 'longest_word_host', 
    'longest_word_path', 'avg_words_raw', 'avg_word_host', 'avg_word_path', 'phish_hints'
}

HTML_FEATURES = {
    'nb_hyperlinks', 'ratio_intHyperlinks', 'ratio_extHyperlinks', 'ratio_nullHyperlinks', 'links_in_tags', 'safe_anchor'
}

MEDIA_FEATURES = {
    'nb_extCSS', 'external_favicon', 'ratio_intMedia', 'ratio_extMedia'
}

JAVASCRIPT_FEATURES = {
    'login_form', 'submit_email', 'sfh', 'iframe', 'popup_window', 'onmouseover', 'right_clic'
}

CONTENT_METADATA_FEATURES = {
    'empty_title', 'domain_in_title', 'domain_with_copyright'
}

WHOIS_FEATURES = {
    'whois_registered_domain', 'domain_registration_length', 'domain_age'
}

REPUTATIONAL_FEATURES = {
    'web_traffic', 'dns_record', 'google_index', 'page_rank', 'statistical_report'
}

REDIRECTION_ERR_METRICS = {
    'ratio_intRedirection', 'ratio_extRedirection', 'ratio_intErrors', 'ratio_extErrors'
}

FEATURE_CATEGORIES = {
    "URL Length Features": URL_LENGTH_FEATURES,
    "URL Numeric Features": URL_NUMERIC_FEATURES,
    "URL Structural Features": URL_STRUCTURAL_FEATURES,
    "URL Behavioral Features": URL_BEHAVIOR_FEATURES,
    "Domain and Subdomain Features": DOMAIN_AND_SUBDOMAIN_FEATURES,
    "Word Statistics": WORD_STATS, 
    "HTML Features": HTML_FEATURES,
    "Media Features": MEDIA_FEATURES,
    "JavaScript Features": JAVASCRIPT_FEATURES,
    "Content Metadata Features": CONTENT_METADATA_FEATURES,
    "WHOIS Features": WHOIS_FEATURES,
    "Reputational Features": REPUTATIONAL_FEATURES,
    "Redirectional/Error Metrics": REDIRECTION_ERR_METRICS
}
