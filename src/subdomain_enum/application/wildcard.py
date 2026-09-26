"""Детект wildcard DNS."""

import random
import string

from subdomain_enum.infrastructure.dns import resolve_domain

RANDOM_NAME_LENGTH = 12
DEFAULT_QUANTITY = 3


def _generate_random_name(lenght: int = RANDOM_NAME_LENGTH) -> str:
    # Генерирует случайное имя из букв и цифр
    albet = string.ascii_lowercase + string.digits
    return "".join(random.choices(albet, k=lenght))


def detect_wildcard(
    domain: str, timeout: float = 2.0, quantity: int = DEFAULT_QUANTITY
) -> set[str] | None:
    # Определяет, есть ли у домена wildcard-запись

    results: list[list[str] | None] = []

    for _ in range(quantity):
        random_name = _generate_random_name()
        full_name = f"{random_name}.{domain}"
        ip = resolve_domain(full_name, timeout=timeout)
        results.append(ip)

    if any(ip is None for ip in results):
        return None

    # Все имена резолвятся. Проверяем, что IP одинаковые. Берём первое и сравниваем с остальными
    first = set(results[0])
    for ip in results[1:]:
        if set(ip) != first:
            return None

    return first
