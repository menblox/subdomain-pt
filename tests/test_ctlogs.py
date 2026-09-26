"""Тесты для infrastructure/ctlogs.py"""

import json
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

from subdomain_enum.infrastructure.ctlogs import fetch_subdomains


class TestFetchSubdomains(unittest.TestCase):
    def _mock_response(self, data):
        # Создаёт мок HTTP ответа с заданным JSON
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(data).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        return mock_response

    @patch("subdomain_enum.infrastructure.ctlogs.urllib.request.urlopen")
    def test_success(self, mock_urlopen):
        # Успешный парсинг одной записи
        data = {
            "rows": [
                {"match": "www.example.com"},
                {"match": "api.example.com"},
            ],
        }
        mock_urlopen.return_value = self._mock_response(data)

        result = fetch_subdomains("example.com")

        self.assertEqual(result, ["api.example.com", "www.example.com"])

    @patch("subdomain_enum.infrastructure.ctlogs.urllib.request.urlopen")
    def test_filters_other_domains(self, mock_urlopen):
        # Имена не из нашего домена отбрасываются
        data = {
            "rows": [
                {"match": "www.example.com"},
                {"match": "www.other.com"},
                {"match": "notexample.com"},
            ],
        }
        mock_urlopen.return_value = self._mock_response(data)

        result = fetch_subdomains("example.com")

        self.assertEqual(result, ["www.example.com"])

    @patch("subdomain_enum.infrastructure.ctlogs.urllib.request.urlopen")
    def test_strips_wildcard_prefix(self, mock_urlopen):
        # *.example.com -> example.com
        data = {
            "rows": [
                {"match": "*.example.com"},
                {"match": "*.api.example.com"},
            ],
        }
        mock_urlopen.return_value = self._mock_response(data)

        result = fetch_subdomains("example.com")

        self.assertEqual(result, ["api.example.com", "example.com"])

    @patch("subdomain_enum.infrastructure.ctlogs.urllib.request.urlopen")
    def test_deduplication(self, mock_urlopen):
        # Одинаковые имена не дублируются
        data = {
            "rows": [
                {"match": "www.example.com"},
                {"match": "www.example.com"},
                {"match": "WWW.EXAMPLE.COM"},
            ],
        }
        mock_urlopen.return_value = self._mock_response(data)

        result = fetch_subdomains("example.com")

        self.assertEqual(result, ["www.example.com"])

    @patch("subdomain_enum.infrastructure.ctlogs.urllib.request.urlopen")
    def test_lowercase(self, mock_urlopen):
        # Имена приводятся к нижнему регистру
        data = {"rows": [{"match": "WWW.Example.COM"}]}
        mock_urlopen.return_value = self._mock_response(data)

        result = fetch_subdomains("example.com")

        self.assertEqual(result, ["www.example.com"])

    @patch("subdomain_enum.infrastructure.ctlogs.urllib.request.urlopen")
    def test_skips_empty_match(self, mock_urlopen):
        # Пустые match пропускаются
        data = {
            "rows": [
                {"match": ""},
                {"match": "www.example.com"},
                {"match": "   "},
            ],
        }
        mock_urlopen.return_value = self._mock_response(data)

        result = fetch_subdomains("example.com")

        self.assertEqual(result, ["www.example.com"])

    @patch("subdomain_enum.infrastructure.ctlogs.urllib.request.urlopen")
    def test_skips_non_dict_rows(self, mock_urlopen):
        # Записи не-словари пропускаются
        data = {"rows": ["string", 42, {"match": "www.example.com"}]}
        mock_urlopen.return_value = self._mock_response(data)

        result = fetch_subdomains("example.com")

        self.assertEqual(result, ["www.example.com"])

    @patch("subdomain_enum.infrastructure.ctlogs.urllib.request.urlopen")
    def test_skips_non_string_match(self, mock_urlopen):
        # match не-строка пропускается
        data = {"rows": [{"match": 42}, {"match": "www.example.com"}]}
        mock_urlopen.return_value = self._mock_response(data)

        result = fetch_subdomains("example.com")

        self.assertEqual(result, ["www.example.com"])

    @patch("subdomain_enum.infrastructure.ctlogs.urllib.request.urlopen")
    def test_network_error(self, mock_urlopen):
        # URLError -> пустой список
        mock_urlopen.side_effect = urllib.error.URLError("network down")

        result = fetch_subdomains("example.com")

        self.assertEqual(result, [])

    @patch("subdomain_enum.infrastructure.ctlogs.urllib.request.urlopen")
    def test_timeout(self, mock_urlopen):
        # TimeoutError -> пустой список
        mock_urlopen.side_effect = TimeoutError()

        result = fetch_subdomains("example.com")

        self.assertEqual(result, [])

    @patch("subdomain_enum.infrastructure.ctlogs.urllib.request.urlopen")
    def test_invalid_json(self, mock_urlopen):
        # Битый JSON -> пустой список
        mock_response = MagicMock()
        mock_response.read.return_value = b"not a json"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = fetch_subdomains("example.com")

        self.assertEqual(result, [])

    @patch("subdomain_enum.infrastructure.ctlogs.urllib.request.urlopen")
    def test_data_not_dict(self, mock_urlopen):
        # JSON не объект -> пустой список
        mock_urlopen.return_value = self._mock_response([1, 2, 3])

        result = fetch_subdomains("example.com")

        self.assertEqual(result, [])

    @patch("subdomain_enum.infrastructure.ctlogs.urllib.request.urlopen")
    def test_rows_not_list(self, mock_urlopen):
        # rows не список -> пустой список
        mock_urlopen.return_value = self._mock_response({"rows": "not a list"})

        result = fetch_subdomains("example.com")

        self.assertEqual(result, [])

    @patch("subdomain_enum.infrastructure.ctlogs.urllib.request.urlopen")
    def test_empty_rows(self, mock_urlopen):
        # Пустой rows -> пустой список
        mock_urlopen.return_value = self._mock_response({"rows": []})

        result = fetch_subdomains("example.com")

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
