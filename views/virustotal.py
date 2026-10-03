from models.network.virustotal import fetch_virustotal_stats
from views.helpers import print_header, print_kv
from views.style import highlight_green, highlight_red, highlight_yellow


def print_virus_total_stats(url: str):
    print_header("VirusTotal Malware Scan")

    stats = fetch_virustotal_stats(url)

    if stats is None:
        print("[INFO] Failed to fetch statistics within alloted time.")
        return
        
    num_undetected, num_harmless, num_suspicious, num_malicious = highlight_stats(stats)
    
    print_kv("Undetected", num_undetected)
    print_kv("Harmless", num_harmless)
    print_kv("Suspicious", num_suspicious)
    print_kv("Malicious", num_malicious)


def get_stats(stats: dict):
    num_undetected = stats["undetected"]
    num_harmless = stats["harmless"]
    num_suspicious = stats["suspicious"]
    num_malicious = stats["malicious"]

    return num_undetected, num_harmless, num_suspicious, num_malicious


def highlight_stats(stats: dict):
    num_undetected, num_harmless, num_suspicious, num_malicious = get_stats(stats)

    num_total = sum(
        [num_undetected, num_harmless, num_suspicious, num_malicious]
    )

    num_undetected = highlight_stable_stats(num_undetected, num_harmless)
    num_harmless = highlight_stable_stats(num_harmless, num_undetected)
    num_suspicious = highlight_critical_stats(num_suspicious, num_total)
    num_malicious = highlight_critical_stats(num_malicious, num_total)

    return num_undetected, num_harmless, num_suspicious, num_malicious


def highlight_stable_stats(stat: int, other_stat: int):
    color = (
        highlight_red(stat)
        if stat == 0 and other_stat == 0
        else highlight_green(stat)
    )
    return color


def highlight_critical_stats(stat: int, num_total: int):
    if stat == 0:
        color = highlight_green(stat)
    elif stat > (0.5 * num_total):
        color = highlight_red(stat)
    else:
        color = highlight_yellow(stat)
    
    return color
