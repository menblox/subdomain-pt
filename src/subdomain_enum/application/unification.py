"""Объединение источников имён и DNS-резолва"""

import concurrent.futures
from functools import partial

from subdomain_enum.infrastructure.dns import resolve_domain


def unification_names(
    names: list[str],
    timeout: float = 2.0,
    max_workers: int = 30,
    wildcard_ip: set[str] | None = None,
) -> list[tuple[str, list[str] | None]]:
    # Резолвит список имён в IP-адреса параллельно

    if not names:
        return []

    resolver = partial(resolve_domain, timeout=timeout)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        ip_list = list(ex.map(resolver, names))

    results: list[tuple[str, list[str] | None]] = []

    for name, ip in zip(names, ip_list, strict=True):
        if wildcard_ip and ip is not None:
            if set(ip) == wildcard_ip:
                # Имя резолвится ровно в wildcard-IP это фантом,
                # такого поддомена реально не существует
                results.append((name, None))
                continue
        results.append((name, ip))

    return results
