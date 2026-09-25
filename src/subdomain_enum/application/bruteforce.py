"""Брутфорс поддоменов по словарю с параллельным резолвом"""

import concurrent.futures
from functools import partial

from subdomain_enum.infrastructure.dns import resolve_domain


def load_wordlist(path:str) -> list[str]:
    #Читает файл-словарь и возвращает список слов
    words: list[str] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            word = line.strip()
            if not word or word.startswith("#"):
                continue
            words.append(word)

    return words

def bruteforce(
        domain: str, 
        words: list[str], 
        timeout: float = 2.0, 
        max_workers: int = 30
    ) -> list[tuple[str, list[str] | None]]:
    #Перебирает слова из списка, формируя поддомены

    if not words:
        return []

    full_names = [f"{word}.{domain}" for word in words]

    resolver = partial(resolve_domain, timeout=timeout)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        ip_list = list(ex.map(resolver, full_names))

    return list(zip(full_names, ip_list, strict=True))