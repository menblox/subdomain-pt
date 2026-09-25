"""пассивный поиск РФ поддоменов через Certificate Transparency."""

import ssl
import json
import urllib.error
import urllib.request


CTRSH_URL = "https://ct.tlscc.ru/?q={domain}&output=json"

context = ssl._create_unverified_context()

def fetch_subdomains_ru(domain: str, timeout: float = 10.0) -> list[str]:

    url = CTRSH_URL.format(domain=domain)
    request = urllib.request.Request(url, headers={"User-Agent": "subdomain-enum/0.1"})

    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            raw = response.read().decode("utf-8")
            #print("raw: ", raw)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print("ошибка: ", e)
        return[]


    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print("ошибка: ", e)
        return []

    if not isinstance(data, list):
        print("ошибка: data не список")
        return []

    names: set[str] = set()

    for row in data:
        if not isinstance(row, dict):
            print("ошибка: row не словарь")
            continue

        raw_names: list[str] = []

        for field in ("common_name", "name_value"):
            value = row.get(field, "")
            if isinstance(value, str) and value:
                raw_names.extend(value.split("\n"))

        for name in raw_names:
            name = name.strip().lower()

            if not name:
                print("ошибка: name отсутствует")
                continue

            if name.startswith("*."):
                name=name[2:]

            if name == domain or name.endswith("." + domain):
                names.add(name)

    return sorted(names)