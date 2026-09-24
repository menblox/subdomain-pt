import sys
sys.path.insert(0, "src")

from subdomain_enum.ctlogs import fetch_subdomains
from subdomain_enum.unification import unification_names

names = fetch_subdomains("github.com")
print(f"Имён из crt.sh: {len(names)}")

results = unification_names(names)

for name, ip in results:
    if ip:
        print(f"{name}\t{', '.join(ip)}")
    else:
        print(f"{name}\tN/A")