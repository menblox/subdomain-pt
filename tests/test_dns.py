"""Тесты для infrastructure/dns.py"""

import socket
import unittest
from unittest.mock import patch

from subdomain_enum.infrastructure.dns import resolve_domain


class TestResolveDomain(unittest.TestCase):
    @patch("subdomain_enum.infrastructure.dns.socket.getaddrinfo")
    def test_success_ipv4(self, mock_getaddrinfo):
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("140.82.121.4", 0))
        ]

        result = resolve_domain("example.com")

        self.assertEqual(result, ["140.82.121.4"])

    @patch("subdomain_enum.infrastructure.dns.socket.getaddrinfo")
    def test_success_multiple_ip(self, mock_getaddrinfo):
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.1.1.1", 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("2.2.2.2", 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("3.3.3.3", 0)),
        ]

        result = resolve_domain("example.com")

        self.assertEqual(result, ["1.1.1.1", "2.2.2.2", "3.3.3.3"])

    @patch("subdomain_enum.infrastructure.dns.socket.getaddrinfo")
    def test_deduplication(self, mock_getaddrinfo):
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.1.1.1", 0)),
            (socket.AF_INET, socket.SOCK_DGRAM, 17, "", ("1.1.1.1", 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("2.2.2.2", 0)),
        ]

        result = resolve_domain("example.com")

        self.assertEqual(result, ["1.1.1.1", "2.2.2.2"])

    @patch("subdomain_enum.infrastructure.dns.socket.getaddrinfo")
    def test_ipv4_and_ipv6(self, mock_getaddrinfo):
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.1.1.1", 0)),
            (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("2606:2800::1", 0, 0, 0)),
        ]

        result = resolve_domain("example.com")

        self.assertIn("1.1.1.1", result)
        self.assertIn("2606:2800::1", result)
        self.assertEqual(len(result), 2)

    @patch("subdomain_enum.infrastructure.dns.socket.getaddrinfo")
    def test_gaierror(self, mock_getaddrinfo):
        mock_getaddrinfo.side_effect = socket.gaierror("Name or service not known")

        result = resolve_domain("nonexistent-xyz.com")

        self.assertIsNone(result)

    @patch("subdomain_enum.infrastructure.dns.socket.getaddrinfo")
    def test_oserror(self, mock_getaddrinfo):
        mock_getaddrinfo.side_effect = OSError("Network is unreachable")

        result = resolve_domain("example.com")

        self.assertIsNone(result)

    @patch("subdomain_enum.infrastructure.dns.socket.getaddrinfo")
    def test_empty_result(self, mock_getaddrinfo):
        mock_getaddrinfo.return_value = []

        result = resolve_domain("example.com")

        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()