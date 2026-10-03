from models.network.certs import *
from models.risk.classifiers import classify_expiration_date
from models.risk_context import RiskContext
from utils.text_utils import cutoff_print_statement
from views.helpers import print_header, print_kv
from views.style import highlight_green, highlight_red, highlight_yellow


def print_cert_analysis(hostname: str, ctx: RiskContext):
    print_header("SSL/TLS Certificate Analysis")
    cert = get_tls_certificate(hostname, ctx)
    print_trusted_chain(cert)

    if not cert:
        return
    
    print_certificate_status(cert, ctx)
    print_certificate_identity(cert, ctx)
    print_certificate_lifecycle(cert, ctx)
    print_certificate_relationships(cert, hostname, ctx)


def print_trusted_chain(cert: Certificate):
    trusted_ca_chain_flag = highlight_green("Yes") if cert else highlight_red("No")
    print_kv("Trusted Chain", trusted_ca_chain_flag)


def print_certificate_status(cert: Certificate, ctx: RiskContext):
    cert_status = (
        highlight_green("Valid") 
        if cert.is_valid(ctx) 
        else highlight_red("Expired")
    )
    print_kv("Certificate Status", cert_status + "\n")


def print_certificate_identity(cert: Certificate, ctx: RiskContext):
    print_kv("Subject CN", cert.subject_cn)
    print_kv("Issuer Org", cert.issuer_org_name + "\n")
    
    if cert.issuer_org_name == "Let's Encrypt":
        ctx.add("lets_encrypt_cert")


def print_certificate_lifecycle(cert: Certificate, ctx: RiskContext):
    age = cert.get_age(ctx)
    age_colored = (
        highlight_green(age) 
        if age < 47 
        else highlight_yellow(age)
    )
    value = f"{age_colored} days ago"

    print_kv("Last Renewed", value)
    print_expiration_date(cert, ctx)


def print_certificate_relationships(cert: Certificate, hostname: str, ctx: RiskContext):
    self_signed_status = (
        highlight_red("Yes")
        if is_self_signed(cert, ctx)
        else highlight_green("No")
    )
    hostname_cert_match = (
        highlight_green("Yes") 
        if verify_hostname(cert, hostname, ctx) 
        else highlight_red("No")
    )
    sans_str = ", ".join(cert.sans)
    sans_str = cutoff_print_statement(sans_str)

    print_kv("\nSelf-Signed", self_signed_status)
    print_kv("Hostname Match", hostname_cert_match)
    print_kv("SANs", sans_str)


def print_expiration_date(cert: Certificate, ctx: RiskContext):
    if not cert.is_valid(ctx):
        return
    
    exp_date = cert.not_after.date()
    days = cert.days_until_expiration()
    days_colored = classify_expiration_date(days)
    value = f"{exp_date} ({days_colored} days from now)"

    print_kv("Expiration Date", value)
