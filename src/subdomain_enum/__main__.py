import socket
import sys


def resolve_domain(domain: str, timeout: float) -> str | None:

    socket.setdefaulttimeout(timeout)
    try:
        results = socket.getaddrinfo(domain, None)
    except socket.gaierror:
        return None
    except OSError:
        return None
    if not results:
        return None

    # Первый кортеж: (family, type, proto, canonname, sockaddr)
    # sockaddr для IPv4 — ('8.6.112.0', 0), для IPv6 — ('2606:...', 0, 0, 0)
    # В обоих случаях [0] — это IP.
    first = results[0]
    sockaddr = first[4]
    return sockaddr[0]


def load_wordlist(path: str) -> list[str]:
    words: list[str] = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            word = line.strip()

            words.append(word)

    return words

def enumerate_subdomains(domain: str, words: list[str], timeout: float = 2.0) -> list[tuple[str, str | None]]:
    """
    Принимает:
        domain: базовый домен
        words: список слов поддоменов
        timeout: таймаут DNS-запроса, по умолчанию 2.0

    Возвращает:
        список кортежей (полное_имя, IP_или_None).
    """

    results: list[tuple[str, str | None]] = []

    for word in words:
        full_name = f"{word}.{domain}"

        ip = resolve_domain(full_name, timeout)

        results.append((full_name, timeout))

    return results
        


def main() -> int:
    if len(sys.argv) != 2:
        print("Использование: python -m subdomain_enum <домен>", file=sys.stderr)
        return 1

    domain = sys.argv[1]
    ip = resolve_domain(domain)

    if ip is None:
        print(f"{domain}\tN/A")
    else:
        print(f"{domain}\t{ip}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
