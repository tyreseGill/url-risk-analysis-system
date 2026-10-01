from models.rules_engine import deduce_rule
from utils.text_utils import cutoff_print_statement
from views.style import highlight_green, highlight_yellow, highlight_red


EXPLANATIONS = {
    "young_domain": "Phishing sites often have extremely short lifespans.",
    "expires_shortly": "Future connections to this site are ill-advised as this site will soon to be unsecure and any traffic on this site may be visible to bad actors.",
    "expired_domain": "If not resolved, an expired domain provides the opportunity for a malicious user to purchase the domain name for their own illegitimate use.",
    "no_https": "Sites unsupportive of HTTPS do not encrypt traffic – making it possible for bad actors to sniff out sensitive data such as any emails or passwords that are sent.",
    "sus_keywords": "URLs containing certain keywords may be an indicator that a link is malicious.",
    "multiple_subdomains": "URLs containing multiple subdomains may be attempting to decieve users by hiding the true domain.",
    "ip_address": "IP-based URLs are not human-readable, providing no information regarding the domain.",
    "at_symbol_in_url": 'Bad actors often utilize the "@" symbol to conceal malicious links.',
    "hyphens_in_url": 'Phishing sites often include hypens ("-") in the domain name to fool users into confusing it with a legitimate domain.',
    "digits_in_url": "Phishing sites often substitute letters with similar-looking digits (e.g. 0 instead of o) in the domain name to fool users into confusing it with a legitimate domain.",
    "special_chars": "Phishing sites often substitute letters with similar-looking unicode characters (e.g. õ instead of o) in the domain name to fool users into confusing it with a legitimate domain.",
    "uncommon_tld": "Bad actors motivated by financial gain are more likely to purchase uncommon top-level domains in exchange for cheaper prices.",
    "long_url": "Long URLs may be attempting to conceal malicious parameters.",
    "url_shortner": "URL shortners hide the destination link and may redirect to an untrusted domain.",
    "expired_tls_cert": "An expired SSL/TLS certificate makes it possible for bad actors to view your traffic to this site unencrypted.",
    "unreliable_cert": "The authenticity of the certificate of this site cannot be validated.",
    "cert_in_need_of_renewal": "An SSL/TLS certificate has a recommended lifetime of 47 days. The longer a certificate goes without renewal, the more likely it is to be exploited by bad actors and result in a data breach.",
    "hostname_mismatch": "The certificate does not match the requested domain, which may indicate interception or misconfiguration.",
    "self_signed_cert": "A self-signed certificate is not to be trusted.",
    "lets_encrypt_cert": 'Certificates offered by this CA are free and only serve to verify domain ownership – they do NOT verify the identity of the site owner. As such, they can be abused by bad actors to trick users into thinking a site is legit.',
    "many_scripts": "Pages with many scripts may rely on dynamic or obfuscated behavior.",
    "external_links": "External links may redirect users to untrusted domains.",
    "mismatched_links": "One or more displayed links don't match the expected destination.",
    "hidden_elements": "Hidden elements may be used to obscure malicious content or trick users.",
    "overlay_detected": "Overlays can be used to capture user interaction or spoof legitimate interfaces.",
    "country_mismatch": "The domain is associated with a country unassociated with the user's region.",
    "no_mx_records": "No MX records found for the domain. This indicates that the domain is not configured to receive email."
}

STATEMENTS = {
    "young_domain": "Young domain",
    "expires_shortly": "Domain expires shortly; renewal uncertainty may indicate risk",
    "expired_domain": "Expired domain",
    "no_https": "No HTTPS support",
    "sus_keywords": "Suspicious keywords in URL",
    "multiple_subdomains": "Multiple subdomains in URL",
    "ip_address": "URL contains an IP address",
    "at_symbol_in_url": 'URL contains an "@" symbol',
    "hyphens_in_url": 'Domain name contains an "-" symbol',
    "digits_in_url": 'Domain name contains digits',
    "special_chars": 'Domain name contains special/unicode characters',
    "uncommon_tld": "Unusual top-level domain",
    "long_url": "Unusually long URL",
    "url_shortner": "Uses URL shortner",
    "expired_tls_cert": "Expired SSL/TLS certificate",
    "cert_in_need_of_renewal": "SSL/TLS certificate has surpassed recommended lifetime",
    "unreliable_cert": "SSL/TLS certificate not trusted",
    "hostname_mismatch": "Hostname does not match SSL/TLS certificate info",
    "self_signed_cert": "Self-signed certificate",
    "lets_encrypt_cert": 'SSL/TLS certificate issued by an automated public CA',
    "many_scripts": "Many scripts",
    "external_links": "External links",
    "mismatched_links": "Mismatched links",
    "hidden_elements": "Hidden elements",
    "overlay_detected": "Overlay detected",
    "country_mismatch": "Mismatching country",
    "no_mx_records": "No MX Records Found"
}

RISK_VALUES = {
    "young_domain": 10,
    "expires_shortly": 10,
    "expired_domain": 10,
    "no_https": 30,
    "sus_keywords": 5,
    "multiple_subdomains": 10,
    "ip_address": 30,
    "at_symbol_in_url": 20,
    "hyphens_in_url": 10,
    "digits_in_url": 10,
    "special_chars": 10,
    "uncommon_tld":5,
    "long_url": 5,
    "url_shortner": 25,
    "unreliable_cert": 30,
    "expired_tls_cert": 10,
    "cert_in_need_of_renewal": 5,
    "hostname_mismatch": 25,
    "self_signed_cert": 10,
    "lets_encrypt_cert": 5,
    "many_scripts": 5,
    "external_links": 5,
    "mismatched_links": 30,
    "hidden_elements": 5,
    "overlay_detected": 5,
    "country_mismatch": 5,
    "no_mx_records": 5
}


class RiskContext:
    """Represents a collection of the risks extrapolated from a given URL."""

    def __init__(self):
        self.signals = set()

    def add(self, signal: str):
        self.signals.add(signal)

    def print_statements(self, explain_statement):
        if self.signals:
            print()

        for signal in self.signals:
            risk_value = RISK_VALUES[signal]
            statement = cutoff_print_statement(STATEMENTS[signal])
            statement = (
                highlight_red(statement)
                if risk_value >= 10
                else highlight_yellow(statement)
            )
            print(f" - {statement}")

            if explain_statement:
                explanation = cutoff_print_statement(EXPLANATIONS[signal], extra_padding="  ")
                print(f"\t↳ {explanation}")
                
    def print_risk_score(self):
        risk_score = sum(
            RISK_VALUES[signal] for signal in self.signals
        )
        
        if 0 <= risk_score <= 10:
            risk_score = highlight_green(risk_score)
        elif risk_score <= 20:
            risk_score = highlight_yellow(risk_score)
        else:
            risk_score = highlight_red(risk_score)

        print(f"Risk Score: {risk_score}")

    def print_conclusion(self):
        deductions = cutoff_print_statement(
            deduce_rule(self.signals),
            cutoff_length=60,
            extra_padding=" "
        )

        if deductions == "":
            deductions = highlight_green("All Clear")

        print(f"\nVerdict: {deductions}")
