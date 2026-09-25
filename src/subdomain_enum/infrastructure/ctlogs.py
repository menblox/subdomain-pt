"""crt.sh пассивный поиск поддоменов через Certificate Transparency."""

import json
import urllib.error
import urllib.request

CTRSH_URL = "https://api.ctlogs.dev/v1/subdomains/{domain}"

def fetch_subdomains(domain: str, timeout: float = 10.0) -> list[str]:
    #Запрашивает crt.sh и возвращает список уникальных поддоменов

    url = CTRSH_URL.format(domain=domain)
    print(url)
    request = urllib.request.Request(url, headers={"User-Agent": "subdomain-enum/0.1"})

    try: 
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")

    except (urllib.error.URLError, TimeoutError, OSError):
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, dict):
        return []

    rows = data.get("rows", [])
    if not isinstance(rows, list):
        return []
    
    names: set[str] = set()

    for row in rows:
        if not isinstance(row, dict):
            continue

        match = row.get("match", "")
        if not isinstance(match, str):
            continue

        name = match.strip().lower()

        if not name:
            continue

        if name.startswith("*."):
            name=name[2:]

        if name == domain or name.endswith("." + domain):
            names.add(name)

    return sorted(names)