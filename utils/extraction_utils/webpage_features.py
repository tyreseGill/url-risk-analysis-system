
# HTML
def get_nb_hyperlinks(url: str) -> float:
    pass

def get_ratio_int_hyperlinks(url: str) -> float:
    pass

def get_ratio_ext_hyperlinks(url: str) -> float
    pass

def get_links_in_tags(url: str) -> int:
    pass

def get_safe_anchors(url: str) -> int:
    pass

# Media
def has_external_favicon(url: str) -> bool:
    pass

def get_ratio_int_media(url: str) -> float:
    pass

def get_ratio_ext_media(url: str) -> float:
    pass
    
def get_nb_ext_CSS(url: str) -> int:
    pass


# JavaScript
def has_login_form(url: str) -> bool:
    pass

def contains_iframe(url: str) -> bool:
    pass

def has_popup_window(url: str) -> bool:
    pass

def has_onmouseover_event(url: str) -> bool:
    pass

def has_right_clic_event(url: str) -> bool:
    pass


# Content Metadata
def has_empty_title(url: str) -> bool:
    pass

def has_domain_in_title(url: str) -> bool:
    pass

def has_domain_with_copyright(url: str) -> bool:
    pass


# Redirectional Error Metrics
def get_ratio_ext_redirection(url: str) -> float:
    pass

def get_ratio_ext_errors(url: str) -> float:
    pass
