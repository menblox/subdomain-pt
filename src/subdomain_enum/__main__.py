import socket
import sys


def resolve_domain(domain: str, timeout: float = 2.0) -> str | None:

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
