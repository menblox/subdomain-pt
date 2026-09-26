"""DNS-резолвер с soft-timeout через ThreadPoolExecutor."""

import concurrent.futures
import socket


def resolve_domain(domain: str, timeout: float = 2.0) -> list[str]:
    # Резолвит домен в список уникальных IP-адресов (IPv4 + IPv6)

    # Запуск getaddrinfo в отдельном потоке, чтобы можно было прервать ожидание по таймауту#
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        # принимает: (socket.getaddrinfo, сам домен, порт(не указываем))
        future = executor.submit(socket.getaddrinfo, domain, None)

        try:
            results = future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:  # таймаут
            return None
        except socket.gaierror:
            return None
        except OSError:
            return None

    if not results:
        return None

    # Собираем уникальные IP-адреса
    # Каждый результат - это кортеж:
    # (family, type, proto, canonname, sockaddr)
    # sockaddr[0] - это IP (строка)

    ip: set[str] = set()
    for result in results:
        sockaddr = result[4]
        ip.add(sockaddr[0])

    if not ip:
        return None

    return sorted(ip)
