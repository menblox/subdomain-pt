import sys

sys.path.insert(0, "src")

from subdomain_enum.infrastructure.ctlogs_ru import fetch_subdomains_ru

names = fetch_subdomains_ru("yandex.ru", timeout=30)
print(f"Найдено: {len(names)}")
for name in names[:30]:
    print(name)
    