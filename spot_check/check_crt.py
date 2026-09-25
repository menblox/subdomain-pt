import sys

sys.path.insert(0, "src")

from subdomain_enum.infrastructure.ctlogs import fetch_subdomains

names = fetch_subdomains("github.com", timeout=30)
print(f"Найдено: {len(names)}")
for name in names[:30]:
    print(name)