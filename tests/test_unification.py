"""Тесты для application/unification.py"""

import unittest
from unittest.mock import patch

from subdomain_enum.application.unification import unification_names


class TestUnificationNames(unittest.TestCase):

    @patch("subdomain_enum.application.unification.resolve_domain")
    def test_simple_no_filter(self, mock_resolve):
        #Без wildcard_ip фильтр не применяется
        mock_resolve.side_effect = [
            ["1.1.1.1"],
            ["2.2.2.2"],
            None,
        ]

        result = unification_names(["a.com", "b.com", "c.com"])

        self.assertEqual(result, [
            ("a.com", ["1.1.1.1"]),
            ("b.com", ["2.2.2.2"]),
            ("c.com", None),
        ])

    @patch("subdomain_enum.application.unification.resolve_domain")
    def test_empty_names(self, mock_resolve):
        #Пустой список имён пустой результат
        result = unification_names([])

        self.assertEqual(result, [])
        mock_resolve.assert_not_called()

    @patch("subdomain_enum.application.unification.resolve_domain")
    def test_wildcard_filter(self, mock_resolve):
        #Имена с wildcard-IP помечаются как None
        #Все имена резолвятся в wildcard-IP
        mock_resolve.return_value = ["213.180.204.242"]

        wildcard_ip = {"213.180.204.242"}
        result = unification_names(
            ["a.yandex.ru", "b.yandex.ru"],
            wildcard_ip=wildcard_ip,
        )

        #Оба имени фантомы, ip = None
        self.assertEqual(result, [
            ("a.yandex.ru", None),
            ("b.yandex.ru", None),
        ])

    @patch("subdomain_enum.application.unification.resolve_domain")
    def test_wildcard_filter_partial(self, mock_resolve):
        #Только совпадающие с wildcard имена фильтруются
        mock_resolve.side_effect = [
            ["213.180.204.242"],   # wildcard → фантом
            ["1.1.1.1"],           # реальный
            ["213.180.204.242"],   # wildcard → фантом
        ]

        wildcard_ip = {"213.180.204.242"}
        result = unification_names(
            ["a.yandex.ru", "real.yandex.ru", "b.yandex.ru"],
            wildcard_ip=wildcard_ip,
        )

        self.assertEqual(result, [
            ("a.yandex.ru", None),
            ("real.yandex.ru", ["1.1.1.1"]),
            ("b.yandex.ru", None),
        ])

    @patch("subdomain_enum.application.unification.resolve_domain")
    def test_no_wildcard_ip_none(self, mock_resolve):
        #wildcard_ip=None фильтр не применяется
        mock_resolve.return_value = ["1.1.1.1"]

        result = unification_names(["a.com"], wildcard_ip=None)

        self.assertEqual(result, [("a.com", ["1.1.1.1"])])

    @patch("subdomain_enum.application.unification.resolve_domain")
    def test_wildcard_ip_empty(self, mock_resolve):
        #wildcard_ip=set() фильтр не применяется
        mock_resolve.return_value = ["1.1.1.1"]

        result = unification_names(["a.com"], wildcard_ip=set())

        self.assertEqual(result, [("a.com", ["1.1.1.1"])])

    @patch("subdomain_enum.application.unification.resolve_domain")
    def test_multiple_wildcard_ip(self, mock_resolve):
        #Wildcard может вернуть несколько IP и все должны совпасть
        mock_resolve.return_value = ["1.1.1.1", "2.2.2.2"]

        wildcard_ip = {"1.1.1.1", "2.2.2.2"}
        result = unification_names(["a.com"], wildcard_ip=wildcard_ip)

        self.assertEqual(result, [("a.com", None)])

    @patch("subdomain_enum.application.unification.resolve_domain")
    def test_partial_ip_not_filtered(self, mock_resolve):
        #Частичное совпадение IP НЕ фильтруется
        mock_resolve.return_value = ["1.1.1.1", "3.3.3.3"]

        wildcard_ip = {"1.1.1.1", "2.2.2.2"}
        result = unification_names(["a.com"], wildcard_ip=wildcard_ip)

        self.assertEqual(result, [("a.com", ["1.1.1.1", "3.3.3.3"])])

    @patch("subdomain_enum.application.unification.resolve_domain")
    def test_order_preserved(self, mock_resolve):
        #Порядок сохраняется
        mock_resolve.return_value = None

        names = ["c.com", "a.com", "b.com"]
        result = unification_names(names)

        result_names = [name for name, _ in result]
        self.assertEqual(result_names, names)

    @patch("subdomain_enum.application.unification.resolve_domain")
    def test_timeout_and_workers_passed(self, mock_resolve):
        #timeout доходит до resolve_domain
        mock_resolve.return_value = None

        unification_names(["a.com"], timeout=5.0, max_workers=10)

        _, kwargs = mock_resolve.call_args
        self.assertEqual(kwargs.get("timeout"), 5.0)


if __name__ == "__main__":
    unittest.main()