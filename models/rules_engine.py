
RULES = [
    # URL Structure
    {
        "name": "Possible Domain Impersonation",
        "any": {"multiple_subdomains", "digits_in_url", "hyphens_in_url", "special_chars"}
    },
    {
        "name": "Shortened URL Concealment",
        "all": {"url_shortner"}
    },
    {
        "name": "IDN homograph attack",
        "all": {"special_chars"}
    },
    {
        "name": "URL Obfuscation Pattern",
        "all": {"long_url", "sus_keywords"}
    },
    {
        "name": "IP-Based Phishing Attempt",
        "all": {"ip_address"},
        # "any": {"no_https"}
    },
    # Domain Identity
    {
        "name": "High Risk of Phishing",
        "all": {"young_domain", "external_links"},
        "any": {"multiple_subdomains", "ip_address", "at_symbol_in_url", "lets_encrypt_cert"}
    },
    # DNS Infrastructure
    {
        "name": "No MX Records",
        "all": {"no_mx_records"},
    },
    # TODO: Enable user to add country of residence to interpret this
    {
        "name": "Country Mismatch",
        "all": {"country_mismatch"},
    },
    # Transport Security
    {
        "name": "Insecure Connection",
        "all": {"no_https"}
    },
    # SSL/TLS Certificate
    {
        "name": "Certificate Trust Issue",
        "all": {"unreliable_cert"},
    },
    # HTML/CSS
    {
        "name": "Deceptive Links",
        "all": {"mismatched_links"},
        "any": {"external_links"}
    },
    # TODO: Update detection methods to reduce the rate of false-positives before implementation
    # {
    #     "name": "Clickjacking",
    #     "all": {"hidden_elements", "overlay_detected"}
    # },
    # {
    #     "name": "Overlay-Based Phishing",
    #     "all": {"overlay_detected"},
    #     "any": {"hidden_elements", "mismatched_links"}
    # },
    # {
    #     "name": "Hidden Content Manipulation",
    #     "all": {"hidden_elements"},
    #     "any": {"overlay_detected", "external_links"}
    # }
]


def deduce_rule(signals: set) -> str:
    """
    Given a set of signals, infers any applicable risks.

    :param signals: The set of indicators associated with risks.
    :return: Text representing rules deduced from given given signals.
    """
    from views.style import highlight_red, highlight_yellow

    rules_str = []

    for rule in RULES:
        rule_name = rule.get("name")

        all_rule_satisfied = rule_matches(rule, signals)
        any_rule_satisfied = rule_matches(rule, signals)

        if all_rule_satisfied and any_rule_satisfied:
            risk_weight = calc_risk_weight(rule)
            rule_name = highlight_red(rule_name) if risk_weight >= 20 else highlight_yellow(rule_name)
            rules_str.append(rule_name)

    return ", ".join(rules_str)


def rule_matches(rule: dict, signals: set) -> bool:
    """
    Determines if the given signals collected satisfy "all" the required elements and at least one of the "any" elements for a given rule.

    :param rule: Dictionary object specifying the partial and complete sets of elements to satisfy a rule.
    :param signals: Set of compiled red flags used to reach a consensus on a URL's safety.
    :return: True, if the specified type doesn't exist for the given rule or all the required signals match.
    """
    all_elems = rule.get("all", [])
    any_elems = rule.get("any", [])

    all_satisfied = all(
        signal in signals
        for signal in all_elems
    )
    
    any_satisfied = any(
        signal in signals
        for signal in any_elems
        ) if any_elems else True
    
    return all_satisfied and any_satisfied


def calc_risk_weight(rule: dict) -> int:
    """
    Sums up combined risks of a rule based on signals.

    :param rule: The rule to calculate a risk from.
    :return: An integer value representing risk score.
    """
    from models.risk_context import RISK_VALUES
    
    rule_elems = rule.get("all", set()) | rule.get("any", set())
    rule_risk_value = sum(
        RISK_VALUES[elem] for elem in rule_elems
    )
    return rule_risk_value
