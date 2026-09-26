"""Тесты для infrastructure/ctlogs_ru.py"""

import json
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

from subdomain_enum.infrastructure.ctlogs_ru import fetch_subdomains_ru


class TestFetchSubdomainsRu(unittest.TestCase):

    def _mock_response(self, data):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(data).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        return mock_response

    @patch("subdomain_enum.infrastructure.ctlogs_ru.urllib.request.urlopen")
    def test_success(self, mock_urlopen):
        #Парсинг common_name и name_value
        data = [
            {"common_name": "dev.bank.yandex.ru", "name_value": "dev.bank.yandex.ru"},
            {"common_name": "api.yandex.ru", "name_value": "api.yandex.ru"},
        ]
        mock_urlopen.return_value = self._mock_response(data)

        result = fetch_subdomains_ru("yandex.ru")

        self.assertEqual(result, ["api.yandex.ru", "dev.bank.yandex.ru"])

    @patch("subdomain_enum.infrastructure.ctlogs_ru.urllib.request.urlopen")
    def test_name_value_multiple(self, mock_urlopen):
        #name_value с \\n — несколько имён
        data = [
            {
                "common_name": "www.yandex.ru",
                "name_value": "www.yandex.ru\napi.yandex.ru\nmail.yandex.ru",
            },
        ]
        mock_urlopen.return_value = self._mock_response(data)

        result = fetch_subdomains_ru("yandex.ru")

        self.assertEqual(result, ["api.yandex.ru", "mail.yandex.ru", "www.yandex.ru"])

    @patch("subdomain_enum.infrastructure.ctlogs_ru.urllib.request.urlopen")
    def test_common_name_only(self, mock_urlopen):
        #Если name_value пустое, берём common_name
        data = [{"common_name": "www.yandex.ru", "name_value": ""}]
        mock_urlopen.return_value = self._mock_response(data)

        result = fetch_subdomains_ru("yandex.ru")

        self.assertEqual(result, ["www.yandex.ru"])

    @patch("subdomain_enum.infrastructure.ctlogs_ru.urllib.request.urlopen")
    def test_deduplication(self, mock_urlopen):
        #Дубликаты между common_name и name_value убираются
        data = [
            {"common_name": "www.yandex.ru", "name_value": "www.yandex.ru"},
        ]
        mock_urlopen.return_value = self._mock_response(data)

        result = fetch_subdomains_ru("yandex.ru")

        self.assertEqual(result, ["www.yandex.ru"])

    @patch("subdomain_enum.infrastructure.ctlogs_ru.urllib.request.urlopen")
    def test_strips_wildcard(self, mock_urlopen):
        #*.yandex.ru -> yandex.ru
        data = [{"common_name": "*.yandex.ru", "name_value": ""}]
        mock_urlopen.return_value = self._mock_response(data)

        result = fetch_subdomains_ru("yandex.ru")

        self.assertEqual(result, ["yandex.ru"])

    @patch("subdomain_enum.infrastructure.ctlogs_ru.urllib.request.urlopen")
    def test_filters_other_domains(self, mock_urlopen):
        #Имена не из нашего домена отбрасываются
        data = [
            {"common_name": "www.yandex.ru", "name_value": "www.google.com"},
        ]
        mock_urlopen.return_value = self._mock_response(data)

        result = fetch_subdomains_ru("yandex.ru")

        self.assertEqual(result, ["www.yandex.ru"])

    @patch("subdomain_enum.infrastructure.ctlogs_ru.urllib.request.urlopen")
    def test_network_error(self, mock_urlopen):
        #URLError -> пустой список
        mock_urlopen.side_effect = urllib.error.URLError("network down")

        result = fetch_subdomains_ru("yandex.ru")

        self.assertEqual(result, [])

    @patch("subdomain_enum.infrastructure.ctlogs_ru.urllib.request.urlopen")
    def test_invalid_json(self, mock_urlopen):
        #Битый JSON -> пустой список
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html>error</html>"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = fetch_subdomains_ru("yandex.ru")

        self.assertEqual(result, [])

    @patch("subdomain_enum.infrastructure.ctlogs_ru.urllib.request.urlopen")
    def test_data_not_list(self, mock_urlopen):
        #JSON не список -> пустой список
        mock_urlopen.return_value = self._mock_response({"rows": []})

        result = fetch_subdomains_ru("yandex.ru")

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()