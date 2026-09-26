"""Тесты для application/wildcard.py"""

import unittest
from unittest.mock import patch

from subdomain_enum.application.wildcard import detect_wildcard


class TestDetectWildcard(unittest.TestCase):
    @patch("subdomain_enum.application.wildcard.resolve_domain")
    def test_wildcard_detected(self, mock_resolve):
        # Все три случайных имени резолвятся в один IP wildcard
        mock_resolve.return_value = ["213.180.204.242"]

        result = detect_wildcard("yandex.ru")

        self.assertEqual(result, {"213.180.204.242"})
        self.assertEqual(mock_resolve.call_count, 3)

    @patch("subdomain_enum.application.wildcard.resolve_domain")
    def test_no_wildcard(self, mock_resolve):
        # Все три имени не резолвятся wildcard нет
        mock_resolve.return_value = None

        result = detect_wildcard("github.com")

        self.assertIsNone(result)
        self.assertEqual(mock_resolve.call_count, 3)

    @patch("subdomain_enum.application.wildcard.resolve_domain")
    def test_different_ip_no_wildcard(self, mock_resolve):
        # Имена резолвятся в разные IP это не wildcard
        mock_resolve.side_effect = [
            ["1.1.1.1"],
            ["2.2.2.2"],
            ["3.3.3.3"],
        ]

        result = detect_wildcard("github.com")

        self.assertIsNone(result)

    @patch("subdomain_enum.application.wildcard.resolve_domain")
    def test_partial_resolve_no_wildcard(self, mock_resolve):
        # Одно имя не резолвится wildcard нет
        mock_resolve.side_effect = [
            ["1.1.1.1"],
            None,
            ["1.1.1.1"],
        ]

        result = detect_wildcard("github.com")

        self.assertIsNone(result)

    @patch("subdomain_enum.application.wildcard.resolve_domain")
    def test_multiple_ip(self, mock_resolve):
        # Wildcard может вернуть несколько IP все должны совпасть
        mock_resolve.return_value = ["1.1.1.1", "2.2.2.2"]

        result = detect_wildcard("github.com")

        self.assertEqual(result, {"1.1.1.1", "2.2.2.2"})

    @patch("subdomain_enum.application.wildcard.resolve_domain")
    def test_order_ip(self, mock_resolve):
        # Порядок IP не важен сравниваем множества
        mock_resolve.side_effect = [
            ["1.1.1.1", "2.2.2.2"],
            ["2.2.2.2", "1.1.1.1"],
            ["1.1.1.1", "2.2.2.2"],
        ]

        result = detect_wildcard("github.com")

        self.assertEqual(result, {"1.1.1.1", "2.2.2.2"})

    @patch("subdomain_enum.application.wildcard.resolve_domain")
    def test_custom_quantity(self, mock_resolve):
        # Можно задать количество проб
        mock_resolve.return_value = ["1.1.1.1"]

        result = detect_wildcard("github.com", quantity=5)

        self.assertEqual(result, {"1.1.1.1"})
        self.assertEqual(mock_resolve.call_count, 5)

    @patch("subdomain_enum.application.wildcard.resolve_domain")
    def test_random_names(self, mock_resolve):
        # Каждый вызов использует новое случайное имя
        mock_resolve.return_value = ["1.1.1.1"]

        detect_wildcard("github.com", quantity=3)

        # Собираем все аргументы, с которыми вызывался мок
        called_names = [call.args[0] for call in mock_resolve.call_args_list]

        # Все имена должны быть разными
        self.assertEqual(len(called_names), len(set(called_names)))

        # Все имена должны оканчиваться на .github.com
        for name in called_names:
            self.assertTrue(name.endswith(".github.com"))


if __name__ == "__main__":
    unittest.main()
