import sys
import time

sys.path.insert(0, "src")

from subdomain_enum.application.unification import unification_names
from subdomain_enum.application.wildcard import detect_wildcard
from subdomain_enum.infrastructure.ctlogs import fetch_subdomains

domain = "yandex.ru"

names = fetch_subdomains(domain)
print(f"Имён из ctlogs.dev: {len(names)}")

wildcard_ip = detect_wildcard(domain)
print(f"Wildcard: {wildcard_ip}")

start = time.time()
results = unification_names(names, wildcard_ip=wildcard_ip)
elapsed = time.time() - start

found = 0
for name, ips in results:
    if ips:
        print(f"{name}\t{', '.join(ips)}")
        found += 1
    else:
        print(f"{name}\tN/A")

print(f"\nНайдено: {found} из {len(names)}")
print(f"Время: {elapsed:.2f} сек")