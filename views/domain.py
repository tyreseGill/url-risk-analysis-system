from datetime import datetime as dt

from models.risk.classifiers import normalize_expiration_date
from views.helpers import print_header, print_kv
from views.style import highlight


def print_domain_identity_analysis(risk: dict, query: dict):
    domain_name = query.domain_name.lower()
    exp_date = normalize_expiration_date(query.expiration_date)
    registar = query.registrar

    print_header("Domain Identity Analysis")
    print_kv("Domain Name", domain_name)
    print_domain_age(risk)
    print_expiration_info(risk, exp_date)
    print_kv("Registrar", registar)
    print_domain_registration_status(risk)


def print_domain_age(risk: dict):
    color = risk["age"]["color"]
    value = risk["age"]["value"]
    unit = risk["age"]["unit"]
    
    age = f"{value} {unit}"
    value = highlight(age, color)
    print_kv("Age", value)


def print_expiration_info(risk: dict, exp_date: dt):
    color = risk["exp_date"]["color"]
    value = highlight(exp_date.date(), color)
    print_kv("Expiration Date", value)


def print_domain_registration_status(risk: dict):
    color = risk["domain_reg"]["color"]
    status = risk["domain_reg"]["status"]
    value = highlight(status, color)
    print_kv("Domain Registration Status", value)
    