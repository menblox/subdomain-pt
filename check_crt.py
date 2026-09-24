import sys
sys.path.insert(0, "src")

from src.subdomain_enum.crtsh import fetch_crtsh

names = fetch_crtsh("github.com", timeout=30)
print(f"Найдено: {len(names)}")
for name in names[:30]:
    print(name)