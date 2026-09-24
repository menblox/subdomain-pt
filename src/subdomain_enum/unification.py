"""Объединение источников имён и DNS-резолва"""

import concurrent.futures
from functools import partial

from subdomain_enum.dns import resolve_domain

def unification_names(names: list[str], timeout: float = 2.0, max_workers: int = 30) -> list[tuple[str, list[str] | None]]:
    """Резолвит список имён в IP-адреса параллельно"""

    if not names:
        return []
    
    resolver = partial(resolve_domain, timeout=timeout)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        ip_list = list(ex.map(resolver, names))

    return list(zip(names, ip_list, strict=True))  # Соединяем имена с их IP в пары