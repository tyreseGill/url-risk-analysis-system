import socket
import ssl
from datetime import datetime
from datetime import timezone as tz

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import Certificate as CryptCert

from models.risk_context import RiskContext
from models.url.parsing import extract_hostname, extract_url_components
from utils.animations import display_load_animation


class Certificate:
    """Represents an SSL/TLS certificate provided by a server."""

    def __init__(self, cert: CryptCert):
        self.subject = cert.subject.rfc4514_string()
        self.issuer = cert.issuer.rfc4514_string()
        
        self.subject_cn = cert.subject.get_attributes_for_oid(
            x509.NameOID.COMMON_NAME
        )[0].value

        self.issuer_country_code = cert.issuer.get_attributes_for_oid(
            x509.NameOID.COUNTRY_NAME
        )[0].value
        self.issuer_org_name = cert.issuer.get_attributes_for_oid(
            x509.NameOID.ORGANIZATION_NAME
        )[0].value
        self.issuer_cn = cert.issuer.get_attributes_for_oid(
            x509.NameOID.COMMON_NAME
        )[0].value
        self.not_after = cert.not_valid_after_utc
        self.not_before = cert.not_valid_before_utc
        self.sans = [
            san.value 
            for san in 
            cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
        ]

    def __repr__(self):
        return f'Common Name: {self.subject_cn}, Issuer Org: {self.issuer_org_name}, Issuer CN: {self.issuer_cn}, Version: {self.version}, Valid Between: {self.not_before} thru {self.not_after}, SANS: {self.sans}'

    def is_valid(self, ctx: RiskContext):
        current_time = datetime.now(tz.utc)
        validity_flag = self.not_before <= current_time <= self.not_after
        if not validity_flag and ctx:
            ctx.add("expired_tls_cert")
        return validity_flag
    
    def days_until_expiration(self):
        current_time = datetime.now(tz.utc)
        return (self.not_after - current_time).days
    
    def get_age(self, ctx: RiskContext):
        current_time = datetime.now(tz.utc).date()
        age_days = (current_time - self.not_before.date()).days
        if age_days > 47 and ctx:
            ctx.add("cert_in_need_of_renewal")
        return age_days


def get_tls_certificate(url: str, ctx: RiskContext) -> Certificate:
    """
    Establishes an HTTPS connection to host site and fetches SSL/TLS certificate.

    :param url: URL to obtain certificate from.
    :param ctx: RiskContext object to add context to.
    :return: A Certificate class object version developed from fetched SSL/TLS Certificate.
    """
    hostname = extract_hostname(url)

    # Disables verification to allow for inspection of certificate details
    insecure_context = ssl.create_default_context() 
    insecure_context.check_hostname = False
    insecure_context.verify_mode = ssl.CERT_NONE

    contexts = {
        "secure SSL/TLS certificate": (
            ssl.create_default_context()      # Ensures valid certificate
        ),
        "insecure SSL/TLS certificate": (
            insecure_context                  # Fallback when certificate is invalid
        )
    }

    # Attempts to obtain SSL/TLS certificate
    for cert_type, context in contexts.items():
        def fetch_certificate():
            try:
                with socket.create_connection((hostname, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        # Fetches binary of certificate
                        cert_bytes = ssock.getpeercert(binary_form=True)

                        # Converts certificate from binary to DER format
                        cert = x509.load_der_x509_certificate(
                            cert_bytes,
                            default_backend()
                        )

                        # Returns meaningful certificate if error doesn't occur
                        if cert is not None:
                            return Certificate(cert)

            except ssl.SSLError:  # Handles error in certificate verification process
                ctx.add("unreliable_cert")

            return None

        result = display_load_animation(
            fetch_certificate,
            f"Attempting to fetch {cert_type}"
        )

        if result is not None:
            return result

    print("[INFO] Failed to fetch SSL/TLS certificate.")
    return None


def verify_hostname(cert: Certificate, url: str, ctx: RiskContext) -> bool:
    """
    Performs check to verify that hostname and certificate match,
    ensuring the site is secure and not fraudulent.

    :param cert: Certificate to parse.
    :param url: Url to inspect.
    :return: True, if hostname matches certificate information. Else, false.
    """
    sub, dom, tld = extract_url_components(url)
    hostname = f"{dom}.{tld}"
    match_found = False

    # Includes subdomain in hostname if a subdomain exists
    if sub:
        hostname = f"{sub}.{dom}.{tld}"

    for san in cert.sans:
        # Comparison check for comparing hostname to a SAN with a wildcard subdomain
        if san.startswith("*."):
            base_domain = san[2:]  # Normalizes domain name to exclude wildcard subdomains
            same_domain = hostname.endswith("." + base_domain)                # Checks if domain name is same
            same_depth = (hostname.count(".") == base_domain.count(".") + 1)  # Checks if domain level is same

            if same_domain and same_depth:
                match_found = True

        # Comparison check for comparing hostname with explicit SAN
        else:
            if san == hostname:
                match_found = True
        
        # Breaks loop when match found to avoid overwrite
        if match_found:
            break

    if not match_found:
        ctx.add("hostname_mismatch")

    return match_found


def is_self_signed(cert: Certificate, ctx: RiskContext) -> bool:
    """
    Performs check to verify whether a certificate was self-signed or not.

    Args:
        cert: Certificate to check.
    
    Returns:
        bool: True, if the subject and issuer of the certificate are the same. Else, false.
    """
    subject_cn = cert.subject_cn
    issuer_cn  = cert.issuer_cn
    self_signed_flag =  bool(subject_cn == issuer_cn)

    if self_signed_flag and ctx:
        ctx.add("self_signed_cert")

    return self_signed_flag
