import sys
import time

sys.path.insert(0, "src")

from subdomain_enum.application.bruteforce import bruteforce, load_wordlist
from subdomain_enum.application.wildcard import detect_wildcard

domain = "github.com"
words = load_wordlist("wordlists/subdomains-5000.txt")
print(f"Слов: {len(words)}")

wildcard_ips = detect_wildcard(domain)
print(f"Wildcard: {wildcard_ips}")

start = time.time()
raw = bruteforce(domain, words, timeout=2.0, max_workers=30)
elapsed = time.time() - start

found_raw = sum(1 for _, ips in raw if ips)
print(f"\nБез фильтра: {found_raw} из {len(words)}")

phantom = sum(
    1 for _, ips in raw
    if ips and wildcard_ips and set(ips) == wildcard_ips
)
print(f"Из них фантомов (wildcard-IP): {phantom}")
print(f"Реальных: {found_raw - phantom}")
print(f"Время: {elapsed:.2f} сек")